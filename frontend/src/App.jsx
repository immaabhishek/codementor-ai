import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const sampleCode = `int maxProfit(vector<int>& prices) {
    int profit = 0;

    for(int i = 0; i < prices.size(); i++) {
        for(int j = i + 1; j < prices.size(); j++) {
            if(prices[j] > prices[i]) {
                profit = max(profit, prices[j] - prices[i]);
            }
        }
    }

    return profit;
}`;

  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("cpp");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const savedHistory = localStorage.getItem("codementor-history");

    if (savedHistory) {
      setHistory(JSON.parse(savedHistory));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem("codementor-history", JSON.stringify(history));
  }, [history]);

  const getRiskClass = (risk) => {
    if (risk === "High") return "risk-high";
    if (risk === "Medium") return "risk-medium";
    return "risk-low";
  };

  const analyzeCode = async () => {
    if (code.trim() === "") {
      alert("Please paste some code first");
      return;
    }

    try {
      setLoading(true);
      setResult(null);

      const response = await axios.post("http://127.0.0.1:8000/api/analyze", {
        code,
        language,
      });

      const analysisData = response.data.analysis;
      setResult(analysisData);

      const newHistoryItem = {
        language: language,
        risk: analysisData.ml_bug_risk.risk_level,
        complexity: analysisData.time_complexity.complexity,
        lines: analysisData.features.non_empty_lines,
      };

      setHistory((prev) => [newHistoryItem, ...prev].slice(0, 5));
    } catch (error) {
      console.log(error);
      alert("Something went wrong. Make sure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const clearAll = () => {
    setCode("");
    setResult(null);
  };

  const loadSampleCode = () => {
    setCode(sampleCode);
    setResult(null);
  };

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem("codementor-history");
  };

  const downloadReport = () => {
    if (!result) {
      alert("No report available. Analyze code first.");
      return;
    }

    const report = `
CodeMentor AI - Code Review Report
==================================

Language: ${language}

Risk Level: ${result.ml_bug_risk.risk_level}
ML Confidence: ${result.ml_bug_risk.confidence}%
ML Model Prediction: ${result.ml_bug_risk.ml_model_prediction}
Rule Score: ${result.ml_bug_risk.rule_score}

Time Complexity: ${result.time_complexity.complexity}
Reason: ${result.time_complexity.reason}

Code Features:
--------------
Total Lines: ${result.features.total_lines}
Non-empty Lines: ${result.features.non_empty_lines}
Loops: ${result.features.loops}
Conditions: ${result.features.conditions}
Nested Loop: ${result.features.nested_loop ? "Yes" : "No"}
Uses Sort: ${result.features.uses_sort ? "Yes" : "No"}
Binary Search Pattern: ${
      result.features.binary_search_pattern ? "Yes" : "No"
    }

Feedback:
---------
${result.feedback.map((item, index) => `${index + 1}. ${item}`).join("\n")}

AI Code Review:
---------------
${
  result.llm_review.enabled
    ? result.llm_review.review
    : result.llm_review.message
}

Submitted Code:
---------------
${code}
`;

    const blob = new Blob([report], { type: "text/plain" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = "codementor-ai-report.txt";
    link.click();

    URL.revokeObjectURL(url);
  };

  return (
    <div className="app">
      <header className="hero">
        <div className="badge">ML + AI + LLM Project</div>
        <h1>CodeMentor AI</h1>
        <p>
          Analyze code quality, predict bug risk using ML, and generate AI code
          reviews using Gemini.
        </p>
      </header>

      <main className="container">
        <section className="left-box">
          <div className="top-row">
            <div>
              <h2>Paste Your Code</h2>
              <p className="small-text">
                Supports C++, Python, JavaScript and Java
              </p>
            </div>

            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              <option value="cpp">C++</option>
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="java">Java</option>
            </select>
          </div>

          <textarea
            placeholder="Paste your code here..."
            value={code}
            onChange={(e) => setCode(e.target.value)}
          ></textarea>

          <div className="button-row">
            <button
              className="primary-btn"
              onClick={analyzeCode}
              disabled={loading}
            >
              {loading ? "Analyzing..." : "Analyze Code"}
            </button>

            <button className="secondary-btn" onClick={loadSampleCode}>
              Sample Code
            </button>

            <button className="danger-btn" onClick={clearAll}>
              Clear
            </button>
          </div>

          {history.length > 0 && (
            <div className="history-box">
              <div className="history-header">
                <h3>Recent Analyses</h3>

                <button className="clear-history-btn" onClick={clearHistory}>
                  Clear History
                </button>
              </div>

              {history.map((item, index) => (
                <div className="history-item" key={index}>
                  <span>{item.language.toUpperCase()}</span>
                  <span>{item.risk} Risk</span>
                  <span>{item.complexity}</span>
                  <span>{item.lines} lines</span>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="right-box">
          <div className="result-header">
            <h2>Analysis Result</h2>
            {loading && <span className="loader">AI is reviewing...</span>}
          </div>

          {!result && !loading && (
            <div className="empty-box">
              <h3>No analysis yet</h3>
              <p>Paste your code and click Analyze Code to get results.</p>
            </div>
          )}

          {loading && (
            <div className="loading-box">
              <div className="spinner"></div>
              <p>Running ML risk prediction and Gemini code review...</p>
            </div>
          )}

          {result && (
            <>
              <button className="download-btn" onClick={downloadReport}>
                Download AI Review Report
              </button>

              <div className="cards">
                <div
                  className={`card ${getRiskClass(
                    result.ml_bug_risk.risk_level
                  )}`}
                >
                  <h3>Risk Level</h3>
                  <p>{result.ml_bug_risk.risk_level}</p>
                </div>

                <div className="card">
                  <h3>ML Confidence</h3>
                  <p>{result.ml_bug_risk.confidence}%</p>
                </div>

                <div className="card">
                  <h3>Time Complexity</h3>
                  <p>{result.time_complexity.complexity}</p>
                </div>

                <div className="card">
                  <h3>Rule Score</h3>
                  <p>{result.ml_bug_risk.rule_score}</p>
                </div>
              </div>

              <div className="section">
                <h3>Time Complexity Reason</h3>
                <p>{result.time_complexity.reason}</p>
              </div>

              <div className="section">
                <h3>Code Features</h3>
                <div className="feature-grid">
                  <span>Total Lines: {result.features.total_lines}</span>
                  <span>
                    Non-empty Lines: {result.features.non_empty_lines}
                  </span>
                  <span>Loops: {result.features.loops}</span>
                  <span>Conditions: {result.features.conditions}</span>
                  <span>
                    Nested Loop: {result.features.nested_loop ? "Yes" : "No"}
                  </span>
                  <span>
                    Uses Sort: {result.features.uses_sort ? "Yes" : "No"}
                  </span>
                  <span>
                    Binary Search Pattern:{" "}
                    {result.features.binary_search_pattern ? "Yes" : "No"}
                  </span>
                  <span>
                    ML Prediction: {result.ml_bug_risk.ml_model_prediction}
                  </span>
                </div>
              </div>

              <div className="section">
                <h3>Feedback</h3>
                <ul>
                  {result.feedback.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>

              <div className="section ai-review">
                <h3>AI Code Review</h3>

                {result.llm_review.enabled ? (
                  <pre>{result.llm_review.review}</pre>
                ) : (
                  <p>{result.llm_review.message}</p>
                )}
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;