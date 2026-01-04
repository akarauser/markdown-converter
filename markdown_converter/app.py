import argparse
import json
import os
import re
from typing import Any

from .utils._logger import logger


def search_for_scripts(source_path: str) -> list[Any]:
    """
    Searchs for folder to find scripts and appends those to certain list.
    Returns a list of scripts path as str.

    Args:
        source_path (str): Path to source folder.
    """
    scripts = []
    try:
        for root, dirs, files in os.walk(source_path):
            if "_docs" not in root:
                for file in files:
                    if file.endswith((".ipynb", ".py")):
                        scripts.append(root + "\\" + file)
        return scripts
    except Exception as e:
        logger.error(f"An error occurred while searching scripts: {e}")


def convert_to_markdown(script_path, destination_path):
    """
    Converts a Python script to a Markdown (.md) file.

    Args:
        script_path (str): Path to the Python script file.
        destination_path (str): Path to save the Markdown file.
    """
    try:
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)
    except Exception:
        logger.error("Failed to create folder.")

    try:
        if ".py" in script_path:
            with open(script_path, encoding="utf-8") as f:
                script_content = f.read()
        else:
            with open(script_path, encoding="utf8") as f:
                script_content = json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found at {script_path}")
        return
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return

    md_content = ""
    if ".py" in script_path:
        lines: list[str] | Any = script_content.splitlines()

        for line in lines:
            # Strip leading/trailing whitespace
            line: str | Any = line.strip()

            # Comments (lines starting with "#")
            if line.startswith("#"):
                md_content += f"*  {line}\n"
            # Docstrings (triple quotes)
            elif line.startswith('"""'):
                md_content += f"**  {line}**\n"
            # Blank lines (preserve blank lines in markdown)
            elif line == "":
                md_content += "\n"
            # Code lines (assuming anything not a comment or docstring is code)
            else:
                md_content += f"  {line}\n"
    else:
        for i in range(len(script_content["cells"])):
            for line in script_content["cells"][i]["source"]:
                # Strip leading/trailing whitespace
                line = line.strip()

                # Images
                if ";base64," in line:
                    md_content += re.sub("\\(data:image([^)]+)\\)", "\n", line)
                # Comments (lines starting with "#")
                elif line.startswith("#"):
                    md_content += f"*  {line}\n"
                # Docstrings (triple quotes)
                elif line.startswith('"""'):
                    md_content += f"**  {line}**\n"
                # Blank lines (preserve blank lines in markdown)
                elif line == "":
                    md_content += "\n"
                # Code lines (assuming anything not a comment or docstring is code)
                else:
                    md_content += f"  {line}\n"

    try:
        with open(
            destination_path
            + f"{script_path.split(args.source_path)[-1].split('.py')[0].split('.ipynb')[0].replace('\\', '+').lstrip('+')}"
            + ".md",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(md_content)
        logger.info(
            f"{script_path.split(args.source_path)[-1]} successfully converted."
        )
    except Exception as e:
        logger.error(f"\nError writing to file: {e}\n")


def main(source_path: str, destination_path: str):
    """
    Main function to convert scripts to .md files.

    Args:
        source_path (str): Path of source folder of scripts.
        destination_path (str): Path of destination folder of .md files.
    """
    for script_path in search_for_scripts(source_path):
        convert_to_markdown(script_path, destination_path)
    print("\nDone.")


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(
            description="Creates .md files from Python scripts."
        )
        parser.add_argument(
            "-s", "--source_path", metavar="", help="Path to the source folder"
        )
        parser.add_argument(
            "-d",
            "--destination_path",
            metavar="",
            help="Path to the destination folder.",
        )
        args: argparse.Namespace = parser.parse_args()

        main(args.source_path, args.destination_path)

    except Exception as e:
        logger.error(f"An error occured: {e}")
