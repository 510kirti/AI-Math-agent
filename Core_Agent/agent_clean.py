# agent_clean.py - Main Cognitive Agent Orchestrator (No .env dependency)
import asyncio
import os
import json
import google.generativeai as genai
from typing import Dict, Any, Optional

# Import cognitive phase modules
from Core_Agent.perception import PerceptionAgent
from Core_Agent.memory import MemoryAgent  
from Core_Agent.decision import DecisionAgent
from Core_Agent.action import ActionAgent

# Import Pydantic models
from Core_Agent.models import (
    PerceptionInput, PerceptionOutput,
    MemoryInput, MemoryOutput, 
    DecisionInput, DecisionOutput,
    ActionInput, ActionOutput,
    CognitiveAnalysisResult
)

class CognitiveAgent:
    """
    Main cognitive agent that orchestrates all four cognitive phases.
    Coordinates Perception, Memory, Decision, and Action agents using Gemini 1.5 Flash.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the cognitive agent with all phase modules
        
        Args:
            api_key: Gemini API key (required)
        """
        # Configure Gemini API - try multiple sources
        if not api_key:
            api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            print("❌ GEMINI_API_KEY not found!")
            print("💡 Solutions:")
            print("   1. Pass api_key directly: CognitiveAgent(api_key='your_key')")
            print("   2. Set environment variable: set GEMINI_API_KEY=your_key")
            print("   3. Get API key from: https://aistudio.google.com/app/apikey")
            raise ValueError("GEMINI_API_KEY must be provided")
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Test the API key with a simple call
            print("🔑 Testing Gemini API key...")
            test_response = self.model.generate_content("Hello")
            print("✅ Gemini API key working!")
            
        except Exception as e:
            print(f"❌ Gemini API configuration failed: {e}")
            print("💡 Check if your API key is valid")
            raise ValueError(f"Failed to configure Gemini API: {e}")
        
        # Initialize all cognitive phase agents
        self.perception = PerceptionAgent(self.model)
        self.memory = MemoryAgent(self.model)
        self.decision = DecisionAgent(self.model)
        self.action = ActionAgent(self.model)
        
        print("🧠 Cognitive Agent initialized with Gemini 1.5 Flash")
        print("📡 Perception Agent ready")
        print("🧠 Memory Agent ready") 
        print("⚡ Decision Agent ready")
        print("🚀 Action Agent ready")
    
    async def analyze(self, expression: str, memory_summary: str) -> CognitiveAnalysisResult:
        """
        Complete cognitive analysis of a mathematical expression
        
        Args:
            expression: Mathematical expression to analyze and solve
            memory_summary: Current memory state summary from MCP server
            
        Returns:
            CognitiveAnalysisResult: Complete results from all cognitive phases
        """
        print(f"\n{'='*80}")
        print(f"🧠 STARTING COMPLETE COGNITIVE ANALYSIS")
        print(f"🎯 Expression: {expression}")
        print(f"🤖 Powered by Gemini 1.5 Flash + Modular Architecture")
        print(f"{'='*80}")
        
        try:
            # PHASE 1: PERCEPTION
            print(f"\n📡 PHASE 1: PERCEPTION ANALYSIS")
            print("-" * 50)
            
            perception_input = PerceptionInput(expression=expression)
            perception_result = await self.perception.analyze(perception_input)
            
            if not perception_result.is_valid:
                print(f"❌ Perception failed: {perception_result.error_message}")
                # Return early with error state
                return self._create_error_result(expression, perception_result, "perception_error")
            
            self._display_perception_results(perception_result)
            
            # PHASE 2: MEMORY CONSULTATION
            print(f"\n🧠 PHASE 2: MEMORY CONSULTATION")
            print("-" * 50)
            
            memory_input = MemoryInput(
                expression=expression,
                perception_data=perception_result,
                memory_summary=memory_summary
            )
            memory_result = await self.memory.consult(memory_input)
            
            self._display_memory_results(memory_result)
            
            # PHASE 3: DECISION MAKING
            print(f"\n⚡ PHASE 3: DECISION MAKING")
            print("-" * 45)
            
            decision_input = DecisionInput(
                expression=expression,
                perception_data=perception_result,
                memory_data=memory_result
            )
            decision_result = await self.decision.decide(decision_input)
            
            self._display_decision_results(decision_result)
            
            # PHASE 4: ACTION EXECUTION
            print(f"\n🚀 PHASE 4: ACTION EXECUTION")
            print("-" * 45)
            
            action_input = ActionInput(
                expression=expression,
                perception_data=perception_result,
                decision_data=decision_result
            )
            action_result = await self.action.execute(action_input)
            
            self._display_action_results(action_result)
            
            # Create complete result
            is_successful = not str(action_result.result).startswith("Error")
            
            cognitive_result = CognitiveAnalysisResult(
                expression=expression,
                perception=perception_result,
                memory=memory_result,
                decision=decision_result,
                action=action_result,
                success=is_successful
            )
            
            print(f"\n{'='*80}")
            print(f"🎯 COGNITIVE ANALYSIS COMPLETE")
            print(f"📊 Result: {action_result.result}")
            print(f"🏆 Status: {'✅ SUCCESS' if is_successful else '❌ FAILED'}")
            print(f"{'='*80}")
            
            return cognitive_result
            
        except Exception as e:
            print(f"❌ Cognitive analysis failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Create error result
            return self._create_error_result(expression, None, f"system_error: {str(e)}")
    
    async def quick_solve(self, expression: str) -> ActionOutput:
        """
        Quick solve without detailed cognitive analysis
        
        Args:
            expression: Mathematical expression to solve
            
        Returns:
            ActionOutput: Quick solving result
        """
        print(f"🚀 Quick Solve: {expression}")
        
        try:
            # Simple perception check
            perception_input = PerceptionInput(expression=expression)
            perception_result = await self.perception.analyze(perception_input)
            
            if not perception_result.is_valid:
                return ActionOutput(
                    result=f"Error: {perception_result.error_message}",
                    steps=["Invalid expression"],
                    confidence=0.0,
                    verification="Cannot verify invalid expression",
                    execution_notes="Expression failed perception validation"
                )
            
            # Direct action with minimal decision
            simple_decision = DecisionOutput(
                selected_method="direct_calculation",
                final_confidence=0.7,
                show_working_steps=False,
                verification_level="minimal",
                reasoning="Quick solve mode - using direct calculation",
                execution_strategy="Fast execution with basic verification",
                risk_assessment="medium"
            )
            
            action_input = ActionInput(
                expression=expression,
                perception_data=perception_result,
                decision_data=simple_decision
            )
            
            return await self.action.execute(action_input)
            
        except Exception as e:
            print(f"❌ Quick solve failed: {e}")
            return ActionOutput(
                result=f"Error: {str(e)}",
                steps=["Quick solve failed"],
                confidence=0.0,
                verification="Cannot verify due to error",
                execution_notes=f"Quick solve encountered error: {str(e)}"
            )
    
    def _display_perception_results(self, perception: PerceptionOutput):
        """Display formatted perception results"""
        print(f"✅ Validity: {perception.is_valid}")
        print(f"🔢 Operands: {perception.operands}")
        print(f"🔧 Operators: {perception.operators}")
        print(f"📊 Complexity: {perception.complexity}")
        print(f"⚖️  Order Ops Required: {perception.requires_order_ops}")
        print(f"🎯 Difficulty: {perception.estimated_difficulty}/10")
        print(f"📝 Analysis: {perception.perception_notes}")
    
    def _display_memory_results(self, memory: MemoryOutput):
        """Display formatted memory results"""
        print(f"📊 Success Rate: {memory.session_success_rate}")
        print(f"🎯 Strategy Rec: {memory.strategy_recommendation}")
        print(f"📈 Confidence Modifier: {memory.confidence_modifier:.2f}")
        print(f"🔍 Similar Problems: {memory.similar_problems_found}")
        print(f"🧠 Insights: {memory.memory_insights}")
        print(f"📋 Approach: {memory.recommended_approach}")
    
    def _display_decision_results(self, decision: DecisionOutput):
        """Display formatted decision results"""
        print(f"🎯 Method: {decision.selected_method}")
        print(f"📊 Confidence: {decision.final_confidence:.3f}")
        print(f"📝 Show Steps: {decision.show_working_steps}")
        print(f"🔍 Verification: {decision.verification_level}")
        print(f"⚠️  Risk: {decision.risk_assessment}")
        print(f"💭 Reasoning: {decision.reasoning}")
        print(f"📋 Strategy: {decision.execution_strategy}")
    
    def _display_action_results(self, action: ActionOutput):
        """Display formatted action results"""
        print(f"📊 Result: {action.result}")
        print(f"🎯 Confidence: {action.confidence:.3f}")
        print(f"📝 Steps ({len(action.steps)} total):")
        for i, step in enumerate(action.steps, 1):
            print(f"   {i}. {step}")
        print(f"🔍 Verification: {action.verification}")
        print(f"📋 Notes: {action.execution_notes}")
    
    def _create_error_result(self, expression: str, perception: Optional[PerceptionOutput], error_type: str) -> CognitiveAnalysisResult:
        """Create error result when cognitive analysis fails"""
        
        # Create minimal error responses for each phase
        error_perception = perception or PerceptionOutput(
            is_valid=False,
            operands=[],
            operators=[],
            complexity="simple",
            requires_order_ops=False,
            estimated_difficulty=1,
            error_message=f"Error in {error_type}",
            perception_notes=f"Analysis failed due to {error_type}"
        )
        
        error_memory = MemoryOutput(
            session_success_rate="Error - unable to access memory",
            strategy_recommendation="conservative_approach",
            confidence_modifier=0.5,
            similar_problems_found=0,
            memory_insights=f"Memory consultation failed due to {error_type}",
            recommended_approach="Conservative approach due to system error"
        )
        
        error_decision = DecisionOutput(
            selected_method="conservative_detailed",
            final_confidence=0.0,
            show_working_steps=True,
            verification_level="extra",
            reasoning=f"System error in {error_type} - using safest approach",
            execution_strategy="Conservative detailed approach due to system error",
            risk_assessment="high"
        )
        
        error_action = ActionOutput(
            result=f"Error: {error_type}",
            steps=[f"Analysis failed due to {error_type}"],
            confidence=0.0,
            verification="Cannot verify due to system error",
            execution_notes=f"Execution failed due to {error_type}"
        )
        
        return CognitiveAnalysisResult(
            expression=expression,
            perception=error_perception,
            memory=error_memory,
            decision=error_decision,
            action=error_action,
            success=False
        )
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get comprehensive information about the cognitive agent"""
        
        return {
            "agent_name": "Modular Cognitive Math Agent",
            "llm_model": "Gemini 1.5 Flash",
            "architecture": "Modular with Pydantic validation",
            "phases": {
                "perception": self.perception.get_phase_info(),
                "memory": self.memory.get_phase_info(), 
                "decision": self.decision.get_phase_info(),
                "action": self.action.get_phase_info()
            },
            "capabilities": [
                "Complete cognitive analysis",
                "Quick problem solving",
                "Modular phase execution",
                "Pydantic data validation",
                "Strategic decision making",
                "Memory-driven learning"
            ],
            "data_flow": [
                "Expression → Perception Analysis",
                "Perception + Memory → Memory Consultation",
                "Perception + Memory → Strategic Decision",
                "Perception + Decision → Mathematical Execution"
            ]
        }