import docker
import threading
import time

client = docker.from_env()
container = client.containers.get("kali")

def run_command(command: str, timeout: int = 10):
    result = {'stdout': '', 'exit_code': None}
    execution_completed = threading.Event()
    
    def execute():
        exec_result = container.exec_run(command, stdout=True, stderr=True)
        result['stdout'] = exec_result.output.decode().strip()
        result['exit_code'] = exec_result.exit_code
        execution_completed.set()
    
    thread = threading.Thread(target=execute)
    thread.daemon = True
    thread.start()
    
    if execution_completed.wait(timeout=timeout):
        return result
    else:
        return {
            'stdout': f"Command timed out after {timeout} seconds",
            'exit_code': 124  # Using 124 as timeout exit code (same as Linux timeout command)
        }

if __name__ == "__main__":
    response = run_command("lsb_release -a")
    print("Output:\n", response['stdout'])
