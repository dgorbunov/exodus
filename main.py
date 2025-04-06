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

def main():
    tasks = make_initial_call()
    
    for task in tasks:
        make_task_call(task)

def make_initial_call():
    completion = client.beta.chat.completions.parse(
        model="grok-2-latest",
        messages=[
            {"role": "system", "content": initial_system_prompt},
            {"role": "user", "content": "192.168.1.0/24"},
        ], 
        response_format=InitialFormattedResponse
    )
    return completion.choices[0].message.parsed

def make_task_call(task, 
                    task_context = []):

    if task_context == []:
        task_context = [
            {"role": "system", "content": task_system_prompt},
            {"role": "user", "content": task},
        ]

    completion = client.beta.chat.completions.parse(
        model="grok-2-latest",
        messages=task_context,
        response_format=TaskFormattedResponse
    ).choices[0].message.parsed

    #Add topic and log to task_context
    task_context.append({"role": "assistant", "content": f"Command Run: {completion.bashcommand} Topic: {completion.topic} Log:{completion.log}\n"})

    #Send bash command to kali and store response
    response = shell.run_command(completion.bashcommand)

    #Add response to task_context
    task_context.append({"role": "user", "content": f"Bash Output: {response['stdout']} Exit Code: {response['exit_code']}"})

    if(completion.success):
        return completion
    else:
        return make_task_call(task, task_context)


def compile_notes():
    pass
def save_json():
    pass
    
# JSON response formats


if __name__ == "__main__":
    main()
