# CodeMentor AI

CodeMentor AI is a full-stack ML + AI + LLM powered code review platform that analyzes code quality, predicts bug risk, detects time complexity, and generates AI-based code review reports.

## Features

- Code analysis for C++, Python, JavaScript, and Java
- ML-based bug risk prediction
- Hybrid ML + rule-based risk scoring
- Time complexity detection
- Gemini LLM-powered code review
- AI-generated optimization suggestions
- Edge case suggestions
- Downloadable AI review report
- Recent analysis history using localStorage
- Professional React dashboard

## Tech Stack

### Frontend
- React
- Vite
- Axios
- CSS

### Backend
- FastAPI
- Python
- scikit-learn
- NumPy
- Gemini API
- dotenv

## Project Structure

```text
codementor-ai
│
├── backend
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
├── frontend
│   ├── src
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md