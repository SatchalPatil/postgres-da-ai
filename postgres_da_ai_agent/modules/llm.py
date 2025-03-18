"""
Purpose:
    Interact with a local Ollama model.
    Provide supporting prompt engineering functions.
"""

from typing import Any, Dict
from ollama import generate  # Assumes an Ollama Python client is available

def prompt(user_prompt: str) -> str:
    response = generate(model="llama3.1:8b", prompt=user_prompt)
    
    # Debug: Print response and its type
    print("Full response:", response)
    print("Response type:", type(response))
    
    # Attempt 1: Use vars() if response is a custom object with __dict__
    try:
        response_dict = vars(response)
        print("Response vars:", response_dict)
        if "response" in response_dict:
            return str(response_dict["response"]).strip()
    except TypeError:
        # If vars() fails, response might not be an object with __dict__
        pass

    # Attempt 2: If response is a dict
    if isinstance(response, dict) and "response" in response:
        return str(response["response"]).strip()

    # Attempt 3: Use getattr to retrieve the 'response' attribute
    resp_val = getattr(response, "response", None)
    if resp_val is not None:
        return str(resp_val).strip()

    # If none of the above worked, print available attributes for debugging.
    print("Available attributes:", dir(response))
    raise AttributeError("Response object does not contain a 'response' attribute")

def add_cap_ref(prompt: str, prompt_suffix: str, cap_ref: str, cap_ref_content: str) -> str:
    """
    Attaches a capitalized reference to the prompt.
    
    Example:
        prompt = 'Refactor this code.'
        prompt_suffix = 'Make it more readable using this EXAMPLE.'
        cap_ref = 'EXAMPLE'
        cap_ref_content = 'def foo():\n    return True'
        
        returns:
            'Refactor this code. Make it more readable using this EXAMPLE.
            
            EXAMPLE
            
            def foo():
                return True'
    """
    new_prompt = f"{prompt} {prompt_suffix}\n\n{cap_ref}\n\n{cap_ref_content}"
    return new_prompt
