from infrastructure.collectors.ssh_collector import SSHCollector
from infrastructure.models import KPI, MetricSample
from infrastructure.parsers.cpu_parser import parse_cpu_usage


def collect_cpu(server):

    kpi = KPI.objects.filter(
        category="CPU",
        enabled=True
    ).order_by("execution_order").first()

    if not kpi:
        raise ValueError("CPU KPI not configured")

    collector = SSHCollector(server)

    try:

        collector.connect()

        result = collector.execute(
            kpi.linux_command
        )

        if not result["success"]:

            return MetricSample.objects.create(
                server=server,
                kpi=kpi,
                metric_name="cpu_usage",
                status="FAILED",
                raw_output=result["stdout"],
                error_message=result["stderr"]
            )

        cpu_value = parse_cpu_usage(
            result["stdout"]
        )

        return MetricSample.objects.create(
            server=server,
            kpi=kpi,
            metric_name="cpu_usage",
            value=cpu_value,
            raw_output=result["stdout"],
            status="SUCCESS"
        )

    except Exception as exc:

        return MetricSample.objects.create(
            server=server,
            kpi=kpi,
            metric_name="cpu_usage",
            status="FAILED",
            error_message=str(exc)
        )

    finally:

        collector.close()