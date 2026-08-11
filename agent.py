import os
import sys
import time
import django
import logging

# ---------------------------------------
# Fix path for PyInstaller EXE
# ---------------------------------------
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Initialize Django
django.setup()

# ---------------------------------------
# Import after django.setup()
# ---------------------------------------
from infrastructure.services.metric_collector import MetricCollector

logging.basicConfig(
    filename="agent.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

collector = MetricCollector()

print("KarvOps Agent Started")

while True:
    try:
        collector.collect()
        print("Metrics Collected Successfully")
    except Exception as e:
        print(e)
        logging.exception(e)

    time.sleep(60)