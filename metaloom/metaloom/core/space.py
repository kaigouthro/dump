from metaloom.core.agent_advanced import Agent
from metaloom.core.messages import Message
from metaloom.core.states import StatusList
from typing import Dict

class Space:
    def __init__(self):
        self.agents        = {}
        self.working_memory= {}
        self.messages      = []

    def add_agents(self, agents: Dict[str, Agent]):
        for agent_id, agent in agents.items():
            assert isinstance(agent, Agent), "Invalid agent type."
            self.agents[agent_id] = agent

    def add_agent(self, agent: Agent):
        assert isinstance(agent, Agent), "Invalid agent type."
        print(f"Adding agent: {agent}")
        self.agents[agent.agent_id] = agent

    def route_message(self, message: Message):
        assert isinstance(message, Message), "Invalid message type."
        print(f"Routing message: {message}")
        if message.target in self.agents:
            self.agents[message.target].messaging.receive(message)

    def retrieve_all_messages(self):
        for agent_id, agent in self.agents.items():
            assert isinstance(agent, Agent), "Invalid agent type."
            while not agent.outbox.empty():
                if message := agent.outbox.get():
                    assert isinstance(message, Message), "Invalid message type."
                    self.route_message(message)
                if agent.outbox.empty():
                    break

    def run_all_agents(self):
        for agent_id, agent in self.agents.items():
            assert isinstance(agent, Agent), "Invalid agent type."
            agent.execute_messages()

    def __str__(self):
        return f"Space({len(self.agents)} agents)"


