# models.py - Pydantic Models for Cognitive Architecture
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal, Union
from datetime import datetime

# Input/Output Models for each phase

class PerceptionInput(BaseModel):
    """Input for perception phase"""
    expression: str = Field(..., description="Mathematical expression to analyze")

class PerceptionOutput(BaseModel):
    """Output from perception phase"""
    is_valid: bool = Field(..., description="Whether the expression is valid")
    operands: List[Union[float, str]] = Field(..., description="List of numbers in the expression")
    operators: List[str] = Field(..., description="List of operators in the expression")
    complexity: Literal["simple", "medium", "complex"] = Field(..., description="Complexity level")
    requires_order_ops: bool = Field(..., description="Whether order of operations is required")
    estimated_difficulty: int = Field(..., ge=1, le=10, description="Difficulty rating 1-10")
    error_message: Optional[str] = Field(None, description="Error message if invalid")
    perception_notes: str = Field(..., description="Detailed analysis notes")

class MemoryInput(BaseModel):
    """Input for memory consultation phase"""
    expression: str = Field(..., description="Current mathematical expression")
    perception_data: PerceptionOutput = Field(..., description="Perception analysis results")
    memory_summary: str = Field(..., description="Current memory state summary")

class MemoryOutput(BaseModel):
    """Output from memory consultation phase"""
    session_success_rate: str = Field(..., description="Description of current performance")
    strategy_recommendation: Literal["conservative_approach", "standard_verification", "confident_direct"] = Field(..., description="Recommended strategy")
    confidence_modifier: float = Field(..., ge=0.5, le=1.0, description="Confidence adjustment factor")
    similar_problems_found: int = Field(..., ge=0, description="Number of similar problems in memory")
    memory_insights: str = Field(..., description="Analysis of memory patterns")
    recommended_approach: str = Field(..., description="Specific strategy explanation")

class DecisionInput(BaseModel):
    """Input for decision making phase"""
    expression: str = Field(..., description="Mathematical expression to solve")
    perception_data: PerceptionOutput = Field(..., description="Perception analysis")
    memory_data: MemoryOutput = Field(..., description="Memory consultation results")

class DecisionOutput(BaseModel):
    """Output from decision making phase"""
    selected_method: Literal["direct_calculation", "standard_with_check", "step_by_step_verification", "conservative_detailed"] = Field(..., description="Chosen solving method")
    final_confidence: float = Field(..., ge=0.0, le=1.0, description="Final confidence level")
    show_working_steps: bool = Field(..., description="Whether to show detailed steps")
    verification_level: Literal["minimal", "standard", "high", "extra"] = Field(..., description="Level of verification required")
    reasoning: str = Field(..., description="Explanation of decision logic")
    execution_strategy: str = Field(..., description="Specific solving approach")
    risk_assessment: Literal["low", "medium", "high"] = Field(..., description="Risk level assessment")

class ActionInput(BaseModel):
    """Input for action execution phase"""
    expression: str = Field(..., description="Mathematical expression to solve")
    perception_data: PerceptionOutput = Field(..., description="Perception analysis")
    decision_data: DecisionOutput = Field(..., description="Decision making results")

class ActionOutput(BaseModel):
    """Output from action execution phase"""
    result: str = Field(..., description="Mathematical result or error message")
    steps: List[str] = Field(..., description="List of calculation steps")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Execution confidence")
    verification: str = Field(..., description="Verification result description")
    execution_notes: str = Field(..., description="Detailed execution process notes")

# Memory storage models

class ProblemResult(BaseModel):
    """Individual problem result for memory storage"""
    timestamp: datetime = Field(default_factory=datetime.now)
    problem: str = Field(..., description="The mathematical expression")
    result: str = Field(..., description="The result or error message")
    success: bool = Field(..., description="Whether the solution was successful")
    strategy_used: Optional[str] = Field(None, description="Strategy that was used")
    confidence: Optional[float] = Field(None, description="Confidence level")

class MemoryStatus(BaseModel):
    """Current memory status"""
    total_problems: int = Field(default=0, description="Total problems attempted")
    success_count: int = Field(default=0, description="Number of successful solutions")
    error_count: int = Field(default=0, description="Number of failed attempts")
    success_rate: str = Field(default="0%", description="Success rate percentage")
    operation_stats: Dict[str, int] = Field(default_factory=lambda: {
        "addition": 0, "subtraction": 0, "multiplication": 0, "division": 0
    }, description="Statistics for each operation type")
    recent_history: List[ProblemResult] = Field(default_factory=list, description="Recent problem history")

class MemorySummary(BaseModel):
    """Memory summary for LLM prompting"""
    summary: str = Field(..., description="Human-readable memory summary")
    raw_data: MemoryStatus = Field(..., description="Raw memory statistics")

# Complete cognitive analysis result

class CognitiveAnalysisResult(BaseModel):
    """Complete result from cognitive analysis"""
    expression: str = Field(..., description="Original mathematical expression")
    perception: PerceptionOutput = Field(..., description="Perception phase results")
    memory: MemoryOutput = Field(..., description="Memory consultation results")
    decision: DecisionOutput = Field(..., description="Decision making results")
    action: ActionOutput = Field(..., description="Action execution results")
    success: bool = Field(..., description="Overall success status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")

# Tool request/response models for MCP

class StoreResultRequest(BaseModel):
    """Request to store a problem result"""
    problem: str = Field(..., description="Mathematical expression")
    result: str = Field(..., description="Result or error message")
    success: bool = Field(..., description="Whether it was successful")
    strategy_used: Optional[str] = Field(None, description="Strategy used")
    confidence: Optional[float] = Field(None, description="Confidence level")

class StoreResultResponse(BaseModel):
    """Response from storing a result"""
    status: str = Field(..., description="Status message")
    problem: str = Field(..., description="Stored problem")
    result: str = Field(..., description="Stored result")
    success: bool = Field(..., description="Stored success status")
    total_problems: int = Field(..., description="Total problems after storing")

class ResetMemoryResponse(BaseModel):
    """Response from resetting memory"""
    status: str = Field(..., description="Reset status message")
    message: str = Field(..., description="Detailed reset message")