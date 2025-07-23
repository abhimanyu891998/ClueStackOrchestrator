
import json
import logging
import os
from typing import TypedDict, Optional, Dict, Any

from anthropic import Anthropic
from langchain.chat_models import init_chat_model
from langsmith import traceable
from dotenv import load_dotenv
from langchain.agents import AgentExecutor
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent
from langsmith.wrappers import wrap_anthropic
from pydantic import BaseModel, Field
from langchain import hub, __all__
import requests

from LoggingAgent.schema import LogQLOutput, LogItem, LogAgentOutput
from consts import CLAUDE_SONNET_4_LATEST, LOGS_LOOKBACK_DAYS, LOGS_LIMIT_ON_EACH_FETCH, \
    LOGS_FETCH_QUERY_ENDPOINT, CLAUDE_SONNET_3_5_LATEST
from datetime import datetime, timezone

import os
from schema import RootAgentState
from utils import read_file, pretty_print_message, pretty_print_messages

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('../logs_agent.log')
    ]
)
logger = logging.getLogger(__name__)



def datetime_to_unix_epoch(datetime_str: str) -> int:
    """
    Convert a datetime string in format '2025-07-18 20:08:06' to UTC Unix epoch timestamp.

    Args:
        datetime_str (str): Datetime string in format 'YYYY-MM-DD HH:MM:SS'

    Returns:
        int: UTC Unix epoch timestamp

    Raises:
        ValueError: If datetime string format is invalid

    Example:
        >>> datetime_to_unix_epoch('2025-07-18 20:08:06')
        1758394086
    """
    try:
        # Parse the datetime string into a naive datetime object
        dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        # Make it timezone-aware by setting it to UTC
        dt_utc = dt.replace(tzinfo=timezone.utc)
        # Convert to UTC epoch timestamp
        epoch_time = int(dt_utc.timestamp())
        logger.debug(f"Converted {datetime_str} to UTC epoch time {epoch_time}")
        return epoch_time
    except ValueError as e:
        logger.error(f"Failed to parse datetime string '{datetime_str}': {e}")
        raise ValueError(f"Invalid datetime format '{datetime_str}'. Expected format: YYYY-MM-DD HH:MM:SS") from e

@tool
def get_logql_from_nl_query(query: str, user_application: str) -> LogQLOutput:
    """
    Convert natural language query to LogQL query for Grafana execution.

    Args:
        query (str): Natural language query describing log search requirements
        user_application (str): Target application name for log filtering

    Returns:
        LogQLOutput: Structured output containing LogQL query and optional time filters

    Examples:
        -   get_logql_from_nl_query("Show me all error logs for today","marketdata-publisher")
            returns:
            LogQLOutput(logql_query='{application="marketdata-publisher"} | json | levelname=~"(?i)error"',
                       from_time='2025-07-21 00:00:00', to_time='2025-07-21 23:59:59')

        -   get_logql_from_nl_query("Where all did the application go into burst mode?", "marketdata-publisher")
            returns:
            LogQLOutput(logql_query='{application="marketdata-publisher"} | json | message =~ "(?i).*burst.*"',
                       from_time='', to_time='')

    Raises:
        Exception: If system prompt files cannot be read or LLM invocation fails
    """
    try:
        # Load system prompts and resources
        current_dir = os.path.dirname(os.path.abspath(__file__))
        wiki = read_file(os.path.join(current_dir, "system_prompts/logql_guide.md"))
        system_prompt = read_file(os.path.join(current_dir, "system_prompts/sp_logql_refresher.md"))
        sample_logs = read_file(os.path.join(current_dir, "system_prompts/sample_logs_wiki.md"))

        # Get current UTC time for reference
        utc_date_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Processing LogQL query generation at UTC: {utc_date_time}")

    except Exception as e:
        logger.error(f"Failed to load system prompt files: {e}")
        raise Exception(f"Failed to initialize LogQL query generation: {e}") from e

    system_prompt = system_prompt.format(
        knowledge_wiki=wiki,
        utc_date_and_time=utc_date_time,
        user_application=user_application,
        sample_logs=sample_logs
    )

    try:
        llm = ChatAnthropic(
            model_name=CLAUDE_SONNET_4_LATEST,
            temperature=0.1,
            timeout=60,
            stop=None
        )

        llm_with_output = llm.with_structured_output(LogQLOutput)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]

        logger.debug(f"Sending query to LLM: {query}")
        result = llm_with_output.invoke(messages)
        logger.info(f"Generated LogQL query: {result}")
        return result

    except Exception as e:
        logger.error(f"Failed to generate LogQL query: {e}")
        raise Exception(f"LogQL query generation failed: {e}") from e

