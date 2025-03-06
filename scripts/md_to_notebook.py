#!/usr/bin/env python3
"""
Convert markdown cookbook to Jupyter notebook.
"""

import json
import re
import os
import sys
from typing import List, Dict, Any


def parse_markdown(md_content: str) -> List[Dict[str, Any]]:
    """Parse markdown content into notebook cells."""
    cells = []
    current_text = []
    in_code_block = False
    code_language = ""

    for line in md_content.split("\n"):
        if line.startswith("```"):
            if in_code_block:
                # End code block
                if current_text:
                    cells.append(
                        {
                            "cell_type": "code",
                            "metadata": {},
                            "outputs": [],
                            "execution_count": None,
                            "source": current_text,
                        }
                    )
                current_text = []
                in_code_block = False
            else:
                # Start code block
                if current_text:
                    cells.append(
                        {
                            "cell_type": "markdown",
                            "metadata": {},
                            "source": current_text,
                        }
                    )
                current_text = []
                in_code_block = True
                code_language = line[3:].strip()
                if code_language != "python":
                    # Skip non-Python code blocks
                    in_code_block = False
            continue

        if in_code_block and code_language == "python":
            current_text.append(line)
        elif not in_code_block:
            current_text.append(line)

    # Add remaining content
    if current_text:
        cells.append(
            {
                "cell_type": "markdown" if not in_code_block else "code",
                "metadata": {},
                "source": current_text,
            }
        )

    # Clean up cell sources
    for cell in cells:
        if isinstance(cell["source"], list):
            cell["source"] = "\n".join(cell["source"])
        if cell["source"].strip() == "":
            continue

    return [cell for cell in cells if cell["source"].strip()]


def create_notebook(cells: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a Jupyter notebook from cells."""
    return {
        "cells": cells,
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
                "version": "3.8.0",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }


def main():
    """Convert markdown to notebook."""
    if len(sys.argv) != 3:
        print("Usage: python md_to_notebook.py input.md output.ipynb")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, "r", encoding="utf-8") as f:
        md_content = f.read()

    cells = parse_markdown(md_content)
    notebook = create_notebook(cells)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1)

    print(f"Created notebook: {output_file}")


if __name__ == "__main__":
    main()
