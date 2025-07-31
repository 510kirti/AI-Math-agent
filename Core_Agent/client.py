# client.py - Modular Cognitive Client
import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv


# Import the modular cognitive agent
from Core_Agent.agent_clean import CognitiveAgent
from Core_Agent.models import CognitiveAnalysisResult

# Load environment variables
load_dotenv()

class ModularMathClient:
    """
    Modular math client that coordinates between:
    - MCP Server (memory/tools only)
    - Cognitive Agent (LLM prompting + modular phases)
    """
    
    def __init__(self):
        self.server_path = "mcpserver.py"  # MCP server for tools only
        self.session = None
        self.cognitive_agent = None
        
    async def connect(self):
        """Connect to MCP server and initialize cognitive agent"""
        print("🔧 Connecting to Modular MCP Server...")
        
        # Connect to MCP server
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_path],
            cwd="."
        )
        
        

        # from mcp.client.stdio import stdio_client
        self.stdio_client = stdio_client(server_params)
        self.read, self.write = await self.stdio_client.__aenter__()


        self.session = ClientSession(self.read, self.write)
        await self.session.__aenter__()
        await self.session.initialize()
        
        # Get available tools
        tools_result = await self.session.list_tools()
        tools = tools_result.tools
        print(f"✅ MCP Connected! Available tools: {[tool.name for tool in tools]}")
        
        # Initialize cognitive agent
        print("🧠 Initializing Cognitive Agent...")
        self.cognitive_agent = CognitiveAgent()
        print("✅ Cognitive Agent ready!")
        
        return self.session
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if hasattr(self, 'stdio_client'):
            await self.stdio_client.__aexit__(None, None, None)
        print("🔌 Disconnected from server")
    
    def safe_parse_result(self, result):
        """Safely parse MCP tool result"""
        try:
            if hasattr(result, 'content') and result.content:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return json.loads(content.text)
                else:
                    return content
            else:
                return result
        except Exception as e:
            print(f"⚠️  Error parsing result: {e}")
            return str(result)
    
    async def solve_with_complete_cognitive_analysis(self, expression: str) -> CognitiveAnalysisResult:
        """
        Complete cognitive analysis using modular architecture
        """
        try:
            # Get memory summary from MCP server
            memory_result = await self.session.call_tool("get_memory_summary")
            memory_data = self.safe_parse_result(memory_result)
            memory_summary = memory_data.get("summary", "No memory available") if isinstance(memory_data, dict) else str(memory_data)
            
            # Run complete cognitive analysis
            cognitive_result = await self.cognitive_agent.analyze(expression, memory_summary)
            
            # Store result in MCP server
            await self._store_result(cognitive_result)
            
            # Show impact analysis
            await self._show_memory_impact()
            
            return cognitive_result
            
        except Exception as e:
            print(f"❌ Error in cognitive analysis: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def simple_solve(self, expression: str):
        """Simple solve without detailed cognitive analysis"""
        try:
            print(f"🚀 Simple Solve: {expression}")
            
            # Quick solve using cognitive agent
            action_result = await self.cognitive_agent.quick_solve(expression)
            
            print(f"📊 Result: {action_result.result}")
            print(f"📊 Confidence: {action_result.confidence:.3f}")
            
            if action_result.steps:
                print(f"📊 Steps:")
                for i, step in enumerate(action_result.steps, 1):
                    print(f"   {i}. {step}")
            
            # Store result
            is_success = not str(action_result.result).startswith("Error")
            await self.session.call_tool(
                "store_result",
                arguments={
                    "problem": expression,
                    "result": str(action_result.result),
                    "success": is_success,
                    "strategy_used": "quick_solve",
                    "confidence": action_result.confidence
                }
            )
            
            return action_result
            
        except Exception as e:
            print(f"❌ Error in simple solve: {e}")
            return None
    
    async def get_detailed_memory_status(self):
        """Get detailed memory status and analysis"""
        print(f"\n🧠 DETAILED MEMORY STATUS")
        print("=" * 60)
        
        try:
            # Get memory status
            status_result = await self.session.call_tool("get_memory_status")
            status_data = self.safe_parse_result(status_result)
            
            if isinstance(status_data, dict):
                print(f"📊 LEARNING PROGRESS:")
                print(f"   • Total Problems: {status_data.get('total_problems', 0)}")
                print(f"   • Success Rate: {status_data.get('success_rate', '0%')}")
                print(f"   • Success Count: {status_data.get('success_count', 0)}")
                print(f"   • Error Count: {status_data.get('error_count', 0)}")
                
                ops = status_data.get('operation_stats', {})
                print(f"\n🔧 OPERATION EXPERIENCE:")
                total_ops = sum(ops.values())
                for op, count in ops.items():
                    percentage = (count / total_ops * 100) if total_ops > 0 else 0
                    print(f"   • {op.title()}: {count} times ({percentage:.1f}%)")
                
                # Get performance trends
                trends_result = await self.session.call_tool("analyze_performance_trends")
                trends_data = self.safe_parse_result(trends_result)
                
                if isinstance(trends_data, dict):
                    print(f"\n📈 PERFORMANCE ANALYSIS:")
                    analysis = trends_data.get('overall_performance', {})
                    print(f"   • Error Rate: {analysis.get('error_rate', '0%')}")
                    print(f"   • Learning Trend: {trends_data.get('learning_trend', 'unknown')}")
                    
                    op_analysis = trends_data.get('operation_analysis', {})
                    print(f"   • Most Experienced: {op_analysis.get('most_experienced', 'none')}")
                    print(f"   • Least Experienced: {op_analysis.get('least_experienced', 'none')}")
                    
                    recommendations = trends_data.get('recommendations', [])
                    if recommendations:
                        print(f"\n💡 RECOMMENDATIONS:")
                        for rec in recommendations:
                            print(f"   • {rec}")
            
            return status_data
            
        except Exception as e:
            print(f"❌ Error getting memory status: {e}")
            return None
    
    async def analyze_expression_only(self, expression: str):
        """Get only perception analysis"""
        print(f"\n🔍 PERCEPTION ANALYSIS ONLY: {expression}")
        print("-" * 50)
        
        try:
            from models import PerceptionInput
            
            perception_input = PerceptionInput(expression=expression)
            perception_result = await self.cognitive_agent.perception.analyze(perception_input)
            
            print(f"✅ Validity: {perception_result.is_valid}")
            print(f"🔢 Operands: {perception_result.operands}")
            print(f"🔧 Operators: {perception_result.operators}")
            print(f"📊 Complexity: {perception_result.complexity}")
            print(f"🎯 Difficulty: {perception_result.estimated_difficulty}/10")
            print(f"📝 Notes: {perception_result.perception_notes}")
            
            if perception_result.error_message:
                print(f"⚠️  Error: {perception_result.error_message}")
            
            return perception_result
            
        except Exception as e:
            print(f"❌ Error in perception analysis: {e}")
            return None
    
    async def get_recent_history(self, limit: int = 5):
        """Get recent problem history"""
        print(f"\n📚 RECENT HISTORY (Last {limit} problems)")
        print("-" * 50)
        
        try:
            history_result = await self.session.call_tool("get_recent_history", arguments={"limit": limit})
            history_data = self.safe_parse_result(history_result)
            
            if isinstance(history_data, dict):
                recent_problems = history_data.get('recent_problems', [])
                
                if not recent_problems:
                    print("📝 No problems solved yet")
                    return
                
                for i, problem in enumerate(recent_problems, 1):
                    timestamp = problem.get('timestamp', 'Unknown time')
                    status = "✅" if problem.get('success') else "❌"
                    strategy = problem.get('strategy_used', 'Unknown')
                    confidence = problem.get('confidence')
                    
                    print(f"{i}. {status} {problem.get('problem')} → {problem.get('result')}")
                    print(f"   Strategy: {strategy}, Confidence: {confidence:.3f if confidence else 'N/A'}")
                    print(f"   Time: {timestamp}")
                    print()
                
                analysis = history_data.get('analysis', {})
                print(f"📊 Recent Success Rate: {analysis.get('success_rate', '0%')}")
                print(f"📈 Trend: {analysis.get('trend', 'unknown')}")
            
            return history_data
            
        except Exception as e:
            print(f"❌ Error getting recent history: {e}")
            return None
    
    async def reset_memory(self):
        """Reset memory"""
        print(f"\n🔄 Resetting Memory...")
        
        try:
            reset_result = await self.session.call_tool("reset_memory")
            reset_data = self.safe_parse_result(reset_result)
            
            if isinstance(reset_data, dict):
                print(f"✅ {reset_data.get('status', 'Memory reset')}")
                print(f"📝 {reset_data.get('message', '')}")
            else:
                print(f"✅ {reset_data}")
            
            return reset_data
            
        except Exception as e:
            print(f"❌ Error resetting memory: {e}")
            return None
    
    async def _store_result(self, cognitive_result: CognitiveAnalysisResult):
        """Store cognitive analysis result in MCP server"""
        
        try:
            await self.session.call_tool(
                "store_result",
                arguments={
                    "problem": cognitive_result.expression,
                    "result": str(cognitive_result.action.result),
                    "success": cognitive_result.success,
                    "strategy_used": cognitive_result.decision.selected_method,
                    "confidence": cognitive_result.action.confidence
                }
            )
        except Exception as e:
            print(f"⚠️  Warning: Failed to store result in memory: {e}")
    
    async def _show_memory_impact(self):
        """Show memory impact after solving"""
        
        try:
            print(f"\n💾 MEMORY IMPACT:")
            print("-" * 30)
            
            status_result = await self.session.call_tool("get_memory_status")
            status_data = self.safe_parse_result(status_result)
            
            if isinstance(status_data, dict):
                print(f"📊 Total Problems: {status_data.get('total_problems', 0)}")
                print(f"📈 Success Rate: {status_data.get('success_rate', '0%')}")
                
                # Get recent history to show trend
                history_result = await self.session.call_tool("get_recent_history", arguments={"limit": 3})
                history_data = self.safe_parse_result(history_result)
                
                if isinstance(history_data, dict):
                    trend = history_data.get('analysis', {}).get('trend', 'unknown')
                    print(f"📈 Recent Trend: {trend}")
        
        except Exception as e:
            print(f"⚠️  Warning: Could not show memory impact: {e}")

async def interactive_modular_session():
    """Run interactive session with modular cognitive architecture"""
    client = ModularMathClient()
    
    try:
        await client.connect()
        
        print("🧠 INTERACTIVE MODULAR MATH AGENT")
        print("=" * 80)
        print("🏗️  Modular Architecture: Perception + Memory + Decision + Action")
        print("🤖 LLM Engine: Gemini 1.5 Flash with specialized prompting")
        print("📊 Data Models: Pydantic validation and type safety")
        print("🔧 MCP Server: Tools and memory management only")
        print("")
        print("🔍 What you'll see for each problem:")
        print("   📡 PHASE 1: Perception Module (expression analysis)")
        print("   🧠 PHASE 2: Memory Module (strategy recommendations)")  
        print("   ⚡ PHASE 3: Decision Module (method selection)")
        print("   🚀 PHASE 4: Action Module (mathematical execution)")
        print("   💾 Memory Impact Analysis")
        print("")
        print("Commands:")
        print("  📝 Enter math expression → Complete modular cognitive analysis")
        print("  📝 'solve <expr>' → Simple solve without detailed analysis")
        print("  📊 'status' → Detailed memory status and performance analysis")
        print("  🔍 'analyze <expr>' → Perception module analysis only")
        print("  📚 'history [n]' → Recent problem history (default: 5)")
        print("  🔄 'reset' → Reset memory and restart learning")
        print("  ❌ 'quit' → Exit session")
        print("-" * 80)
        print("💡 TIP: Try sequence: 5+3, then 12×4, then 25+17×3")
        print("💡 Watch how each module adapts and learns!")
        
        while True:
            user_input = input("\n🤖 Enter command: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Thank you for exploring the modular cognitive architecture!")
                break
            elif user_input.lower() == 'status':
                await client.get_detailed_memory_status()
            elif user_input.lower() == 'reset':
                await client.reset_memory()
                print("🔄 All modules reset! Next problem will show fresh learning behavior.")
            elif user_input.lower().startswith('solve '):
                expr = user_input[6:].strip()
                await client.simple_solve(expr)
            elif user_input.lower().startswith('analyze '):
                expr = user_input[8:].strip()
                await client.analyze_expression_only(expr)
            elif user_input.lower().startswith('history'):
                parts = user_input.split()
                limit = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 5
                await client.get_recent_history(limit)
            elif user_input and not user_input.startswith(('status', 'reset', 'solve', 'analyze', 'history', 'quit')):
                # Complete modular cognitive analysis
                await client.solve_with_complete_cognitive_analysis(user_input)
            else:
                print("❓ Commands: <math_expr>, solve <expr>, analyze <expr>, history [n], status, reset, quit")
    
    except KeyboardInterrupt:
        print("\n👋 Session interrupted by user")
    except Exception as e:
        print(f"❌ Interactive session failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(interactive_modular_session())