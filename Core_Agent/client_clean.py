# client_clean.py - Clean Client Without .env Issues
import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Import the clean cognitive agent (no .env dependency)
from Core_Agent.agent_clean import CognitiveAgent
from Core_Agent.models import CognitiveAnalysisResult

class CleanMathClient:
    """
    Clean math client without .env dependencies
    """
    
    def __init__(self, api_key: str):
        self.server_path = "mcpserver.py"
        self.session = None
        self.cognitive_agent = None
        self.api_key = api_key
        
    async def connect(self):
        """Connect to MCP server and initialize cognitive agent"""
        print("🔧 Connecting to Modular MCP Server...")
        
        # Connect to MCP server
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_path],
            cwd="."
        )
        
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
        self.cognitive_agent = CognitiveAgent(api_key=self.api_key)
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
    
    async def solve_with_complete_cognitive_analysis(self, expression: str):
        """Complete cognitive analysis using modular architecture"""
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
    
    async def _store_result(self, cognitive_result):
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
        
        except Exception as e:
            print(f"⚠️  Warning: Could not show memory impact: {e}")

def get_api_key():
    """Get API key from user"""
    print("🔑 GEMINI API KEY SETUP")
    print("=" * 40)
    print("💡 Get your API key from: https://aistudio.google.com/app/apikey")
    print()
    
    api_key = input("Enter your Gemini API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided!")
        return None
    
    if api_key.startswith("AIza"):
        return api_key
    else:
        print("⚠️  Warning: API key should start with 'AIza'")
        return api_key

async def interactive_session():
    """Interactive session without .env dependencies"""
    
    # Get API key from user
    api_key = get_api_key()
    if not api_key:
        print("❌ Cannot proceed without API key!")
        return
    
    client = CleanMathClient(api_key)
    
    try:
        await client.connect()
        
        print("\n🧠 CLEAN MODULAR MATH AGENT")
        print("=" * 50)
        print("🚀 No .env file needed - API key provided directly")
        print("🏗️  Modular Architecture: Perception + Memory + Decision + Action")
        print("🤖 LLM Engine: Gemini 1.5 Flash")
        print("")
        print("Commands:")
        print("  📝 Enter math expression → Complete cognitive analysis")
        print("  📝 'solve <expr>' → Simple solve")
        print("  ❌ 'quit' → Exit")
        print("-" * 50)
        
        while True:
            user_input = input("\n🤖 Enter command: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower().startswith('solve '):
                expr = user_input[6:].strip()
                await client.simple_solve(expr)
            elif user_input:
                await client.solve_with_complete_cognitive_analysis(user_input)
            else:
                print("❓ Enter a math expression or 'quit'")
    
    except KeyboardInterrupt:
        print("\n👋 Session interrupted")
    except Exception as e:
        print(f"❌ Session failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.disconnect()

async def quick_test():
    """Quick test function"""
    
    print("🧪 QUICK TEST MODE")
    print("=" * 30)
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        return
    
    try:
        # Test just the cognitive agent without MCP server
        print("\n🧠 Testing Cognitive Agent...")
        agent = CognitiveAgent(api_key=api_key)
        
        # Simple test
        print("\n🧮 Testing: 5 + 3")
        result = await agent.quick_solve("5 + 3")
        
        print(f"\n✅ Test Result: {result.result}")
        print("🎉 Cognitive Agent working!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        asyncio.run(quick_test())
    else:
        asyncio.run(interactive_session())python client_clean.py test