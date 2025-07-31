# decision.py - Decision Phase Module
import asyncio
import json
import google.generativeai as genai
from typing import Optional
from Core_Agent.models import DecisionInput, DecisionOutput, PerceptionOutput, MemoryOutput

class DecisionAgent:
    """
    Decision making phase agent responsible for strategic choices about problem-solving approach.
    Uses Gemini 1.5 Flash for intelligent decision making based on perception and memory inputs.
    """
    
    def __init__(self, model: genai.GenerativeModel):
        self.model = model
        self.phase_name = "DECISION"
        
    async def decide(self, input_data: DecisionInput) -> DecisionOutput:
        """
        Make strategic decision using LLM prompting
        
        Args:
            input_data: DecisionInput containing expression, perception, and memory data
            
        Returns:
            DecisionOutput: Strategic decisions about solving approach
        """
        print(f"⚡ {self.phase_name}: Making strategic decision for '{input_data.expression}'")
        
        decision_prompt = self._create_decision_prompt(input_data)
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content, decision_prompt
            )
            
            # Parse and validate JSON response
            result_dict = self._parse_llm_response(response.text)
            result = DecisionOutput(**result_dict)
            
            print(f"✅ {self.phase_name}: Decision complete - {result.selected_method} with {result.final_confidence:.3f} confidence")
            return result
            
        except Exception as e:
            print(f"❌ {self.phase_name}: Error during decision making: {e}")
            return self._create_error_response(input_data, str(e))
    
    def _create_decision_prompt(self, input_data: DecisionInput) -> str:
        """Create the decision making prompt for Gemini"""
        
        return f"""
You are the decision-making system for a mathematical agent.

PROBLEM: "{input_data.expression}"

PERCEPTION ANALYSIS:
{json.dumps(input_data.perception_data.model_dump(), indent=2)}

MEMORY CONSULTATION:
{json.dumps(input_data.memory_data.model_dump(), indent=2)}

Based on perception analysis and memory consultation, make a strategic decision. Respond with ONLY a JSON object:

{{
    "selected_method": "direct_calculation|standard_with_check|step_by_step_verification|conservative_detailed",
    "final_confidence": number 0.0-1.0,
    "show_working_steps": boolean,
    "verification_level": "minimal|standard|high|extra",
    "reasoning": "detailed explanation of decision logic",
    "execution_strategy": "specific approach for solving",
    "risk_assessment": "low|medium|high"
}}

METHOD SELECTION GUIDELINES:

1. DIRECT_CALCULATION:
   - Use when: High confidence (≥0.8) + simple problems
   - Characteristics: Quick execution, minimal steps shown, basic verification
   - Best for: Proven expertise + straightforward arithmetic

2. STANDARD_WITH_CHECK:
   - Use when: Moderate confidence (0.6-0.8) + standard problems
   - Characteristics: Show key steps, verify result once
   - Best for: Familiar problem types with good track record

3. STEP_BY_STEP_VERIFICATION:
   - Use when: Lower confidence (0.4-0.6) + medium complexity
   - Characteristics: Show all operations, verify each step
   - Best for: Learning phase or unfamiliar problem types

4. CONSERVATIVE_DETAILED:
   - Use when: Low confidence (<0.4) + complex problems or error history
   - Characteristics: Detailed breakdown, multiple verification methods
   - Best for: New agent, recent errors, or very complex problems

VERIFICATION LEVEL GUIDELINES:

1. MINIMAL: Just final answer check
   - Use with: High confidence, simple problems, proven expertise
   
2. STANDARD: Key steps + single verification method
   - Use with: Moderate confidence, standard complexity
   
3. HIGH: All steps + double-checking
   - Use with: Lower confidence, learning situations
   
4. EXTRA: Detailed breakdown + multiple verification approaches
   - Use with: Very low confidence, complex problems, error recovery

CONFIDENCE CALCULATION:
Base confidence from memory consultation, then adjust for:
- Problem complexity (simple +0.1, medium +0.0, complex -0.1)
- Order of operations requirement (if required -0.05)
- Difficulty level (subtract 0.02 per difficulty point above 5)
- Recent error patterns (subtract 0.1 if similar errors found)

DECISION FACTORS TO ANALYZE:

1. PERCEPTION vs MEMORY ALIGNMENT:
   - Does problem complexity match agent's confidence level?
   - Are there mismatches that require adjustment?
   - How do difficulty ratings compare to past successes?

2. STRATEGY RECOMMENDATION IMPACT:
   - How does memory's strategy recommendation influence method choice?
   - Should confidence modifier be applied fully or adjusted?
   - Are there perception factors that override memory advice?

3. RISK vs EFFICIENCY BALANCE:
   - What's the cost of being wrong vs being slow?
   - How does this fit the agent's learning objectives?
   - Should the agent stretch capabilities or play safe?

4. ERROR PREVENTION FOCUS:
   - Are there specific error patterns to avoid?
   - What verification level prevents likely mistakes?
   - How can working steps support accuracy?

5. LEARNING OPTIMIZATION:
   - Will this approach support skill development?
   - Is this an opportunity to build confidence?
   - How does this decision impact future performance?

REASONING EXPLANATION:
Provide detailed explanation covering:
- Why this method was chosen over alternatives
- How perception and memory inputs influenced the decision
- What specific factors drove confidence level
- How risk assessment was determined
- Expected outcomes and success factors

EXECUTION STRATEGY:
Provide specific guidance for the action phase:
- Detailed approach for mathematical execution
- Key checkpoints and verification steps
- Error handling considerations
- Quality assurance measures

Remember: The goal is to maximize success probability while supporting appropriate learning and growth.

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
    
    def _create_error_response(self, input_data: DecisionInput, error_msg: str) -> DecisionOutput:
        """Create error response when decision making fails"""
        
        return DecisionOutput(
            selected_method="conservative_detailed",  # Safest option
            final_confidence=0.5,  # Moderate default
            show_working_steps=True,  # Show steps for safety
            verification_level="high",  # Extra verification
            reasoning=f"Decision system failed: {error_msg}. Using safe default approach with high verification to ensure accuracy despite system error.",
            execution_strategy="Careful step-by-step approach due to decision error. Will use detailed breakdown and multiple verification methods to compensate for decision system failure.",
            risk_assessment="high"  # High risk due to system error
        )
    
    def get_method_info(self, method: str) -> dict:
        """Get detailed information about a specific method"""
        
        methods = {
            "direct_calculation": {
                "description": "Quick execution with minimal verification",
                "use_case": "High confidence + simple problems",
                "steps_shown": "Minimal",
                "verification": "Basic final check",
                "speed": "Fast",
                "accuracy_focus": "Efficiency over details"
            },
            "standard_with_check": {
                "description": "Balanced approach with key steps and verification",
                "use_case": "Moderate confidence + standard problems", 
                "steps_shown": "Key steps only",
                "verification": "Single verification method",
                "speed": "Medium",
                "accuracy_focus": "Balanced speed and accuracy"
            },
            "step_by_step_verification": {
                "description": "Detailed steps with verification at each stage",
                "use_case": "Lower confidence + medium complexity",
                "steps_shown": "All operations",
                "verification": "Step-by-step checking",
                "speed": "Slower",
                "accuracy_focus": "Accuracy over speed"
            },
            "conservative_detailed": {
                "description": "Maximum detail with multiple verification methods",
                "use_case": "Low confidence + complex problems",
                "steps_shown": "Complete breakdown",
                "verification": "Multiple methods",
                "speed": "Slowest",
                "accuracy_focus": "Maximum accuracy and safety"
            }
        }
        
        return methods.get(method, {"error": "Unknown method"})
    
    def get_phase_info(self) -> dict:
        """Get information about this cognitive phase"""
        
        return {
            "phase": self.phase_name,
            "description": "Makes strategic decisions about problem-solving approach based on perception and memory",
            "input_model": "DecisionInput",
            "output_model": "DecisionOutput", 
            "capabilities": [
                "Method selection based on confidence and complexity",
                "Confidence level calculation",
                "Verification level determination",
                "Risk assessment",
                "Strategic reasoning and explanation"
            ],
            "methods": {
                "direct_calculation": "Fast execution, minimal verification",
                "standard_with_check": "Balanced approach with standard verification",
                "step_by_step_verification": "Detailed steps with careful checking",
                "conservative_detailed": "Maximum detail and multiple verification"
            },
            "verification_levels": {
                "minimal": "Basic final answer check",
                "standard": "Key steps + single verification",
                "high": "All steps + double-checking", 
                "extra": "Detailed breakdown + multiple verification methods"
            }
        }