
# infrastructure/services/metric_collector.py

import csv
import re

from infrastructure.config.kpi_config import KPI_CONFIG

from infrastructure.models import MetricSample

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
                    # PARSE
                    # ==================================================

                    value = self.parse_value(

                        raw_output,

                        metric_name=kpi["name"]
                    )

                    # ==================================================
                    # FORMAT UPTIME
                    #
                    # Command returns seconds:
                    #
                    # 11040
                    #
                    # Database stores:
                    #
                    # 3 h 4 min
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
                    # PARSE SUCCESS
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

                    # ==================================================
                    # PARSE FAILED
                    # ==================================================

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
