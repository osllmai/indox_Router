"""
Convert a markdown file to a Jupyter notebook.
"""

import json
import re
import sys


def convert_markdown_to_notebook(markdown_file, notebook_file):
    """
    Convert a markdown file to a Jupyter notebook.

    Args:
        markdown_file: Path to the markdown file.
        notebook_file: Path to the output notebook file.
    """
    # Read the markdown file
    with open(markdown_file, "r", encoding="utf-8") as f:
        markdown = f.read()

    # Initialize the notebook structure
    notebook = {
        "cells": [],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.10",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    # Split the markdown into chunks
    chunks = re.split(r"(```python[\s\S]*?```)", markdown)

    for chunk in chunks:
        if chunk.startswith("```python"):
            # This is a code cell
            code = chunk.replace("```python", "").replace("```", "").strip()
            notebook["cells"].append(
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": code.split("\n"),
                }
            )
        elif chunk.strip():
            # This is a markdown cell
            notebook["cells"].append(
                {"cell_type": "markdown", "metadata": {}, "source": chunk.split("\n")}
            )

    # Write the notebook to a file
    with open(notebook_file, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=2)

    print(f"Converted {markdown_file} to {notebook_file}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_to_notebook.py <markdown_file> <notebook_file>")
        sys.exit(1)

    markdown_file = sys.argv[1]
    notebook_file = sys.argv[2]

    convert_markdown_to_notebook(markdown_file, notebook_file)
