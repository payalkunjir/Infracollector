from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from infrastructure.services.metric_collector import MetricCollector


scheduler = BackgroundScheduler()


def collect_metrics():
    print("=" * 60)
    print("SCHEDULER: STARTING KPI COLLECTION")
    print("=" * 60)

    try:
        collector = MetricCollector()
        collector.collect()

        print("=" * 60)
        print("SCHEDULER: COLLECTION COMPLETED")
        print("=" * 60)

    except Exception as e:
        print(f"SCHEDULER ERROR: {e}")


def start_scheduler():

    if scheduler.running:
        print("Scheduler is already running.")
        return

    # ==========================================
    # RUN IMMEDIATELY + EVERY 60 SECONDS
    # ==========================================

    scheduler.add_job(
        collect_metrics,
        trigger="interval",
        seconds=60,
        id="infrastructure_kpi_collection",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        next_run_time=datetime.now()
    )

    scheduler.start()

    print("=" * 60)
    print("Infrastructure KPI Scheduler Started")
    print("Collection starts immediately.")
    print("Next collection will run every 60 seconds.")
    print("=" * 60)