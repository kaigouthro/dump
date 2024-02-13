import time
from queue import SimpleQueue
from typing import Dict

from metaloom.core.runners import Runner


class Message:
    """
    Represents a message object with various attributes and methods.

    Attributes:
        action (str)     : The action associated with the message.
        target (str)     : The target of the message.
        sender (str)     : The sender of the message.
        title (str)      : The title of the message.
        text (str)       : The text content of the message.
        data (Dict)      : Additional data associated with the message.
        update (bool)    : Indicates whether the message has been updated.
        preempt (bool)   : Indicates whether the message is preemptive.
        read (bool)      : Indicates whether the message has been read.
        timestamp (float): The timestamp of the message.

    Methods:
        mark_read(): Marks the message as read.
        mark_unread(): Marks the message as unread.
        mark_preempt(): Marks the message as preemptive.
        create_new(target: str, title: str, text: str): Creates a new message with the specified parameters.
        update_text(text: str): Updates the text content of the message.
        __str__(): Returns a formatted string representation of the message object.
    """
    action   : str
    target   : str
    sender   : str = ""
    title    : str = ""
    text     : str = ""
    data     : Dict
    read     : bool
    timestamp: float

    def __str__(self):
        return self.__dict__

    def mark_read(self):
        self.read = True

    def mark_unread(self):
        self.read = False


    def create_new(self, target: str, title: str, text: str):
        self.target = target
        self.title = title
        self.text = text
        self.timestamp = time.time()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class MessageManager(Runner):
    def __init__(self, agent, inbox: SimpleQueue|None = None, outbox: SimpleQueue|None = None, name="Messaging", description="Inbox and Outbox"):
        super().__init__(name, description)
        self.agent = agent
        self.inbound_queue  = inbox or SimpleQueue()
        self.outbound_queue = outbox or SimpleQueue()

    def send_message(self, message: Message):
        assert isinstance(message, Message), "Invalid message type."
        message.sender = self.agent.agent_id
        self.outbound_queue.put(message)
        return True

    def put_inbox(self, message: Message):
        assert isinstance(message, Message), "Invalid message type."
        self.inbound_queue.put(message)

    def get_outbox(self):
        return self.outbound_queue.get()


    def __str__(self):
        return f"MessageManager(agent_id='{self.agent.agent_id}')"


