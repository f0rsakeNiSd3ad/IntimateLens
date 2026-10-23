import re
import json
from typing import List, Dict, Any, Tuple, Optional
from models import ChatMessage, NormalizedMessage

# Regex patterns for common chat export formats
WHATSAPP_BRACKET_REGEX = re.compile(
    r"^\[([\d\/\.-]+(?:,\s*|\s+)[\d:]+(?:\s*(?:[ap]\.?m\.?|[AP]M))?)\]\s*([^:]+):\s*(.*)$",
    re.IGNORECASE
)

WHATSAPP_DASH_REGEX = re.compile(
    r"^([\d\/\.-]+(?:,\s*|\s+)[\d:]+(?:\s*(?:[ap]\.?m\.?|[AP]M))?)\s*[-–—]\s*([^:]+):\s*(.*)$",
    re.IGNORECASE
)

INSTAGRAM_REGEX = re.compile(
    r"^([A-Za-z0-9_\s\-\.]{2,30})\s*\(([^)]+)\):\s*(.*)$"
)

GENERIC_TIMESTAMP_REGEX = re.compile(
    r"^(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\s+([^:]+):\s*(.*)$",
    re.IGNORECASE
)

GENERIC_NAME_COLON_REGEX = re.compile(
    r"^([A-Za-z0-9_\s\-\.]{2,30}):\s*(.*)$"
)

SYSTEM_PATTERNS = [
    "end-to-end encrypted",
    "created group",
    "changed the subject",
    "security code changed",
    "left the group",
    "added you",
    "joined using this group's invite link",
]


def clean_line(line: str) -> str:
    """Strips invisible characters (LTR/RTL marks) and normalizes non-breaking whitespace."""
    cleaned = line.strip().strip("\u200e\u200f\ufeff")
    cleaned = cleaned.replace("\u202f", " ").replace("\xa0", " ")
    return cleaned


def is_system_message(text: str) -> bool:
    """Checks if a message is an automated chat system message."""
    lower = text.lower()
    return any(pattern in lower for pattern in SYSTEM_PATTERNS)


def parse_json_chat(content_str: str) -> List[ChatMessage]:
    """Parse JSON formatted chat exports."""
    try:
        data = json.loads(content_str)
        messages = []
        if isinstance(data, dict):
            for key in ["messages", "chats", "data", "conversation"]:
                if key in data and isinstance(data[key], list):
                    data = data[key]
                    break
        
        if isinstance(data, list):
            for idx, item in enumerate(data):
                if isinstance(item, dict):
                    sender = (
                        item.get("sender") or 
                        item.get("author") or 
                        item.get("from") or 
                        item.get("name") or 
                        "Unknown"
                    )
                    text = (
                        item.get("text") or 
                        item.get("message") or 
                        item.get("content") or 
                        ""
                    )
                    timestamp = (
                        item.get("timestamp") or 
                        item.get("date") or 
                        item.get("time") or 
                        f"Msg #{idx+1}"
                    )
                    if text.strip() and not is_system_message(text):
                        messages.append(ChatMessage(
                            timestamp=str(timestamp).strip(),
                            sender=str(sender).strip(),
                            message=str(text).strip()
                        ))
        return messages
    except Exception as e:
        return []


