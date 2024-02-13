from queue import SimpleQueue
from typing import Callable, Dict, Optional
from metaloom.core.runners import Runner
from metaloom.core.messages import MessageManager, Message
from metaloom.core.states import StatusItem, StatusList
from metaloom.core.space import Space as _space

class Agent:
    def __init__(self, agent_id: str, space: Optional[_space] = None):
        self.agent_id   = agent_id
        self.space      = space or _space()
        self.state      = StatusList()
        self.state.add(agent_id, "idle")
        self.inbox      = SimpleQueue()
        self.outbox     = SimpleQueue()
        self.messaging  = MessageManager(self,inbox=self.inbox,outbox=self.outbox)
        self.multirunner= Runner(agent_id, "Agent Runnable")
        self.runtypes   = self.multirunner.runtypes
        self.runners    = {}

    def add_runner(self, type : str, *args, **kwargs):
        assert isinstance(type, str), "Invalid runner type."
        assert type in self.runtypes, "Invalid runner type."
        assert 'name' in kwargs, "Missing runner name."
        self.runners[kwargs['name']] = self.stage(type, *args, **kwargs)

    def remove_runner(self, runner_name):
        assert isinstance(runner_name, str), "Invalid runner name type."
        del self.runners[runner_name]

    def stage(self, runner_type, *args, **kwargs):
        assert isinstance(runner_type, str), "Invalid runner name type."
        runner = self.runners[runner_type]
        return runner(*args, **kwargs)

    def cue(self, runner_name, input_data):
        runner = self.runners[runner_name]
        return runner(input_data)

    def report(self, message):
        self.messaging.send_message(message)

    def get_messages(self):
        return self.messaging.inbound_queue

    def execute_messages(self):
        while not self.messaging.inbound_queue.empty():
            if message := self.messaging.inbound_queue.get():
                assert isinstance(message, Message), "Invalid message type."
                self.process_message(message)

    def process_message(self, message: Message):
        """
        Process a message's action and input data.
        use it to invoke the runner with the input data.
        """
        assert isinstance(message, Message), "Invalid message type."
        self.state.set_status(self.agent_id, 'processing', message.action)
        try:
            output = self.cue(message.action, message.data)
            self.state.set_success(self.agent_id)
            return output
        except Exception as e:
            self.state.set_error(self.agent_id, str(e))
