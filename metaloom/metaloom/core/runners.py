from typing import Any, Callable, Dict, List

from langchain_core.runnables import (
    Runnable,
    RunnableBranch,
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
    RunnableSequence,
    RunnableWithFallbacks,
)
from metaloom.core.states import StatusItem


class BaseRunner(Runnable):
    """
    A custom Runner that performs some AI prompt calling or NLP activity.

    Args:
        config (dict): Configuration parameters for the Runner.

    Returns:
        The output of the AI prompt calling or NLP activity.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.status = StatusItem('initiaized')

    def update_status(self, new_status, new_vaalue):
        self.status.set(new_status, new_vaalue)

    def invoke(self, input_data: Any) -> Any:
        self.status.set("running")
        try:
            # Perform the AI prompt calling or NLP activity
            output_data = input_data
            self.status.set("complete")
        except Exception as e:
            self.status.set("error", str(e))
            raise
        return output_data


class BranchRunner(RunnableBranch):
    """
    A custom Runner for branching logic based on conditions.

    Args:
        *args: Variable number of condition-runnable pairs.

    Returns:
        The output of the selected branch.

    Examples:
        branch_Runner = BranchRunner(
            (condition1, runnable1),
            (condition2, runnable2),
            (condition3, runnable3)
        )
        output = branch_Runner.invoke(input_data)
    """

    def __init__(self, *args):
        self.branches = args
        self.status = StatusItem('initiaized')

    def update_status(self, new_status, new_vaalue):
        self.status.set(new_status, new_vaalue)

    def invoke(self, input_data: Any) -> Any:
        self.status.set("running")
        try:
            # Perform the branching logic based on conditions
            for condition, runnable in self.branches:
                if condition:
                    output_data = runnable.invoke(input_data)
                    self.status.set("complete")
                    return output_data
            self.status.set("error", "No branch condition matched")
        except Exception as e:
            self.status.set("error", str(e))
            raise
        return None


class SimpleLambda(RunnableLambda):
    """
    A custom Runner for executing a lambda function.

    Args:
        function (function): The lambda function to be executed.

    Returns:
        The output of the lambda function.

    Examples:
        lambda_Runner = SimpleLambda(lambda x: x + 1)
        output = lambda_Runner.invoke(input_data)
    """

    def __init__(self, function: Callable[[Any], Any | None]):
        self.function = function
        self.status = StatusItem('initiaized')

    def update_status(self, new_status, new_vaalue):
        self.status.set(new_status, new_vaalue)

    def invoke(self, input_data: Any) -> Any:
        self.status.set("running")
        try:
            # Execute the lambda function
            output_data = self.function(input_data)
            self.status.set("complete")
        except Exception as e:
            self.status.set("error", str(e))
            raise
        return output_data

class ParallelRunner(RunnableParallel):
    """
    A custom Runner for executing runnables in parallel.

    Args:
        runnables (dict): A dictionary of runnables to be executed in parallel.

    Returns:
        The outputs of the runnables as a dictionary.

    Examples:
        parallel_Runner = ParallelRunner(
            runnables={"task1": runnable1, "task2": runnable2, "task3": runnable3}
        )
        output = parallel_Runner.invoke(input_data)
    """

    def __init__(self, runnables: Dict[str, Runnable]):
        self.runnables = runnables
        self.status = StatusItem('initiaized')

    def update_status(self, new_status, new_vaalue):
        self.status.set(new_status, new_vaalue)

    def invoke(self, input_data: Any) -> Dict[str, Any]:
        self.status.set("running")
        try:
            output_data = {
                name: runnable.invoke(input_data) for name, runnable in self.runnables.items()
            }
            self.status.set("complete")
        except Exception as e:
            self.status.set("error", str(e))
            raise
        return output_data


class PassthroughRunner(RunnablePassthrough):
    """
    A custom Runner for passing through the input data.

    Returns:
        The input data as it is.

    Examples:
        passthrough_Runner = PassthroughRunner()
        output = passthrough_Runner.invoke(input_data)
    """

    @staticmethod
    def invoke(input_data: Any) -> Any:
        return input_data


class SequenceRunner(RunnableSequence):
    """
    A custom Runner for executing runnables in sequence.

    Args:
        first (Runnable): The first runnable to be executed.
        middle (list): A list of runnables to be executed in the middle.
        last (Runnable): The last runnable to be executed.

    Returns:
        The output of the last runnable.

    Examples:
        sequence_Runner = SequenceRunner(first=runnable1, middle=[runnable2, runnable3], last=runnable4)
        output = sequence_Runner.invoke(input_data)
    """

    def __init__(self, first: Runnable, middle: List[Runnable], last: Runnable):
        self.runnables = [first] + middle + [last]
        self.status = StatusItem('initiaized')

    def update_status(self, new_status, new_vaalue):
        self.status.set(new_status, new_vaalue)

    def invoke(self, input_data: Any) -> Any:
        self.status.set("running")
        try:
            # Execute the runnables in sequence
            output_data = input_data
            for runnable in self.runnables:
                output_data = runnable.invoke(output_data)
            self.status.set("complete")
        except Exception as e:
            self.status.set("error", str(e))
            raise
        return output_data


class FallbacksRunner(RunnableWithFallbacks):
    """
    A custom Runner for executing a primary runnable with fallback options.

    Args:
        runnable (Runnable): The primary runnable to be executed.
        fallbacks (list): A list of fallback runnables.

    Returns:
        The output of the primary runnable if successful, otherwise the output of the first successful fallback.

    Examples:
        fallbacks_Runner = FallbacksRunner(runnable=primary_runnable, fallbacks=[fallback_runnable1, fallback_runnable2])
        output = fallbacks_Runner.invoke(input_data)
    """

    def __init__(self, runnable: Runnable, fallbacks: List[Runnable]):
        self.runnable = runnable
        self.fallbacks = fallbacks
        self.status = StatusItem('initiaized')

    def update_status(self, new_status, new_vaalue):
        self.status.set(new_status, new_vaalue)

    def invoke(self, input_data: Any) -> Any:
        """
        Execute the primary runnable with fallback options.

        Args:
            input_data: The input data for the runnables.

        Returns:
            The output of the primary runnable if successful, otherwise the output of the first successful fallback.
        """
        self.status.set("running")
        try:
            # Execute the primary runnable with fallback options
            output_data = self.runnable.invoke(input_data)
            if output_data is None:
                for fallback in self.fallbacks:
                    output_data = fallback.invoke(input_data)
                    if output_data is not None:
                        break
            self.status.set("complete")
        except Exception as e:
            self.status.set("error", str(e))
            raise
        return output_data


class Runner(Runnable):
    """
    A custom Runner class for executing runnables.

    Args:
        name (str): The name of the Runner.
        description (str): The description of the Runner.

    Returns:
        The output of the Runnable.

    Examples:
        runner = Runner(name="my_runner", description="My Runner")
        runner.sequence(
            first=SimpleLambda(lambda x: x+1),
            middle=[SimpleLambda(lambda x: x+3), SimpleLambda(lambda x: x-2)],
            last=SimpleLambda(lambda x: x*2)
        )
        output = runner.invoke(input_data)
    """

    def __init__(self, name: str, description: str):
        self.name: str = name
        self.description: str = description
        self.status: StatusItem = StatusItem(name)
        self.runnable: Any = None
        self.runtypes = {
            "base": self.base,
            "function": self.function,
            # "branch": self.branch,
            # "parallel": self.parallel,
            # "passthrough": self.passthrough,
            # "sequence": self.sequence,
            # "fallback": self.fallback,
        }

    def invoke(self, *args, **kwargs):
        self.status.set("running")
        try:
            result = self.runnable.invoke(*args, **kwargs)
            self.status.set("complete")
            return result
        except Exception as e:
            self.status.set("error", str(e))
            raise

    def base(self, config, invoke : bool = False, *args, **kwargs):
        """
        Calls the BaseRunner class.

        Args:
            config (dict): Configuration parameters for the Runner.

        Returns:
            The output of the BaseRunner.
        """
        self.runnable = BaseRunner(config)
        if invoke:
            return self.runnable.invoke(*args,**kwargs)

    def passthrough(self, invoke : bool = False, *args, **kwargs):
        """
        Calls the PassthroughRunner class.

        Returns:
            The output of the PassthroughRunner.
        """
        self.runnable = PassthroughRunner()
        if invoke:
            return self.runnable.invoke(*args,**kwargs)

    def function(self, function, invoke : bool = False, *args, **kwargs):
        """
        Calls the SimpleLambda class.

        Args:
            function (function): The lambda function to be executed.

        Returns:
            The output of the SimpleLambda.
        """
        self.runnable = SimpleLambda(function)
        if invoke:
            return self.runnable.invoke(*args,**kwargs)

    # def branch(self, *args, invoke : bool = False):
    #     """
    #     Calls the BranchRunner class.

    #     Args:
    #         *args: Variable number of condition-runnable pairs.

    #     Examples:
    #         branch_Runner = BranchRunner(
    #             (condition1, runnable1),
    #             (condition2, runnable2),
    #             (condition3, runnable3)
    #         )
    #         output = branch_Runner.invoke(input_data)

    #     Returns:
    #         The output of the BranchRunner.
    #     """
    #     self.runnable = BranchRunner(*args)
    #     if invoke:
    #         return self.runnable.invoke()

    # def parallel(self, runnables, invoke : bool = False, *args, **kwargs):
    #     """
    #     Calls the ParallelRunner class.

    #     Args:
    #         runnables (dict): A dictionary of runnables to be executed in parallel.

    #     Returns:
    #         The output of the ParallelRunner.
    #     """
    #     self.runnable = ParallelRunner(runnables)
    #     if invoke:
    #         return self.runnable.invoke(*args,**kwargs)

    # def sequence(self, first, middle, last, invoke : bool = False, *args, **kwargs):
    #     """
    #     Calls the SequenceRunner class.

    #     Args:
    #         first (Runnable): The first runnable to be executed.
    #         middle (list): A list of runnables to be executed in the middle.
    #         last (Runnable): The last runnable to be executed.

    #     Returns:
    #         The output of the SequenceRunner.
    #     """
    #     self.runnable = SequenceRunner(first, middle, last)
    #     if invoke:
    #         return self.runnable.invoke(*args,**kwargs)

    # def fallback(self, runnable, fallbacks, invoke : bool = False, *args, **kwargs):
    #     """
    #     Calls the FallbacksRunner class.

    #     Args:
    #         runnable (Runnable): The primary runnable to be executed.
    #         fallbacks (list): A list of fallback runnables.

    #     Returns:
    #         The output of the FallbacksRunner.
    #     """
    #     self.runnable = FallbacksRunner(runnable, fallbacks)
    #     if invoke:
    #         return self.runnable.invoke(*args,**kwargs)
