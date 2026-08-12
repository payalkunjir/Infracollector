import os

from django.apps import AppConfig


class InfrastructureConfig(AppConfig):

    default_auto_field = "django.db.models.BigAutoField"

    name = "infrastructure"

    def ready(self):

        # Prevent scheduler from starting twice
        if os.environ.get("RUN_MAIN") != "true":
            return

        # from infrastructure.services.schedular import start_scheduler

        # start_scheduler()