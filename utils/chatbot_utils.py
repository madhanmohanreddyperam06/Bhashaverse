"""
BhashaVerse 2.0 - Chatbot & Cultural AI Engine
Provides Retrieval-Augmented Generation (RAG) over the local SQLite corpus,
supporting Gemini, Groq, OpenAI, and a built-in Offline Cultural Knowledge Engine.
"""

from __future__ import annotations
import os
import re
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

from config import SUPPORTED_LANGUAGES, LANGUAGE_NAMES, LANGUAGE_BY_NAME
from database import search_proverbs, get_approved_proverbs


# ==========================================
# Corpus Retrieval for Grounded RAG
# ==========================================

STOPWORDS = {
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "is", "are",
    "was", "were", "and", "or", "what", "which", "who", "whom", "this", "that",
    "these", "those", "am", "be", "been", "being", "have", "has", "had", "do",
    "does", "did", "tell", "me", "about", "give", "some", "any", "explain",
    "meaning", "proverb", "proverbs", "saying", "sayings", "idiom", "idioms"
}


def extract_keywords(query: str) -> List[str]:
    """Extract significant keywords from a user prompt."""
    tokens = re.findall(r"[\w']+", query.lower())
    return [t for t in tokens if len(t) > 2 and t not in STOPWORDS]


def detect_mentioned_language(query: str) -> Optional[str]:
    """Detect if a user prompt explicitly asks for a particular Indian language."""
    q_lower = query.lower()
    for lang in SUPPORTED_LANGUAGES:
        if lang["name"].lower() in q_lower or lang["native_name"].lower() in q_lower:
            return lang["name"]
        if lang["code"].lower() in q_lower.split():
            return lang["name"]
    return None


def get_relevant_proverbs_context(
    query: str,
    language_filter: Optional[str] = None,
    limit: int = 5,
    db_path: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """
    Search SQLite corpus for proverbs semantically or lexically matching the query.
    Used to ground both LLM prompt context and the offline engine.
    """
    detected_lang = language_filter or detect_mentioned_language(query)
    lang_param = detected_lang if detected_lang and detected_lang != "All" else None

    keywords = extract_keywords(query)
    results: List[Dict[str, Any]] = []
    seen_ids = set()

    # 1. First attempt full query search
    if keywords:
        search_term = " ".join(keywords[:3])
        matches, _ = search_proverbs(
            query=search_term,
            language=lang_param,
            limit=limit,
            db_path=db_path
        )
        for m in matches:
            if m["id"] not in seen_ids:
                results.append(m)
                seen_ids.add(m["id"])

    # 2. If fewer than limit, search individual keywords
    if len(results) < limit and keywords:
        for kw in keywords:
            matches, _ = search_proverbs(
                query=kw,
                language=lang_param,
                limit=limit - len(results),
                db_path=db_path
            )
            for m in matches:
                if m["id"] not in seen_ids:
                    results.append(m)
                    seen_ids.add(m["id"])
            if len(results) >= limit:
                break

    # 3. If still empty, fetch representative proverbs from the detected language or general corpus
    if not results:
        fallback_matches = get_approved_proverbs(limit=limit, db_path=db_path)
        if lang_param:
            fallback_matches = [m for m in fallback_matches if m.get("language") == lang_param][:limit]
        for m in fallback_matches:
            if m["id"] not in seen_ids:
                results.append(m)
                seen_ids.add(m["id"])

    return results


def format_proverbs_context_string(proverbs: List[Dict[str, Any]]) -> str:
    """Format proverb records into clean structured context for LLM grounding."""
    if not proverbs:
        return "No specific database proverbs matched the query."

    lines = []
    for idx, p in enumerate(proverbs, 1):
        trans = f' (Translation: "{p.get("english_translation")}")' if p.get("english_translation") else ""
        ctx = f' Context: {p.get("cultural_context")}' if p.get("cultural_context") else ""
        lines.append(
            f"{idx}. [{p.get('language')}] \"{p.get('proverb')}\"{trans}\n"
            f"   - Meaning: {p.get('meaning')}\n"
            f"   - Category: {p.get('category', 'Wisdom')}{ctx}"
        )
    return "\n\n".join(lines)


# ==========================================
# Engine 1: Intelligent Offline Engine
# ==========================================

def generate_offline_response(
    query: str,
    context_proverbs: List[Dict[str, Any]],
    language_filter: Optional[str] = None
) -> str:
    """
    Cultural knowledge synthesizer operating offline from the verified corpus.
    """
    q_lower = query.lower()
    detected_lang = language_filter or detect_mentioned_language(query)

    response_parts = []

    # Greeting
    if any(greet in q_lower for greet in ["hello", "hi", "namaste", "vanakkam", "namaskara", "adaab", "pranam"]):
        response_parts.append("**Namaste!** Here are proverbs and wisdom from our multilingual corpus:")

    # If proverbs were retrieved
    if context_proverbs:
        for p in context_proverbs[:4]:
            lang = p.get("language", "Indian")
            trans_line = f"\n> *Translation:* \"{p.get('english_translation')}\"" if p.get("english_translation") else ""
            ctx_line = f"\n> *Context:* {p.get('cultural_context')}" if p.get("cultural_context") else ""

            card = (
                f"### [{lang}] {p.get('proverb')}\n"
                f"{trans_line}\n"
                f"> **Meaning:** {p.get('meaning')}"
                f"{ctx_line}\n"
                f"> `{p.get('category', 'Wisdom')}`\n"
            )
            response_parts.append(card)
    else:
        response_parts.append(
            "No direct match found in the corpus. Try searching for a specific topic, keyword, or language."
        )

    return "\n\n".join(response_parts)


# ==========================================
# Engine 2: LLM API Integration (Gemini, Groq, OpenAI)
# ==========================================

SYSTEM_PROMPT_TEMPLATE = """You are BhashaAI (भाषा-AI), a warm, wise, culturally knowledgeable Indian linguistic scholar and folklore storyteller.
Your mission is to preserve, celebrate, and explain traditional Indian proverbs, folk idioms (lokoktiyan, samethalu, pazhamozhigal, dakhla), and regional wisdom across India's languages.

You have access to verified proverbs from the BhashaVerse database:
=== VERIFIED CORPUS GROUNDING ===
{corpus_context}
================================

Guidelines for your answers:
1. Always present original proverbs in their authentic native script (e.g. తెలుగు, हिन्दी, தமிழ், বাংলা, मराठी, اُردُو, ગુજરાતી, ಕನ್ನಡ, മലയാളം, ଓଡ଼ିଆ).
2. For Urdu, preserve correct Nastaliq/Perso-Arabic script.
3. Provide an accurate English translation and explain the metaphorical/philosophical meaning.
4. Share the cultural or village context (e.g., agrarian roots, folklore, festival connections) whenever possible.
5. If the user asks for equivalents across languages (e.g., Telugu vs. Hindi), draw meaningful comparisons.
6. Adopt a warm, respectful, respectful 'elder wisdom' / 'dadi-ma / nani-ma / thatha' tone combined with scholarly linguistic accuracy.
7. If the user asks general questions, connect them thoughtfully back to timeless Indian proverbs and ethical teachings.
"""


def get_configured_api_keys() -> Dict[str, Optional[str]]:
    """Check environment variables and Streamlit secrets for LLM API keys."""
    keys: Dict[str, Optional[str]] = {
        "gemini": os.getenv("GEMINI_API_KEY"),
        "groq": os.getenv("GROQ_API_KEY"),
        "openai": os.getenv("OPENAI_API_KEY"),
    }
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            for k in ["GEMINI_API_KEY", "gemini_api_key"]:
                if k in st.secrets:
                    keys["gemini"] = str(st.secrets[k]).strip()
            for k in ["GROQ_API_KEY", "groq_api_key"]:
                if k in st.secrets:
                    keys["groq"] = str(st.secrets[k]).strip()
            for k in ["OPENAI_API_KEY", "openai_api_key"]:
                if k in st.secrets:
                    keys["openai"] = str(st.secrets[k]).strip()
    except Exception:
        pass
    return keys


def call_gemini_api(api_key: str, system_prompt: str, user_prompt: str) -> str:
    """Call Google Gemini API via official google-genai SDK or REST API."""
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{system_prompt}\n\nUser Question: {user_prompt}",
        )
        if response and hasattr(response, "text") and response.text:
            return response.text
    except Exception:
        # Fallback to direct REST API if SDK throws any version/network conflict
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_prompt}\n\nUser Question: {user_prompt}"}
                    ]
                }
            ]
        }
        resp = requests.post(url, json=payload, timeout=25)
        if resp.status_code == 200:
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        raise RuntimeError(f"Gemini API returned HTTP {resp.status_code}: {resp.text}")


