# Make initial call to Grok giving it additional context
# Save the formatted reposne as JSON
# Send the bash command from json to kali
# We record the response
# Make all suqbsequent callt to grok based on the response
# TODO: Add hault condition
# Compile all command notes to summarize the effects of the attacks and the security of the system

from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI
import os
from dotenv import load_dotenv
import shell

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.x.ai/v1/",
)

def main():
    response = make_initial_call()
    #send_bash_command(response)
    #make_subsequent_calls()
    #compile_notes()
    #save_json()
    for task in response.tasklist:
        shell.run_command(task)

initial_system_prompt = """
Generate bash commands to execute. 
"""

def make_initial_call():
    completion = client.beta.chat.completions.parse(
        model="grok-2-latest",
        messages=[
            {"role": "system", "content": initial_system_prompt},
            {"role": "user", "content": "make a directory"},
        ], 
        response_format=InitialFormattedResponse
    )
    return completion.choices[0].message.parsed

def send_bash_command():
    pass
def add_more_context_to_system_prompt():
    pass
def make_subsequent_calls():
    pass    
def compile_notes():
    pass
def save_json():
    pass
    
# JSON response formats

class InitialFormattedResponse(BaseModel):
    tasklist: List[str] = Field(description="List of tasks to execute")

class TaskFormattedResponse(BaseModel):
    bashcommand: str = Field(description="Bash command to execute")
    topic: str = Field(description="Topic of the bash command")
    log: str = Field(description="Log entry for command context")
    success: bool = Field(description="Whether the task has been completed successfully")

if __name__ == "__main__":
    main()
