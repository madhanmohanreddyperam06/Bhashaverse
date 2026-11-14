# 🌿Bhashaverse
 Preserving Languages. Connecting Cultures. Empowering AI

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Ollama](https://img.shields.io/badge/Ollama-black?logo=ollama&logoColor=white)](https://ollama.ai/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
---

## Project Overview

**BhashaVerse** is an open-source, community-driven digital humanities platform built to collect, preserve, organize, and explore traditional Indian proverbs, folk sayings (*lokoktiyan / samethalu / pazhamozhigal / dakhla*), idioms, and generational cultural expressions.

India is home to thousands of oral traditions passed down through generations. However, in an era of rapid digital homogenization, nuanced regional expressions and rural folk idioms risk fading into obscurity. Furthermore, modern AI and Large Language Models often fail to comprehend figurative Indian speech, translating idioms literally and losing cultural essence.

BhashaVerse bridges this gap by creating a human-verified, structured, multilingual parallel corpus that safeguards India's linguistic heritage and provides researchers with open datasets for Natural Language Processing (NLP) and cultural AI alignment.

---

## Key Features

- **10 Supported Indian Languages:** Comprehensive native script support across Indo-Aryan, Dravidian, and Perso-Arabic language families.
- **Frictionless Community Contributions:** Native speakers can contribute proverbs anonymously without mandatory logins or intrusive OAuth tracking.
- **Advanced Search & Discovery:** Full-text search across original proverb text, English translations, and meanings, coupled with language and category filtering and sorting.
- **Secure Maintainer Moderation Console:** Role-restricted portal for verifying submissions, editing metadata, rejecting spam with audit logs, and maintaining corpus integrity.
- **Real-Time SQLite Analytics:** Dynamic metric cards and interactive Plotly visualizations tracking corpus growth, language distribution, and thematic trends.
- **BhashaAI Cultural Wisdom Chatbot (RAG + Dual Engine):**
  - Interactive AI assistant grounded on the BhashaVerse verified corpus.
  - Answers questions about Indian folk sayings, philosophical meanings, and village folktales.
  - Provides cross-lingual proverb matching (e.g. matching a Telugu saying with its Hindi, Tamil, or English equivalent).
  - **Dual-Engine Architecture:** Integrates Gemini, Groq, or OpenAI when an API key is available, or runs **100% offline** via the built-in Native Corpus Engine without needing any API keys.
- **High-Fidelity Dataset Exports:**
  - **CSV Export:** Encoded with **UTF-8 with BOM (`utf-8-sig`)**, ensuring native Indian scripts (Devanagari, Telugu, Tamil, Bengali, Nastaliq, etc.) open properly in Microsoft Excel and data science libraries without character corruption.
  - **JSON Export:** Structured JSON with `ensure_ascii=False` and clean indentation for machine learning ingestion.
- **Contributor Privacy Guaranteed:** Contributor emails are strictly shielded from public display and excluded from all public dataset downloads.
- **Lightweight & Resilient:** Pure Python, SQLite with Write-Ahead Logging (WAL) and foreign keys, parameter-bound SQL queries preventing injection, and responsive CSS design.

---

## Supported Languages

BhashaVerse supports 10 major Indian regional languages with complete native script typography and text direction:

| # | Language | Native Script | Code | Script Family | Text Direction | Sample Proverb |
|---|----------|---------------|------|---------------|----------------|----------------|
| 1 | **Hindi** | हिन्दी | `hi` | Devanagari | LTR | *अधजल गगरी छलकत जाए।* |
| 2 | **Telugu** | తెలుగు | `te` | Telugu | LTR | *అడుసు తొక్కనేల కాలు కడగనేల.* |
| 3 | **Tamil** | தமிழ் | `ta` | Tamil | LTR | *சிறு துளி பெரு வெள்ளம்.* |
| 4 | **Bengali** | বাংলা | `bn` | Bengali | LTR | *দশের লাঠি একের বোঝা।* |
| 5 | **Marathi** | मराठी | `mr` | Devanagari | LTR | *शितावरून भाताची परीक्षा.* |
| 6 | **Urdu** | اُردُو | `ur` | Perso-Arabic | **RTL** | *ڈوبتے کو تنکے کا سہارا۔* |
| 7 | **Gujarati** | ગુજરાતી | `gu` | Gujarati | LTR | *ઝાઝા હાથ રળિયામણા.* |
| 8 | **Kannada** | ಕನ್ನಡ | `kn` | Kannada | LTR | *ಹಾಸಿಗೆ ಇದ್ದಷ್ಟು ಕಾಲು చాచు.* |
| 9 | **Malayalam** | മലയാളം | `ml` | Malayalam | LTR | *മിന്നുന്നതെല്ലാം പൊன்னಲ್ಲ.* |
| 10 | **Odia** | ଓଡ଼ିଆ | `or` | Odia | LTR | *ବିନ୍ଦୁ ବିନ୍ଦୁ ଜଳରେ ସିନ୍ଧୁ ଗଠନ।* |

---

## Thematic Categories

Contributions can be categorized into 11 themes:
- **Wisdom**
- **Life Lessons**
- **Relationships**
- **Nature**
- **Agriculture**
- **Family**
- **Society**
- **Education**
- **Morality**
- **Tradition**
- **Other**

---

## Technology Stack

- **Python:** Core programming language (v3.10+)
- **FastAPI:** High-performance RESTful API backend (`/api`) with interactive Swagger docs (`/docs`)
- **Uvicorn:** Lightning-fast ASGI web server implementation
- **Streamlit:** Modern web application and user interface framework (v1.30+)
- **Ollama:** Local AI model orchestration and LLM inference engine
- **SQLite:** Embedded transactional database with WAL mode and foreign key enforcement
- **Styling:** Custom CSS (`Frontend/assets/styles.css`) in permanent dark theme with Times New Roman typography
- **Data Analysis & Visualization:** [Pandas](https://pandas.pydata.org/) and [Plotly Express](https://plotly.com/python/)
- **Testing:** [pytest](https://docs.pytest.org/) with FastAPI `TestClient`
- **License:** Open-source under the [MIT License](https://opensource.org/licenses/MIT)

---

## Project Architecture

```text
Bhashaverse/
│
├── run.py                      # Multi-process launcher (concurrent or independent)
├── requirements.txt            # Python dependencies (FastAPI, Uvicorn, Streamlit, etc.)
├── README.md                   # Complete documentation
│
├── Backend/                    # 🚀 All Backend-Related Code
│   ├── main.py                 # FastAPI application entrypoint with CORS & lifespan
│   ├── config.py               # Server settings, database paths & language metadata
│   ├── database.py             # SQLite database engine, WAL mode, CRUD & search
│   ├── schemas.py              # Pydantic request and response models
│   ├── routes/                 # Modular API routers
│   │   ├── proverbs.py         # Search, filter, pagination, retrieve, submit
│   │   ├── chat.py             # Multilingual cultural RAG inference
│   │   ├── analytics.py        # Corpus statistics, distributions & charts
│   │   ├── moderation.py       # Authentication, pending queue, review & audits
│   │   └── exports.py          # UTF-8 BOM CSV & JSON dataset stream downloads
│   └── utils/                  # Backend utilities
│       ├── chatbot_utils.py    # Grounded RAG search, Ollama & LLM drivers
│       ├── validation.py       # Form inputs validation & duplicate checking
│       ├── export_utils.py     # UTF-8 BOM CSV & formatted JSON serialization
│       ├── moderation_utils.py # Timing-attack resistant passkey verification
│       ├── language_utils.py   # Script Unicode block detection & text direction
│       └── windows_patch.py    # Windows asyncio socket disconnect silence handler
│
├── Frontend/                   # 🌿 All Frontend-Related Code
│   ├── app.py                  # Streamlit main entrypoint & cultural AI chat interface
│   ├── config.py               # Frontend configuration & API endpoint settings
│   ├── api_client.py           # Centralized HTTP client consuming FastAPI REST APIs
│   ├── assets/
│   │   └── styles.css          # Dark theme stylesheet & typography protections
│   ├── components/             # Reusable Streamlit components
│   │   ├── navbar.py           # Header renderer & CSS injector
│   │   ├── sidebar.py          # Brand identity, navigation, chat settings & author credit
│   │   ├── proverb_card.py     # Theme-aware proverb card with native font & RTL support
│   │   └── metric_cards.py     # KPI metric summary blocks
│   ├── pages/                  # Streamlit multi-page interface
│   │   ├── 1_Explore_Proverbs.py # Corpus search, filters & Previous/Next pagination
│   │   ├── 2_Add_Proverb.py    # Proverb submission form & receipt
│   │   ├── 3_Dashboard.py      # Real-time analytics charts & open research downloads
│   │   ├── 4_Moderation.py     # Passkey-restricted maintainer review & actions
│   │   └── 5_About.py          # Mission, architecture & supported languages
│   └── utils/                  # Frontend formatting & display utilities
│       ├── formatting.py       # Safe HTML escaping, ISO date format & text truncation
│       ├── language_utils.py   # Script display labels & RTL helpers
│       └── windows_patch.py    # Harmless disconnect suppressor
│
├── data/
│   └── bhashaverse.db          # Thread-safe SQLite database with Write-Ahead Logging
│
└── tests/                      # Automated test suite (100% passing)
    ├── test_backend_api.py     # FastAPI TestClient endpoints verification
    ├── test_chatbot.py         # Chatbot RAG retrieval & offline engine tests
    ├── test_database.py        # Database schema, Unicode & CRUD tests
    ├── test_validation.py      # Input validation & duplicate detection tests
    ├── test_moderation.py      # Timing-attack resistant auth tests
    └── test_export.py          # CSV UTF-8 BOM & JSON privacy tests
```

---

## Database Schema Overview

The SQLite database (`bhashaverse.db`) consists of two relational tables:

### Table: `proverbs`
Stores all submitted, approved, and rejected cultural proverbs.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique numeric ID |
| `submission_uuid` | TEXT | UNIQUE NOT NULL | Public tracking UUID |
| `proverb` | TEXT | NOT NULL | Proverb text in native regional script |
| `language` | TEXT | NOT NULL | Language name (e.g. "Telugu") |
| `language_code` | TEXT | NOT NULL | ISO code (e.g. "te") |
| `english_translation` | TEXT | NULL | Optional English translation |
| `meaning` | TEXT | NOT NULL | Explanation of the proverb |
| `cultural_context` | TEXT | NULL | Folkloric, agricultural, or historical context |
| `category` | TEXT | NULL | Thematic category |
| `contributor_name` | TEXT | NULL | Contributor attribution or "Anonymous" |
| `contributor_email` | TEXT | NULL | Private contact email (never exported) |
| `status` | TEXT | NOT NULL DEFAULT 'pending' | Status: `pending`, `approved`, `rejected` |
| `rejection_reason` | TEXT | NULL | Reason logged if rejected |
| `created_at` | TEXT | NOT NULL | ISO 8601 UTC submission timestamp |
| `updated_at` | TEXT | NULL | ISO 8601 UTC modification timestamp |
| `moderated_at` | TEXT | NULL | ISO 8601 UTC review timestamp |
| `moderated_by` | TEXT | NULL | Maintainer handle |

**Indexes:**
- `idx_proverbs_language` on `language`
- `idx_proverbs_status` on `status`
- `idx_proverbs_category` on `category`
- `idx_proverbs_created_at` on `created_at`
- `idx_proverbs_submission_uuid` on `submission_uuid`

### Table: `moderation_logs`
Immutable audit trail capturing all submissions, edits, approvals, and rejections.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique log ID |
| `proverb_id` | INTEGER | NOT NULL, FK → `proverbs(id)` | References parent proverb (CASCADE on delete) |
| `action` | TEXT | NOT NULL | `submitted`, `approved`, `rejected`, `edited`, `restored_to_pending` |
| `moderator` | TEXT | NULL | Identifier of the actor |
| `reason` | TEXT | NULL | Details or justification |
| `timestamp` | TEXT | NOT NULL | ISO 8601 UTC timestamp |

---

## Installation & Local Execution

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/BhashaVerse.git
cd BhashaVerse
```

### Step 2: Create and Activate a Virtual Environment
```bash
# On Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# On Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Set your preferred Maintainer Secret Key:
```ini
MODERATOR_KEY=your_secret_passkey_here
```
*(If unset, the application defaults to the secure local testing key `bhashaverse_maintainer_2026`).*

### Step 5: Run the Test Suite
Ensure that all unit tests pass:
```bash
python -m pytest -v
```

### Step 6: Launch Bhashaverse

You can run both the **FastAPI REST Backend** and **Streamlit Web Frontend** concurrently using the unified launcher:

```bash
python run.py
```

- **Interactive API Documentation (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **FastAPI REST API Base:** [http://127.0.0.1:8000/api](http://127.0.0.1:8000/api)
- **Streamlit Web Platform:** [http://127.0.0.1:8501](http://127.0.0.1:8501)

You can also run them independently if desired:
```bash
python run.py backend    # Starts only FastAPI on port 8000
python run.py frontend   # Starts only Streamlit on port 8501
```

---

## Moderation Workflow

1. **Submission:** A contributor submits a proverb via the **Contribute** form. It is assigned a tracking UUID and stored in SQLite with `status = 'pending'`.
2. **Access Control:** The **Moderation Console** (`Frontend/pages/4_Moderation.py`) requires a maintainer passkey (`MODERATOR_KEY`) verified via constant-time comparison (`hmac.compare_digest`).
3. **Review Actions:**
   - **Approve:** Moves the submission to `approved`. The proverb immediately becomes publicly visible on the Explore page and included in dataset exports.
   - **Edit & Approve:** Corrects typos in native scripts or refines translations before approving.
   - **Reject:** Marks the submission as `rejected` and logs a required justification reason.
   - **Restore:** Re-evaluates rejected submissions and returns them to the pending queue.
4. **Audit Trail:** Every action records an immutable row in `moderation_logs`.

---

## Dataset Exports for NLP & AI Research

Researchers and data scientists can download the verified corpus directly from the **Dashboard** (`Frontend/pages/3_Dashboard.py`):

- **CSV Download:** Generated using Python's `utf-8-sig` encoding (UTF-8 with Byte Order Mark). This prevents script corruption when opened in spreadsheet software like Microsoft Excel while remaining clean for Pandas `pd.read_csv()`.
- **JSON Download:** Generated with `json.dumps(data, ensure_ascii=False, indent=2)`, preserving all native characters unescaped.
- **Privacy Standard:** Contributor email addresses and internal notes are strictly omitted from public downloads.

---

## Deployment Guide

### Deploying to Streamlit Community Cloud

1. Push your repository to GitHub.
2. Visit [share.streamlit.io](https://share.streamlit.io/) and create a new app.
3. Select your repository, branch (`main`), and set the main file path to `Frontend/app.py`.
4. In the App Settings under **Secrets**, add your maintainer key:
   ```toml
   MODERATOR_KEY = "your_strong_secret_key"
   ```
5. Click **Deploy**.

> [!IMPORTANT]
> **Storage Durability Notice:**
> Streamlit Community Cloud runs in ephemeral containers. While SQLite is perfect for lightweight, zero-configuration local and edge deployments, local SQLite files may reset upon full container rebuilds. For long-term production persistence on hosted environments, BhashaVerse's database layer is modular and can be easily backed up or paired with cloud storage or PostgreSQL.

---

## Contribution Guidelines

We welcome community contributions from developers, linguists, and cultural enthusiasts!

1. **Fork the repo** and create a feature branch (`git checkout -b feature/my-feature`).
2. Follow **PEP 8** coding standards.
3. Add unit tests for new functionality in `tests/`.
4. Run `python -m pytest -v` to ensure all tests pass.
5. Submit a descriptive Pull Request.

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
You are free to use, modify, distribute, and integrate this software and its open datasets for research, education, and commercial applications.
