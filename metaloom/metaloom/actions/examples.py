def minidocs():
    """
    A Runnable is a unit of work that can be invoked, batched, streamed, transformed, and composed.
    These classes can be combined to form pipelines that can be used to construct actions that can be invoked by agents.

    RunnableConfigurableField:
    - Represents a configurable field with an ID, name, and description.

    ConfigurableFieldSingleOption:
    - Represents a configurable field with a single default option.

    ConfigurableFieldMultiOption:
    - Represents a configurable field with multiple default options.

    RouterInput:
    - Represents input for the RouterRunnable.

    RouterRunnable:
    - Executes a specific runnable based on the input key.

    Runnable:
    - Base class for defining a custom runnable.

    MyRunnableClass (Runnable):
    - Inherits from Runnable and performs work on the input data.

    RunnableSerializable:
    - Base class for serializable runnables.

    MySerializableRunnable (RunnableSerializable):
    - Inherits from RunnableSerializable and performs work on the input data.

    RunnableBinding:
    - Binds additional parameters to a runnable.

    RunnableBranch:
    - Takes a set of conditions and their corresponding runnables and executes the runnable that satisfies the condition.

    RunnableConfig:
    - Configures a runnable with additional parameters.

    RunnableGenerator:
    - Invokes a generator function and returns the yielded values.

    RunnableLambda:
    - Runs a lambda function on the input data.

    RunnableParallel:
    - Executes multiple runnables in parallel.

    RunnablePassthrough:
    - Passes the input data unchanged.

    RunnableSequence:
    - Executes runnables sequentially, with the output of each runnable serving as the input of the next.

    RunnableWithFallbacks:
    - Executes a primary runnable and falls back to alternative runnables if it fails.

    runnable_sequence (RunnableSequence):
    - Represents a sequence of runnables.

    """


# Importing necessary modules
from langchain_core.runnables import (
    ConfigurableField,
    ConfigurableFieldSingleOption,
    ConfigurableFieldMultiOption,
    RouterInput,
    RouterRunnable,
    Runnable,
    RunnableBranch,
    RunnableConfig,
    RunnableGenerator,
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
    RunnableSequence,
    RunnableWithFallbacks
)

# ConfigurableField
# Create a configurable field
field = ConfigurableField(id="my_id", name="my_field", description="my_description")

# ConfigurableFieldSingleOption
# Create a configurable field with a default option
single_option_field : ConfigurableFieldSingleOption = ConfigurableFieldSingleOption(
    id          = "my_id",
    options     = {"option1": 1, "option2": 2},
    default     = "option1",
    name        = "my_field",
    description = "my_description"
)

# Use the default option
single_option_field.default

# ConfigurableFieldMultiOption
# Create a configurable field with multiple default options
multi_option_field : ConfigurableFieldMultiOption = ConfigurableFieldMultiOption(
    id          = "my_id",
    options     = {"1":1, "2":2, "3":3},
    default     = ["1", "2"],
    name        = "my_field",
    description = "my_description"
)

# Use the default options
multi_option_field.default

# RouterInput
# Create a router input
input_obj = RouterInput(key="add", input=10)

# RouterRunnable
# Create runnable functions
runnable1 = RunnableLambda(lambda x: x + 1)
runnable2 = RunnableLambda(lambda x: x * 2)

# Create a router runnable
router_runnable = RouterRunnable(runnables={"add": runnable1, "multiply": runnable2})

# Route the input to the selected runnable
print("Route the input to the selected runnable")
output = router_runnable.invoke(input_obj)
print(output)

# MyRunnableClass
# Custom subclass of the Runnable class
class MyRunnableClass(Runnable):
    def invoke(self, input_data):
        return input_data * 2

# Create an instance of MyRunnableClass
my_runnable = MyRunnableClass()

# Invoke the runnable with input_data
print("Invoke the runnable with input_data")
print(output)
output = my_runnable.invoke(input_data=10)

# RunnableBinding
# Create a runnable
my_runnable = RunnableLambda(lambda x: x + 1)

# Bind additional params to the runnable
bound_runnable = my_runnable.bind(param1=2)

