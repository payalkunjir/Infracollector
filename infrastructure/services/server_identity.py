import socket
import platform


def get_hostname():
    return socket.gethostname()


def get_os():
    system = platform.system()

    if system == "Windows":
        return "WINDOWS"

    if system == "Linux":
        return "LINUX"

    return system.upper()


def get_local_ip():

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    try:
        # This does not actually send data.
        # It allows Python to determine the local interface/IP.
        sock.connect(("8.8.8.8", 80))

        return sock.getsockname()[0]

    except Exception:

        return "127.0.0.1"

    finally:

        sock.close()


def get_server_identity():

    return {
        "hostname": get_hostname(),
        "ip_address": get_local_ip(),
        "operating_system": get_os()
    }