# mcpserver.py - Modular MCP Server with Pydantic Models
import asyncio
import json
from typing import List
from datetime import datetime
import mcp
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Import Pydantic models
from Core_Agent.models import (
    MemoryStatus, MemorySummary, ProblemResult,
    StoreResultRequest, StoreResultResponse, ResetMemoryResponse
)

class ModularMemoryStore:
    """
    Modular memory storage system using Pydantic models for data validation
    """
    
    def __init__(self):
        self.session_history: List[ProblemResult] = []
        self.memory_status = MemoryStatus()
        
    def store_result(self, request: StoreResultRequest) -> StoreResultResponse:
        """Store a problem result with full validation"""
        
        # Create problem result record
        problem_result = ProblemResult(
            problem=request.problem,
            result=request.result,
            success=request.success,
            strategy_used=request.strategy_used,
            confidence=request.confidence
        )
        
        # Add to history
        self.session_history.append(problem_result)
        
        # Update memory status
        self.memory_status.total_problems += 1
        
        if request.success:
            self.memory_status.success_count += 1
        else:
            self.memory_status.error_count += 1
        
        # Calculate success rate
        success_rate = (self.memory_status.success_count / self.memory_status.total_problems) * 100
        self.memory_status.success_rate = f"{success_rate:.1f}%"
        
        # Update operation statistics
        self._update_operation_stats(request.problem)
        
        # Keep recent history (last 10 items)
        self.memory_status.recent_history = self.session_history[-10:]
        
        return StoreResultResponse(
            status="Result stored successfully",
            problem=request.problem,
            result=request.result,
            success=request.success,
            total_problems=self.memory_status.total_problems
        )
    
    def get_memory_status(self) -> MemoryStatus:
        """Get current memory status"""
        return self.memory_status
    
    def get_memory_summary(self) -> MemorySummary:
        """Get memory summary suitable for LLM prompting"""
        
        if self.memory_status.total_problems == 0:
            summary_text = "No previous experience. This is a fresh start."
        else:
            success_rate = (self.memory_status.success_count / self.memory_status.total_problems) * 100
            
            summary_text = f"""AGENT MEMORY SUMMARY:
- Total Problems Solved: {self.memory_status.total_problems}
- Success Rate: {success_rate:.1f}% ({self.memory_status.success_count}/{self.memory_status.total_problems})
- Operation Experience: {self.memory_status.operation_stats}
- Recent Performance Trend: {self._analyze_recent_trend()}"""
            
            if self.memory_status.error_count > 0:
                summary_text += f"\n- Recent Errors: {self.memory_status.error_count} failures recorded"
            
            if self.session_history:
                last = self.session_history[-1]
                summary_text += f"\n- Last Problem: '{last.problem}' → {last.result} ({'SUCCESS' if last.success else 'FAILED'})"
                
                if last.strategy_used:
                    summary_text += f"\n- Last Strategy Used: {last.strategy_used}"
        
        return MemorySummary(
            summary=summary_text,
            raw_data=self.memory_status
        )
    
    def reset_memory(self) -> ResetMemoryResponse:
        """Reset all memory data"""
        self.session_history.clear()
        self.memory_status = MemoryStatus()
        
        return ResetMemoryResponse(
            status="Memory reset successfully",
            message="All learning history cleared. Agent will start fresh with conservative approach."
        )
    
    def _update_operation_stats(self, problem: str):
        """Update operation statistics based on problem content"""
        
        if "+" in problem:
            self.memory_status.operation_stats["addition"] += 1
        if "-" in problem:
            self.memory_status.operation_stats["subtraction"] += 1
        if "*" in problem or "×" in problem or "x" in problem.lower():
            self.memory_status.operation_stats["multiplication"] += 1
        if "/" in problem or "÷" in problem:
            self.memory_status.operation_stats["division"] += 1
    
    def _analyze_recent_trend(self) -> str:
        """Analyze recent performance trend"""
        
        if len(self.session_history) < 2:
            return "insufficient data"
        
        recent_5 = self.session_history[-5:]
        recent_successes = sum(1 for r in recent_5 if r.success)
        
        if recent_successes >= 4:
            return "strongly improving"
        elif recent_successes >= 3:
            return "improving"
        elif recent_successes >= 2:
            return "mixed"
        else:
            return "declining"

# Initialize memory store
memory_store = ModularMemoryStore()

