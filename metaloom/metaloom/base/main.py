import inspect
import json
import logging
from types import MappingProxyType
from typing import Any, Callable, Dict, List, Optional

from langchain.chains.llm import LLMChain as Chain
from langchain.llms.openai import OpenAIChat as LLM
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.load import load, mapping
from pydantic import create_model
from pydantic.v1 import BaseModel



# Configure logging
# logging.basicConfig(level=logging.INFO)
#LOGGER = logging.getLogger('metaloom')


from functools import wraps

from types import MappingProxyType

def create(name: str, func: Callable) -> Any:
    params : MappingProxyType[str, inspect.Parameter] = inspect.signature(func).parameters
    fields = {k : (v.annotation.__name__, v.default) for k, v in params.items()}
    model = create_model(name, field_definitions=dict(fields))
    model.model_config = {'extra' : 'allow'}
    return model

Output : BaseModel  = create("Output", inspect.formatargvalues)



def p(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        #LOGGER.info("Running {} with args: {} and kwargs: {}", func.__name__, args, kwargs)
        return func(*args, **kwargs)

    return wrapper


def convert_quotes(json_str: str) -> Dict[str, Any]:

    @staticmethod
    def parse_value(value: str) -> Any:
        if value.isdigit():
            return int(value)
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        if "." in value:
            try:
                return float(value)
            except ValueError:
                pass
        return value

    try:
        json_dict = json.loads(json_str)
        return {key: parse_value(value) for key, value in json_dict.items()}
    except json.JSONDecodeError as e:
        #LOGGER.error("Failed to convert JSON string: {}", json_str)
        raise e


class RunnableFunction:
    """
    A class representing a runnable function.

    Attributes:
        llm: The LLM object.
        function: The function to be invoked.
        input_template: The input template for the function.

    Methods:
        get_function_params: Get the parameters of the function.
        get_description: Get the description of the function.
        get_inputs: Get the input variables of the function.
        get_placeholders: Get the placeholders for the input variables.
        get_example: Get an example of the function's input.
        invoke: Invoke the function with the given inputs.
        process_response: Process the response returned by the function.
    """
    def __init__(
        self,
        llm,
        function,
        input_template: str,
    ) -> None:
        self.llm = llm
        self.function = function
        self.input_template = input_template
        self.prompt = PromptTemplate.from_template(template=input_template)
        self.output_parser = PydanticOutputParser

    def get_function_params(self):
        """
        Get the parameters of the function.

        Returns:
            The parameters of the function.
        """
        return inspect.signature(self.function)

    def get_description(self) -> Optional[str]:
        """
        Get the description of the function.

        Returns:
            The description of the function.
        """
        return inspect.getdoc(self.function)

    def get_inputs(self) -> List[str]:
        """
        Get the input variables of the function.

        Returns:
            The input variables of the function.
        """
        return self.prompt.input_variables

    def get_placeholders(self) -> str:
        """
        Get the placeholders for the input variables.

        Returns:
            The placeholders for the input variables.
        """
        return ", ".join([f" {{{v}}} " for v in self.prompt.input_variables])

    def get_example(self) -> str:
        """
        Get an example of the function's input.

        Returns:
            An example of the function's input.
        """
        signatures = inspect.signature(self.function).parameters.values()
        example = [f"{ param.name }" for param in signatures]
        return " ".join(example)

    def invoke(self, inputs: Dict[str, Any]) -> dict:
        """
        Invoke the function with the given inputs.

        Args:
            inputs: The inputs for the function.

        Returns:
            The response returned by the function.
        """
        response_vars = inspect.signature(self.function).parameters.keys()

        def get_response_template()-> Dict[str, str]:
            return {var: "{"+var+"}" for var in response_vars}

        response_template = get_response_template()

        prompt = ChatPromptTemplate.from_messages([(
            "system",
            """Ensure response is in json format and it is parseable by `json.loads`.
                if there is no input or keys for output, pass an empty dictionary.
                if there is a list of inputs, pass them as a list of dictionaries with the same keys.
                if instructed on optional keys, omit optional keys not used""",
                            ),
                            ("ai", "What is the output format?"),
                            (
                            "user", """
                Note: If any keys were mentioned as optional in the instructions and there is no sufficient data, those k/v pairs may be omitted,

                # These are the keys for output to be used:\n{response_template}
                """
                    ), ("user", f"Input Request for the output Dict:\n{self.input_template}"
                    )
                ])

        def create(name: str, func: Callable) -> Any:
            params : MappingProxyType[str, inspect.Parameter] = inspect.signature(func).parameters
            fields = {k : (v.annotation.__name__, v.default) for k, v in params.items()}
            model = create_model(name, field_definitions=dict(fields))
            model.model_config = {'extra' : 'allow'}
            return model

        Output : type[BaseModel]  = create("Output", self.function)

        chain = Chain(
            llm=self.llm,
            prompt=self.prompt,
            output_parser=self.output_parser(pydantic_object = Output),
        )

        if len(response_vars) == 0:
            chain.return_final_only = True

        response = chain.invoke({**inputs})
        if response_vars  and 'chain_name' in response_vars:
            return self.function(chain_name=response_vars['chain_name'], kwargs = response)

        print(response)
        return self.process_response(response)

    def process_response(self, response: Dict[str, Any]) -> Any:
        """
        Process the response returned by the function.

        Args:
            response: The response returned by the function.

        Returns:
            The processed response.
        """
        if "pass_through" in response:
            return {"text": self.function()}

        if "text" not in response:
            return {"text": "No response"}

        response_data = response.get("text")
        #LOGGER.info("Response data: {}", response_data)

        if isinstance(response_data, dict):
            return self.function(**response_data)

        if isinstance(response_data, str):
            try:
                return convert_quotes(response_data)
            except json.JSONDecodeError as e:
                #LOGGER.error("Failed to convert JSON string: {}", response_data)
                raise e

        if isinstance(response_data, list):
            return [self.function(**data) for data in response_data if isinstance(data, dict)]


class RunnableLambda(RunnableFunction):

    def __init__(
        self                                  ,
        llm                                   ,
        function                              ,
        input_template : str                  ,
        description    : Optional[str] = None ,
        example        : Optional[str] = None ) -> None:
        super().__init__(llm, function, input_template)
        self.description = description
        self.example = example

    def get_description(self) -> Optional[str]:
        return self.description

    def get_example(self) -> Optional[str]:
        return self.example


class RunnableChain:

    def __init__(self, llm) -> None:
        self.function_mapping: Dict[str, Dict[str, Any]] = {}
        self.chains: Dict[str, Dict[str, Any]] = {}
        self.llm = llm
        self.runner = RunnableFunction
        self.add_function(
            "transform",
            self.transform_params,
            "Use this name for the func_name: {function}, use this dict input: {input}",
            "Rewrites an input to conform",
        )

    def add_function(
        self,
        name: str,
        function,
        input_template: str,
        description   : Optional[str] = None,
        example       : Optional[str] = None,
        ) -> None     :
        self.function_mapping[name] = {
            "function"       : function        ,
            "input_template" : input_template  ,
            "description"    : description     ,
            "example"        : example
        }

    def get_runner(self, func_name: str) -> RunnableFunction:
        if func_name not in self.function_mapping:
            raise KeyError(f"Function '{func_name}' does not exist")
        return self.runner(
            llm=self.llm,
            function=self.function_mapping[func_name]["function"],
            input_template=self.function_mapping[func_name]["input_template"],
        )

    def cue(self, func_name: str, kwargs: dict) -> Any:
        runnable = self.get_runner(func_name)
        return runnable.invoke(**kwargs)

    def define_sequence_chain(self, chain_name: str, function_names: List[str]) -> None:
        if len(function_names) < 2:
            raise ValueError("Must have more than one function to make a chain sequence")
        function_set = set(function_names)
        mapping_set = set(self.function_mapping)
        if not function_set.issubset(mapping_set):
            raise KeyError("One of the functions is not in the function mapping dict")
        self.chains[chain_name] = {"sequence": function_names}

    def define_parallel_chain(self, chain_name: str, function_names: List[str]) -> None:
        if len(function_names) < 2:
            raise ValueError("Must have more than one function to make a parallel chain sequence")
        function_set = set(function_names)
        mapping_set = set(self.function_mapping)
        if not function_set.issubset(mapping_set):
            raise KeyError("One of the functions is not in the function mapping dict")
        self.chains[chain_name] = {"parallel": function_names}

    def transform_params(self, func_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        runnable = self.get_runner(func_name)
        inputs = runnable.get_inputs()
        prompt = ChatPromptTemplate.from_messages(
            [("system","Transform the input data to match the output keys: {output_keys}"),

            # ("User", "The data you return in the json will be used by the User as the input to be used to fill this template: {new_plate}"),
            # ("ai"  , "What output keys are required for the json"                             ),
            # ("user"       , """These keys are required : {output_keys}.
            # Return ONLY a STRING JSON with these keys, NOT a markdown block, using values created from the input data."""),
            ("user"       , "this is my input data: {data}"                                          )
            ]
            )


        def create(name: str, func: Callable) -> Any:
            params : MappingProxyType[str, inspect.Parameter] = inspect.signature(func).parameters
            fields = {k : (v.annotation.__name__, v.default) for k, v in params.items()}
            model = create_model(name, field_definitions=dict(fields))
            model.model_config = {'extra' : 'allow'}
            return model

        Output : BaseModel  = create("Output", runnable.function)
        class Output_Parser(Output.__class__):
            class Config:
                extra = "forbid"
                arbitrary_types_allowed = True
            def __init__(self):
                super().__init__()
            @staticmethod
            def parse_obj(json_object: Dict[str, Any]) :
                return Output.parse_obj(json_object)

        input_data = { "data": {**input_data}, "output_keys": inputs}
        chain      = Chain ( llm = self.llm, prompt=prompt, output_parser=runnable.output_parser(pydantic_object=Output_Parser) )
        out        = chain.invoke(input_data)

        return out["text"] if "text" in out else {}

    def call_chain(self, chain_name: str, **kwargs: Any) -> Any:
        if not isinstance(kwargs, dict):
            kwargs = {k: v for k, v in dict(kwargs).items() if v is not None}
        if chain_name not in self.chains:
            raise KeyError(f"Chain '{chain_name}' does not exist")
        chaintype  =  "parallel" if "parallel" in self.chains[chain_name] else "sequence"
        links      =  self.chains[chain_name][chaintype]
        bus        =  []
        for i, link in enumerate(links):
            output = {}
            step_info = {
                i:  {
                    "name": link,
                    "inputs": dict(kwargs.items()),  # kwargs,
                    "output": [],
                    "next": links[i + 1] if i < len(links) - 1 else None,
                    }
                }

            kwargs["chain_name"] = link
            if link not in self.chains:
                kwargs.pop("chain_name")

            if chaintype == "sequence":
                inputs = self.transform_params(func_name=link, input_data=kwargs)
                print(inputs)  # kwargs['chain_name'] = link
                if "chain_name" in inputs:
                    inputs.pop("chain_name")
                runnable = self.get_runner(link)
                output = runnable.invoke(inputs)
                kwargs = output
            elif chaintype == "parallel":
                # if isinstance(kwargs, dict):
                inputs = self.transform_params(func_name=link, input_data=kwargs)
                print(inputs)  # kwargs['chain_name'] = link
                if isinstance(inputs, dict):
                    runnable = self.get_runner(link)
                    output = runnable.invoke(inputs)
            step_info[i]["output"] = output

            bus.append(step_info)
        return bus

    def get_definition(self, func_name: str) -> Dict[str, Any]:
        if func_name not in self.function_mapping:
            raise KeyError(f"Function '{func_name}' does not exist")
        runner = self.get_runner(func_name)
        return {
            "description": runner.get_description(),
            "input_template": runner.input_template,
            "inputs": runner.get_inputs(),
            "args": runner.get_function_params(),
            "example": runner.get_example(),
        }

    def get_all_definitions(self) -> Dict[str, Dict[str, Any]]:
        return {func_name: self.get_definition(func_name) for func_name in self.function_mapping}

    def print_definitions(self) -> None:
        for func_name in self.function_mapping:
            print(self.get_definition(func_name))


API_KEY = " "

# Step 1: Import necessary modules and libraries


from dotenv import load_dotenv
from langchain_google_vertexai import VertexAI

load_dotenv()


def load_chain():
    project_name = "okguis"
    return VertexAI(
        model_name       = "gemini-pro",
        max_output_tokens= 8000,
        temperature      = 0.5,
        project          = project_name,
        streaming        = False,
    )


llm  = load_chain()




###################
def test():
    '''
    # Method: convert_quotes
    ## Description: Converts a JSON string into a Python dictionary, replacing single and double quotes with double quotes.
    ## Usage:

    json_str = '{"name": "John", "age": 20}'
    result = convert_quotes(json_str)
    print(result)
    # Output: {'name': 'John', 'age': 20}

    # Method: RunnableFunction
    ## Description: A class that represents a runnable function, which can be called with a set of input parameters to get an output.
    ## Usage:

    function = lambda x: x + 1
    runnable = RunnableFunction(llm, function, input_template="Add 1 to {input_value}")
    result = runnable.invoke({"input_value": 10})  # runnable.invoke(input_value=10)
    print(result)
    # Output: 11


    # Method: get_inputs
    ## Description: Gets the list of input variable names for a runnable function.
    ## Usage:

    template = "My name is {name} and I am {age} years old."
    runnable = RunnableFunction(llm, lambda x, y: x + y, template)
    inputs = runnable.get_inputs()
    print(inputs)
    # Output: ['name', 'age']

    # Method: get_placeholders
    ## Description: Gets the placeholder string for the input values of a runnable function.
    ## Usage:

    template = "My name is {name} and I am {age} years old."
    runnable = RunnableFunction(llm, lambda x, y: x + y, template)
    placeholders = runnable.get_placeholders()
    print(placeholders)
    # Output: " {'name'}  {'age'}"

    # Method: get_example
    ## Description: Gets an example of how to call a runnable function.
    ## Usage:

    template = "My name is {name} and I am {age} years old."
    inputs = ["name", "age"]
    runnable = RunnableFunction(llm, lambda x, y: x + y, template)
    example = runnable.get_example()
    print(example)
    # Output: "[name] [age]"

    # Method: invoke
    ## Description: Invokes a runnable function with a set of input values.
    ## Usage:

    function = lambda x: x + 1
    runnable = RunnableFunction(llm, function, input_template="Add 1 to {input_value}")
    result = runnable.invoke({"input_value": 10})  # runnable.invoke(input_value=10)
    print(result)
    # Output: 11


    # Method: RunnableChain
    ## Description: A class that represents a set of runnable functions that can be called with a set of input values.
    ## Usage:

    import json

    def transform_params(function_name, input_dict):
        json_str = json.dumps(input_dict)
        return convert_quotes(json_str)

    mfr = RunnableChain(llm)
    mfr.add_function(
        "transform",
        transform_params,
        "Transform input into a form that can be used by another function.",
        "Convert a python dictionary to a JSON string and replace single and double quotes with double quotes.",
        "{{input_dict}}"
    )

    result = mfr.cue("transform", {"name": "John", "age": 20})
    print(result)
    # Output: '{"name": "John", "age": 20}'

    # Method: add_function
    ## Description: Adds a new runnable function to the set.
    ## Usage:

    mfr = RunnableChain(llm)
    mfr.add_function(
        "transform",
        transform_params,
        "Transform input into a form that can be used by another function.",
        "Convert a python dictionary to a JSON string and replace single and double quotes with double quotes.",
        "{{input_dict}}"
    )

    # Method: add_func_dict
    ## Description: Adds a dictionary of runnable functions to the set.
    ## Usage:

    mfr = RunnableChain(llm)
    mfr.add_func_dict({
        "transform": {
            "function": transform_params,
            "input_template": "Transform input into a form that can be used by another function.",
            "description": "Convert a python dictionary to a JSON string and replace single and double quotes with double quotes.",
            "example": "{{input_dict}}"
        }
    })

    # Method: get_runner
    ## Description: Gets a runnable function by name.
    ## Usage:

    mfr = RunnableChain(llm)
    mfr.add_function(
        "transform",
        transform_params,
        "Transform input into a form that can be used by another function.",
        "Convert a python dictionary to a JSON string and replace single and double quotes with double quotes.",
        "{{input_dict}}"
    )

    runner = mfr.get_runner("transform")
    result = runner.invoke(input_dict={"name": "John", "age": 20})
    print(result)
    # Output: '{"name": "John", "age": 20}'

    # Method: cue
    ## Description: Calls a runnable function with a set of input values.
    ## Usage:

    mfr = RunnableChain(llm)
    mfr.add_function(
        "transform",
        transform_params,
        "Transform input into a form that can be used by another function.",
        "Convert a python dictionary to a JSON string and replace single and double quotes with double quotes.",
        "{{input_dict}}"
    )

    result = mfr.cue("transform", input_dict={"name": "John", "age": 20})
    print(result)
    # Output: '{"name": "John", "age": 20}'

    # Method: add_chain
    ## Description: Adds a chain of runnable functions to the set.
    ## Usage:

    mfr = RunnableChain(llm)
    mfr.add_function(
        "transform",
        transform_params,
        "Transform input into a form that can be used by another function.",
        "Convert a python dictionary to a JSON string and replace single and double quotes with double quotes.",
        "{{input_dict}}"
    )

    mfr.add_chain("transform_chain", ["transform"])

    # Method: get_next
    ## Description: Gets the next runnable function in a chain based on the output of the previous function.
    ## Usage:

    mfr = RunnableChain(llm)
    mfr.add_function(
        "transform",
        transform_params,
        "Transform input into a form that can be used by another function.",
        "Convert a python dictionary to a JSON string and replace single and double quotes with double quotes.",
        "{{input_dict}}"
    )

    mfr.add_chain("transform_chain", ["transform"])

    output = mfr.get_next("transform", output={"name": "John", "age": 20})
    print(output)
    # Output: {'name': 'John', 'age': 20}

    # Method: call_chain
    ## Description: Calls a chain of runnable functions with a set of input values.
    ## Usage:

    mfr = RunnableChain(llm)
    mfr.add_function(
        "transform",
        transform_params,
        "Transform input into a form that can be used by another function.",
        "Convert a python dictionary to a JSON string and replace single and double quotes with double quotes.",
        "{{input_dict}}"
    )

    mfr.add_chain("transform_chain", ["transform"])

    result = mfr.call_chain("transform_chain", input_dict={"name": "John", "age": 20})
    print(result)
    # Output: '{"name": "John", "age": 20}'

    # Method: transform_params
    ## Description: Transforms a set of input values into a form that can be used by another function.
    ## Usage:

    mfr = RunnableChain(llm)
    mfr.add_function(
        "transform",
        transform_params,
        "Transform input into a form that can be used by another function.",
        "Convert a python dictionary to a JSON string and replace single and double quotes with double quotes.",
        "{{input_dict}}"
    )

    result = mfr.transform_params("transform", input_dict={"name": "John", "age": 20})
    print(result)
    # Output: '{"name": "John", "age": 20}'

    # Method: render_output
    ## Description: Renders the output of a set of runnable functions.
    ## Usage:

    mfr = RunnableChain(llm)
    mfr.add_function(
        "transform",
        transform_params,
        "Transform input into a form that can be used by another function.",
        "Convert a python dictionary to a JSON string and replace single and double quotes with double quotes.",
        "{{input_dict}}"
    )

    result = mfr.render_output([lambda x: x + 1, lambda x: x * 2])
    print(result)
    # Output: [2, 4]

    # Method: get_definition
    ## Description: Gets the definition of a runnable function.
    ## Usage:

    mfr = RunnableChain(llm)
    mfr.add_function(
        "transform",
        transform_params,
        "Transform input into a form that can be used by another function.",
        "Convert a python dictionary to a JSON string and replace single and double quotes with double quotes.",
        "{{input_dict}}"
    )

    definition = mfr.get_definition("transform")
    print(definition)
    # Output: {
    #     "description": "Transform input into a form that can be used by another function.",
    #     "template": "Transform input into a form that can be used by another function.",
    #     "inputs": ["input_dict"],
    #     "args": [],
    #     "example": "{{input_dict}}"
    # }

    # Method: get_all_definitions
    ## Description: Gets the definitions of all runnable functions in the set.
    ## Usage:

    mfr = RunnableChain(llm)
    mfr.add_function(
        "transform",
        transform_params,
        "Transform input into a form that can be used by another function.",
        "Convert a python dictionary to a JSON string and replace single and double quotes with double quotes.",
        "{{input_dict}}"
    )

    definitions = mfr.get_all_definitions()
    print(definitions)
    # Output: {
    #     "transform": {
    #         "description": "Transform input into a form that can be used by another function.",
    #         "template": "Transform input into a form that can be used by another function.",
    #         "inputs": ["input_dict"],
    #         "args": [],
    #         "example": "{{input_dict}}"
    #     }
    # }

    # Method: print_definitions
    ## Description: Prints the definitions of all runnable functions in the set.
    ## Usage:

    mfr = RunnableChain(llm)
    mfr.add_function(
        "transform",
        transform_params,
        "Transform input into a form that can be used by another function.",
        "Convert a python dictionary to a JSON string and replace single and double quotes with double quotes.",
        "{{input_dict}}"
    )

    mfr.print_definitions()
    # Output:
    # Function: transform
    # Description: Transform input into a form that can be used by another function.
    # Template: Transform input into a form that can be used by another function.
    # Inputs: ["input_dict"]
    # Args: []
    # Example: {{input_dict}}
    '''
    pass