# RunnableBranch
# Create conditions and runnables
condition1       = lambda x: x % 2 == 0
condition2       = lambda x: x % 3 == 0
runnable1        = RunnableLambda(lambda x: x * 2)
runnable2        = RunnableLambda(lambda x: x * 3)
default_runnable = RunnableLambda(lambda x: x)

# Create a branch runnable
branch_runnable = RunnableBranch(
    (condition1, runnable1),
    (condition2, runnable2),
    bound_runnable
)

# Invoke the branch runnable with input
print("Invoke the branch runnable with input")
print(output)
output = branch_runnable.invoke(3)

# RunnableConfig
# Custom subclass of the Runnable class
class MyRunnable(Runnable):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def invoke(self, input_data):
        # Perform work using the config
        config_value = self.config.get("key")
        return input_data + config_value

# Create a config for the runnable
config = {"key": "value"}

# Create an instance of MyRunnable and pass the config
configurable_runnable = MyRunnable(config)

# Invoke the configurable runnable with input_data
print("Invoke the configurable runnable with input_data")
print(output)
output = configurable_runnable.invoke("input")

# Define a custom generator function
def my_generator(input):
    yield from list(input)


# Create a RunnableGenerator instance
generator = RunnableGenerator(my_generator)

# Invoke the generator with a single input
print("Invoke the generator with a single input")
inputs = [1, 2, 3, 4, 5]
output = generator.invoke(inputs)
print(output)  # Output: 2, 3, 4, 5, 6

# Batch multiple inputs and invoke the generator
output = generator.batch(inputs)
print(output)  # Output:

# Stream the output of the generator
input_stream = 6
output = generator.batch([input_stream])
output_stream = generator.stream(input_stream)

for item in output_stream:
    print(item)  # Output: 7

# RunnableLambda
# Create a runnable lambda
runnable = RunnableLambda(lambda x: x + 1)

# Invoke the lambda runnable with input
print("Invoke the lambda runnable with input")
print(output)
output = runnable.invoke(2)

# RunnableParallel
# Create runnable functions
runnable1 = RunnableLambda(lambda x: x * 2)
runnable2 = RunnableLambda(lambda x: x * 3)

# Create a parallel runnable
parallel_runnable = RunnableParallel(runnables={"multiply2": runnable1, "multiply3": runnable2})

# Invoke the parallel runnable with input
print("Invoke the parallel runnable with input")
print(output)
output = parallel_runnable.invoke(2)

# RunnablePassthrough
# Create a passthrough runnable
passthrough_runnable = RunnablePassthrough()

# Invoke the passthrough runnable with input
print("Invoke the passthrough runnable with input")
print(output)
output = passthrough_runnable.invoke("input")

# RunnableSequence
# Create runnable functions
runnable1 = RunnableLambda(lambda x: x + 1)
runnable2 = RunnableLambda(lambda x: x * 2)

# Create a sequence runnable
sequence_runnable = runnable1 | runnable2

# Configure the sequence runnable
print("Configure the sequence runnable")
print(output)
output = sequence_runnable.invoke(
    input == 2,
    RunnableConfig(
        tags            = ['tag1', 'tag2'],
        metadata        = {"key": "value"},
        run_name        = "run_name",
        max_concurrency = None,
        recursion_limit = 2
    )
)

# RunnableWithFallbacks
# Create runnable functions
primary_runnable = RunnableLambda(lambda x: x + 1)
fallback_runnable = RunnableLambda(lambda x: x * 2)

# Create a fallbacks runnable
fallbacks_runnable = RunnableWithFallbacks(
    runnable=primary_runnable,
    fallbacks=[fallback_runnable, RunnableLambda(lambda x: x - 3)]
)

# Invoke the fallbacks runnable with input
print("Invoke the fallbacks runnable with input")
print(output)
output = fallbacks_runnable.invoke(2)

# RunnableSequence
# Create runnable functions
runnable1 = RunnableLambda(lambda x: x + 1)
runnable2 = RunnableLambda(lambda x: x * 2)
runnable3 = RunnableLambda(lambda x: x - 3)

# Create a runnable sequence
runnable_sequence = RunnableSequence(
    first = runnable1,
    middle = [runnable2, runnable3],
    last = sequence_runnable
)

# Invoke the runnable sequence with input
print("Invoke the runnable sequence with input")
print(output)
output = runnable_sequence.invoke(2)
