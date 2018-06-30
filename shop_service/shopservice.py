from flask import Flask

app = Flask(__name__)


@app.route("/")
def main():
    return "Hello World, I'm the Shop service"

if __name__ == '__main__':
    app.run(port=80, host='0.0.0.0', debug=True)