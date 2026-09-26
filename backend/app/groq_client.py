"""
Thin wrapper around the Groq API.

NOTE: The assignment brief specifies gemma2-9b-it and llama-3.3-70b-versatile,
but Groq has since deprecated both. This project uses qwen/qwen3.6-27b,
Groq's current non-OpenAI-branded chat model, for both roles — still 100%
Groq's API, same GROQ_API_KEY, same groq SDK.

IMPORTANT - qwen/qwen3.6-27b is a *reasoning* model with "thinking mode".
Left at its defaults it will:
  1. Spend several seconds generating an internal <think>...</think> block
     before the real answer (this is what was making PDF/text extraction
     feel slow -- every complaint runs 5 sequential calls through the
     LangGraph pipeline, each paying that thinking-time cost).
  2. Return that <think> block as part of message.content, which is why
     the "Ask me anything" chat looked broken -- the reasoning trace was
     being shown to the user instead of a clean answer.

Fix: explicitly set reasoning_format="hidden" (Groq strips the <think>
block server-side, content is just the final answer) and
reasoning_effort="none" for the fast/structured steps so the model skips
thinking mode entirely. The CAPA/root-cause step keeps light reasoning
since it benefits from it, but still hides the trace.
Docs: https://console.groq.com/docs/reasoning

Created by Tanvi Sakhale
"""
import os
import re
import json
import warnings
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

FAST_MODEL = "qwen/qwen3.8-27b"
REASONING_MODEL = "qwen/qwen3.8-27b"

_THINK_TAG_RE = re.compile(r"<think>.*?</think>", re.DOTALL)
_reasoning_kwargs_supported = True  # flips to False the first time the SDK rejects them


def _strip_think_tags(text: str) -> str:
    """Backup cleanup: removes any <think>...</think> block regardless of
    whether reasoning_format="hidden" was honored (older SDKs ignore it)."""
    return _THINK_TAG_RE.sub("", text or "").strip()


def call_groq(system_prompt: str, user_prompt: str, model: str = FAST_MODEL,
               json_mode: bool = True, temperature: float = 0.2,
               max_tokens: int = 4096, reasoning_effort: str = "none") -> str:
    """Call Groq chat completions and return the raw text content.

    reasoning_effort="none" puts qwen/qwen3.6-27b in non-thinking mode,
    which is both faster and gives a plain final answer with nothing to
    strip. Pass reasoning_effort="default" only for steps that genuinely
    need deeper multi-step reasoning (e.g. CAPA recommendations).

    Older versions of the `groq` package don't know about the
    reasoning_effort / reasoning_format parameters yet and raise
    TypeError if you pass them. If that happens once, we remember it for
    the rest of the process and skip sending those params again -- the
    <think> tag is then just stripped client-side instead in
    _strip_think_tags(). Run `pip install --upgrade groq` to get native
    support (faster, since Groq skips thinking mode server-side).
    """
    global _reasoning_kwargs_supported

    base_kwargs = dict(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    if json_mode:
        base_kwargs["response_format"] = {"type": "json_object"}

    if _reasoning_kwargs_supported:
        try:
            response = _client.chat.completions.create(
                reasoning_effort=reasoning_effort,
                reasoning_format="hidden",
                **base_kwargs,
            )
            return _strip_think_tags(response.choices[0].message.content)
        except TypeError:
            _reasoning_kwargs_supported = False
            warnings.warn(
                "Installed `groq` package doesn't support reasoning_effort/"
                "reasoning_format -- run `pip install --upgrade groq` for "
                "faster responses. Falling back to client-side <think> "
                "stripping for now.",
                stacklevel=2,
            )

    response = _client.chat.completions.create(**base_kwargs)
    return _strip_think_tags(response.choices[0].message.content)


def call_groq_json(system_prompt: str, user_prompt: str, model: str = FAST_MODEL,
                    temperature: float = 0.2, max_tokens: int = 4096,
                    reasoning_effort: str = "none") -> dict:
    """Call Groq and parse the response as JSON, with a safe fallback."""
    raw = call_groq(system_prompt, user_prompt, model=model,
                     json_mode=True, temperature=temperature, max_tokens=max_tokens,
                     reasoning_effort=reasoning_effort)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        cleaned = raw.strip().strip("`")
        cleaned = cleaned.replace("json\n", "", 1) if cleaned.startswith("json\n") else cleaned
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {}


def classify_chat_intent(message: str) -> bool:
    """
    Bonus feature: auto-fill-from-chat.

    Combines two signals, OR'd together, so a single LLM miss doesn't
    silently block the feature:

    1. A cheap, fast (reasoning_effort='none') LLM classification call.
    2. A keyword heuristic: pharma-complaint field labels (product, batch,
       customer, etc.) appearing together strongly imply this is complaint
       data being submitted, regardless of how the LLM classified it.

    If EITHER signal says "this is complaint data," the extraction pipeline
    runs. This trades a few false positives (an unusual question that happens
    to mention "batch" gets extracted) for much better recall on real
    complaint submissions -- the more important failure mode to avoid here.
    """
    system = (
        "Classify a message sent to a pharmaceutical QMS complaint-intake chat "
        "assistant. Respond ONLY with JSON: "
        '{"is_complaint_data": true|false}. '
        "true = the message describes a NEW customer complaint with concrete "
        "details -- e.g. it names a product, a batch/lot number, a customer, "
        "manufacturing/expiry dates, quantities, or describes a quality issue "
        "(damage, contamination, odor, discoloration, packaging defect, etc). "
        "This is true even if the message is formatted as a list of labeled "
        "fields (like 'Product: X, Batch: Y') rather than a sentence. "
        "false = the message is a plain question, greeting, or general chat "
        "that does not itself contain new complaint data to log.\n\n"
        "Examples:\n"
        '"Product: Amoxicillin 250mg, Batch: AX123, customer found broken capsules" -> true\n'
        '"What is the risk classification for this complaint?" -> false\n'
        '"Customer XYZ Pharmacy reported discoloration in batch B4521" -> true\n'
        '"Can you summarize this complaint for me?" -> false'
    )
    llm_says_yes = bool(call_groq_json(system, message, model=FAST_MODEL).get("is_complaint_data", False))

    heuristic_keywords = (
        "product", "batch", "lot no", "lot #", "lot number", "customer",
        "manufactur", "expiry", "expiration", "quantity", "complaint",
        "contamina", "discolor", "defect", "damage", "odor", "odour",
        "leak", "crack", "broken", "particle", "specks", "mislabel",
    )
    lowered = message.lower()
    keyword_hits = sum(1 for kw in heuristic_keywords if kw in lowered)
    heuristic_says_yes = keyword_hits >= 2 and len(message.strip()) >= 30

    return llm_says_yes or heuristic_says_yes