# Create MCP server
server = Server("modular-math-server")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="store_result",
            description="Store a math problem result with full validation using Pydantic models",
            inputSchema={
                "type": "object",
                "properties": {
                    "problem": {"type": "string", "description": "The mathematical expression"},
                    "result": {"type": "string", "description": "The result or error message"},
                    "success": {"type": "boolean", "description": "Whether the solution was successful"},
                    "strategy_used": {"type": "string", "description": "Strategy that was used (optional)"},
                    "confidence": {"type": "number", "description": "Confidence level 0.0-1.0 (optional)"}
                },
                "required": ["problem", "result", "success"]
            }
        ),
        Tool(
            name="get_memory_status",
            description="Get current memory status with full statistics using Pydantic models",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_memory_summary",
            description="Get memory summary optimized for LLM prompting with Pydantic validation",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="reset_memory",
            description="Reset all memory and start fresh with Pydantic response validation",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_recent_history",
            description="Get recent problem history with detailed analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of recent problems to return (default: 5)"}
                },
                "required": []
            }
        ),
        Tool(
            name="analyze_performance_trends",
            description="Analyze performance trends and patterns in the memory data",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle MCP tool calls with Pydantic validation"""
    
    try:
        if name == "store_result":
            # Validate input using Pydantic
            request = StoreResultRequest(**arguments)
            response = memory_store.store_result(request)
            
            return [TextContent(
                type="text", 
                text=response.model_dump_json(indent=2)
            )]
            
        elif name == "get_memory_status":
            status = memory_store.get_memory_status()
            
            return [TextContent(
                type="text",
                text=status.model_dump_json(indent=2)
            )]
            
        elif name == "get_memory_summary":
            summary = memory_store.get_memory_summary()
            
            return [TextContent(
                type="text",
                text=summary.model_dump_json(indent=2)
            )]
            
        elif name == "reset_memory":
            response = memory_store.reset_memory()
            
            return [TextContent(
                type="text",
                text=response.model_dump_json(indent=2)
            )]
            
        elif name == "get_recent_history":
            limit = arguments.get("limit", 5)
            recent_history = memory_store.session_history[-limit:] if memory_store.session_history else []
            
            # Convert to JSON serializable format
            history_data = {
                "recent_problems": [problem.model_dump() for problem in recent_history],
                "count": len(recent_history),
                "analysis": {
                    "success_rate": f"{sum(1 for p in recent_history if p.success) / len(recent_history) * 100:.1f}%" if recent_history else "0%",
                    "most_recent_result": recent_history[-1].model_dump() if recent_history else None,
                    "trend": memory_store._analyze_recent_trend()
                }
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(history_data, indent=2, default=str)
            )]
            
        elif name == "analyze_performance_trends":
            status = memory_store.get_memory_status()
            
            # Perform trend analysis
            analysis = {
                "overall_performance": {
                    "total_problems": status.total_problems,
                    "success_rate": status.success_rate,
                    "error_rate": f"{(status.error_count / status.total_problems * 100):.1f}%" if status.total_problems > 0 else "0%"
                },
                "operation_analysis": {
                    "most_experienced": max(status.operation_stats, key=status.operation_stats.get) if any(status.operation_stats.values()) else "none",
                    "least_experienced": min(status.operation_stats, key=status.operation_stats.get) if any(status.operation_stats.values()) else "none",
                    "operation_distribution": status.operation_stats
                },
                "learning_trend": memory_store._analyze_recent_trend(),
                "recommendations": []
            }
            
            # Generate recommendations based on performance
            if status.total_problems == 0:
                analysis["recommendations"].append("No experience yet - start with simple problems")
            elif float(status.success_rate.replace('%', '')) >= 80:
                analysis["recommendations"].append("High success rate - can attempt more complex problems")
                analysis["recommendations"].append("Consider using confident_direct strategy")
            elif float(status.success_rate.replace('%', '')) >= 60:
                analysis["recommendations"].append("Good success rate - maintain balanced approach")
                analysis["recommendations"].append("Continue with standard_verification strategy")
            else:
                analysis["recommendations"].append("Lower success rate - focus on conservative approach")
                analysis["recommendations"].append("Use step_by_step_verification for learning")
            
            return [TextContent(
                type="text",
                text=json.dumps(analysis, indent=2)
            )]
            
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        error_result = {
            "error": str(e),
            "tool": name,
            "arguments": arguments,
            "error_type": type(e).__name__
        }
        return [TextContent(
            type="text", 
            text=json.dumps(error_result, indent=2)
        )]

async def main():
    """Main function to run the modular MCP server"""
    print("🔧 Starting Modular Math MCP Server")
    print("=" * 60)
    print("📦 Features:")
    print("   🗃️  Pydantic model validation")
    print("   📊 Advanced memory analytics") 
    print("   📋 LLM-optimized summaries")
    print("   🔄 Complete memory management")
    print("   📈 Performance trend analysis")
    print("=" * 60)
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())