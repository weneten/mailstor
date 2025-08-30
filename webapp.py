from __future__ import annotations

import os
from pathlib import Path
from typing import List

from flask import Flask, abort, redirect, render_template_string, send_from_directory, url_for

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
ATTACHMENT_PREFIX = "mailstor"


def _list_files() -> List[str]:
    files: List[str] = []
    for directory in sorted(BASE_DIR.iterdir()):
        if directory.is_dir() and directory.name.startswith(ATTACHMENT_PREFIX):
            for file in sorted(directory.iterdir()):
                if file.is_file():
                    rel_path = f"{directory.name}/{file.name}"
                    files.append(rel_path)
    return files


@app.route("/")
def index():
    files = _list_files()
    return render_template_string(
        """
        <!doctype html>
        <title>Files</title>
        <h1>Your Files</h1>
        <ul>
        {% for f in files %}
          <li>{{ f }} - <a href="{{ url_for('download_file', path=f) }}">download</a> | <a href="{{ url_for('delete_file', path=f) }}">delete</a></li>
        {% else %}
          <li>No files found.</li>
        {% endfor %}
        </ul>
        """,
        files=files,
    )


@app.route("/download/<path:path>")
def download_file(path: str):
    target = (BASE_DIR / path).resolve()
    if not target.is_file() or BASE_DIR.resolve() not in target.parents:
        abort(404)
    return send_from_directory(target.parent, target.name, as_attachment=True)


@app.route("/delete/<path:path>")
def delete_file(path: str):
    target = (BASE_DIR / path).resolve()
    if (
        not target.is_file()
        or BASE_DIR.resolve() not in target.parents
        or not target.parent.name.startswith(ATTACHMENT_PREFIX)
    ):
        abort(404)
    target.unlink()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
