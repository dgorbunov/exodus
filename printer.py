from typing import List

class Printer:
    def add_task_list(self, addTaskList: List[str]):
        print(f"\033[1;34m\nTasks Added: ===================\033[0m")
        for task in addTaskList:
            print(f"\033[1;32m\n    + {task}\033[0m")

    def remove_task_list(self, removeTaskList: List[str]):
        print(f"\033[1;34m\nTasks Removed: =================\033[0m")
        for task in removeTaskList:
            print(f"\033[1;31m\n    - {task}\033[0m")

    def tasks(self, tasks: List[str]):
        print(f"\033[1;34m\nCurrent Task List: =============\033[0m")
        for task in tasks:
            print(f"\033[1;37m\n    • {task}\033[0m")

    def run_command(self, topic: str, log: str, command: str):
        print(f"\033[1;35m\n --- {topic} --- \033[0m")
        print(f"\033[1;34m\nRunning:\n{log}\033[0m")
        print(f"\033[1;34m\nRunning:\n{command}\033[0m")

    def output(self, output: str):
        print(f"\033[1;33m\nOutput:\n{output}\n\n\033[0m")

    def summary(self, summary: str):
        print(f"\033[1;37m\nSummary:\n{summary}\033[0m")

    def finish(self):
        print(f"\033[1;33m\n FINISHED RUNNINNG DIAGNOSTIC \033[0m")

    def begin_task(self, task):
        print(f"\033[1;35m\n BEGINNING: {task} \033[0m")
        

    