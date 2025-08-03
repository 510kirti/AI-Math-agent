# action.py - Action Phase Module
import asyncio
import json
import google.generativeai as genai
from typing import Optional
from Core_Agent.models import ActionInput, ActionOutput, PerceptionOutput, DecisionOutput

class ActionAgent:
    """
    Action execution phase agent responsible for solving mathematical problems.
    Uses Gemini 1.5 Flash for intelligent mathematical execution following strategic decisions.
    """
    
    def __init__(self, model: genai.GenerativeModel):
        self.model = model
        self.phase_name = "ACTION"
        
    async def execute(self, input_data: ActionInput) -> ActionOutput:
        """
        Execute mathematical calculation using LLM prompting
        
        Args:
            input_data: ActionInput containing expression, perception, and decision data
            
        Returns:
            ActionOutput: Mathematical execution results
        """
        print(f"🚀 {self.phase_name}: Executing calculation for '{input_data.expression}'")
        
        action_prompt = self._create_action_prompt(input_data)
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content, action_prompt
            )
            
            # Parse and validate JSON response
            result_dict = self._parse_llm_response(response.text)
            
            # Fix common validation issues
            result_dict = self._validate_and_fix_result(result_dict)
            
            result = ActionOutput(**result_dict)
            
            # Determine success status
            is_successful = not str(result.result).startswith("Error")
            status = "SUCCESS" if is_successful else "FAILED"
            
            print(f"✅ {self.phase_name}: Execution complete - Result: {result.result} ({status})")
            return result
            
        except Exception as e:
            print(f"❌ {self.phase_name}: Error during execution: {e}")
            return self._create_error_response(input_data, str(e))
    
    def _create_action_prompt(self, input_data: ActionInput) -> str:
        """Create the action execution prompt for Gemini"""
        
        return f"""
You are the action execution system for a mathematical agent.

PROBLEM TO SOLVE: "{input_data.expression}"

PERCEPTION ANALYSIS:
{json.dumps(input_data.perception_data.model_dump(), indent=2)}

STRATEGIC DECISION:
{json.dumps(input_data.decision_data.model_dump(), indent=2)}

Execute the mathematical calculation following the decided strategy. If the problem is a function (e.g., 'y = x^2'), also generate a list of (x, y) coordinates for plotting. Generate points for x from -10 to 10 with a step of 1. Respond with ONLY a JSON object:

{{
    "result": "number or Error: description",
    "steps": ["list of calculation steps"],
    "confidence": number 0.0-1.0,
    "verification": "verification result description", 
    "execution_notes": "detailed explanation of process",
    "plot_points": [
        {{ "x": -10, "y": 100 }},
        ...
        {{ "x": 10, "y": 100 }}
    ]
}}

EXECUTION STRATEGY GUIDELINES:

1. DIRECT_CALCULATION:
   - Calculate quickly with minimal intermediate steps
   - Show only essential operations
   - Basic verification: check final answer once
   - Focus on efficiency and speed

2. STANDARD_WITH_CHECK:
   - Show main calculation steps clearly
   - Include one verification method (reverse operation or substitution)
   - Balance detail with efficiency
   - Demonstrate key mathematical reasoning

3. STEP_BY_STEP_VERIFICATION:
   - Show every operation step in detail
   - Verify intermediate results where applicable
   - Explain mathematical reasoning at each step
   - Build confidence through transparent process

4. CONSERVATIVE_DETAILED:
   - Complete breakdown of every operation
   - Multiple verification methods
   - Extensive explanation of mathematical principles
   - Maximum transparency and checking

VERIFICATION LEVEL REQUIREMENTS:

1. MINIMAL:
   - Quick final answer check
   - Simple substitution or mental verification

2. STANDARD:
   - Verify using one alternative method
   - Check order of operations compliance
   - Confirm result reasonableness

3. HIGH:
   - Multiple verification approaches
   - Step-by-step result checking
   - Alternative calculation method
   - Detailed reasonableness assessment

4. EXTRA:
   - Comprehensive verification using multiple methods
   - Cross-check with different approaches
   - Detailed mathematical principle verification
   - Extensive error-checking procedures

CRITICAL MATHEMATICAL RULES:

1. ORDER OF OPERATIONS (PEMDAS/BODMAS):
   - Parentheses/Brackets first
   - Exponents/Orders (powers, roots)
   - Multiplication and Division (left to right)
   - Addition and Subtraction (left to right)

2. EDGE CASE HANDLING:
   - Division by zero: Return "Error: Division by zero"
   - Invalid operations: Return "Error: Invalid operation"
   - Undefined results: Return "Error: Undefined result"
   - Overflow/underflow: Handle gracefully

3. ACCURACY REQUIREMENTS:
   - Use appropriate precision for the calculation
   - Round final results appropriately
   - Maintain accuracy through intermediate steps
   - Handle floating-point precision issues

STEP FORMATTING GUIDELINES:
- Use clear, descriptive language
- Show mathematical notation properly
- Explain reasoning for each major step
- Include intermediate results where helpful
- Make the process easy to follow and verify

VERIFICATION EXAMPLES:
For "25 + 17 × 3":
- Standard: "Check: 25 + (17 × 3) = 25 + 51 = 76 ✓"
- High: "Verification 1: 25 + 51 = 76 ✓, Verification 2: 76 - 25 = 51 = 17 × 3 ✓"

CONFIDENCE CALCULATION:
- Start with decision confidence level
- Adjust based on calculation complexity encountered
- Reduce if edge cases or unusual situations arise
- Increase if calculation proceeds smoothly as expected

EXECUTION NOTES:
Provide detailed explanation including:
- How the strategic decision was implemented
- Any challenges or considerations during execution
- Quality of verification results
- Assessment of result reliability
- Any recommendations for similar future problems

IMPORTANT REMINDERS:
- Mathematical accuracy is absolutely critical
- Follow the decided strategy faithfully
- Show appropriate level of detail based on verification level
- Handle all edge cases gracefully
- Provide clear, understandable explanations

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
    
    def _create_error_response(self, input_data: ActionInput, error_msg: str) -> ActionOutput:
        """Create error response when action execution fails"""
        
        return ActionOutput(
            result=f"Error: {error_msg}",
            steps=[
                f"Action execution failed: {error_msg}",
                "Unable to complete mathematical calculation",
                "System error prevented normal execution"
            ],
            confidence=0.0,  # No confidence in failed execution
            verification="Unable to verify due to execution error",
            execution_notes=f"Action execution system encountered an error: {error_msg}. "
                          f"The mathematical calculation for '{input_data.expression}' could not be completed. "
                          f"This may be due to system issues, invalid expression format, or other technical problems."
        )
    
    def _validate_and_fix_result(self, result_dict: dict) -> dict:
        """Validate and fix common issues in LLM response"""
        
        # Fix result field - ensure it's a string
        if "result" in result_dict:
            result_value = result_dict["result"]
            if isinstance(result_value, (int, float)):
                result_dict["result"] = str(result_value)
            elif not isinstance(result_value, str):
                result_dict["result"] = str(result_value)
        
        # Ensure steps is a list of strings
        if "steps" in result_dict:
            steps = result_dict["steps"]
            if not isinstance(steps, list):
                result_dict["steps"] = [str(steps)]
            else:
                result_dict["steps"] = [str(step) for step in steps]
        
        # Ensure confidence is a float between 0 and 1
        if "confidence" in result_dict:
            try:
                confidence = float(result_dict["confidence"])
                result_dict["confidence"] = max(0.0, min(1.0, confidence))
            except (ValueError, TypeError):
                result_dict["confidence"] = 0.5
        
        # Ensure verification and execution_notes are strings
        for field in ["verification", "execution_notes"]:
            if field in result_dict and not isinstance(result_dict[field], str):
                result_dict[field] = str(result_dict[field])
        
        return result_dict
    
    def get_method_details(self, method: str) -> dict:
        """Get detailed execution information for a specific method"""
        
        method_details = {
            "direct_calculation": {
                "approach": "Efficient and fast",
                "steps_detail": "Minimal - only essential operations shown",
                "verification": "Basic final check",
                "use_case": "Simple problems with high confidence",
                "example": "For '5 + 3': Direct calculation: 5 + 3 = 8"
            },
            "standard_with_check": {
                "approach": "Balanced detail and efficiency", 
                "steps_detail": "Key steps with clear reasoning",
                "verification": "Single verification method",
                "use_case": "Standard problems with moderate confidence",
                "example": "For '25 + 17 × 3': Step 1: 17 × 3 = 51, Step 2: 25 + 51 = 76, Verify: 25 + (17 × 3) = 76 ✓"
            },
            "step_by_step_verification": {
                "approach": "Detailed and methodical",
                "steps_detail": "All operations shown with explanations",
                "verification": "Step-by-step checking", 
                "use_case": "Learning situations or medium complexity",
                "example": "Complete breakdown with verification at each major step"
            },
            "conservative_detailed": {
                "approach": "Maximum detail and safety",
                "steps_detail": "Complete breakdown with extensive explanation",
                "verification": "Multiple verification methods",
                "use_case": "Complex problems or low confidence situations",
                "example": "Exhaustive step-by-step with multiple verification approaches"
            }
        }
        
        return method_details.get(method, {"error": "Unknown method"})
    
    def get_phase_info(self) -> dict:
        """Get information about this cognitive phase"""
        
        return {
            "phase": self.phase_name,
            "description": "Executes mathematical calculations following strategic decisions with appropriate verification",
            "input_model": "ActionInput",
            "output_model": "ActionOutput",
            "capabilities": [
                "Mathematical calculation execution",
                "Strategy-appropriate step presentation",
                "Multi-level verification", 
                "Edge case handling",
                "Confidence assessment of results"
            ],
            "execution_methods": {
                "direct_calculation": "Fast execution, minimal steps",
                "standard_with_check": "Balanced approach with verification",
                "step_by_step_verification": "Detailed steps with checking",
                "conservative_detailed": "Maximum detail and multiple verification"
            },
            "verification_capabilities": {
                "minimal": "Quick final check",
                "standard": "Single verification method", 
                "high": "Multiple verification approaches",
                "extra": "Comprehensive verification with multiple methods"
            },
            "mathematical_features": [
                "Order of operations (PEMDAS/BODMAS)",
                "Edge case handling (division by zero, etc.)",
                "Precision management",
                "Multiple verification methods",
                "Clear step-by-step explanations"
            ]
        }