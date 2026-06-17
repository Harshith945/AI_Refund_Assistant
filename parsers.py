"""
parsers.py
----------
PydanticOutputParser instances built from models.py schemas.
Each parser injects {format_instructions} into the prompt and
parses raw LLM output back into a typed Python object.
"""

from langchain_core.output_parsers import PydanticOutputParser
from models import AssistantResponse, ConfirmationResponse

assistant_parser    = PydanticOutputParser(pydantic_object=AssistantResponse)
confirmation_parser = PydanticOutputParser(pydantic_object=ConfirmationResponse)
