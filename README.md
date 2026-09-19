# CodeMentor AI

CodeMentor AI is a full-stack code review assistant. It analyzes C++, Python, JavaScript, and Java code to predict bug risk, detect algorithmic time complexity, retrieve reference coding rules via RAG, and generate code reviews powered by Gemini AI.

---

## Features

- **Static Metric Analysis**: Counts lines, loops, nesting levels, condition branches, sorting calls, and binary search patterns.
- **ML Bug Risk Classifier**: Uses a `RandomForestClassifier` trained on code metrics combined with a rule safety score to rate risk as Low, Medium, or High.
- **Time Complexity Detection**: Detects common time complexities (`O(1)`, `O(n)`, `O(n²)`, `O(log n)`, `O(n log n)`) based on code structures.
- **RAG Knowledge Base**: Uses Gemini embeddings (`gemini-embedding-001`) and vector similarity to fetch relevant DSA patterns, language guidelines, and anti-patterns.
- **Gemini AI Review**: Generates detailed code reviews covering logic, edge cases, optimizations, and interview tips. Includes automatic model fallback if one model is busy.
- **Report Download & History**: Download review reports as `.txt` files and store recent analysis history in local storage.

---

## Tech Stack

- **Frontend**: React, Vite, Axios, CSS
- **Backend**: FastAPI, Uvicorn, Python
- **Machine Learning & RAG**: scikit-learn, NumPy, Gemini API (`google-genai`)

---

## How It Works

```text
Code Input (React UI) ──► FastAPI Backend ──► Static Metrics Extractor
                                                 │
  ┌──────────────────────────────────────────────┴──────────────────────────────┐
  ▼                                              ▼                              ▼
ML Classifier (RandomForest)           Time Complexity Engine          RAG Vector Retrieval
  │                                              │                              │
  └──────────────────────────────┬───────────────┴──────────────────────────────┘
                                 ▼
                     Gemini LLM Code Reviewer
                                 │
                                 ▼
                 Analysis Dashboard + Export Report
```

---

## Project Structure

```text
codementor-ai/
├── backend/
│   ├── main.py              # FastAPI server, ML logic, and Gemini API integration
│   ├── rag_store.py         # RAG vector index, embeddings, and search
│   ├── requirements.txt     # Backend dependencies
│   └── knowledge_base/      # JSON files for DSA, language rules, and anti-patterns
│       ├── dsa_patterns.json
│       ├── language_guidelines.json
│       └── bug_antipatterns.json
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   └── App.css          # App styling
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## Quick Start

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file inside the `backend` folder:

```env
GEMINI_API_KEY=your_api_key_here
```

Start backend:

```bash
uvicorn main:app --reload
```

Server runs on `http://127.0.0.1:8000`.

---

### 2. Frontend Setup

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

App runs on `http://localhost:5173`.

---

## API Endpoint

### `POST /api/analyze`

**Request:**

```json
{
  "code": "int maxProfit(vector<int>& prices) { ... }",
  "language": "cpp"
}
```

**Response:**

```json
{
  "success": true,
  "language": "cpp",
  "analysis": {
    "features": { "total_lines": 15, "loops": 2, "nested_loop": 1 },
    "time_complexity": { "complexity": "O(n²)", "reason": "Nested loops found." },
    "ml_bug_risk": { "risk_level": "Medium", "confidence": 75.0 },
    "feedback": ["Nested loops found. Check if solution can be optimized."],
    "rag_context": [
      {
        "title": "Two Pointers Technique",
        "category": "dsa",
        "recommendation": "Use two pointers to reduce complexity to O(n)."
      }
    ],
    "llm_review": {
      "enabled": true,
      "review": "Detailed AI code review..."
    }
  }
}
```