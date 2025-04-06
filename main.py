# Make initial call to Grok giving it additional context
# Save the formatted reposne as JSON
# Send the bash command from json to kali
# We record the response
# Make all suqbsequent callt to grok based on the response
# TODO: Add hault condition
# Compile all command notes to summarize the effects of the attacks and the security of the system

from pydantic import BaseModel, Field
from datetime import date
from enum import Enum
from typing import List
from openai import OpenAI
import os
from dotenv import load_dotenv
import shell

load_dotenv()

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url="https://api.x.ai/v1/",
)


class InitialFormattedResponse(BaseModel):
    tasklist: List[str] = Field(description="List of tasks to execute")

class TaskFormattedResponse(BaseModel):
    bashcommand: str = Field(description="Bash command to execute")
    topic: str = Field(description="Topic of the bash command")
    log: str = Field(description="Log entry for command context")
    success: bool = Field(description="Whether the task has been completed successfully")


initial_system_prompt = """
You are a specialized assistant designed to help ethical hackers and penetration testers by generating efficient, ethical, and legally compliant tasks and commands using Kali Linux default tools.
Your job is to take a given IP range/ subnet, list of open ports; and url and generate a step-by-step list of tasks that will detect common vulnerabilities. Do not give code examples,
but instead provide rough ideas that would work well. Avoid nmap or port scanning, as the legality of it is slightly grey. Use hydra to run through the list of ports and generate scripts to test vuln. Keep 
it short and succint (max 7 entries)
"""

task_system_prompt = """
Generate a bash commands to complete the following task:
"""

def main():
    tasks = make_initial_call()
    print(tasks)
    

def make_initial_call():
    completion = client.beta.chat.completions.parse(
        model="grok-2-latest",
        messages=[
            {"role": "system", "content": initial_system_prompt},
            {"role": "user", "content": "192.168.1.0/24"},
        ], 
        response_format=InitialFormattedResponse
    )
    return completion.choices[0].message.parsed.tasklist


def send_command(command: str):
    print(f"\033[32mRunning:\n{command}\033[0m")
    response = shell.run_command(command)
    print(f"\033[33mOutput:\n{response['stdout']}\033[0m")


def compile_notes():
    pass
def save_json():
    pass

if __name__ == "__main__":
    main()
