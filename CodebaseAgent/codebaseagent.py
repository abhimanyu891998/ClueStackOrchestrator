from anthropic import Anthropic
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain_core.tools import StructuredTool
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
from langchain_mcp_adapters.tools import load_mcp_tools
from langsmith.wrappers import wrap_anthropic
from pydantic import BaseModel, Field
from langsmith import traceable
from consts import CLAUDE_SONNET_4_LATEST


async def get_deepwiki_tools()->[StructuredTool]:
    client = MultiServerMCPClient({
        "deepwiki": {
            "url": "https://mcp.deepwiki.com/sse",
            "transport": "sse"
        }
    })
    tools = await client.get_tools()
    return tools

@traceable
async def codebase_agent() -> CompiledStateGraph:
    tools: [StructuredTool] = await get_deepwiki_tools()
    class Output(BaseModel):
        source_code: str = Field(description="Actual Source code extraction related to the query")
        start_line_number: int = Field(description="Start Line number of the source-code extraction")
        end_line_numebr: int = Field(description="End line number of the the source-code extraction")
        function_name: str = Field(description="Function name (if any) of the source-code extraction")

    template = '''You are an expert code base extractor. 
       You will be given a natural language codebase query and a github repo.
       You have to use the tools to ask the right questions to get the relevant codebase, the start and end line number and the function name if any. 
       We only care about the acutal source code so you will need to modify the user query if needed to focus on code extraction. 
       Ensure to only get the source-code, the start and end line number and the function name.
      
       Use the following format:

       User Query: The user's codebase query and the repo.
       Thought: you should always think about what to do
       Action: the action to take, should be one of [{tool_names}]
       Action Input: the input to the action
       Observation: the result of the action
       ... (this Thought/Action/Action Input/Observation can repeat N times)
       Thought: I now know the final logs relevant to the user's query.
       Final Answer: The source-code, the start and end line number and the function name conforming to the user's query in the desirable format.

       Begin!
       '''
    load_dotenv()
    agent = create_react_agent(
        # model="openai:gpt-4.1",
        model=init_chat_model(f"anthropic:{CLAUDE_SONNET_4_LATEST}"),
        tools=tools,
        prompt=template,
        response_format= Output,
        name="codebase_agent"
    )
    return agent

    # user_query = "What is the exact code for the function in main.py line no 180? in repo - abhimanyu891998/cluestackmvpserver"
    # input = {"messages": [HumanMessage(content=user_query)]}
    # async for chunk in agent.astream(input, stream_mode="updates"):
    #     print(chunk)
    #     print()