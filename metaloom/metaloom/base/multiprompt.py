import enum
import json
import re
from enum import Enum
from typing import Any, List, Sequence
from pydantic import create_model
from typing import Callable
import inspect

from dotenv import load_dotenv
from langchain_google_vertexai import VertexAI
from langchain.output_parsers import EnumOutputParser, ResponseSchema, StructuredOutputParser
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnableSequence, chain
from langchain_core.prompts.chat import MessageLike
from langchain_core.tools import tool
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.pydantic_v1 import BaseModel


# Load chat model
def gemini(stream=False, memory=None) -> VertexAI:
    # Initialize Vertex AI
    load_dotenv()
    project_name = "okguis"
    return VertexAI(
        model_name="gemini-pro",
        max_output_tokens=8000,
        temperature=0.2,
        project=project_name,
        streaming=stream,
    )


from types import MappingProxyType


def create(name: str, func: Callable) -> Any:
    params: MappingProxyType[str, inspect.Parameter] = inspect.signature(
        func).parameters
    fields = {k: (v.annotation.__name__, v.default) for k, v in params.items()}
    model = create_model(name, field_definitions=dict(fields))
    model.model_config = {'extra': 'allow'}
    return model


Output: BaseModel = create("Output", inspect.formatargvalues)

# priint the `Output` model
# print(Output)


# Create a BaseOutputParser that takes either a string or a BaseMessage as input and converts it to the desired output format.
class DynamicStructured(StructuredOutputParser):

    def __init__(self, *args):
        super().__init__(response_schemas=[])
        # To use PyAnnotate indexing instead of getattr(self, x)
        self.response_schemas = [
            schema for schema in args if isinstance(schema, ResponseSchema)
        ]

    def from_dict(self, key, my_dict) -> StructuredOutputParser:
        enum_options = enum.Enum(key, {**my_dict})
        return self._from_enum(enum_options)

    def _from_enum(self, enum_options) -> StructuredOutputParser:
        return StructuredOutputParser(response_schemas=[
            ResponseSchema(name=output.name, description=output.value)
            for output in enum_options
        ])


# Create a BaseOutputParser that takes either a string or a BaseMessage as input and converts it to the desired output format.
class DynamicEnum(EnumOutputParser):

    class _enum_dummy(Enum):
        pass

    def __init__(self):
        super().__init__(enum=self._enum_dummy)
        # To use PyAnnotate indexing instead of getattr(self, x)

    def from_dict(self, key, my_dict) -> EnumOutputParser:
        enum_options = enum.Enum(key, {**my_dict})
        return self._from_enum(enum_options)

    def _from_enum(self, enum_options) -> EnumOutputParser:
        self.enum = enum_options
        return self


def selection_fields(my_enum, count=1):
    vals = {name: value.value for name, value in my_enum.__members__.items()}
    return (
        f"\nFor the `{my_enum.__name__}` key in output, select {count} of the following descriptins:\n"
        + ''.join([
            f"'{attr}' --> description: {description}\n"
            for (attr, description) in vals.items()
        ]))


def meta_fields(my_enum):
    vals = {name: value.value for name, value in my_enum.__members__.items()}
    return (
        f"\nFor the `{my_enum.__name__}` key in your output, Fill in the meta fields described.\n"
        + ''.join([
            f' "{attr}" : <value>, // {value}\n'
            for (attr, value) in vals.items()
        ]))


