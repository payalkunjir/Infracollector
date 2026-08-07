import platform


def get_operating_system():

    system = platform.system()

    if system == "Linux":
        return "LINUX"

    elif system == "Windows":
        return "WINDOWS"

    else:
        return "UNKNOWN"