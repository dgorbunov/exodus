# Make initial call to Grok giving it additional context
# Save the formatted reposne as JSON
# Send the bash command from json to kali
# We record the response
# Make all suqbsequent callt to grok based on the response
# TODO: Add hault condition
# Compile all command notes to summarize the effects of the attacks and the security of the system

from docker import client
from pydantic import BaseModel, Field
from datetime import date
from enum import Enum
from typing import List


def main():
    make_initial_call()
    send_bash_command()
    make_subsequent_calls()
    compile_notes()
    save_json()


def make_initial_call():
    completion = client.Completion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "What is the current date?"},
            {"role": "user", "content": "What is the current date?"},
        ], 
        response_format=FormattedResponse
    )
    response = FormattedResponse(**completion.choices[0].message.content)
    return response

def send_bash_command():
    pass
def add_more_context_to_system_prompt():
    pass
def generate_gameplan():
    pass
def make_subsequent_calls():
    pass    
def compile_notes():
    pass
def save_json():
    pass
    
# JSON response format
class FormattedResponse(BaseModel):
    bashcommand: str = Field(description="Bash command to execute")
    topic: str = Field(description="Topic of the bash command")
    log: str = Field(description="Log entry for command context")
    success: bool = Field(description="Success of the command")
if __name__ == "__main__":
    main()
