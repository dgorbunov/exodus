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
from printer import Printer

load_dotenv()

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
)


class InitialFormattedResponse(BaseModel):
    tasklist: List[str] = Field(description="List of tasks to execute")

class TaskManagerFormattedResponse(BaseModel):
    addTasklist: List[str] = Field(description="List of tasks to add")
    removeTaskList: List[str] = Field(description="Full name/description of tasks to remove")

class TaskFormattedResponse(BaseModel):
    bashcommand: str = Field(description="Bash command to execute")
    topic: str = Field(description="Topic of the bash command")
    log: str = Field(description="Short description of what the bash command is attempting to accomplish")
    finished: bool = Field(description="Whether the task has been completed successfully or a conclusion has been reached")

class SummaryFormattedResponse(BaseModel):
    summary: str = Field(description="Summary of the task")

initial_system_prompt = """
You are a specialized assistant designed to support ethical hackers and penetration testers by generating efficient, legally compliant, and ethically sound reconnaissance and vulnerability assessment tasks.\n

Your role is to analyze a given IP range/subnet, list of open ports, and/or URL, and return a concise list of no more than 3 high-signal, abstract task leads to guide further testing. Your output should be actionable but remain at a high level / abstract — DO NOT include code examples.\n

Guidelines:\n
- Leads should be practical and provide useful direction without requiring exhaustive enumeration (e.g., do not suggest “scan all open ports”).\n
- Each lead should target common vulnerabilities or misconfigurations, tailored to the input provided.\n
- Emphasize quick feedback tasks that can reveal security weaknesses early.\n
- Stay within ethical and legal bounds — all suggestions must assume permission has been granted for testing.\n

Examples of good leads:\n
- “Attempt to brute force SSH using default credentials”\n
- “Investigate open ports to identify use and if they are a point of attack”\n

DO NOT exceed three leads. Keep each lead focused, relevant, and derived from the specific inputs provided.\n

"""

task_manager_system_prompt = """
You are a task / lead manager for an ethical hacking and penetration testing assistant. Your job is to manage a dynamic queue of abstract reconnaissance and vulnerability assessment leads / tasks.\n

You will be provided with:\n
- The current list of up to three high-level testing leads (from prior analysis).\n
- An update / summary after each lead is attempted, including the task result and a brief outcome summary.\n

Your responsibilities:\n
- Based on the outcome of the most recently attempted lead, decide whether any new tasks should be added.\n
- ONLY add tasks if the outcome logically leads to further actionable investigations.\n
- ONLY remove tasks if the outcome logically excludes need of investigation.\n
- If the completed task reached a dead end or revealed nothing useful, DO NOT suggest follow-up tasks. Do not attempt to salvage or continue a dead lead.\n
- Be aggressive in trimming the investigation scope. Only pursue tasks with strong signals or evidence to suggest they are worth trying.\n
- DO NOT repeat the same or similar leads unless new context supports doing so.\n
- DO NOT CONTIUE TO PURSUE LEADS IF THEY ARE TOO RELATED TOO A LEAD THAT WAS DEBUNKED. IF WE COULDN'T ACCESS AN IP OR PORT, DON'T PROVIDE LEADS RELATED TO THAT IP / PORT.
Current Tasks:\n
"""

