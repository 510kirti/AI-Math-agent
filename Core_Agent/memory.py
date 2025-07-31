# memory.py - Memory Phase Module
import asyncio
import json
import google.generativeai as genai
from typing import Optional
from Core_Agent.models import MemoryInput, MemoryOutput, PerceptionOutput

class MemoryAgent:
    """
    Memory consultation phase agent responsible for analyzing past experiences 
    and recommending strategies based on learned patterns.
    Uses Gemini 1.5 Flash for intelligent memory analysis and strategy recommendation.
    """
    
    def __init__(self, model: genai.GenerativeModel):
        self.model = model
        self.phase_name = "MEMORY"
        
    async def consult(self, input_data: MemoryInput) -> MemoryOutput:
        """
        Consult memory and recommend strategy using LLM prompting
        
        Args:
            input_data: MemoryInput containing expression, perception data, and memory summary
            
        Returns:
            MemoryOutput: Strategy recommendations based on experience
        """
        print(f"🧠 {self.phase_name}: Consulting memory for '{input_data.expression}'")
        
        memory_prompt = self._create_memory_prompt(input_data)
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content, memory_prompt
            )
            
            # Parse and validate JSON response
            result_dict = self._parse_llm_response(response.text)
            result = MemoryOutput(**result_dict)
            
            print(f"✅ {self.phase_name}: Consultation complete - recommending {result.strategy_recommendation}")
            return result
            
        except Exception as e:
            print(f"❌ {self.phase_name}: Error during consultation: {e}")
            return self._create_error_response(input_data, str(e))
    
    def _create_memory_prompt(self, input_data: MemoryInput) -> str:
        """Create the memory consultation prompt for Gemini"""
        
        return f"""
You are the memory consultation system for a mathematical agent.

CURRENT PROBLEM: "{input_data.expression}"

PERCEPTION ANALYSIS:
{json.dumps(input_data.perception_data.model_dump(), indent=2)}

AGENT'S MEMORY AND EXPERIENCE:
{input_data.memory_summary}

Your task is to analyze the agent's experience and recommend an approach. Respond with ONLY a JSON object:

{{
    "session_success_rate": "descriptive string about current performance",
    "strategy_recommendation": "conservative_approach|standard_verification|confident_direct",
    "confidence_modifier": number 0.5-1.0,
    "similar_problems_found": number,
    "memory_insights": "detailed analysis of patterns",
    "recommended_approach": "specific strategy explanation"
}}

STRATEGY RECOMMENDATION GUIDELINES:

1. CONSERVATIVE_APPROACH:
   - Use for: New agents, recent failures, complex problems
   - Characteristics: Step-by-step verification, high caution, detailed explanations
   - When: Success rate < 60%, recent errors, first-time problem types

2. STANDARD_VERIFICATION:
   - Use for: Moderate experience, medium complexity problems
   - Characteristics: Balanced speed vs accuracy, standard checking
   - When: Success rate 60-79%, mixed recent performance, familiar problem types

3. CONFIDENT_DIRECT:
   - Use for: High success rate agents, simple/familiar problems
   - Characteristics: Fast execution, minimal verification, trust in abilities
   - When: Success rate ≥ 80%, recent successes, simple problem complexity

CONFIDENCE MODIFIER GUIDELINES:
- 0.5-0.6: Low confidence (new agent, recent errors, very complex problem)
- 0.7-0.8: Moderate confidence (some success, standard problems, learning phase)
- 0.9-1.0: High confidence (proven track record, simple problems, expertise)

ANALYSIS FACTORS TO CONSIDER:

1. SUCCESS RATE IMPACT:
   - How does current success rate affect recommended confidence?
   - Are there patterns in successful vs failed attempts?
   - What does the trend suggest about learning progress?

2. PROBLEM SIMILARITY:
   - Has the agent solved similar complexity problems before?
   - Are there matching operation types in recent history?
   - What strategies worked well for similar problems?

3. RECENT PERFORMANCE PATTERNS:
   - Are there consecutive successes building confidence?
   - Any recent failures that should trigger caution?
   - Is the agent improving, declining, or stable?

4. COMPLEXITY VS EXPERIENCE:
   - How does current problem complexity match agent's proven abilities?
   - Should the agent stretch its capabilities or play it safe?
   - What's the risk/reward balance for this problem?

5. ERROR PATTERN ANALYSIS:
   - Are there specific error types that match this problem?
   - Should certain operation types trigger extra caution?
   - What lessons from past failures apply here?

MEMORY INSIGHTS ANALYSIS:
- Identify meaningful patterns in the agent's learning journey
- Note areas of developing expertise or persistent challenges
- Explain how past experiences inform current recommendation
- Consider both short-term recent patterns and longer-term trends

RECOMMENDED APPROACH:
- Provide specific, actionable strategy guidance
- Explain how the recommendation balances risk vs efficiency
- Consider the agent's growth and learning objectives
- Tailor advice to the specific problem characteristics

Remember: The goal is to maximize success probability while supporting appropriate risk-taking for learning and growth.

Return ONLY the JSON object, no other text or formatting.
"""

    def _parse_llm_response(self, response_text: str) -> dict:
        """Parse and clean LLM response to extract JSON"""
        
        json_text = response_text.strip()
        
        # Remove common formatting artifacts
        if json_text.startswith('```json'):
            json_text = json_text[7:-3]
        elif json_text.startswith('```'):
            json_text = json_text[3:-3]
        
        json_text = json_text.strip()
        
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")
    
    def _create_error_response(self, input_data: MemoryInput, error_msg: str) -> MemoryOutput:
        """Create error response when memory consultation fails"""
        
        return MemoryOutput(
            session_success_rate=f"Error accessing memory: {error_msg}",
            strategy_recommendation="conservative_approach",  # Safe default
            confidence_modifier=0.6,  # Moderate confidence default
            similar_problems_found=0,
            memory_insights=f"Memory consultation failed: {error_msg}. Using safe defaults.",
            recommended_approach="Using conservative approach due to memory access issues. Recommend step-by-step verification and careful execution."
        )
    
    def get_phase_info(self) -> dict:
        """Get information about this cognitive phase"""
        
        return {
            "phase": self.phase_name,
            "description": "Consults past experiences to recommend optimal problem-solving strategies",
            "input_model": "MemoryInput", 
            "output_model": "MemoryOutput",
            "capabilities": [
                "Success rate analysis",
                "Strategy recommendation based on experience",
                "Confidence level adjustment",
                "Pattern recognition in problem history",
                "Risk assessment for current problem"
            ],
            "strategies": {
                "conservative_approach": "High caution, step-by-step verification",
                "standard_verification": "Balanced approach with standard checking", 
                "confident_direct": "Fast execution with minimal verification"
            }
        }