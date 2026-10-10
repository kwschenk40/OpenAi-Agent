from collections.abc import Callable
import json

from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.write_file import schema_write_file, write_file
from functions.run_python_file import schema_run_python_file, run_python_file

available_functions = [
    schema_get_files_info,
    schema_get_file_content,
    schema_write_file, 
    schema_run_python_file,
]

function_map: dict[str, Callable[..., str]] = {
    "get_file_content": get_file_content,
    "get_files_info": get_files_info,
    "run_python_file": run_python_file,
    "write_file": write_file,
}

def _tool_message(tool_call, content: str) -> dict:
    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": content,
    }

def call_function(tool_call, verbose: bool = False) -> dict:
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments or "{}")
    if verbose:
        print(f" - Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")
    func = function_map.get(function_name)
    if func is None:
        return _tool_message(tool_call, f"Error: Unknown function: {function_name}")
    working_directory = "./calculator"
    function_args["working_directory"] = working_directory
    try:
        result = func(**function_args)
    except TypeError as e:  # missing or unexpected arguments from the model
        result = f"Error: Bad arguments for {function_name}: {e}"

    return _tool_message(tool_call, result)