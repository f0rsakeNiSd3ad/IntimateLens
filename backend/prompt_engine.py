import json
import asyncio
from typing import Optional, Any, Dict, List
from models import ChatMessage, NormalizedMessage
from chunking import chunk_chat_messages, estimate_tokens, MAX_CHUNK_TOKENS
from parser import format_chat_for_prompt, parse_normalized_text
from psychological_engine import PsychologicalEngine

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    torch = None
    AutoModelForCausalLM = None
    AutoTokenizer = None
    pipeline = None
    HAS_TRANSFORMERS = False


class PromptEngine:
    """Manages the two-pass LLM prompting pipeline and integrates the PsychologicalEngine."""
    
    def __init__(self, model_name: str = "Qwen/Qwen2.5-7B-Instruct"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self._initialized = False
        self.psych_engine = PsychologicalEngine()

    async def initialize(self):
        if self._initialized:
            return
        
        if not HAS_TRANSFORMERS or torch is None:
            print("Transformers/PyTorch not installed. Operating with high-accuracy on-device PsychologicalEngine.")
            self._initialized = False
            return

        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if torch.cuda.is_available() else torch.float32

            print(f"Attempting to load model {self.model_name} on {device}...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, trust_remote_code=True
            )
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=dtype,
                device_map="auto" if device == "cuda" else None,
                trust_remote_code=True,
            )

            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                torch_dtype=dtype,
            )
            self._initialized = True
            print(f"Model {self.model_name} initialized successfully.")
        except Exception as e:
            print(f"Neural model note: {e}. Falling back to PsychologicalEngine.")
            self._initialized = False

    def _build_translator_prompt(self, chat_text: str, user_instructions: str) -> str:
        return f"""You are an expert relationship translator and phonetic transcriptionist.

Your task is to analyze the following chat conversation transcript and:
1. Identify all language dialects and phonetic patterns (e.g., Hinglish, Romanized Spanish, Hindi in English script).
2. Transcribe phonetic/hybrid text to Standard English while preserving the exact emotional tone (sarcasm, anger, love, humor, irony).
3. Fix any broken encoding/characters that appear garbled.
4. Preserve the original speaker labels exactly as they appear.
5. Do NOT summarize or shorten the conversation. Output the full transcript in clean, grammatically correct Standard English, maintaining the exact same number of messages and flow.

User context: "{user_instructions}"

Original chat text:
{chat_text}

Output ONLY the clean English normalized transcript, nothing else."""

    def _build_psychologist_prompt(self, normalized_text: str) -> str:
        return f"""You are a licensed relationship psychologist performing a structured analysis of a couple's conversation using the Gottman Method and Attachment Theory.

Analyze the normalized English conversation below and output a JSON object strictly conforming to the following schema:

{{
  "toxicity_score": 0-100,
  "affection_levels": {{
    "person_a": 0-100,
    "person_b": 0-100
  }},
  "key_red_flags": ["flag 1", "flag 2"],
  "key_green_flags": ["flag 1", "flag 2"],
  "verdict": "Repairable",
  "actionable_advice": ["advice 1", "advice 2"],
  "gottman_breakdown": {{
    "criticism_score": 0-100,
    "contempt_score": 0-100,
    "defensiveness_score": 0-100,
    "stonewalling_score": 0-100,
    "notes": "clinical observations"
  }},
  "timeline_events": [
    {{
      "timestamp": "original timestamp or N/A",
      "speaker": "speaker name",
      "message": "quote",
      "sentiment_impact": -100 to 100,
      "label": "Contempt Spike, Bids for Connection, Defensiveness, etc"
    }}
  ]
}}

Strict requirements:
- Output ONLY valid JSON. No markdown code blocks, no surrounding text.
- verdict MUST be exactly one of: "Repairable", "Critical", or "Recommend Ending".
- Map timeline_events to major emotional and SPAFF inflection points.

Normalized conversation:
{normalized_text}"""

    async def analyze_pass1_translate(self, chat_text: str, user_instructions: str) -> Optional[str]:
        """Pass 1: Translate/Normalize the chat text."""
        if not self._initialized or self.pipeline is None:
            return chat_text
        
        prompt = self._build_translator_prompt(chat_text, user_instructions)
        messages = [{"role": "user", "content": prompt}]
        
        def _generate():
            outputs = self.pipeline(
                messages,
                max_new_tokens=2048,
                do_sample=False,
                temperature=0.0,
            )
            return outputs[0]["generated_text"][-1]["content"]

        try:
            generated = await asyncio.to_thread(_generate)
            return generated.strip()
        except Exception as e:
            print(f"Pass 1 translation error: {e}")
            return chat_text

    async def analyze_pass2_psychologist(self, normalized_text: str) -> Optional[Dict]:
        """Pass 2: Psychological analysis of normalized text."""
        if not self._initialized or self.pipeline is None:
            return None
        
        prompt = self._build_psychologist_prompt(normalized_text)
        messages = [{"role": "user", "content": prompt}]
        
        def _generate():
            outputs = self.pipeline(
                messages,
                max_new_tokens=2048,
                do_sample=False,
                temperature=0.0,
            )
            return outputs[0]["generated_text"][-1]["content"]

        generated = ""
        try:
            generated = await asyncio.to_thread(_generate)
            json_start = generated.find("{")
            json_end = generated.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = generated[json_start:json_end]
                return json.loads(json_str)
            else:
                return json.loads(generated)
        except json.JSONDecodeError as e:
            print(f"Pass 2 JSON parse error: {e}")
            return None
        except Exception as e:
            print(f"Pass 2 analysis error: {e}")
            return None

    async def run_full_analysis(
        self, 
        messages: List[ChatMessage],
        user_instructions: str = ""
    ) -> Optional[Dict]:
        """Run the complete psychological analysis pipeline."""
        # Handle chunking if transcript is massive
        token_estimate = sum(estimate_tokens(f"{m.sender}: {m.message}") for m in messages)
        if token_estimate > MAX_CHUNK_TOKENS:
            chunks = chunk_chat_messages(messages, max_tokens=MAX_CHUNK_TOKENS)
            eval_messages = chunks[0] + (chunks[-1] if len(chunks) > 1 else [])
        else:
            eval_messages = messages

        chat_text = format_chat_for_prompt(eval_messages)

        # Pass 1: Translate/Normalize
        normalized_str = await self.analyze_pass1_translate(chat_text, user_instructions)
        normalized_messages = parse_normalized_text(normalized_str or chat_text, eval_messages)

        # Pass 2: Analyze via neural pipeline if available, else clinical PsychologicalEngine
        result = None
        if self._initialized and self.pipeline is not None:
            result = await self.analyze_pass2_psychologist(normalized_str)
        
        if not result:
            result = self.psych_engine.analyze_conversation(eval_messages)

        # Attach normalized conversation
        result["normalized_conversation"] = [
            m.model_dump() for m in normalized_messages
        ]
        return result