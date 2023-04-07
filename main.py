# Note: you need to be using OpenAI Python v0.27.0 for the code below to work

"""
as an example, I enter the following prompt:
    create a website

my app then needs to run this code:
    install dependencies in node/python server
    create an html, css, js file
    start the server with specific port
    output "successfully done"

portion of api response is run on bash, rest is outputted to user, bash also needs to be fed back in to the api as a message


"""


import openai
import json

from flask import Flask, render_template, request
import subprocess
import json


with open ("config.json", "r") as f:
    config = json.load(f)

openai.api_key = config['openai_api_key']



def run_command(command):
    output = subprocess.check_output(command, shell=True)
    return output.decode('utf-8')


init_app_api_request = """The API is designed to take a user prompt as input, which is sent from a web application to the API. The prompt is expected to be a string that begins with "START_USER_PROMPT:" and ends with "END_USER_PROMPT". This string should contain a task or problem description that the user wants to solve.

The API will return a JSON object with two keys: "user_output" and "bash_output". The value of "user_output" is a string that will be displayed to the user, and it should contain any information or output that the API wants to communicate to the user. The value of "bash_output" is a string that will be executed as a command in an Ubuntu container, and it should contain a valid bash command that can be executed in the container.

When the API executes the bash command, the output of the command will be piped back to the API as a message. This message will be a string that begins with "START_BASH_OUTPUT:" and ends with "END_BASH_OUTPUT". This string should contain the output of the bash command that was executed in the container.

The API is allowed to persist any information that it deems important for future context. This could include things like the user prompt, the bash command that was executed, and the output of the command. This information could be stored in a database or other persistent storage mechanism.

Overall, this API is designed to allow a user to send a task or problem description to the API, receive a response that includes both user-facing output and the result of executing a bash command, and optionally persist information for future use."""

def initialize_chat():
  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo", 
    messages=[
      {
     "role": "system",
     "content": init_app_api_request
     },
    ]
  )
  completion_parsed = json.loads(completion)
  user_output = completion_parsed['user_output']
  bash_output = completion_parsed['bash_output']

  for bo in bash_output:
     run_command(bo)

  print(completion)


def get_response(prompt):
  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo", 
    messages=[
      {"role": "system", "content": "Explain the different API Chat GPT roles of user assistant and system"},
    ]
  )
  return completion



app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        command = request.form['command']
        output = run_command(command)
        return render_template('index.html', output=output.decode('utf-8'))
    else:
        return render_template('index.html')

if __name__ == '__main__':
    initialize_chat()
    app.run(debug=True)
