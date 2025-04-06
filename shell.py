import docker

client = docker.from_env()
container = client.containers.get("kali")

def run_command(command: str):
    exec_result = container.exec_run(command, stdout=True, stderr=True)
    return {
        'stdout': exec_result.output.decode().strip(),
        'exit_code': exec_result.exit_code
    }

if __name__ == "__main__":
    response = run_command("lsb_release -a")
    print("Output:\n", response['stdout'])