@tool
def get_logs(logql_query: str, from_time: Optional[str] = None, to_time: Optional[str] = None) -> list[LogItem]:
    """
    Fetch logs from Grafana using LogQL query.

    Args:
        logql_query (str): LogQL query to execute
        from_time (Optional[str]): Start time in format YYYY-MM-DD HH:MM:SS
        to_time (Optional[str]): End time in format YYYY-MM-DD HH:MM:SS

    Returns:
        dict: Dictionary containing logs - {"logs": [LogItem]}

    Raises:
        ValueError: If time format is invalid
        Exception: If API request fails
    """
    endpoint = LOGS_FETCH_QUERY_ENDPOINT
    logger.info(f"Fetching logs with query: {logql_query} for from time: {from_time} to time: {to_time}")

    # Validate and convert time parameters
    start_time = None
    end_time = None

    if from_time and to_time:
        try:
            # Validate time format
            datetime.strptime(from_time, '%Y-%m-%d %H:%M:%S')
            datetime.strptime(to_time, '%Y-%m-%d %H:%M:%S')
            # Convert to epoch
            start_time = datetime_to_unix_epoch(from_time)
            end_time = datetime_to_unix_epoch(to_time)
            logger.debug(f"Using time range: {from_time} to {to_time}")
        except ValueError as e:
            logger.warning(f"Invalid time format, using default lookback: {e}")

    # Build query parameters
    query_params = {
        "query": logql_query,
        "limit": LOGS_LIMIT_ON_EACH_FETCH,
    }

    if start_time and end_time:
        query_params["start"] = start_time
        query_params["end"] = end_time
    else:
        query_params["since"] = f"{LOGS_LOOKBACK_DAYS}d"
        query_params["direction"] = "backward"

    # Get credentials with validation
    username = os.getenv('GRAFANA_USERNAME')
    password = os.getenv('GRAFANA_PWD')

    logger.info(f"Quering with username - {username} and pwd - {password}")

    if not username or not password:
        logger.error("Missing Grafana credentials in environment variables")
        raise ValueError("GRAFANA_USERNAME and GRAFANA_PWD environment variables are required")

    # Execute query
    try:
        logger.debug(f"Executing query with params: {query_params}")
        response = requests.get(
            endpoint,
            params=query_params,
            auth=(username, password),
            timeout=30
        )
        response.raise_for_status()
        result = response.json()

        # Process results
        logs = []
        if result.get('data', {}).get('result'):
            result_data = result['data']['result']
            for entry in result_data:
                values = entry.get('values' ,[])
                for value in values:
                    log_str = value[-1]
                    log_item = LogItem.model_validate_json(log_str)
                    logs.append(log_item)
            logger.info(f"Successfully retrieved {len(logs)} log entries")
        elif 'error' in result:
            logger.error(f"Grafana API error: {result['error']}")
            raise Exception(f"Grafana API error: {result['error']}")

        return logs

    except requests.exceptions.Timeout:
        logger.error("Request timeout while fetching logs")
        raise Exception("Request timeout while fetching logs from Grafana")
    except requests.exceptions.ConnectionError:
        logger.error("Connection error while fetching logs")
        raise Exception("Failed to connect to Grafana API")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        raise Exception(f"Failed to fetch logs from Grafana: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error while fetching logs: {e}")
        raise Exception(f"Unexpected error occurred: {e}") from e

@traceable
def logging_agent() -> CompiledStateGraph:
    """
    Main agent to handle log extraction and parsing logic.
    """
    template = '''You are an expert log extractor. You will be given a natural language log query and an application name from the user.
    You have to extract the logs for the application given the tools you have access to. You can always assume that there are logs present, if 
    you're not getting logs then try to make the query a bit more inclusive to get more details.

    Use the following format:

    User Query: The user's log extraction query and the application name.
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final logs relevant to the user's query.
    Final Answer: the logs, logql query, from and to time in the desirable format.

    Begin!
    '''
    user_query = "Logs for issues regarding data being stale encountered by my application - marketdata-publisher?",
    agent = create_react_agent(
        model=init_chat_model(f"anthropic:{CLAUDE_SONNET_4_LATEST}"),
        # model="openai:gpt-4.1",
        tools=[get_logql_from_nl_query, get_logs],
        response_format=LogAgentOutput,
        prompt=template,
        name="logs_agent"
    )
    return agent
    # inputs = {"messages": [HumanMessage(content=user_query)]}
    # response = agent.invoke(inputs, {'recursion_limit': 10})
    # structured_response:LogAgentOutput = response['structured_response']
    # logger.info("---------AGENT EXECUTED---------")
    # logger.info("Logs retrieved: ")
    # for log in structured_response.logs:
    #     print(log)
    # logger.info(f"LogQL query: {structured_response.logql_query}")
    #
    # return RootAgentState(
    #     messages=state.messages,
    #     logs=state.logs + structured_response.logzs,
    #     codebase=state.codebase
    # )


class LoggingReasoningOutput(BaseModel):
    """Output model for logging reasoning analysis."""
    resolved: bool = Field(description="Whether the query is resolved or not")
    resolution_justification: str = Field(description="Justification for the resolution")


if __name__ == '__main__':
    """
        Main function to demonstrate LogsAgent functionality.
        """
    load_dotenv()
    logging_agent()
    # query = "Going into burst-mode?"
    # user_application = "marketdata-publisher"
    #
    # try:
    #     logger.info(f"Starting LogsAgent demo with query: {query}")
    #
    #     data_input = {
    #         "query": query,
    #         "user_application": user_application
    #     }
    #
    #     logql_query_result: LogQLOutput = get_logql_from_nl_query.invoke(data_input)
    #
    #     results = get_logs.invoke({
    #         "logql_query": logql_query_result.logql_query,
    #         "from_time": logql_query_result.from_time,
    #         "to_time": logql_query_result.to_time
    #     }
    #     )
    #
    #     log_entries = results['logs']
    #
    #     # Display results
    #     for log in log_entries:
    #         print(f"{log.asctime}: {log.levelname} - {log.message}")
    #     else:
    #         print("No logs found matching the query.")
    #
    # except Exception as e:
    #     logger.error(f"Demo execution failed: {e}")
    #     print(f"Error: {e}")

