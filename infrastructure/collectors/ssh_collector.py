import paramiko


class SSHCollector:

    def __init__(self, server):

        self.server = server

        self.client = None

    def connect(self):

        self.client = paramiko.SSHClient()

        self.client.set_missing_host_key_policy(
            paramiko.AutoAddPolicy()
        )

        self.client.connect(

            hostname=self.server.ip_address,

            port=self.server.ssh_port,

            username=self.server.ssh_username,

            key_filename=self.server.pem_file.path,

            timeout=20,

            look_for_keys=False,

            allow_agent=False
        )

    def execute(self, command):

        if self.client is None:

            self.connect()

        stdin, stdout, stderr = (
            self.client.exec_command(
                command,
                timeout=60
            )
        )

        output = stdout.read().decode(
            "utf-8",
            errors="replace"
        )

        error = stderr.read().decode(
            "utf-8",
            errors="replace"
        )

        exit_code = stdout.channel.recv_exit_status()

        return {

            "success": exit_code == 0,

            "stdout": output.strip(),

            "stderr": error.strip(),

            "return_code": exit_code

        }

    def close(self):

        if self.client:

            self.client.close()

            self.client = None