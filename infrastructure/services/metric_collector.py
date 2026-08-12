# infrastructure/services/metric_collector.py

import csv
import re

from infrastructure.config.kpi_config import KPI_CONFIG

from infrastructure.models import (
    MetricSample,
    ProcessMetric,
    ServiceMetric,
    NetworkMetric,
)


from infrastructure.services.server_service import (
    get_or_create_local_server
)

from infrastructure.collectors.local_collector import (
    LocalCollector
)

from infrastructure.collectors.os_detector import (
    get_operating_system
)


class MetricCollector:

    def __init__(self):

        self.os_type = get_operating_system()

        self.collector = LocalCollector(
            self.os_type
        )

    # ==========================================================
    # GET OS COMMAND
    # ==========================================================

    def get_command(self, kpi):

        if self.os_type == "LINUX":

            return kpi.get("linux")

        if self.os_type == "WINDOWS":

            return kpi.get("windows")

        return None

    # ==========================================================
    # GET DETAIL COMMAND
    # ==========================================================

    def get_detail_command(self, kpi):

        if self.os_type == "LINUX":
            return kpi.get("detail_linux")

        if self.os_type == "WINDOWS":
            return kpi.get("detail_windows")

        return None

    # ==========================================================
    # FORMAT NUMBER
    #
    # Examples:
    # 91.0            -> 91

    def format_number(self, value):

        value = str(value).strip()

        if not value:
            return None

        try:

            number = round(float(value), 2)

            # Remove unnecessary .0
            if number.is_integer():

                return str(int(number))

            return str(number)

        except ValueError:

            return value

    # ==========================================================
    # FORMAT UPTIME
    #
    # Output:
    # 3 h 4 min
    # ==========================================================

    def format_uptime(self, seconds):

        try:

            seconds = int(float(seconds))

        except (
            ValueError,
            TypeError
        ):

            return None

        days = seconds // 86400

        hours = (
            seconds % 86400
        ) // 3600

        minutes = (
            seconds % 3600
        ) // 60

        if days > 0:

            return (
                f"{days} d "
                f"{hours} h "
                f"{minutes} min"
            )

        return (
            f"{hours} h "
            f"{minutes} min"
        )

    # ==========================================================
    # PARSE SINGLE SCALAR VALUE
    # ==========================================================

    def parse_value(
        self,
        output,
        metric_name=None
    ):

        if output is None:

            return None

        text = str(output).strip()

        if not text:

            return None

        # ------------------------------------------------------
        # Numeric pattern
        # ------------------------------------------------------

        numeric_pattern = re.compile(
            r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)"
            r"(?:[eE][+-]?\d+)?$"
        )

        # ------------------------------------------------------
        # Text/status values that we allow
        # ------------------------------------------------------

        text_status_pattern = re.compile(
            r"^[A-Za-z][A-Za-z0-9 _-]*$"
        )

        # ------------------------------------------------------
        # Process output line by line
        # ------------------------------------------------------

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        # ------------------------------------------------------
        # FIRST PRIORITY:
        # exact scalar output
        # ------------------------------------------------------

        for line in reversed(lines):

            clean = (
                line
                .strip()
                .strip('"')
                .strip()
            )

            if not clean:

                continue

            # ==================================================
            # BOOLEAN
            # ==================================================

            if clean.lower() == "true":

                return "True"

            if clean.lower() == "false":

                return "False"

            # ==================================================
            # EXACT NUMBER
            # ==================================================

            normalized = clean.replace(
                ",",
                ""
            )

            if numeric_pattern.fullmatch(
                normalized
            ):

                return self.format_number(
                    normalized
                )


            if text_status_pattern.fullmatch(
                clean
            ):

                allowed_statuses = {
                    "healthy",
                    "unhealthy",
                    "unknown",
                    "running",
                    "stopped",
                    "active",
                    "inactive",
                    "enabled",
                    "disabled",
                    "passed",
                    "failed",
                    "resolved",
                    "available",
                    "unavailable",
                    "online",
                    "offline",
                    "connected",
                    "disconnected"
                }

                if clean.lower() in allowed_statuses:

                    return clean

        # ------------------------------------------------------
        # SECOND PRIORITY:
        # typeperf / CSV-like output
        #
        # Example:
        #
        # "08/07/2026 11:28:13.741","12.641489"
        #
        # Take ONLY final CSV field.
        # ------------------------------------------------------

        for line in reversed(lines):

            if "," not in line:

                continue

            try:

                row = next(
                    csv.reader(
                        [line]
                    )
                )

            except (
                csv.Error,
                StopIteration
            ):

                continue

            if not row:

                continue

            last_value = (
                row[-1]
                .strip()
                .strip('"')
            )

            last_value = (
                last_value
                .replace(",", "")
            )

            if numeric_pattern.fullmatch(
                last_value
            ):

                return self.format_number(
                    last_value
                )

        # ------------------------------------------------------
        # No valid scalar/status value
        # ------------------------------------------------------

        return None

    # ==========================================================
    # SAVE METRIC SAMPLE
    # ==========================================================

    def save_metric(
        self,
        server,
        category,
        metric_name,
        value,
        raw_output,
        status,
        error_message=None
    ):

        metric_type = (
            f"{category} - {metric_name}"
        )

        metric = MetricSample.objects.create(

            server=server,

            metric_type=metric_type,

            metric_value=value,

            raw_output=raw_output,

            status=status,

            error_message=error_message
        )

        print(
            f"SAVED MetricSample: "
            f"{metric.metric_type} = "
            f"{metric.metric_value} "
            f"[{metric.status}]"
        )

        return metric

    # ==========================================================
    # PARSE PROCESS DETAIL OUTPUT
    # ==========================================================
    def parse_process_details(self, output):

        rows = []

        if not output:
            return rows

        reader = csv.DictReader(
            output.splitlines()
        )

        for row in reader:

            try:

                memory_mb = None

                if row.get("WorkingSet64"):
                   memory_mb = round(
                        int(row["WorkingSet64"]) / (1024 * 1024),
                        2
                )

                cpu_percent = None

                if row.get("CpuPercent"):
                    cpu_percent = float(
                        row["CpuPercent"]
                    )

                handle_count = None

                if row.get("Handles"):
                    handle_count = int(
                        row["Handles"]
                    )

                process_id = None

                if row.get("Id"):
                    process_id = int(
                        row["Id"]
                    )

                rows.append({
                    "process_name": row.get(
                        "ProcessName"
                    ),

                    "process_id": process_id,

                    "cpu_percent": cpu_percent,

                    "memory_mb": memory_mb,

                    "handle_count": handle_count,
                })

            except (
                ValueError,
                TypeError
            ) as exc:

                print(
                    f"Process parse error: {exc}"
                )

                continue

        return rows
    # ==========================================================
    # SAVE PROCESS DETAILS
    # ==========================================================

    def save_process_metrics(self, server, rows):

        objects = []

        for row in rows:

            if not row.get("process_name"):
                continue

            objects.append(
                ProcessMetric(
                    server=server,

                    process_name=row.get(
                        "process_name"
                    ),

                    process_id=row.get(
                        "process_id"
                    ),

                    cpu_percent=row.get(
                        "cpu_percent"
                    ),

                    memory_mb=row.get(
                        "memory_mb"
                    ),

                    handle_count=row.get(
                        "handle_count"
                    ),
                )
            )

        if objects:
            ProcessMetric.objects.bulk_create(
                objects
            )

        print(
            f"SAVED ProcessMetric rows: "
            f"{len(objects)}"
        )

        return len(objects)
    # ==========================================================
    # PARSE SERVICE DETAIL OUTPUT
    # ==========================================================

    def parse_service_details(self, output):

        rows = []

        if not output:
            return rows

        text = str(output).strip()

        if not text:
            return rows

        # Windows CSV output
        if text.lstrip().startswith('"Name"'):

            try:
                reader = csv.DictReader(text.splitlines())

                for row in reader:

                    service_name = (
                        row.get("Name") or ""
                    ).strip()

                    if not service_name:
                        continue

                    rows.append({
                        "service_name": service_name,
                        "display_name": (
                            row.get("DisplayName") or ""
                        ).strip() or None,
                        "status": (
                            row.get("State") or ""
                        ).strip() or None,
                        "startup_type": (
                            row.get("StartMode") or ""
                        ).strip() or None,
                    })

            except (csv.Error, ValueError):
                pass

            return rows

        # Linux format:
        # service_name|display_name|status|startup_type
        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            parts = line.split("|", 3)

            if len(parts) != 4:
                continue

            service_name = parts[0].strip()

            if not service_name:
                continue

            rows.append({
                "service_name": service_name,
                "display_name": parts[1].strip() or None,
                "status": parts[2].strip() or None,
                "startup_type": parts[3].strip() or None,
            })

        return rows

    # ==========================================================
    # SAVE SERVICE DETAILS
    # ==========================================================

    def save_service_metrics(self, server, rows):

        objects = []

        for row in rows:

            if not row.get("service_name"):
                continue

            objects.append(
                ServiceMetric(
                    server=server,
                    service_name=row.get("service_name"),
                    display_name=row.get("display_name"),
                    status=row.get("status"),
                    startup_type=row.get("startup_type"),
                )
            )

        if objects:
            ServiceMetric.objects.bulk_create(objects)

        print(
            f"SAVED ServiceMetric rows: {len(objects)}"
        )

        return len(objects)

    # ==========================================================
    # PARSE NETWORK DETAIL OUTPUT
    # ==========================================================

    def parse_network_details(self, output, protocol):

        rows = []

        if not output:
            return rows

        text = str(output).strip()

        if not text:
            return rows

        # Windows CSV output
        if text.lstrip().startswith('"LocalAddress"'):

            try:
                reader = csv.DictReader(text.splitlines())

                for row in reader:

                    rows.append({
                        "protocol": protocol,
                        "local_address": (
                            row.get("LocalAddress") or ""
                        ).strip() or None,
                        "local_port": self.parse_port(
                            row.get("LocalPort")
                        ),
                        "remote_address": (
                            row.get("RemoteAddress") or ""
                        ).strip() or None,
                        "remote_port": self.parse_port(
                            row.get("RemotePort")
                        ),
                    })

            except (csv.Error, ValueError):
                pass

            return rows

        # Linux ss output.
        # Example:
        # ESTAB 0 0 127.0.0.1:5000 10.0.0.2:443
        # UDP may have a similar structure.
        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            # Skip the ss header.
            if line.lower().startswith("state "):
                continue

            parts = line.split()

            if len(parts) < 2:
                continue

            # ss normally has State, Recv-Q, Send-Q, Local, Peer.
            if len(parts) >= 5:
                local_endpoint = parts[-2]
                remote_endpoint = parts[-1]
            else:
                local_endpoint = parts[-2]
                remote_endpoint = parts[-1]

            local_address, local_port = self.split_endpoint(
                local_endpoint
            )

            remote_address, remote_port = self.split_endpoint(
                remote_endpoint
            )

            rows.append({
                "protocol": protocol,
                "local_address": local_address,
                "local_port": local_port,
                "remote_address": remote_address,
                "remote_port": remote_port,
            })

        return rows

    # ==========================================================
    # PARSE PORT
    # ==========================================================

    def parse_port(self, value):

        if value is None:
            return None

        value = str(value).strip()

        if not value or value in ("*", "-", "None"):
            return None

        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    # ==========================================================
    # SPLIT IP:PORT
    # ==========================================================

    def split_endpoint(self, endpoint):

        if endpoint is None:
            return None, None

        endpoint = str(endpoint).strip()

        if not endpoint or endpoint in ("*:*", "-*", "-", "*"):
            return None, None

        # IPv6 in [address]:port format.
        if endpoint.startswith("[") and "]" in endpoint:

            close = endpoint.rfind("]")
            address = endpoint[1:close]
            port = endpoint[close + 1:]

            if port.startswith(":"):
                port = port[1:]

            return (
                address or None,
                self.parse_port(port),
            )

        # Normal IPv4/hostname:port.
        if ":" in endpoint:

            address, port = endpoint.rsplit(":", 1)

            return (
                address or None,
                self.parse_port(port),
            )

        return endpoint, None

    # ==========================================================
    # SAVE NETWORK DETAILS
    # ==========================================================

    def save_network_metrics(self, server, rows):

        objects = []

        for row in rows:

            objects.append(
                NetworkMetric(
                    server=server,
                    protocol=row.get("protocol") or "UNKNOWN",
                    local_address=row.get("local_address"),
                    local_port=row.get("local_port"),
                    remote_address=row.get("remote_address"),
                    remote_port=row.get("remote_port"),
                )
            )

        if objects:
            NetworkMetric.objects.bulk_create(objects)

        print(
            f"SAVED NetworkMetric rows: {len(objects)}"
        )

        return len(objects)

    # ==========================================================
    # COLLECT DETAIL DATA
    # ==========================================================

    def collect_detail_data(
        self,
        server,
        category,
        kpi,
    ):

        detail_command = self.get_detail_command(kpi)

        if not detail_command:
            return

        print()
        print("DETAIL COLLECTION")
        print(f"Detail command: {detail_command}")

        try:
            result = self.collector.execute(
                detail_command
            )

        except Exception as exc:
            print(
                f"Detail collector exception: {exc}"
            )
            return

        if not result.get("success"):

            stderr = (
                result.get("stderr", "")
                or ""
            ).strip()

            print(
                "Detail command failed:"
            )
            print(
                stderr or "Detail command execution failed."
            )
            return

        detail_output = (
            result.get("stdout", "")
            or ""
        ).strip()

        if not detail_output:
            print(
                "Detail command returned no data."
            )
            return

        print(
            f"Detail output received: "
            f"{len(detail_output.splitlines())} lines"
        )

        if category == "PROCESSES":

            rows = self.parse_process_details(
                detail_output
            )

            self.save_process_metrics(
                server,
                rows
            )

        elif category == "SERVICES":

            rows = self.parse_service_details(
                detail_output
            )

            self.save_service_metrics(
                server,
                rows
            )

        elif category == "NETWORK":

            protocol = "TCP" if kpi.get("name") == "TCP Connections" else "UDP"

            rows = self.parse_network_details(
                detail_output,
                protocol
            )

            self.save_network_metrics(
                server,
                rows
            )

    # ==========================================================
    # COLLECT ALL KPIs
    # ==========================================================

    def collect(self):

        print("=" * 60)

        print(
            "STARTING KPI COLLECTION"
        )

        print("=" * 60)

        # ======================================================
        # SERVER
        # ======================================================

        server = get_or_create_local_server()

        print(
            f"Server: {server.name}"
        )

        print(
            f"Server ID: {server.id}"
        )

        print(
            f"Operating System: "
            f"{server.operating_system}"
        )

        # ======================================================
        # CATEGORY
        # ======================================================

        for category, kpis in KPI_CONFIG.items():

            print()

            print("#" * 60)

            print(
                f"STARTING CATEGORY: {category}"
            )

            print("#" * 60)

            # --------------------------------------------------
            # Sort by execution order
            # --------------------------------------------------

            sorted_kpis = sorted(
                kpis,
                key=lambda x: x.get(
                    "execution_order",
                    999999
                )
            )

            # ==================================================
            # KPI
            # ==================================================

            for kpi in sorted_kpis:

                print()

                print("-" * 60)

                print(
                    f"Category: {category}"
                )

                print(
                    f"Execution Order: "
                    f"{kpi.get('execution_order')}"
                )

                print(
                    f"KPI: {kpi.get('name')}"
                )

                # ==================================================
                # GET COMMAND
                # ==================================================

                command = self.get_command(
                    kpi
                )

                if not command:

                    message = (
                        f"No {self.os_type} "
                        f"command available."
                    )

                    print(message)

                    self.save_metric(

                        server=server,

                        category=category,

                        metric_name=kpi["name"],

                        value=None,

                        raw_output="",

                        status="NOT_SUPPORTED",

                        error_message=message
                    )

                    continue

                print(
                    f"Command: {command}"
                )

                # ==================================================
                # EXECUTE
                # ==================================================

                try:

                    result = self.collector.execute(
                        command
                    )

                except Exception as exc:

                    error_message = str(exc)

                    print(
                        "Collector exception:"
                    )

                    print(
                        error_message
                    )

                    self.save_metric(

                        server=server,

                        category=category,

                        metric_name=kpi["name"],

                        value=None,

                        raw_output="",

                        status="FAILED",

                        error_message=error_message
                    )

                    continue

                # ==================================================
                # COMMAND SUCCESS
                # ==================================================

                if result.get("success"):

                    raw_output = (
                        result.get(
                            "stdout",
                            ""
                        )
                        or ""
                    ).strip()

                    print(
                        "Command executed successfully."
                    )

                    print(
                        f"Raw output:\n"
                        f"{raw_output}"
                    )

                    # ==================================================
                    # EXISTING SCALAR KPI FLOW
                    # ==================================================

                    value = self.parse_value(
                        raw_output,
                        metric_name=kpi["name"]
                    )

                    # ==================================================
                    # FORMAT UPTIME
                    # ==================================================

                    if (
                        value is not None
                        and
                        kpi["name"].strip().lower()
                        == "uptime"
                    ):

                        value = self.format_uptime(
                            value
                        )

                    print(
                        f"Parsed value: {value}"
                    )

                    # ==================================================
                    # SAVE EXISTING MetricSample
                    # ==================================================

                    if value is not None:

                        self.save_metric(
                            server=server,
                            category=category,
                            metric_name=kpi["name"],
                            value=value,
                            raw_output=raw_output,
                            status="SUCCESS"
                        )

                    else:

                        message = (
                            "Command succeeded, "
                            "but output did not contain "
                            "a valid scalar numeric/status value."
                        )

                        print(
                            message
                        )

                        self.save_metric(
                            server=server,
                            category=category,
                            metric_name=kpi["name"],
                            value=None,
                            raw_output=raw_output,
                            status="PARSE_FAILED",
                            error_message=message
                        )

                    # ==================================================
                    # NEW DETAIL TABLE FLOW
                    # ==================================================
                    # Only KPIs having detail_linux/detail_windows
                    # execute this second command.

                    self.collect_detail_data(
                        server=server,
                        category=category,
                        kpi=kpi
                    )

                # ==================================================
                # COMMAND FAILED
                # ==================================================

                else:

                    stderr = (
                        result.get(
                            "stderr",
                            ""
                        )
                        or ""
                    ).strip()

                    stdout = (
                        result.get(
                            "stdout",
                            ""
                        )
                        or ""
                    ).strip()

                    error_message = (
                        stderr
                        or
                        "Command execution failed."
                    )

                    print(
                        "Command failed:"
                    )

                    print(
                        error_message
                    )

                    self.save_metric(

                        server=server,

                        category=category,

                        metric_name=kpi["name"],

                        value=None,

                        raw_output=(
                            stderr
                            or stdout
                        ),

                        status="FAILED",

                        error_message=error_message
                    )

            # ======================================================
            # CATEGORY COMPLETED
            # ======================================================

            print()

            print(
                f"COMPLETED CATEGORY: {category}"
            )

        # ==========================================================
        # COMPLETE
        # ==========================================================

        print()

        print("=" * 60)

        print(
            "ALL KPI COLLECTION COMPLETED"
        )

        print("=" * 60)