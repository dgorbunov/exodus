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

class UserInput(BaseModel):
    ip_range: str = Field(description="IP range or subnet to scan.")
    open_ports: List[int] = Field(description="List of open ports to scan.")

class TaskFormattedResponse(BaseModel):
    command: str = Field(description="Bash command to execute in Kali linux default.")
    description: str = Field(description="Description of the bash command being run to be displayed to the user. This should be concise.")
    success: bool = Field(description="Boolean value indicating whether the attack was successful. Only set this to true when you have correctly identified a vulnerability, like finding default credentials for an application.")

class HistoryFormattedResponse(BaseModel):
    history: str = Field(description = "History of steps taken to pen the target")


meta_prompt = """
You are a specialized assistant designed to help ethical hackers, penetration testers, and security consultants by systematically investigating network security using legally compliant commands from Kali Linux default tools.

Your job is to take the provided IP range/subnet and list of potential open ports from the user, and generate commands to run in Kali Linux to bruteforce any vulnerable applications running on open ports.

You should utilize tools/programs available in Kali Linux, including, for example, Hydra. You should decide which tool/program to use based on the port and other intelligence you gather. For example, if port == 21: check anonymous FTP, if port == 22:run hydra with SSH default creds, if port == 80: run whatweb + gobuster lite.

You will bruteforce default credentials for applications using wordlists available in default Kali, but you should also use your own intelligence based off the context of the IP range/subnet and open ports. You should use other intelligence tools like nslookup (or whatever you think is more appropriate) to gather information about the target based off the user provided information.

If a command fails, try again a reasonable number of times. Keep in mind your syntax may be wrong. If it fails too many times, move on. It's your job to investigate any interesting vulnerabilities you may find and report them back to the user.

Do NOT generate more than one command at a time. Use the previous history of commands/responses and continue bruteforcing until you have identified an exploitable vulnerability and set success to True.
"""

history_prompt = """
Generate a succint, concise summary of the previous commands run and their outputs to feed in as context for another task API call to another call in the OpenAI API. This context is important as it will information the next decision the model makes to generate a new command to continue bruteforcing.
"""

def main():
    # Ask user for IP range/subnet and open ports
    ip_input = input("Enter IP range or subnet to scan (e.g., 192.168.1.0/24): ")
    ip_range = ip_input if ip_input.strip() else "192.168.1.0/24"  # Default value
    
    ports_input = input("Enter open ports (comma-separated, e.g., 22,80,443): ")
    if ports_input.strip():
        open_ports = [int(port.strip()) for port in ports_input.split(",") if port.strip().isdigit()]
    else:
        open_ports = [22, 80, 443]  # Default ports
    
    # Create user input object
    user_input = UserInput(ip_range=ip_range, open_ports=open_ports)
    
    # Run task
    while True:
        # Generate tasks based on user input
        task = generateTask(user_input)
        response = run_command(task)


def generateTask(user_input: UserInput):
    completion = client.beta.chat.completions.parse(
        model="grok-2-latest",
        messages=[
            {"role": "system", "content": meta_prompt},
            {"role": "user", "content": f"IP range/subnet: {user_input.ip_range}\nOpen ports: {user_input.open_ports}"},
        ], 
        response_format=TaskFormattedResponse
    )
    
    response_content = completion.choices[0].message.content

    try:
        import json
        parsed_response = json.loads(response_content)
        return TaskFormattedResponse(**parsed_response)
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        print(f"Error parsing API response: {e}")
        print(f"Raw response: {response_content}")
        return None

def run_command(task: TaskFormattedResponse):
    print(f"\033[32mRunning:\n{task.command}\033[0m")
    response = shell.run_command(task.command)
    print(f"\033[33mOutput:\n{response['stdout']}\033[0m")
    print(f"\033[1;37mDescription:\n{task.description}\033[0m")
    
    return response['stdout']


def make_history_call(stdout: str):
    completion = client.beta.chat.completions.parse(
            model = "grok-2-latest",
            messages=[
                {"role": "system", "content": history_prompt},
                {"role": "user", "content": stdout}
            ],
            response_format = HistoryFormattedResponse
    )
    return completion.choices[0].message.parsed



if __name__ == "__main__":
    main()
