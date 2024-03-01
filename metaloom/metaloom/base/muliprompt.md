**Instructions for Constructing Prompt Dicts**

**Purpose:** To create a template for constructing prompt dicts that can be used to generate custom prompts for AI systems.

**Format:**

```python
MY_NEW_PROMPT = {
    "name": "My New Prompt",  # Unique identifier for the prompt
    "system": "Instructions for how to use the prompt",
    "template": "Template for generating the prompt",
    "input_variables": ["Variable 1", "Variable 2"],  # List of input variables used in the template
    "output_variables": {
        "Output Variable 1": "Description of the first output variable",
        "Output Variable 2": "Description of the second output variable",
    },  # Dictionary of output variables and their descriptions
    "meta_requests": {  # Optional dictionary of meta requests for additional information
        "Meta Request 1": {
            "key_1": "Description of the first meta request",
            "key_2": "Description of the second meta request",
        },
        "Meta Request 2": {
            "key_3": "Description of the third meta request",
        },
    },
    "selections": {  # Optional dictionary of selections for different options
        "Selection Key 1": {
            "option1": "Description of the first option",
            "option2": "Description of the second option",
        },
        "Selection Key 2": {
            "option3": "Description of the third option",
        },
    },
}
```

**Instructions:**

1. **Name**: Assign a unique name to the prompt for identification.
2. **System**: Provide instructions on how to use the prompt with the AI system.
3. **Template**: Specify the template for generating the prompt using input variables in curly braces.
4. **Input Variables**: List the input variables that will be used to fill in the template.
5. **Output Variables**: Define the output variables and their descriptions. These will be filled in by the AI system.
6. **Meta Requests (Optional)**: Specify meta requests for additional information that you want the AI to provide in the output.
7. **Selections (Optional)**: Include selections if you want the AI to return a specific option based on the input values.

**Example:**

Consider the following simple prompt dict:

```python
MY_PROMPT = {
    "name": "Example Prompt",
    "system": "Provide an example of an output for the input",
    "template": "Show me an example of {input_val}.",
    "input_variables": ["input_val"],
    "output_variables": {
        "example": "Description of the example output",
    },
}
```

By providing this prompt dict to an AI system, when calling that prompt with `healthy food`, the request would be `Show me an example of 'healthy food'.`

The AI system would then generate an example output based on the input value of 'healthy food', the return output would be:

```json

{ "example": "Fresh fruits and vegetables"}

```


