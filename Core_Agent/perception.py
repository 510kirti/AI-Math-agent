# perception.py - Perception Phase Module
import asyncio
import json
import google.generativeai as genai
from typing import Optional
from Core_Agent.models import PerceptionInput, PerceptionOutput

class PerceptionAgent:
    """
    Perception phase agent responsible for analyzing and understanding mathematical expressions.
    Uses Gemini 1.5 Flash for intelligent expression parsing and complexity assessment.
    """
    
    def __init__(self, model: genai.GenerativeModel):
        self.model = model
        self.phase_name = "PERCEPTION"
        
    async def analyze(self, input_data: PerceptionInput) -> PerceptionOutput:
        """
        Analyze mathematical expression using LLM prompting
        
        Args:
            input_data: PerceptionInput containing the expression to analyze
            
        Returns:
            PerceptionOutput: Structured analysis results
        """
        print(f"🔍 {self.phase_name}: Analyzing expression '{input_data.expression}'")
        
        perception_prompt = self._create_perception_prompt(input_data.expression)
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content, perception_prompt
            )
            
            # Parse and validate JSON response
            result_dict = self._parse_llm_response(response.text)
            result = PerceptionOutput(**result_dict)
            
            print(f"✅ {self.phase_name}: Analysis complete - {result.complexity} complexity, difficulty {result.estimated_difficulty}/10")
            return result
            
        except Exception as e:
            print(f"❌ {self.phase_name}: Error during analysis: {e}")
            return self._create_error_response(input_data.expression, str(e))
    
    def _create_perception_prompt(self, expression: str) -> str:
        """Create the perception analysis prompt for Gemini"""
        
        return f"""
You are a mathematical perception system. Analyze this expression: "{expression}"

Your task is to understand and categorize this mathematical expression. Respond with ONLY a JSON object:

{{
    "is_valid": boolean,
    "operands": [list of numbers],
    "operators": [list of operators as strings],
    "complexity": "simple|medium|complex",
    "requires_order_ops": boolean,
    "estimated_difficulty": number 1-10,
    "error_message": string or null,
    "perception_notes": "detailed analysis"
}}

ANALYSIS GUIDELINES:

1. INPUT VALIDITY:
   - Check for invalid characters, malformed expressions, missing operands
   - Verify mathematical syntax and structure
   - Flag incomplete or nonsensical expressions

2. NUMBER EXTRACTION (operands):
   - Include decimals, negatives (e.g., -5.5, 42, 0.25)
   - Handle scientific notation if present
   - Extract all numeric values in order of appearance

3. OPERATOR IDENTIFICATION (operators):
   - Standard: +, -, *, /, ^ (exponentiation)
   - Alternative symbols: ×, ÷, x (as multiplication)
   - Parentheses: (, ) for grouping
   - Functions: sin, cos, log, sqrt, etc.

4. COMPLEXITY ASSESSMENT:
   - simple: 1-2 operations, basic arithmetic (e.g., "5 + 3", "12 * 4")
   - medium: 3-4 operations, order of operations required (e.g., "25 + 17 × 3")
   - complex: 5+ operations, nested parentheses, functions (e.g., "(2 + 3) × (4 - 1) + 5²")

5. ORDER OF OPERATIONS:
   - Does this require PEMDAS/BODMAS rules?
   - Are there mixed operations that need careful sequencing?
   - Consider parentheses, exponents, multiplication/division, addition/subtraction

6. DIFFICULTY RATING (1-10):
   - 1-2: Very basic arithmetic
   - 3-4: Simple expressions with order of operations
   - 5-6: Medium complexity with multiple operations
   - 7-8: Complex expressions with functions or nested operations
   - 9-10: Advanced mathematical concepts

7. PERCEPTION NOTES:
   - Provide detailed analysis of mathematical structure
   - Note any special considerations or patterns
   - Explain reasoning for complexity and difficulty ratings

EXAMPLES:
- "5 + 3" → simple, difficulty 1, no order ops needed
- "25 + 17 × 3" → medium, difficulty 3, requires order ops  
- "100 ÷ 0" → simple, difficulty 2, but note division by zero issue
- "(2 + 3) × (4 - 1) + 5²" → complex, difficulty 7, requires order ops

IMPORTANT:
- Be thorough but precise in analysis
- If invalid, clearly explain why in error_message
- Focus on mathematical structure, not solving the problem
- Consider edge cases like division by zero

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
    
    def _create_error_response(self, expression: str, error_msg: str) -> PerceptionOutput:
        """Create error response when perception fails"""
        
        return PerceptionOutput(
            is_valid=False,
            operands=[],
            operators=[],
            complexity="simple",  # Default fallback
            requires_order_ops=False,
            estimated_difficulty=1,
            error_message=f"Perception analysis failed: {error_msg}",
            perception_notes=f"Failed to analyze expression '{expression}' due to: {error_msg}"
        )
    
    def get_phase_info(self) -> dict:
        """Get information about this cognitive phase"""
        
        return {
            "phase": self.phase_name,
            "description": "Analyzes mathematical expressions for validity, complexity, and structure",
            "input_model": "PerceptionInput",
            "output_model": "PerceptionOutput",
            "capabilities": [
                "Expression validation",
                "Operand and operator extraction", 
                "Complexity assessment",
                "Difficulty rating",
                "Order of operations analysis"
            ]
        }