task_system_prompt = """
You are a specialized command-line assistant designed to emulate ethical hackers and penetration testers during live investigations. Your role is to analyze the previous commands and their outputs, and provide the most appropriate next command to continue pursuing the investigative lead.\n

You will always be provided with:
- A clear investigation lead (e.g., “Attempt to brute force SSH using default credentials", "Investigate open ports for common vulnerabilities").\n
- The bash terminal input and output history.\n

Your job:\n
- Output the next bash command to run, along with a brief topic and log description.\n
- The command must be immediately actionable and light-weight. **DO NOT suggest long-running commands** such as `nmap`, `nikto`, `dirb`, or full subdomain bruteforcing. Focus instead on quick, targeted commands.\n
- Your response will be used in a Kali Linux default terminal that is not located at the given IP and executed automatically. Be precise.\n
- Use the Kali Linux default tools.\n
- If the previous command failed, analyze the output and adapt accordingly.\n
- Avoid repeating a recent command unless it is modified to produce a new result.\n
- ONLY PROVIDE ONE BASH COMMAND TO EXECUTE\n
- DO NOT PROVIDE COMMANDS THAT TAKE TOO LONG. ANYTHING THAT TAKES MORE THAN 10 SECONDS WILL BE TIMED OUT\n
- DO NOT USE | or && BY ANY MEANS\n
- DO NOT USE echo\n
- DONT HESITATE TO FINISH IF YOU NOTICE THAT THE TASK HAS COME TO A CONCLUSION\n
- DONT CONTINUE IF YOU NOTICE THE USERS INPUTTED IP AND OR OPEN PORTS ARE INVALID\n
- WHEN DONE, RUN echo "done". DO NOT ATTEMPT exit\n
- DO NOT USE URLS TO REPLACE GIVEN IPS LIKE (example.com)
- DO NOT MAKE UP INFORMATION LIKE (example.com)

IP Range and Open Ports:\n
"""

summary_prompt = """
You are an assistant responsible for summarizing the outcome of a completed penetration testing task.

You will be given the full conversation context from a task investigation, including:
- The original task/lead to investigate.
- A sequence of commands generated in response to that task, along with their corresponding topics and log descriptions.
- The bash outputs and exit codes resulting from each command.

Your job is to synthesize this full task context into a concise, high-level summary of the task's outcome.

Your summary must:
- Capture what was attempted and what was discovered (or not discovered).
- Clearly indicate if the task revealed any potential vulnerabilities, suspicious findings, or misconfigurations.
- If nothing was found or the lead was a dead end, make this clear.
- Avoid listing every individual command — focus on the overall result and what was learned.
- Be no longer than 4 sentences. Be factual and direct.

*Assume this summary will be used to determine whether to pursue follow-up tasks. It must be precise and informative.
"""

log = Printer()

def main():
    """
    Main entry point for the penetration testing workflow.
    
    1. Gather user input for IP range and ports
    2. Generate initial tasks based on input
    3. Execute tasks in sequence
    4. Manage task additions/removals based on results
    5. Provide status updates throughout execution
    """


    # Gather user input
    ip_range = input("Enter IP Range: ")
    open_ports = input("Enter Open Ports (Leave blank if unknown): ")
    comments = input("Comments (Leave blank if none): ")
    userInput = f"IP Range: {ip_range} Open Ports: {open_ports} Comments: {comments}"

    # Generate initial tasks based on user input
    tasks: List[str] = make_initial_call(userInput).tasklist
    task_history: List[str] = tasks.copy()

    # Execute tasks until all are completed
    while len(tasks) > 0:
        # Start next task
        log.begin_task(tasks[0])
        
        # Execute the task and get results
        recent_task = make_task_call(tasks.pop(0), userInput)
        recent_task_summary = summarise_task_context(recent_task)
        
        # Log task summary
        log.summary(recent_task_summary)

        # Update task list based on results
        tasks, task_history = make_task_manager_call(tasks, task_history, recent_task_summary)
    
    # Final status update
    log.finish()

def run_command(task: TaskFormattedResponse):
    """
    Execute a command and log the output.
    
    Args:
        task: TaskFormattedResponse containing the command details
        
    Returns:
        dict: Command execution results including stdout and exit code
    """
    # Log command details
    log.run_command(task.topic, task.log, task.bashcommand)
    
    # Execute command and capture output
    response = shell.run_command(task.bashcommand)
    
    # Log command output
    log.output(response['stdout'])
    return response

