# backend/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from Core_Agent.agent_clean import CognitiveAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
API_KEY = os.getenv("GEMINI_API_KEY")
print("DEBUG API KEY:", API_KEY)

# Initialize cognitive agent
agent = CognitiveAgent(api_key=API_KEY)

app = FastAPI()

# Allow CORS for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or use ["chrome-extension://your-extension-id"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExpressionInput(BaseModel):
    expression: str

@app.post("/solve")
async def solve_expression(data: ExpressionInput):
    result = await agent.quick_solve(data.expression)
    return {
        "result": result.result,
        "confidence": result.confidence,
        "steps": result.steps,
        "verification": result.verification,
        "notes": result.execution_notes,
    }

@app.post("/full")
async def full_analysis(data: ExpressionInput):
    """Return complete cognitive analysis for Chrome Extension"""
    memory_summary = "No previous experience. This is a fresh start."  # Optional override
    analysis = await agent.analyze(data.expression, memory_summary)
    
    return {
        "expression": analysis.expression,
        "perception": analysis.perception.model_dump(),
        "memory": analysis.memory.model_dump(),
        "decision": analysis.decision.model_dump(),
        "action": analysis.action.model_dump(),
        "success": analysis.success,
    }
