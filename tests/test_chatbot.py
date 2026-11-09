"""
Tests for BhashaVerse 2.0 Chatbot & Cultural AI Engine.
Verifies keyword extraction, language detection, corpus RAG retrieval,
and offline knowledge generation.
"""

import tempfile
from pathlib import Path
import pytest

from database import init_db, add_proverb, STATUS_APPROVED
from utils.chatbot_utils import (
    extract_keywords,
    detect_mentioned_language,
    get_relevant_proverbs_context,
    format_proverbs_context_string,
    generate_offline_response,
    generate_chat_response
)


@pytest.fixture
def temp_chat_db():
    """Create isolated test DB with sample proverbs for chatbot retrieval testing."""
    temp_dir = tempfile.mkdtemp()
    db_file = Path(temp_dir) / "test_chat.db"
    init_db(db_path=db_file, seed_if_empty=False)

    # Seed 3 distinct proverbs for retrieval testing
    add_proverb(
        proverb="దీపం ఉండగానే ఇల్లు చక్కబెట్టుకోవాలి.",
        language="Telugu",
        language_code="te",
        meaning="Set the house in order while the lamp is still burning. Seize opportunities.",
        english_translation="Make hay while the sun shines.",
        category="Wisdom",
        status=STATUS_APPROVED,
        db_path=db_file,
    )
    add_proverb(
        proverb="अधजल गगरी छलकत जाए।",
        language="Hindi",
        language_code="hi",
        meaning="A half-filled pitcher spills more. Shallow knowledge boasts.",
        english_translation="Empty vessels make the most sound.",
        category="Education",
        status=STATUS_APPROVED,
        db_path=db_file,
    )
    add_proverb(
        proverb="சிறு துளி பெரு வெள்ளம்.",
        language="Tamil",
        language_code="ta",
        meaning="Little drops of water make a mighty deluge. Small efforts compound.",
        english_translation="Little drops make a mighty ocean.",
        category="Wisdom",
        status=STATUS_APPROVED,
        db_path=db_file,
    )

    yield db_file


def test_extract_keywords():
    """Verify keyword extraction filters out stopwords and single letters."""
    query = "What is the proverb about water and rain in Telugu?"
    keywords = extract_keywords(query)
    assert "water" in keywords
    assert "rain" in keywords
    assert "telugu" in keywords
    assert "what" not in keywords
    assert "the" not in keywords
    assert "is" not in keywords


def test_detect_mentioned_language():
    """Verify detection of Indian languages from user prompts."""
    assert detect_mentioned_language("Give me some Telugu proverbs") == "Telugu"
    assert detect_mentioned_language("What is the meaning in Hindi?") == "Hindi"
    assert detect_mentioned_language("Show me தமிழ் sayings") == "Tamil"
    assert detect_mentioned_language("Tell me an Urdu idiom") == "Urdu"
    assert detect_mentioned_language("General proverb about life") is None


def test_get_relevant_proverbs_context(temp_chat_db):
    """Verify RAG retrieval returns grounded proverbs matching search terms."""
    # Search for Telugu / lamp
    results = get_relevant_proverbs_context("lamp opportunities in Telugu", db_path=temp_chat_db)
    assert len(results) > 0
    assert any("దీపం" in r["proverb"] for r in results)

    # Search for Hindi / pitcher
    results_hi = get_relevant_proverbs_context("pitcher vessel in Hindi", db_path=temp_chat_db)
    assert len(results_hi) > 0
    assert any("गगरी" in r["proverb"] for r in results_hi)


def test_format_proverbs_context_string(temp_chat_db):
    """Verify structured context string formatting for LLM injection."""
    results = get_relevant_proverbs_context("Telugu", db_path=temp_chat_db)
    context_str = format_proverbs_context_string(results)
    assert "Telugu" in context_str
    assert "Meaning:" in context_str


def test_generate_offline_response(temp_chat_db):
    """Verify offline response generator constructs informative answers without any API keys."""
    results = get_relevant_proverbs_context("Telugu advice", db_path=temp_chat_db)
    response = generate_offline_response("Give me Telugu advice", results, language_filter="Telugu")
    assert "Telugu" in response
    assert "Meaning" in response
    assert len(response) > 20


def test_generate_chat_response_offline_mode(temp_chat_db):
    """Test full chat entry point in Offline Engine mode."""
    response = generate_chat_response(
        query="Tell me about water and oceans in Tamil",
        engine_choice="Offline Corpus Engine",
        db_path=temp_chat_db
    )
    assert isinstance(response, str)
    assert len(response) > 30
    assert "Tamil" in response or "சிறு துளி" in response or "Meaning" in response

