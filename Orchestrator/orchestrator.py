import asyncio

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph_supervisor import create_supervisor

from CodebaseAgent.codebaseagent import codebase_agent
from LoggingAgent.LogsAgent import logging_agent
from consts import CLAUDE_SONNET_4_LATEST
import os
from schema import RootAgentState
from utils import read_file


async def orchestrator():

    # Get the directory of this file to build absolute paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    system_prompt = read_file(os.path.join(current_dir, "system_prompts/sp_orchestrator.md"))
    component_interaction_diagram = read_file(os.path.join(current_dir, "system_prompts/class_diagram.mermaid"))
    data_flow_diagram = read_file(os.path.join(current_dir, "system_prompts/data_flow.mermaid"))
    system_architecture_diagram = read_file(os.path.join(current_dir, "system_prompts/system_architecture.mermaid"))
    system_overview = read_file(os.path.join(current_dir, "system_prompts/system_overview.md"))

    sp = system_prompt.format(
        system_overview=system_overview,
        system_architecture = system_architecture_diagram,
        data_flow = data_flow_diagram,
        component_interaction_diagram=component_interaction_diagram
    )
    code_agent = await codebase_agent()
    log_agent = logging_agent()
    supervisor = create_supervisor(
        model=init_chat_model(f"anthropic:{CLAUDE_SONNET_4_LATEST}"),
        agents=[log_agent, code_agent],
        prompt=SystemMessage(content=sp),
        add_handoff_messages=True
    )
    supervisor_executor = supervisor.compile()
    return supervisor_executor


async def main():
    graph = await orchestrator()
    user_query = [
        HumanMessage("Marketdata has been stale for more than 10000ms in application: marketdata-publisher for repo: abhimanyu891998/cluestackmvpserver")
    ]
    async for chunk in graph.astream({"messages": user_query}, stream_mode="updates"):
        print(chunk)
        print()

if __name__ == '__main__':
    asyncio.run(main())
