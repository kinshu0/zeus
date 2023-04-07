import openai
import json

from flask import Flask, render_template, request
import subprocess


with open("config.json", "r") as f:
    config = json.load(f)

openai.api_key = config["openai_api_key"]


def run_command(command):
    output = subprocess.check_output(command, shell=True)
    return output.decode("utf-8")


def initialize_chat():
    completion = openai.Completion.create(
        engine="davinci-codex",
        prompt="create a website",
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    response = completion.choices[0].text.strip()

    commands = [
        "echo 'install dependencies in node/python server'",
        "touch index.html style.css script.js",
        "echo 'start the server with specific port'",
    ]

    bash_output = []
    for command in commands:
        output = run_command(command)
        bash_output.append(f"START_BASH_OUTPUT: {output} END_BASH_OUTPUT")

    return {"user_output": response, "bash_output": bash_output}


def get_response(prompt):
    completion = openai.Completion.create(
        engine="davinci-codex",
        prompt=f"START_USER_PROMPT:{prompt}END_USER_PROMPT",
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    response = completion.choices[0].text.strip()

    bash_command = response.split("START_BASH_COMMAND: ")[-1].split(" END_BASH_COMMAND")[0]
    output = run_command(bash_command)
    bash_output = f"START_BASH_OUTPUT: {output} END_BASH_OUTPUT"

    return {"user_output": response, "bash_output": bash_output}


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        prompt = request.form["prompt"]
        response = get_response(prompt)
        return render_template("index.html", response=response)
    else:
        return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
