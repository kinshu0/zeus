import openai
import re
import subprocess
import json
from flask import Flask, render_template, request

# Initialize the OpenAI API with the API key
with open("config.json", "r") as f:
    config = json.load(f)
openai.api_key = config['openai_api_key']

# Regular expression pattern to extract the user prompt from the input
PATTERN = r"START_USER_PROMPT:(.*?)END_USER_PROMPT"

# Create a Flask application instance
app = Flask(__name__)

# Define a function to execute a bash command
def run_command(command):
    output = subprocess.check_output(command, shell=True)
    return output.decode('utf-8')

# Define a function to initialize the chat and return the API response
def initialize_chat():
    init_app_api_request = """The API is designed to take a user prompt as input, which is sent from a web application to the API. The prompt is expected to be a string that begins with "START_USER_PROMPT:" and ends with "END_USER_PROMPT". This string should contain a task or problem description that the user wants to solve.

The API will return a JSON object with two keys: "user_output" and "bash_output". The value of "user_output" is a string that will be displayed to the user, and it should contain any information or output that the API wants to communicate to the user. The value of "bash_output" is a string that will be executed as a command in an Ubuntu container, and it should contain a valid bash command that can be executed in the container.

When the API executes the bash command, the output of the command will be piped back to the API as a message. This message will be a string that begins with "START_BASH_OUTPUT:" and ends with "END_BASH_OUTPUT". This string should contain the output of the bash command that was executed in the container.

The API is allowed to persist any information that it deems important for future context. This could include things like the user prompt, the bash command that was executed, and the output of the command. This information could be stored in a database or other persistent storage mechanism.

Overall, this API is designed to allow a user to send a task or problem description to the API, receive a response that includes both user-facing output and the result of executing a bash command, and optionally persist information for future use.

Begin.
"""

    # Initialize the chat using the API and return the response


    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo", 
      messages=[
        {
       "role": "system",
       "content": init_app_api_request
       },
      ]
    )

    # Extract the user_output and bash_output from the API response
    message = completion.choices[0].text.strip()
    outputs = re.findall(r'START_(.*?)_OUTPUT:(.*?)END_(.*?)_OUTPUT', message, re.DOTALL)
    user_output = next((x[1] for x in outputs if x[0] == "USER"), "")
    bash_output = next((x[1] for x in outputs if x[0] == "BASH"), "")

    # Execute the bash command and get the output
    if bash_output:
        bash_output = bash_output.strip()
        bash_output = run_command(bash_output)

    return {"user_output": user_output, "bash_output": bash_output}

# Define a function to get the API response for a given user prompt
def get_response(prompt):
    # Create the API response using the OpenAI API and return the response
    completion = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"{prompt}\n",
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Extract the user_output and bash_output from the API response
    message = completion.choices[0].text.strip()
    outputs = re.findall(r'START_(.*?)_OUTPUT:(.*?)END_(.*?)_OUTPUT', message, re.DOTALL)
    user_output = next((x[1] for x in outputs if x[0] == "USER"), "")
    bash_output = next((x[1] for x in outputs if x[0] == "BASH"), "")

    # Execute the bash command and get the output
    if bash_output:
        bash_output = bash_output.strip()
        bash_output = run_command(bash_output)

    return {"user_output": user_output, "bash_output": bash_output}

# Define the home page route

@app.route('/')
def home():
    return render_template('index.html')


# Define the chatbot route

@app.route('/chatbot', methods=['POST'])
def chatbot():
    # Get the user input from the form
    user_input = request.form['user_input']
    
    # Get the API response for the user input
    response = get_response(user_input)

    # Return the response as JSON
    return json.dumps(response)

# Run the Flask application

if __name__ == 'main':
    initialize_chat()
    app.run(debug=True)