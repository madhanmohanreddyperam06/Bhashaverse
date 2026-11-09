# BhashaVerse 2.0 📜🇮🇳
### Multilingual Indian Proverb and Cultural Knowledge Collection Platform

> *"Preserving Languages. Connecting Cultures. Empowering AI."*

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Streamlit-red.svg)](https://streamlit.io/)
[![Database](https://img.shields.io/badge/database-SQLite3%20(WAL%20mode)-lightgrey.svg)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 1. Project Overview

**BhashaVerse 2.0** is an open-source, community-driven digital humanities platform built to collect, preserve, organize, and explore traditional Indian proverbs, folk sayings (*lokoktiyan / samethalu / pazhamozhigal / dakhla*), idioms, and generational cultural expressions.

India is home to thousands of oral traditions passed down through generations. However, in an era of rapid digital homogenization, nuanced regional expressions and rural folk idioms risk fading into obscurity. Furthermore, modern AI and Large Language Models often fail to comprehend figurative Indian speech, translating idioms literally and losing cultural essence.

BhashaVerse bridges this gap by creating a human-verified, structured, multilingual parallel corpus that safeguards India's linguistic heritage and provides researchers with open datasets for Natural Language Processing (NLP) and cultural AI alignment.

---

## 2. Key Features

- **🗣️ 10 Supported Indian Languages:** Comprehensive native script support across Indo-Aryan, Dravidian, and Perso-Arabic language families.
- **📝 Frictionless Community Contributions:** Native speakers can contribute proverbs anonymously without mandatory logins or intrusive OAuth tracking.
- **🔍 Advanced Search & Discovery:** Full-text search across original proverb text, English translations, and meanings, coupled with language and category filtering and sorting.
- **🛡️ Secure Maintainer Moderation Console:** Role-restricted portal for verifying submissions, editing metadata, rejecting spam with audit logs, and maintaining corpus integrity.
- **📊 Real-Time SQLite Analytics:** Dynamic metric cards and interactive Plotly visualizations tracking corpus growth, language distribution, and thematic trends.
- **🤖 BhashaAI Cultural Wisdom Chatbot (RAG + Dual Engine):**
  - Interactive AI assistant grounded on the BhashaVerse verified corpus.
  - Answers questions about Indian folk sayings, philosophical meanings, and village folktales.
  - Provides cross-lingual proverb matching (e.g. matching a Telugu saying with its Hindi, Tamil, or English equivalent).
  - **Dual-Engine Architecture:** Integrates Gemini, Groq, or OpenAI when an API key is available, or runs **100% offline** via the built-in Native Corpus Engine without needing any API keys.
- **📥 High-Fidelity Dataset Exports:**
  - **CSV Export:** Encoded with **UTF-8 with BOM (`utf-8-sig`)**, ensuring native Indian scripts (Devanagari, Telugu, Tamil, Bengali, Nastaliq, etc.) open properly in Microsoft Excel and data science libraries without character corruption.
  - **JSON Export:** Structured JSON with `ensure_ascii=False` and clean indentation for machine learning ingestion.
- **🔒 Contributor Privacy Guaranteed:** Contributor emails are strictly shielded from public display and excluded from all public dataset downloads.
- **⚡ Lightweight & Resilient:** Pure Python, SQLite with Write-Ahead Logging (WAL) and foreign keys, parameter-bound SQL queries preventing injection, and responsive CSS design.

---

## 3. Supported Languages

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

## 4. Thematic Categories

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

## 5. Technology Stack

- **Frontend & App Framework:** [Streamlit](https://streamlit.io/) (v1.30+)
- **Styling:** Custom CSS (`assets/styles.css`) with Indian cultural color palette (Deep Indigo `#4338CA`, Saffron `#F59E0B`, Warm Off-White `#FAFAF7`)
- **Backend & Logic:** Python 3.10+ modular services
- **Database:** SQLite 3 via Python standard library `sqlite3`
  - Write-Ahead Logging (WAL) mode
  - Foreign key constraint enforcement (`PRAGMA foreign_keys = ON;`)
  - 100% Parameterized queries (`?` parameter binding)
- **Data Analysis & Visualization:** [Pandas](https://pandas.pydata.org/) and [Plotly Express](https://plotly.com/python/)
- **Testing:** [pytest](https://docs.pytest.org/) with isolated temporary test databases

---

## 6. Project Architecture

```text
BhashaVerse/
│
├── app.py                      # Home / Landing page with live metrics & language showcase
├── database.py                 # SQLite database engine, WAL mode, CRUD, search & exports
├── config.py                   # Centralized configuration, language metadata & constraints
├── requirements.txt            # Python dependencies
├── README.md                   # Complete documentation
├── .gitignore                  # Git exclusions (bytecode, SQLite databases, secrets)
├── .env.example                # Template for environment configuration
│
├── pages/
│   ├── 1_Explore_Proverbs.py   # Corpus search, language/category filters, card view & export
│   ├── 2_Add_Proverb.py        # Proverb submission form with validation & duplicate detection
│   ├── 3_Dashboard.py          # Real-time analytics charts and open research dataset downloads
│   ├── 4_Moderation.py         # Passkey-restricted maintainer review, audit logs & actions
│   ├── 5_About.py              # Mission, NLP significance, and open-source contribution guide
│   └── 6_BhashaAI_Chatbot.py   # Interactive AI Wisdom Chatbot with RAG & dual-engine inference
│
├── components/
│   ├── __init__.py
│   ├── navbar.py               # Custom header renderer and CSS injector
│   ├── sidebar.py              # Brand identity, live counts, language pills & session status
│   ├── proverb_card.py         # Cultural proverb card with native font and RTL support
│   ├── metric_cards.py         # Live metric KPI summary blocks
│   └── footer.py               # Standardized open-source footer
│
├── utils/
│   ├── __init__.py
│   ├── chatbot_utils.py        # RAG retrieval, Gemini/Groq/OpenAI drivers & offline engine
│   ├── language_utils.py       # Unicode script detection, RTL direction, and label formatting
│   ├── validation.py           # Form inputs validation, lengths, email check & duplicate check
│   ├── export_utils.py         # UTF-8 BOM CSV & indented JSON generator with privacy scrubbing
│   ├── moderation_utils.py     # Timing-attack resistant passkey verification and session management
│   └── formatting.py           # Safe HTML escaping, ISO date formatting, and text truncation
│
├── assets/
│   ├── logo.png                # Platform logo
│   └── styles.css              # Custom responsive stylesheet & typography
│
├── data/
│   └── .gitkeep                # Database directory (auto-creates bhashaverse.db)
│
└── tests/
    ├── __init__.py
    ├── test_chatbot.py         # Chatbot RAG retrieval, keyword parsing & offline engine tests
    ├── test_database.py        # Database schema, CRUD, Unicode (10 langs), search, cascade tests
    ├── test_validation.py      # Input constraint and email format tests
    ├── test_moderation.py      # Passkey timing-attack resistant auth tests
    └── test_export.py          # CSV UTF-8 BOM, JSON encoding, and privacy sanitization tests
```

---

## 7. Database Schema Overview

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

## 8. Installation & Local Execution

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

### Step 6: Launch BhashaVerse
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`. On first launch, the database automatically initializes with authentic seed proverbs across all 10 languages!

---

## 9. Moderation Workflow

1. **Submission:** A contributor submits a proverb via the **Contribute** form. It is assigned a tracking UUID and stored in SQLite with `status = 'pending'`.
2. **Access Control:** The **Moderation Console** (`pages/4_Moderation.py`) requires a maintainer passkey (`MODERATOR_KEY`) verified via constant-time comparison (`hmac.compare_digest`).
3. **Review Actions:**
   - **Approve:** Moves the submission to `approved`. The proverb immediately becomes publicly visible on the Explore page and included in dataset exports.
   - **Edit & Approve:** Corrects typos in native scripts or refines translations before approving.
   - **Reject:** Marks the submission as `rejected` and logs a required justification reason.
   - **Restore:** Re-evaluates rejected submissions and returns them to the pending queue.
4. **Audit Trail:** Every action records an immutable row in `moderation_logs`.

---

## 10. Dataset Exports for NLP & AI Research

Researchers and data scientists can download the verified corpus directly from the **Dashboard** (`pages/3_Dashboard.py`):

- **CSV Download:** Generated using Python's `utf-8-sig` encoding (UTF-8 with Byte Order Mark). This prevents script corruption when opened in spreadsheet software like Microsoft Excel while remaining clean for Pandas `pd.read_csv()`.
- **JSON Download:** Generated with `json.dumps(data, ensure_ascii=False, indent=2)`, preserving all native characters unescaped.
- **Privacy Standard:** Contributor email addresses and internal notes are strictly omitted from public downloads.

---

## 11. Deployment Guide

### Deploying to Streamlit Community Cloud

1. Push your repository to GitHub.
2. Visit [share.streamlit.io](https://share.streamlit.io/) and create a new app.
3. Select your repository, branch (`main`), and set the main file path to `app.py`.
4. In the App Settings under **Secrets**, add your maintainer key:
   ```toml
   MODERATOR_KEY = "your_strong_secret_key"
   ```
5. Click **Deploy**.

> [!IMPORTANT]
> **Storage Durability Notice:**
> Streamlit Community Cloud runs in ephemeral containers. While SQLite is perfect for lightweight, zero-configuration local and edge deployments, local SQLite files may reset upon full container rebuilds. For long-term production persistence on hosted environments, BhashaVerse's database layer is modular and can be easily backed up or paired with cloud storage or PostgreSQL.

---

## 12. Contribution Guidelines

We welcome community contributions from developers, linguists, and cultural enthusiasts!

1. **Fork the repo** and create a feature branch (`git checkout -b feature/my-feature`).
2. Follow **PEP 8** coding standards.
3. Add unit tests for new functionality in `tests/`.
4. Run `python -m pytest -v` to ensure all tests pass.
5. Submit a descriptive Pull Request.

---

## 13. License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
You are free to use, modify, distribute, and integrate this software and its open datasets for research, education, and commercial applications.