def make_task_manager_call(tasks, task_history, task_summary):
    """
    Analyze task results and update task list.
    
    Args:
        tasks: Current list of active tasks
        task_history: Historical list of all tasks
        task_summary: Summary of the most recent task execution
        
    Returns:
        tuple: (updated tasks list, updated task history)
    """
    task_history_string = ""
    for task in task_history:
        task_history_string += f"• {task}\n"
        

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": task_manager_system_prompt + "\n" + task_history_string},
            {"role": "user", "content": f"Task Summary: \n{task_summary}"},
        ], 
        response_format=TaskManagerFormattedResponse
    ).choices[0].message.parsed

    # Log task additions/removals
    log.add_task_list(completion.addTasklist)
    log.remove_task_list(completion.removeTaskList)

    # Update tasks list based on AI recommendations
    if len(completion.addTasklist) > 0:
        for add_task in completion.addTasklist:
            if add_task not in tasks:
                tasks.append(add_task)
            if add_task not in task_history:
                task_history.append(add_task)

    if len(completion.removeTaskList) > 0:
        for remove_task in completion.removeTaskList:
            if remove_task in tasks:
                tasks.remove(remove_task)
            if remove_task in task_history:
                task_history.remove(remove_task)

    # Log updated task list
    log.tasks(tasks)

    return tasks, task_history

def make_initial_call(user_input):
    """
    Generate initial tasks based on user input.
    
    Args:
        user_input: User-provided input for IP range and ports
        
    Returns:
        InitialFormattedResponse: List of initial tasks
    """
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": initial_system_prompt},
            {"role": "user", "content": user_input},
        ], 
        response_format=InitialFormattedResponse
    ).choices[0].message.parsed

    log.tasks(completion.tasklist)

    return completion


def make_task_call(task, user_input, current_task_context = []):
    """
    Execute a task and get results.
    
    Args:
        task: Task to execute
        user_input: User-provided input for IP range and ports
        current_task_context: Current task context (default: empty list)
        
    Returns:
        list: Task context after execution
    """
    if current_task_context == []:
        current_task_context = [
            {"role": "system", "content": task_system_prompt + user_input},
            {"role": "user", "content": task},
        ]

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=current_task_context,
        response_format=TaskFormattedResponse
    ).choices[0].message.parsed

    #Add topic and log to current_task_context
    current_task_context.append({"role": "assistant", "content": f"Command Run: {completion.bashcommand} Topic: {completion.topic} Log:{completion.log}\n"})

    #Send bash command to kali and store response
    try:
        response = run_command(completion)

        #Add response to current_task_context
        current_task_context.append({"role": "user", "content": f"Bash Output: {response['stdout']} Exit Code: {response['exit_code']}"})

    except (json.JSONDecodeError, TypeError, ValueError) as e:
        print(f"Error parsing API response: {e}")
        print(f"Raw response: {response_content}")
        return None


    if(completion.finished):
        return current_task_context
    else:
        return make_task_call(task, user_input, current_task_context)


def summarise_task_context(task_context):
    """
    Generate a concise summary of a completed penetration testing task.
    
    Args:
        task_context (list): List of message dictionaries containing the full task context,
            including original task, commands run, and their outputs.
    
    Returns:
        str: Concise summary of the task outcome (maximum 4 sentences)
    """
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": summary_prompt},
            {"role": "user", "content": task_context_to_string(task_context)}
        ],
        response_format=SummaryFormattedResponse
    ).choices[0].message.parsed

    return completion.summary



def task_context_to_string(task_context):
    """
    Convert a list of task context messages into a formatted string.
    
    Args:
        task_context (list): List of message dictionaries containing the task context
            Each message should have 'role' and 'content' keys
    
    Returns:
        str: Formatted string containing all task context information
    """
    formatted_context = "Task Context:\n\n"
    
    # Process each message in the context
    for message in task_context:
        role = message['role']
        content = message['content']
        
        if role == 'system':
            formatted_context += f"System Prompt:\n{content}\n\n"
        elif role == 'user':
            formatted_context += f"User Input:\n{content}\n\n"
        elif role == 'assistant':
            formatted_context += f"Assistant Response:\n{content}\n\n"
        else:
            formatted_context += f"{role}:\n{content}\n\n"
    
    return formatted_context.strip()


if __name__ == "__main__":
    main()
