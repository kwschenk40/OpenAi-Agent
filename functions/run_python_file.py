import os
import subprocess

def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None) -> str:
    try:
        working_dir_abs = os.path.abspath(working_directory)
        file_path_abs = os.path.normpath(os.path.join(working_dir_abs, file_path))
        if os.path.commonpath([working_dir_abs, file_path_abs]) != working_dir_abs:
            return (f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory')
        if os.path.isfile(file_path_abs) == False:
            return (f'Error: "{file_path}" does not exist or is not a regular file')
        if file_path_abs.endswith(".py") == False:
            return (f'Error: "{file_path}" is not a Python file')

        command = ["python", file_path_abs]
        if args:
            command.extend(args)
        result = subprocess.run(command, capture_output=True, cwd=working_dir_abs, text=True, timeout=30)
        output = []
        if result.returncode != 0:
            output.append(f"Process exited with code {result.returncode}")
        if result.stdout == "" and result.stderr == "":
            output.append("No output produced")
        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")
        return "\n".join(output)
    except Exception as e:
        return f"Error: executing Python file: {e}"


schema_run_python_file = {
    "type": "function",
    "function": {
        "name": "run_python_file",
        "description": "Executes a Python (.py) file relative to the working directory, with optional command-line arguments, and returns its stdout/stderr (30 second timeout)",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the Python file to execute, relative to the working directory",
                },
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of command-line arguments to pass to the Python file",
                },
            },
            "required": ["file_path"],
        },
    },
}