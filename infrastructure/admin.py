from django.contrib import admin

from infrastructure.models import (
    Server,
    MetricSample,
    ProcessMetric,
    ServiceMetric,
    NetworkMetric
)
from datetime import timedelta
from django.utils import timezone

class CollectionTimeFilter(admin.SimpleListFilter):
    title = "Collection Time"
    parameter_name = "collection_time"

    def lookups(self, request, model_admin):
        return (
            ("1m", "Last 1 minute"),
            ("10m", "Last 10 minutes"),
            ("30m", "Last 30 minutes"),
            ("1h", "Last 1 hour"),
            ("today", "Today"),
            ("7d", "Last 7 days"),
        )

    def queryset(self, request, queryset):

        now = timezone.now()

        value = self.value()

        if value == "1m":
            start_time = now - timedelta(minutes=1)
            return queryset.filter(collection_time__gte=start_time)

        elif value == "10m":
            start_time = now - timedelta(minutes=10)
            return queryset.filter(collection_time__gte=start_time)

        elif value == "30m":
            start_time = now - timedelta(minutes=30)
            return queryset.filter(collection_time__gte=start_time)

        elif value == "1h":
            start_time = now - timedelta(hours=1)
            return queryset.filter(collection_time__gte=start_time)

        elif value == "today":
            start_time = timezone.localtime(now).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            return queryset.filter(collection_time__gte=start_time)

        elif value == "7d":
            start_time = now - timedelta(days=7)
            return queryset.filter(collection_time__gte=start_time)

        return queryset

@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "hostname",
        "ip_address",
        "operating_system",
        "environment",
        "enabled",
        "created_at",
    )

    list_filter = (
        "operating_system",
        "environment",
        "enabled",
    )

    search_fields = (
        "name",
        "hostname",
        "ip_address",
    )


@admin.register(MetricSample)
class MetricSampleAdmin(admin.ModelAdmin):

    list_display = (
        "host",
        "metric_type",
        "metric_value",
        # "status",
        "collection_time",
    )

    list_filter = (
        "status",
        # "metric_type",
        CollectionTimeFilter,
    )

    search_fields = (
        "server__name",
        "metric_type",
    )

    date_hierarchy = "collection_time"

    ordering = (
        "-collection_time",
    )

    def host(self, obj):
        return obj.server.name

    host.short_description = "Host"


@admin.register(ProcessMetric)
class ProcessMetricAdmin(admin.ModelAdmin):

    list_display = (
        "host",
        "process_name",
        "process_id",
        "handle_count",
        "collection_time",
    )

    list_filter = (
        "collection_time",
    )

    search_fields = (
        "server__name",
        "process_name",
        "process_id",
    )

    date_hierarchy = "collection_time"

    ordering = (
        "-collection_time",
    )

    def host(self, obj):
        return obj.server.name

    host.short_description = "Host"


@admin.register(ServiceMetric)
class ServiceMetricAdmin(admin.ModelAdmin):

    list_display = (
        "host",
        "service_name",
        "display_name",
        "status",
        "start_type",
        "collection_time",
    )

    list_filter = (
        "status",
        "start_type",
        "collection_time",
    )

    search_fields = (
        "server__name",
        "service_name",
        "display_name",
    )

    date_hierarchy = "collection_time"

    ordering = (
        "-collection_time",
    )

    def host(self, obj):
        return obj.server.name

    host.short_description = "Host"


@admin.register(NetworkMetric)
class NetworkMetricAdmin(admin.ModelAdmin):

    list_display = (
        "host",
        "protocol",
        "local_address",
        "local_port",
        "remote_address",
        "remote_port",
        "collection_time",
    )

    list_filter = (
        "protocol",
        "collection_time",
    )

    search_fields = (
        "server__name",
        "local_address",
        "remote_address",
    )

    date_hierarchy = "collection_time"

    ordering = (
        "-collection_time",
    )

    def host(self, obj):
        return obj.server.name

    host.short_description = "Host"