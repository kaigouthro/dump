
**Reference snippets for Creating Runnable Implementations Using the LangChain Library**

- How to import the necessary modules from the LangChain library:
```python
from langchain_core.runnables import ConfigurableField, ConfigurableFieldSingleOption, ConfigurableFieldMultiOption, 
RouterInput, RouterRunnable, Runnable, RunnableBinding, RunnableBranch, RunnableConfig, RunnableGenerator, 
RunnableLambda, RunnableParallel, RunnablePassthrough, RunnableSequence, RunnableWithFallbacks
```

- How to create a `ConfigurableField` object with customizable options:
```python
field = ConfigurableField(id="my_id", name="my_field", description="my_description")
```

- How to create a `ConfigurableFieldSingleOption` object with a default option:
```python
single_option_field = ConfigurableFieldSingleOption(id="my_id", options={"option1": 1, "option2": 2}, 
default="option1", name="my_field", description="my_description")
```

- How to create a `ConfigurableFieldMultiOption` object with multiple default options:
```python
multi_option_field = ConfigurableFieldMultiOption(id="my_id", options={"1": 1, "2": 2, "3": 3}, 
default=["1", "2"], name="my_field", description="my_description")
```

- How to create a `RouterInput` object that represents a router input:
```python
input_obj = RouterInput(key="add", input=10)
```

- How to create runnable functions and route inputs to them using the `RouterRunnable` class:
```python
runnable1 = RunnableLambda(lambda x: x + 1)
runnable2 = RunnableLambda(lambda x: x * 2)
router_runnable = RouterRunnable(runnables={"add": runnable1, "multiply": runnable2})
output = router_runnable.invoke(input_obj)
```

- How to create a custom subclass of the `Runnable` class:
```python
class MyRunnableClass(Runnable):
    def invoke(self, input_data):
        output_data = input_data * 2
        return output_data

my_runnable = MyRunnableClass()
output = my_runnable.invoke(input_data=10)
```

- How to bind additional parameters to a runnable using the `RunnableBinding` class:
```python
my_runnable = RunnableLambda(lambda x: x + 1)
bound_runnable = my_runnable.bind(param1=2)
```

- How to create conditions and runnables using the `RunnableBranch` class:
```python
condition1 = lambda x: x % 2 == 0
condition2 = lambda x: x % 3 == 0
runnable1 = RunnableLambda(lambda x: x * 2)
runnable2 = RunnableLambda(lambda x: x * 3)
default_runnable = RunnableLambda(lambda x: x)
branch_runnable = RunnableBranch((condition1, runnable1), (condition2, runnable2), default_runnable)
output = branch_runnable.invoke(3)
```

- How to  Create custom subclasses of the `Runnable` class that accept a config using the `RunnableConfig` class:
```python
class MyRunnable(Runnable):
    def __init__(self, config):
        super().__init__()
        self.config = config
    
    def invoke(self, input_data):
        config_value = self.config.get("key")
        output_data = input_data + config_value
        return output_data

config = {"key": "value"}
configurable_runnable = MyRunnable(config)
```

- How to  Define custom generator functions using the `RunnableGenerator` class:
```python
def my_generator(input):
    for item in input:
        yield item + 1

generator = RunnableGenerator(my_generator)
output = generator.invoke(5)
```

- How to  Create runnable lambdas using the `RunnableLambda` class:
```python
runnable = RunnableLambda(lambda x: x + 1)
output = runnable.invoke(2)
```

- How to  Execute runnables in parallel using the `RunnableParallel` class:
```python
runnable1 = RunnableLambda(lambda x: x * 2)
runnable2 = RunnableLambda(lambda x: x * 3)
parallel_runnable = RunnableParallel(runnables={"multiply2": runnable1, "multiply3": runnable2})
output = parallel_runnable.invoke(2)
```

- How to  Create passthrough runnables using the `RunnablePassthrough` class:
```python
passthrough_runnable = RunnablePassthrough()
output = passthrough_runnable.invoke("input")
```

- How to  Execute runnables in a sequence using the `RunnableSequence` class:
```python
runnable1 = RunnableLambda(lambda x: x + 1)
runnable2 = RunnableLambda(lambda x: x * 2)
sequence_runnable = RunnableSequence(first=runnable1, middle=[runnable2], last=sequence_runnable)
output = sequence_runnable.invoke(2)
```

- How to  Create runnables with fallback options using the `RunnableWithFallbacks` class:
```python
primary_runnable = RunnableLambda(lambda x: x + 1)
fallback_runnable = RunnableLambda(lambda x: x * 2)
fallbacks_runnable = RunnableWithFallbacks(runnable=primary_runnable, fallbacks=[fallback_runnable])
output = fallbacks_runnable.invoke(2)
```
