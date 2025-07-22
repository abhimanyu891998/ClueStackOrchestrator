
import json
import logging
import os
from typing import TypedDict, Optional, Dict, Any

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import requests
from consts import CLAUDE_SONNET_4_LATEST, LOGS_LOOKBACK_DAYS, LOGS_LIMIT_ON_EACH_FETCH, \
    LOGS_FETCH_QUERY_ENDPOINT, CLAUDE_SONNET_3_5_LATEST
from datetime import datetime, timezone

from utils import read_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs_agent.log')
    ]
)
logger = logging.getLogger(__name__)

class LogQLOutput(BaseModel):
    """Output of a natural language to LogQL query request"""
    logql_query: str = Field(description="Best-fitting LogQL query to be executed on Grafana based on user's request")
    from_time: Optional[str] = Field(
        default="",
        description="Timestamp in format YYYY-MM-DD HH:MM:SS. Optional, not needed, unless query mentions to query by timestamp."
    )
    to_time: Optional[str] = Field(
        default="",
        description="Timestamp in format YYYY-MM-DD HH:MM:SS. Optional, not needed, unless query mentions to query by timestamp."
    )

    @classmethod
    def validate_time_format(cls, v):
        if v and v.strip():
            try:
                datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValueError(f"Time must be in format YYYY-MM-DD HH:MM:SS, got: {v}")
        return v


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
        wiki = read_file("system_prompts/logql/logql_guide.md")
        system_prompt = read_file("system_prompts/logql/sp_logql_refresher.md")
        sample_logs = read_file("system_prompts/logql/sample_logs_wiki_2.md")

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


def get_logs(logql_query: str, from_time: Optional[str] = None, to_time: Optional[str] = None) -> dict:
    """
    Fetch logs from Grafana using LogQL query.

    Args:
        logql_query (str): LogQL query to execute
        from_time (Optional[str]): Start time in format YYYY-MM-DD HH:MM:SS
        to_time (Optional[str]): End time in format YYYY-MM-DD HH:MM:SS

    Returns:
        dict: Dictionary containing logs array

    Raises:
        ValueError: If time format is invalid
        Exception: If API request fails
    """
    endpoint = LOGS_FETCH_QUERY_ENDPOINT
    logger.info(f"Fetching logs with query: {logql_query}")

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
                    logs.append(json.loads(log_str))
            logger.info(f"Successfully retrieved {len(logs)} log entries")
        elif 'error' in result:
            logger.error(f"Grafana API error: {result['error']}")
            raise Exception(f"Grafana API error: {result['error']}")

        return {'logs': logs}

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



logging_applicable_tools = [
    get_logql_from_nl_query
]


class LoggingReasoningOutput(BaseModel):
    """Output model for logging reasoning analysis."""
    resolved: bool = Field(description="Whether the query is resolved or not")
    resolution_justification: str = Field(description="Justification for the resolution")


def main() -> None:
    """
    Main function to demonstrate LogsAgent functionality.
    """
    load_dotenv()

    query = "Going into burst-mode?"
    user_application = "marketdata-publisher"

    try:
        logger.info(f"Starting LogsAgent demo with query: {query}")

        data_input = {
            "query": query,
            "user_application": user_application
        }

        logql_query_result: LogQLOutput = get_logql_from_nl_query.invoke(data_input)

        results = get_logs(
            logql_query_result.logql_query,
            logql_query_result.from_time,
            logql_query_result.to_time
        )

        log_entries = results['logs']

        # Display results
        for i, log in enumerate(log_entries):
            print(f"{log.get('asctime', 'N/A')}: {log.get('levelname', 'N/A')} - {log.get('message', 'N/A')}")
        else:
            print("No logs found matching the query.")

    except Exception as e:
        logger.error(f"Demo execution failed: {e}")
        print(f"Error: {e}")


if __name__ == '__main__':
    main()

