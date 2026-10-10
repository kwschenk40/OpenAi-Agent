import json
import os
import sys
import argparse

from dotenv import load_dotenv
from openai import OpenAI
from prompts import system_prompt
from config import MAX_ITERS

from call_function import available_functions, call_function


def main():

    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")

    if api_key is None:
        raise RuntimeError("OPENROUTER_API_KEY environment variable not set")

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]
    if args.verbose:
        print(f"User prompt: {args.user_prompt}\n")

    for _ in range(MAX_ITERS):
        try:
            final_response = generate_content(client, messages, args.verbose)
            if final_response:
                print("Final response:")
                print(final_response)
                return
        except Exception as e:
            print(f"Error in generate_content: {e}")

    print(f"Maximum iterations ({MAX_ITERS}) reached")
    sys.exit(1)


def generate_content(client: OpenAI, messages: list, verbose: bool) -> str | None:
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        tools=available_functions,
    )
    if not response.usage:
        raise RuntimeError("API response appears to be malformed")

    if verbose:
        print("Prompt tokens:", response.usage.prompt_tokens)
        print("Response tokens:", response.usage.completion_tokens)

    message = response.choices[0].message
    messages.append(message)

    if not message.tool_calls:
        return message.content

    for tool_call in message.tool_calls:
        if tool_call.type != "function":
            continue
        result_message = call_function(tool_call, verbose)
        if not result_message.get("content"):
            raise RuntimeError(f"Empty function response for {tool_call.function.name}")
        if verbose:
            print(f"-> {result_message['content']}")
        messages.append(result_message)

    return None


if __name__ == "__main__":
    main()


#]

#   response = client.chat.completions.create(
#       model="openrouter/free",
#        messages=messages,
#        tools=available_functions,
#    )

#    if response.usage is None:
#        raise RuntimeError("Response does not contain usage metadata")

#    message = response.choices[0].message

#    if args.verbose:
#        print(f"User prompt: {args.user_prompt}")
#        print(f"Prompt tokens: {response.usage.prompt_tokens}")
#        print(f"Response tokens: {response.usage.completion_tokens}")
#        print(f"Response:\n{message.content}")
#    elif message.content:
#        print(f"Response:\n{message.content}")

#    if message.tool_calls:
#        messages.append(message.model_dump(exclude_none=True))
#        for tool_call in message.tool_calls:
#            result_message = call_function(tool_call, verbose=args.verbose)

#            if not result_message.get("content"):               raise RuntimeError(
#                    f"Function {tool_call.function.name} returned no content"
#                )

#            if args.verbose:
#                print(f"-> {result_message['content']}")
  
#if __name__ == '__main__':
#    main()
