import docker

client = docker.from_env()

container = client.containers.get("kali")

def run_command_in_container(command: str):
    exec_result = container.exec_run(command, stdout=True, stderr=True)
    return {
        'stdout': exec_result.output.decode().strip(),
        'exit_code': exec_result.exit_code
    }

# Example usage
response = run_command_in_container("lsb_release -a")
print("Output:\n", response['stdout'])