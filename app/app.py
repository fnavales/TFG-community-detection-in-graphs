from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def main():
    return render_template("miserables.html")

if __name__ == "__main__":
	app.run(host='0.0.0.0')