# Create a BasePromptTemplate that takes in a dictionary of template variables and produces a PromptValue.
class MultiTemplate(ChatPromptTemplate):
    _my_prompts    : dict = {}
    _my_tools      : dict = {} # future, to hold presets
    _my_rules      : dict = {} # future, to hold presets
    _my_reqs       : dict = {} # future, to hold presets
    _my_selections : dict = {} # future, to hold presets
    _my_callbacks  : dict = {} # future, to hold presets
    _my_parsers    : dict = {"structured": DynamicStructured, "enum": DynamicEnum}
    _my_logger     : Any  = None  # not implementd yet
    input_variables: List[str] = []

    def __init__(self, **kwargs):
        kwargs["input_variables"]= kwargs.get("input_variables", [])
        kwargs["template"]       = kwargs.get("template", "")
        kwargs["messages"]       = kwargs.get("messages", [])
        super().__init__(**kwargs)

    def set_parser(self, parser):
        self.output_parser = self._my_parsers[parser]

    def add_template(self, **kwargs):
        assert isinstance(kwargs, dict), f"Expected dict got {type(kwargs)}"
        name = kwargs["name"]
        assert name not in self._my_prompts, f"{name} is already provided and cannot be added again"
        assert "system" in kwargs, f"Expected 'system'   in {kwargs}"
        system = kwargs["system"]
        assert "template" in kwargs, f"Expected 'template' in {kwargs}"
        template = kwargs["template"]
        assert "input_variables" in kwargs, f"Expected 'input_variables'   in {kwargs}"
        input_variables = kwargs["input_variables"]
        assert "output_variables" in kwargs, f"Expected 'output    in {kwargs}"
        output = kwargs["output_variables"]
        meta_requests = kwargs.get("meta_requests", {})
        assert isinstance(
            meta_requests,
            dict | list), f"Expected dict|list got {type(meta_requests)}"
        selections = kwargs.get("selections", {})
        assert isinstance(selections, dict
                            | list), f"Expected dict|list got {type(selections)}"
        callbacks = kwargs.get("callbacks", {})
        assert isinstance(callbacks, dict
                            | list), f"Expected dict|list got {type(callbacks)}"
        self._my_prompts[name] = {
            "system": system,
            "rules": kwargs.get("rules", []),
            "template": template,
            "input_variables": input_variables,
            "output_variables": output,
            "meta_requests": meta_requests,
            "selections": selections,
            "callbacks": callbacks,
        }

    def get_info(self, name):
        return self._my_prompts[name]

    def build_meta_requests(self, requests: list | dict):
        output_reqs = {}
        if isinstance(requests, dict):
            for req, req_dict in requests.items():
                output_reqs[req] = meta_fields(
                    self._my_parsers["enum"]().from_dict(req, req_dict).enum)
        elif isinstance(requests, list):
            for req in requests:
                if req not in self._my_reqs:
                    print(
                        f"{req} Not in the list of avaiilable selections. Skippiing"
                    )
                    continue
                selections = self._my_reqs[req]
                req_dict = {req: self._my_reqs[req]}
                output_reqs[req] = meta_fields(
                    self._my_parsers["enum"]().from_dict(req, req_dict).enum)
        return output_reqs

    def build_selections(self, selections: list | dict):
        options_lists = {}
        if isinstance(selections, dict):
            for sel, sel_dict in selections.items():
                options_lists[sel] = selection_fields(
                    self._my_parsers["enum"]().from_dict(sel, sel_dict).enum)
        elif isinstance(selections, list):
            for sel in selections:
                if sel not in self._my_selections:
                    print(
                        f"{sel} Not in the list of avaiilable selections. Skippiing"
                    )
                    continue
                selections = self._my_selections[sel]
                options_lists[sel] = selection_fields(
                    self._my_parsers["enum"]().from_dict(sel, selections).enum)
        return options_lists

    def build_messages(self, name):
        prompt_config = self._my_prompts[name]
        messages: List = [SystemMessage(type="system", content=prompt_config["system"])]
        if len(prompt_config["output_variables"]) > 0:
            output_variables = self.build_meta_requests(
                {"text": prompt_config["output_variables"]})
            output = "\n".join(list(output_variables.values()))
            messages.append(HumanMessage(content=output))
        if len(prompt_config["meta_requests"]) > 0:
            requests = self.build_meta_requests(prompt_config["meta_requests"])
            meta_request = "\n".join(list(requests.values()))
            messages.append(HumanMessage(content=meta_request))
        if len(prompt_config["selections"]) > 0:
            selectors = self.build_selections(prompt_config["selections"])
            selector = "\n".join(list(selectors.values()))
            messages.append(HumanMessage(content=selector))
        if len(prompt_config["rules"]) > 0:
            rules = (
                "# Ensure your reply does not deviate from the following rules:\n"
                + "\n- ".join(prompt_config["rules"])
            )
            messages.append(HumanMessage(content=rules))
            messages.append(
                AIMessage(
                    content=
                    "I will ensure my response adheres to the instructions, and will not violate the rules, opting for rules in contested situations. {__dummy__}"
                ))
        messages.append(HumanMessage(content=prompt_config["template"]))
        self.messages = messages
        return messages

    def buiild_prompt(self, prompt_name):
        config = self._my_prompts[prompt_name]
        self.metadata = config.get("metadata", {})
        self.input_variables = config["input_variables"]
        self.build_messages(prompt_name)
        kwargs = {
            'template':
            self,
            'input_variables':
            config["input_variables"],
            'messages':
            self.build_messages(prompt_name)
        }
        return MultiTemplate(**kwargs)

    def add_tool(self, tool):
        assert hasattr(
            tool, "name"
        ), "Function has no name, use the @chain decorator if missing."
        assert (tool.name not in self._my_tools
                ), f"{tool.name} is already provided and cannot be added again"
        name = tool.name
        self._my_tools[name] = tool
        return self

    def _myformat(self, input):
        text = self.format_prompt(**input).to_string()
        return re.sub(r"{(\w+)}", lambda match: input[match.group(1)], text)

    # print(MULTIPLATE.get_info("greeting"))
    def cue(self, name, input_dict=None):
        if input_dict is None:
            input_dict = {}
        prompt            = self.buiild_prompt(name)
        llm               = gemini()
        runnable_sequence = RunnableSequence(self._myformat, llm, SimpleJsonOutputParser())
        output            = runnable_sequence.invoke(input_dict)
        print(output)