def call_groq_api(api_key: str, system_prompt: str, user_prompt: str) -> str:
    """Call Groq API using groq client."""
    from groq import Groq
    client = Groq(api_key=api_key)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.7,
    )
    return chat_completion.choices[0].message.content


def call_openai_api(api_key: str, system_prompt: str, user_prompt: str) -> str:
    """Call OpenAI API using openai client."""
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content


def generate_chat_response(
    query: str,
    language_filter: Optional[str] = None,
    engine_choice: str = "Auto-Detect",
    custom_api_key: Optional[str] = None,
    db_path: Optional[Any] = None,
) -> str:
    """
    Main entry point for generating chat responses.
    RAG over SQLite corpus -> LLM or Offline Cultural Knowledge Engine.
    """
    # 1. Retrieve grounded proverbs from the SQLite corpus
    context_proverbs = get_relevant_proverbs_context(
        query=query,
        language_filter=language_filter,
        limit=5,
        db_path=db_path
    )
    corpus_context_str = format_proverbs_context_string(context_proverbs)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(corpus_context=corpus_context_str)

    # 2. Check for API keys
    api_keys = get_configured_api_keys()
    if custom_api_key:
        # Determine which key was passed
        if custom_api_key.startswith("AIza"):
            api_keys["gemini"] = custom_api_key
        elif custom_api_key.startswith("gsk_"):
            api_keys["groq"] = custom_api_key
        elif custom_api_key.startswith("sk-"):
            api_keys["openai"] = custom_api_key
        else:
            api_keys["gemini"] = custom_api_key

    # 3. Route to selected or best available engine
    if engine_choice == "Offline Corpus Engine":
        return generate_offline_response(query, context_proverbs, language_filter)

    try:
        if (engine_choice in ["Auto-Detect", "Gemini"]) and api_keys.get("gemini"):
            return call_gemini_api(api_keys["gemini"], system_prompt, query)
        elif (engine_choice in ["Auto-Detect", "Groq"]) and api_keys.get("groq"):
            return call_groq_api(api_keys["groq"], system_prompt, query)
        elif (engine_choice in ["Auto-Detect", "OpenAI"]) and api_keys.get("openai"):
            return call_openai_api(api_keys["openai"], system_prompt, query)
    except Exception as e:
        # Graceful fallback to offline engine if external LLM call encounters network/quota limits
        offline_res = generate_offline_response(query, context_proverbs, language_filter)
        return (
            f"*(Note: External LLM request encountered an issue [{e}]. "
            f"Switched to BhashaVerse Native Corpus Engine)*\n\n" + offline_res
        )

    # If no API key is available, use the high-quality Offline Engine
    return generate_offline_response(query, context_proverbs, language_filter)

