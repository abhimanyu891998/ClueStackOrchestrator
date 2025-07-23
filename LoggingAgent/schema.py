from typing import Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

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


class LogItem(BaseModel):
    asctime: str = Field(description="Time in UTC in format: YYY-MM-DD HH:MM:SS UTC")
    name: str = Field(description="Logging file name without extension")
    levelname: Literal['INFO', 'WARNING', 'ERROR']
    filename: str = Field(description="Logging file name with extension")
    lineno: int = Field(description="Logging line number in code logging the message")
    funcName: str = Field(description="Function name of logging line")
    message: str = Field(description="Actual message of the log")

    def __str__(self):
        return f"[{self.funcName} - {self.lineno}] - [{self.levelname}] - {self.message}"


class LogAgentOutput(BaseModel):
    logs: list[LogItem] = Field(description="List of log entries")