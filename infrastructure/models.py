from django.db import models


class Server(models.Model):

    OS_CHOICES = [
        ("LINUX", "Linux"),
        ("WINDOWS", "Windows"),
    ]

    name = models.CharField(
        max_length=150
    )

    hostname = models.CharField(
        max_length=255
    )

    ip_address = models.GenericIPAddressField()

    operating_system = models.CharField(
        max_length=20,
        choices=OS_CHOICES,
        default="LINUX"
    )

    ssh_username = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    pem_file = models.FileField(
        upload_to="pem/",
        blank=True,
        null=True
    )

    ssh_port = models.PositiveIntegerField(
        default=22
    )

    application_name = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    environment = models.CharField(
        max_length=50,
        default="PROD"
    )

    enabled = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class MetricSample(models.Model):

    server = models.ForeignKey(
        Server,
        on_delete=models.CASCADE,
        related_name="metrics"
    )

    metric_type = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    metric_value = models.CharField(
     max_length=100,
     null=True,
     blank=True
     )

    raw_output = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=30,
        default="SUCCESS"
    )

    error_message = models.TextField(
        blank=True,
        null=True
    )

    collection_time = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.server.name} - {self.metric_type}"

# class ProcessMetric(models.Model):

#     server = models.ForeignKey(
#         Server,
#         on_delete=models.CASCADE,
#         related_name="process_metrics"
#     )

#     process_name = models.CharField(
#         max_length=255
#     )

#     process_id = models.PositiveIntegerField(
#         blank=True,
#         null=True
#     )

#     handle_count = models.PositiveIntegerField(
#         blank=True,
#         null=True
#     )


#     collection_time = models.DateTimeField(
#         auto_now_add=True
#     )

#     def __str__(self):
#         return (
#             f"{self.server.name} - "
#             f"{self.process_name} - "
#             f"{self.process_id}"
#         )

# class ServiceMetric(models.Model):

#     server = models.ForeignKey(
#         Server,
#         on_delete=models.CASCADE,
#         related_name="service_metrics"
#     )

#     service_name = models.CharField(
#         max_length=255
#     )

#     display_name = models.CharField(
#         max_length=255,
#         blank=True,
#         null=True
#     )

#     status = models.CharField(
#         max_length=50,
#         blank=True,
#         null=True
#     )

#     start_type = models.CharField(
#         max_length=50,
#         blank=True,
#         null=True
#     )

#     collection_time = models.DateTimeField(
#         auto_now_add=True
#     )


#     def __str__(self):
#         return (
#             f"{self.server.name} - "
#             f"{self.service_name}"
#         )

# class NetworkMetric(models.Model):

    # server = models.ForeignKey(
    #     Server,
    #     on_delete=models.CASCADE,
    #     related_name="network_metrics"
    # )

    # protocol = models.CharField(
    #     max_length=10
    # )

    # local_address = models.CharField(
    #     max_length=100,
    #     blank=True,
    #     null=True
    # )

    # local_port = models.PositiveIntegerField(
    #     null=True,
    #     blank=True
    # )

    # remote_address = models.CharField(
    #     max_length=100,
    #     blank=True,
    #     null=True
    # )

    # remote_port = models.PositiveIntegerField(
    #     null=True,
    #     blank=True
    # )

    # collection_time = models.DateTimeField(
    #     auto_now_add=True
    # )

    # def __str__(self):
    #     return (
    #         f"{self.server.name} - "
    #         f"{self.protocol}"
    #     )