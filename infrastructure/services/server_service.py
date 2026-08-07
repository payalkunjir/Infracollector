from infrastructure.models import Server
from infrastructure.services.server_identity import (
    get_server_identity
)


def get_or_create_local_server():

    identity = get_server_identity()

    hostname = identity["hostname"]
    ip_address = identity["ip_address"]
    operating_system = identity["operating_system"]

    print("====================================")
    print("LOCAL SERVER INFORMATION")
    print("Hostname:", hostname)
    print("IP Address:", ip_address)
    print("Operating System:", operating_system)
    print("====================================")

    server = Server.objects.filter(
        hostname=hostname
    ).first()

    if server:

        print(
            f"Server already exists: {server.name}"
        )

        # Update information if it changed
        server.ip_address = ip_address
        server.operating_system = operating_system
        server.enabled = True

        server.save(
            update_fields=[
                "ip_address",
                "operating_system",
                "enabled"
            ]
        )

        return server

    # Server doesn't exist
    server = Server.objects.create(

        name=hostname,

        hostname=hostname,

        ip_address=ip_address,

        operating_system=operating_system,

        environment="UNKNOWN",

        enabled=True
    )

    print(
        f"New server registered: {server.name}"
    )

    return server