import subprocess


class LocalCollector:

    def __init__(self, os_type):

        self.os_type = os_type

    def execute(self, command):

        if not command:

            return {
                "success": False,
                "stdout": "",
                "stderr": "Command is empty",
                "return_code": -1
            }

        try:

            # -----------------------------
            # WINDOWS
            # -----------------------------

            if self.os_type == "WINDOWS":

                # PowerShell commands
                powershell_commands = [
                    "Get-Counter",
                    "Get-WmiObject",
                    "Get-CimInstance",
                    "Get-Process"
                ]

                is_powershell = any(
                    command.strip().startswith(cmd)
                    for cmd in powershell_commands
                )

                if is_powershell:

                    process = subprocess.run(

                        [
                            "powershell.exe",
                            "-NoProfile",
                            "-ExecutionPolicy",
                            "Bypass",
                            "-Command",
                            command
                        ],

                        capture_output=True,

                        text=True,

                        timeout=60
                    )

                else:

                    # CMD commands such as typeperf
                    process = subprocess.run(

                        command,

                        shell=True,

                        capture_output=True,

                        text=True,

                        timeout=60
                    )

            # -----------------------------
            # LINUX
            # -----------------------------

            elif self.os_type == "LINUX":

                process = subprocess.run(

                    command,

                    shell=True,

                    capture_output=True,

                    text=True,

                    timeout=60
                )

            else:

                return {
                    "success": False,
                    "stdout": "",
                    "stderr": (
                        f"Unsupported OS: "
                        f"{self.os_type}"
                    ),
                    "return_code": -1
                }

            return {

                "success": process.returncode == 0,

                "stdout": process.stdout.strip(),

                "stderr": process.stderr.strip(),

                "return_code": process.returncode

            }

        except subprocess.TimeoutExpired:

            return {

                "success": False,

                "stdout": "",

                "stderr": "Command timed out",

                "return_code": -1

            }

        except Exception as e:

            return {

                "success": False,

                "stdout": "",

                "stderr": str(e),

                "return_code": -1

            }