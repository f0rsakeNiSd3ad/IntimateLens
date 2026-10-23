from typing import List
from models import ChatMessage
from parser import format_chat_for_prompt

# Approximate tokens per character (rough estimation: 1 token ≈ 4 characters)
CHARS_PER_TOKEN = 4.0
MAX_CHUNK_TOKENS = 3500

def estimate_tokens(text: str) -> int:
    """Rough estimation of token count from character length."""
    return int(len(text) / CHARS_PER_TOKEN)

def chunk_chat_messages(messages: List[ChatMessage], max_tokens: int = MAX_CHUNK_TOKENS) -> List[List[ChatMessage]]:
    """
    Splits a list of ChatMessage objects into chunks where each chunk does not exceed ~max_tokens.
    Ensures message boundaries are respected.
    """
    chunks: List[List[ChatMessage]] = []
    current_chunk: List[ChatMessage] = []
    current_tokens = 0

    for msg in messages:
        msg_str = f"[{msg.timestamp or ''}] {msg.sender}: {msg.message}\n"
        msg_tokens = estimate_tokens(msg_str)

        if current_chunk and (current_tokens + msg_tokens > max_tokens):
            chunks.append(current_chunk)
            current_chunk = [msg]
            current_tokens = msg_tokens
        else:
            current_chunk.append(msg)
            current_tokens += msg_tokens

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