def parse_chat_text(raw_text: str) -> List[ChatMessage]:
    """Parse raw text chat export (WhatsApp, Instagram, SMS, plain text)."""
    trimmed = raw_text.strip()
    
    # Try JSON parsing only if it looks like a JSON object or array of objects, not bracket-date WhatsApp
    if trimmed.startswith("{") or (trimmed.startswith("[") and not re.match(r"^\[\d{1,2}[\/\.-]", trimmed)):
        parsed_json = parse_json_chat(trimmed)
        if parsed_json:
            return parsed_json

    lines = raw_text.splitlines()
    messages: List[ChatMessage] = []
    current_msg: Optional[ChatMessage] = None

    for line in lines:
        line_str = clean_line(line)
        if not line_str:
            continue

        if is_system_message(line_str):
            continue

        # Check WhatsApp bracket pattern: [12/05/2023, 14:30:15] Alice: Hello
        match_bracket = WHATSAPP_BRACKET_REGEX.match(line_str)
        if match_bracket:
            ts, sender, text = match_bracket.groups()
            if is_system_message(sender) or is_system_message(text):
                continue
            current_msg = ChatMessage(timestamp=ts.strip(), sender=sender.strip(), message=text.strip())
            messages.append(current_msg)
            continue

        # Check WhatsApp dash pattern: 12/05/2023, 14:30 - Alice: Hello
        match_dash = WHATSAPP_DASH_REGEX.match(line_str)
        if match_dash:
            ts, sender, text = match_dash.groups()
            if is_system_message(sender) or is_system_message(text):
                continue
            current_msg = ChatMessage(timestamp=ts.strip(), sender=sender.strip(), message=text.strip())
            messages.append(current_msg)
            continue

        # Check Instagram export pattern: Alice (12/05/2023, 14:30): Hello
        match_ig = INSTAGRAM_REGEX.match(line_str)
        if match_ig:
            sender, ts, text = match_ig.groups()
            if is_system_message(sender) or is_system_message(text):
                continue
            current_msg = ChatMessage(timestamp=ts.strip(), sender=sender.strip(), message=text.strip())
            messages.append(current_msg)
            continue

        # Check generic timestamp pattern: 14:30 Alice: Hello
        match_gen_ts = GENERIC_TIMESTAMP_REGEX.match(line_str)
        if match_gen_ts:
            ts, sender, text = match_gen_ts.groups()
            if is_system_message(sender) or is_system_message(text):
                continue
            current_msg = ChatMessage(timestamp=ts.strip(), sender=sender.strip(), message=text.strip())
            messages.append(current_msg)
            continue

        # Check simple "Sender: Message" pattern
        match_generic = GENERIC_NAME_COLON_REGEX.match(line_str)
        if match_generic:
            sender, text = match_generic.groups()
            if is_system_message(sender) or is_system_message(text):
                continue
            current_msg = ChatMessage(timestamp=f"Msg #{len(messages)+1}", sender=sender.strip(), message=text.strip())
            messages.append(current_msg)
            continue

        # Multiline continuation: if line doesn't match a new message header, append to last message
        if current_msg:
            current_msg.message += " " + line_str
        else:
            # Fallback for header-less first line
            current_msg = ChatMessage(timestamp="Msg #1", sender="Unknown", message=line_str)
            messages.append(current_msg)

    return messages


def format_chat_for_prompt(messages: List[ChatMessage]) -> str:
    """Formats parsed chat messages into a clean block string for LLM input."""
    formatted_lines = []
    for m in messages:
        ts_str = f"[{m.timestamp}] " if m.timestamp else ""
        formatted_lines.append(f"{ts_str}{m.sender}: {m.message}")
    return "\n".join(formatted_lines)


def parse_normalized_text(normalized_text: str, original_messages: Optional[List[ChatMessage]] = None) -> List[NormalizedMessage]:
    """
    Parses normalized text from Pass 1 back into a structured list of NormalizedMessage objects,
    matching with original messages where possible.
    """
    lines = normalized_text.splitlines()
    normalized_list: List[NormalizedMessage] = []
    orig_map = {idx: m for idx, m in enumerate(original_messages or [])}

    for idx, line in enumerate(lines):
        line_clean = clean_line(line)
        if not line_clean:
            continue
        
        # Match [timestamp] sender: text or sender: text
        bracket_match = WHATSAPP_BRACKET_REGEX.match(line_clean)
        colon_match = GENERIC_NAME_COLON_REGEX.match(line_clean)
        
        if bracket_match:
            _, sender, norm_text = bracket_match.groups()
        elif colon_match:
            sender, norm_text = colon_match.groups()
        else:
            # Fallback if no speaker prefix
            sender = orig_map.get(idx).sender if idx in orig_map else "Unknown"
            norm_text = line_clean
        
        orig_text = orig_map.get(idx).message if idx in orig_map else norm_text
        orig_sender = orig_map.get(idx).sender if idx in orig_map else sender
        
        normalized_list.append(NormalizedMessage(
            original_sender=orig_sender,
            normalized_text=norm_text.strip(),
            original_text=orig_text.strip(),
            emotion_tone=None
        ))

    return normalized_list
