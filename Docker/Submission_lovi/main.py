import flask
import os

app = flask.Flask(__name__)

@app.route("/test", methods=["POST"])
def main():
    try:
        # Get the file path from the local machine using Flask
        data = flask.request.get_data().decode("utf-8").strip()

        with open("/app/input.file", "w") as file: 
            file.write(data)

        # Run the Bash script with the file path as an argument
        command = f"bash run.sh /app/input.file"
        os.system(command)

        # Read the output from the script
        with open("/app/UN.vi.translated.desubword", "r") as output_file:
            output = output_file.read()

        result = output
    except Exception as e:
        result = e

    return result

if __name__ == "__main__":
    app.run("0.0.0.0", port=7501)
