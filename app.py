"""
This script is seperate from the entire client-end project
and is not intended for the client to use this script.
"""

from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index() -> None:
    """
    The function `index()` returns the rendered template `index.html`

    The function `index()` is a function that returns the rendered template `index.html`

    Returns:
      The index.html file
    """
    return render_template("index.html")


app.run(host="10.0.0.217", port=5000, debug=False, threaded=True)
