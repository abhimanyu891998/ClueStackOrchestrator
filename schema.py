from typing import Annotated

from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages

from LoggingAgent.schema import LogItem

class RootAgentState(MessagesState):
    logs: list[LogItem]
    codebase: list[str]