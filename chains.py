"""
chains.py
---------
LCEL chains: prompt | llm | parser
Reads GROQ_API_KEY from environment (HuggingFace Spaces Secret).
"""

import os
from langchain_groq import ChatGroq
from prompts import main_prompt, confirmation_prompt
from parsers import assistant_parser, confirmation_parser

# Reads from HuggingFace Spaces Secret — no .env needed
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=os.environ.get("GROQ_API_KEY", ""),
)

main_chain         = main_prompt         | llm | assistant_parser
confirmation_chain = confirmation_prompt | llm | confirmation_parser
