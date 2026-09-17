from fastapi import FastAPI
from pydantic import BaseModel, field_validator
from sklearn.ensemble import RandomForestClassifier
from dotenv import load_dotenv
from google import genai
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeRequest(BaseModel):
    code: str
    language: str

    @field_validator("code")
    @classmethod
    def validate_code(cls, value):
        if not value.strip():
            raise ValueError("Code cannot be empty")

        if len(value) > 50000:
            raise ValueError("Code is too large")

        return value.strip()

    @field_validator("language")
    @classmethod
    def validate_language(cls, value):
        if not value.strip():
            raise ValueError("Language cannot be empty")

        return value.strip().lower()


X_train = np.array([
    [5, 0, 1, 0, 0, 0],
    [10, 1, 1, 0, 0, 0],
    [15, 1, 3, 0, 0, 0],
    [20, 2, 3, 0, 1, 0],
    [25, 2, 5, 0, 0, 0],
    [30, 2, 5, 1, 0, 0],
    [40, 3, 6, 1, 0, 0],
    [60, 4, 8, 1, 1, 0],
    [12, 1, 2, 0, 0, 1],
    [18, 1, 4, 0, 0, 1],
    [8, 0, 0, 0, 0, 0],
    [35, 3, 4, 1, 0, 0],
    [45, 4, 6, 1, 1, 0],
    [22, 2, 2, 1, 0, 0],
    [70, 5, 8, 1, 1, 0],
])

y_train = np.array([
    0, 0, 1, 1, 1,
    2, 2, 2, 0, 1,
    0, 2, 2, 1, 2
])

risk_model = RandomForestClassifier(n_estimators=80, random_state=42)
risk_model.fit(X_train, y_train)


def label_to_risk(label):
    if label == 0:
        return "Low"
    elif label == 1:
        return "Medium"
    return "High"


@app.get("/")
def home():
    return {
        "success": True,
        "message": "CodeMentor AI backend is running"
    }


@app.get("/api/health")
def health():
    return {
        "success": True,
        "status": "UP",
        "service": "CodeMentor AI"
    }


def extract_code_features(code: str):
    lines = code.split("\n")

    total_lines = len(lines)
    non_empty_lines = 0
    loops = 0
    conditions = 0
    max_nested_loop = 0
    current_nested_loop = 0
    uses_sort = 0
    binary_search_pattern = 0

    for line in lines:
        clean_line = line.strip().lower()

        if clean_line != "":
            non_empty_lines += 1

        if "sort(" in clean_line or ".sort(" in clean_line:
            uses_sort = 1

        if "mid" in clean_line and ("low" in clean_line or "high" in clean_line):
            binary_search_pattern = 1

        if "while" in clean_line and ("/= 2" in clean_line or "= mid" in clean_line):
            binary_search_pattern = 1

        if clean_line.startswith("for") or clean_line.startswith("while"):
            loops += 1
            current_nested_loop += 1
            max_nested_loop = max(max_nested_loop, current_nested_loop)

        if clean_line.startswith("if") or " if " in clean_line or clean_line.startswith("else"):
            conditions += 1

        if "}" in clean_line and current_nested_loop > 0:
            current_nested_loop -= 1

    nested_loop = 1 if max_nested_loop >= 2 else 0

    return {
        "total_lines": total_lines,
        "non_empty_lines": non_empty_lines,
        "loops": loops,
        "conditions": conditions,
        "nested_loop": nested_loop,
        "uses_sort": uses_sort,
        "binary_search_pattern": binary_search_pattern
    }



def detect_time_complexity(features):
    loops = features["loops"]
    nested_loop = features["nested_loop"]
    uses_sort = features["uses_sort"]
    binary_search_pattern = features["binary_search_pattern"]

    if uses_sort:
        return {
            "complexity": "O(n log n)",
            "reason": "Sorting function found in the code."
        }

    if binary_search_pattern:
        return {
            "complexity": "O(log n)",
            "reason": "Binary search style pattern found."
        }

    if nested_loop:
        return {
            "complexity": "O(n²)",
            "reason": "Nested loops found in the code."
        }

    if loops == 1:
        return {
            "complexity": "O(n)",
            "reason": "Single loop found in the code."
        }

    if loops > 1:
        return {
            "complexity": "O(n)",
            "reason": "Multiple separate loops found. Usually this is still linear if loops are not nested."
        }

    return {
        "complexity": "O(1)",
        "reason": "No loop or sorting pattern found."
    }


