# 🧠 AI Math Agent: A Cognitive Problem Solver

---

## ✨ Overview

Welcome to the **AI Math Agent**, a sophisticated mathematical problem-solving system powered by Google's **Gemini 1.5 Flash** model. This project is designed with a **modular cognitive architecture**, mimicking how a mind processes information: **Perception**, **Memory**, **Decision**, and **Action**. It's accessible via both a **FastAPI backend** and a **user-friendly Chrome Extension**!

Forget rigid calculators – this agent doesn't just give answers; it thinks through problems, learns from experience, and even explains its reasoning.

---

## 🚀 Features

- 🧠 **Modular Cognitive Architecture**: Breaks down problem-solving into distinct, intelligent phases.
- ⚡ **Gemini 1.5 Flash Powered**: Leverages a powerful LLM for advanced mathematical understanding and execution.
- 🔍 **Intelligent Problem Analysis**:
  - **Perception**: Analyzes expressions for validity, complexity, and difficulty.
  - **Memory**: Consults past experiences to recommend optimal strategies and adjust confidence.
  - **Decision**: Selects the best problem-solving method and verification level based on perceived difficulty and memory insights.
  - **Action**: Executes the chosen strategy, provides step-by-step solutions, and verifies results.
- 📈 **Dynamic Graph Plotting**: Visualizes mathematical functions (e.g., `y = x^2`) directly in the Chrome Extension, with data generated securely by the backend.
- 💾 **Persistent Memory (Planned)**: Future enhancement to enable true long-term learning.
- 🌐 **User-Friendly Chrome Extension**: A simple interface to interact with the agent directly from your browser.
- ⚙️ **FastAPI Backend**: Provides a robust API for the cognitive agent, enabling easy integration.

---

## 🧠 The Cognitive Loop: How It Works

The AI Math Agent processes each mathematical expression through a series of intelligent phases:

### 📡 Perception
The agent first "sees" the problem. It analyzes the expression's syntax, identifies operands and operators, assesses complexity, and estimates difficulty.

### 🧠 Memory
Next, it "remembers." It consults its past problem-solving history (successes, failures, strategies used) to inform its approach for the current problem.

### ⚡ Decision
Based on what it perceived and remembered, the agent "decides" the best course of action. This involves choosing a solving method (e.g., direct calculation, step-by-step verification) and a verification level.

### 🚀 Action
Finally, the agent "acts." It executes the chosen strategy, performs the mathematical computation, generates step-by-step solutions, and verifies the result. For functions, it even generates plotting data!

This detailed process allows the agent to adapt its approach, learn from mistakes, and provide comprehensive insights into its problem-solving journey.

---

## 🛠️ Getting Started

Follow these steps to set up and run the AI Math Agent on your local machine.

### ✅ Prerequisites

- Python 3.9+
- pip (Python package installer)
- Google Chrome browser

---

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-Math-Agent.git
cd AI-Math-Agent
```

---

### 2. Set up Python Environment & Install Dependencies

It's highly recommended to use a virtual environment.

```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

---

### 3. Google Gemini API Key Setup

Your project uses the Google Gemini API. You need to provide your API key securely.

1. Go to [Google AI Studio](https://makersuite.google.com/app) to generate your `GEMINI_API_KEY`.
2. In the root directory of your project (`AI-Math-Agent/`), create a file named `.env`.
3. Add your API key to this file:

```
GEMINI_API_KEY=YOUR_API_KEY_HERE
```

> 🚫 Do NOT share your `.env` file or commit it to version control! It's already included in `.gitignore` for your security.

---

### 4. Run the Backend Server

```bash
cd backend
uvicorn main:app --reload
```

The server will typically run on `http://127.0.0.1:8000`. Keep this terminal window open.

---

### 5. Load the Chrome Extension

1. Open Google Chrome.
2. Navigate to `chrome://extensions`.
3. Enable **"Developer mode"** using the toggle in the top-right corner.
4. Click **"Load unpacked"**.
5. Select the `Chrome_Extension/` folder.

The **"AI Math Solver"** extension icon should now appear in your Chrome toolbar.

---

## 💡 Usage

### ✅ Using the Chrome Extension

1. Click on the "AI Math Solver" icon in your Chrome toolbar.
2. Enter a math expression (e.g., `5 + 3 * 2`, `(10 - 2) / 4`, or `y = x^2`).
3. Click **Solve**.
4. Watch the agent process the problem through all four cognitive phases.
5. For functions like `y = x^2`, a graph will be rendered.

---

### ✅ Using the Python Client (Command Line)

You can also interact with the agent directly via the CLI:

```bash
# From the project root directory
python Core_Agent/client.py
```

Follow the on-screen prompts or use test modes:

```bash
python Core_Agent/client.py test
python Core_Agent/client.py interactive
```

---

## 📂 Project Structure

```
AI-MATH-AGENT/
├── .env                       # Your secret API key (IGNORED by Git)
├── .gitignore                 # Specifies files/folders to ignore
├── backend/
│   ├── main.py                # FastAPI application entry point
│   ├── requirements.txt       # Python dependencies for the backend
│   └── .env                   # Backend-specific .env (if any, also ignored)
├── Chrome_Extension/
│   ├── icon.png               # Extension icon
│   ├── manifest.json          # Chrome Extension manifest file
│   ├── popup.css              # Styling for the extension popup
│   ├── popup.html             # HTML structure for the extension popup
│   └── popup.js               # JavaScript logic for the extension popup (frontend)
├── Core_Agent/
│   ├── __init__.py
│   ├── action.py              # Action Phase: Executes calculations
│   ├── agent_clean.py         # Main Cognitive Agent Orchestrator (clean version)
│   ├── agent.py               # Main Cognitive Agent Orchestrator (with .env dependency)
│   ├── client_clean.py        # Clean Client without .env issues
│   ├── client.py              # Modular Cognitive Client (with .env dependency)
│   ├── decision.py            # Decision Phase: Strategic choices
│   ├── mcp_server.py          # Modular Memory Store / MCP Server (for memory/tools)
│   ├── memory.py              # Memory Phase: Consults past experiences
│   ├── models.py              # Pydantic data models for inter-phase communication
│   ├── perception.py          # Perception Phase: Analyzes expressions
│   └── standalone_test.py     # Standalone test script without MCP server
└── README.md
```

---

## 💡 Future Enhancements

- 💾 **Persistent Memory**: Add database integration (e.g., SQLite, Firestore) for long-term memory.
- 🧮 **Advanced Math Libraries**: Integrate SymPy, NumPy for better symbolic/numerical math.
- 📊 **Interactive Graphing**: Add Plotly.js to allow zoom/pan on graphs.
- 👤 **User Authentication**: Add auth system for personalized memory and settings.
- 📚 **Support for Advanced Math**: Extend to calculus, linear algebra, and statistics.

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for features, improvements, or bug fixes, please:

1. Fork the repository
2. Create a new branch:

```bash
git checkout -b feature/your-feature
```

3. Make your changes
4. Commit them:

```bash
git commit -m 'Add new feature'
```

5. Push your branch:

```bash
git push origin feature/your-feature
```

6. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