def predict_ml_risk(features):
    input_data = np.array([[
        features["non_empty_lines"],
        features["loops"],
        features["conditions"],
        features["nested_loop"],
        features["uses_sort"],
        features["binary_search_pattern"]
    ]])

    prediction = risk_model.predict(input_data)[0]
    probabilities = risk_model.predict_proba(input_data)[0]

    ml_prediction = label_to_risk(prediction)
    ml_confidence = round(float(max(probabilities)) * 100, 2)

    # Rule-based safety score
    rule_score = 0

    if features["non_empty_lines"] > 50:
        rule_score += 2
    elif features["non_empty_lines"] > 25:
        rule_score += 1

    if features["loops"] >= 3:
        rule_score += 2
    elif features["loops"] >= 1:
        rule_score += 1

    if features["nested_loop"] == 1:
        rule_score += 3

    if features["conditions"] >= 5:
        rule_score += 2
    elif features["conditions"] >= 2:
        rule_score += 1

    if features["uses_sort"] == 1:
        rule_score += 1

    if features["binary_search_pattern"] == 1:
        rule_score += 1

    if rule_score <= 2:
        final_risk = "Low"
    elif rule_score <= 5:
        final_risk = "Medium"
    else:
        final_risk = "High"

    # Safety rule
    if features["nested_loop"] == 1 and final_risk == "Low":
        final_risk = "Medium"

    return {
        "risk_level": final_risk,
        "confidence": ml_confidence,
        "ml_model_prediction": ml_prediction,
        "rule_score": rule_score
    }


def generate_feedback(features, ml_risk):
    feedback = []

    if features["non_empty_lines"] > 50:
        feedback.append("Code is lengthy. Try breaking it into smaller functions.")

    if features["nested_loop"] == 1:
        feedback.append("Nested loops found. Check if the solution can be optimized.")

    if features["loops"] >= 3:
        feedback.append("Multiple loops found. Review time complexity carefully.")

    if features["conditions"] >= 5:
        feedback.append("Many conditions found. Code may become harder to debug.")

    if features["uses_sort"] == 1:
        feedback.append("Sorting is used. Make sure O(n log n) complexity is acceptable.")

    if features["binary_search_pattern"] == 1:
        feedback.append("Binary search pattern detected. Check boundary conditions carefully.")

    if ml_risk["risk_level"] == "High":
        feedback.append("ML + rule system predicts high bug risk. Add more edge test cases.")

    if len(feedback) == 0:
        feedback.append("Code looks simple and clean at basic level.")

    return feedback


def generate_llm_review(code, language, features, time_complexity, ml_risk):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "enabled": False,
            "message": "Gemini API key not found. Add GEMINI_API_KEY in .env file."
        }

    prompt = f"""
You are CodeMentor AI, an expert software engineering code reviewer.

Analyze this {language} code.

Code:
{code}

Basic extracted features:
{features}

Detected time complexity:
{time_complexity}

ML bug risk:
{ml_risk}

Give response in this exact format:

1. What this code does:
2. Possible bugs:
3. Edge cases to test:
4. Optimization suggestion:
5. Cleaner code suggestion:
6. Interview explanation:
"""

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return {
            "enabled": True,
            "review": response.text
        }

    except Exception as e:
        return {
            "enabled": False,
            "message": "LLM review failed.",
            "error": str(e)
        }

@app.post("/api/analyze")
def analyze_code(request: CodeRequest):
    features = extract_code_features(request.code)
    time_complexity = detect_time_complexity(features)
    ml_risk = predict_ml_risk(features)
    feedback = generate_feedback(features, ml_risk)

    llm_review = generate_llm_review(
        request.code,
        request.language,
        features,
        time_complexity,
        ml_risk
    )

    return {
        "success": True,
        "language": request.language,
        "analysis": {
            "features": features,
            "time_complexity": time_complexity,
            "ml_bug_risk": ml_risk,
            "feedback": feedback,
            "llm_review": llm_review
        }
    }