# standalone_test.py - Test Without MCP Server
import asyncio
import os

# Import the clean cognitive agent
from Core_Agent.agent_clean import CognitiveAgent

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
    
    return api_key

async def test_cognitive_phases():
    """Test each cognitive phase individually"""
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        return
    
    try:
        print("\n🧠 STANDALONE COGNITIVE AGENT TEST")
        print("=" * 60)
        print("🚀 Testing without MCP server dependency")
        
        # Initialize cognitive agent
        print("\n🔧 Initializing Cognitive Agent...")
        agent = CognitiveAgent(api_key=api_key)
        
        # Test 1: Quick solve
        print("\n" + "="*50)
        print("🧪 TEST 1: Quick Solve")
        print("="*50)
        
        # test_expressions = ["5 + 3", "12 × 4", "25 + 17 × 3"]
        test_expr = input("🧮 Enter a math expression: ").strip()
        print(f"\n🧮 Testing: {test_expr}")
        result = await agent.quick_solve(test_expr)

        print(f"📊 Result: {result.result}")
        print(f"📊 Confidence: {result.confidence:.3f}")
        print(f"📊 Steps: {len(result.steps)} shown")
            
        success = not str(result.result).startswith("Error")
        print(f"🏆 Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        # Test 2: Full cognitive analysis
        print("\n" + "="*50)
        print("🧪 TEST 2: Full Cognitive Analysis")
        print("="*50)
        
        # test_expr = "25 + 17 × 3"
        test_expr = input("🧮 Enter expression for full cognitive analysis: ").strip()

        memory_summary = "No previous experience. This is a fresh start."
        
        print(f"\n🧮 Full Analysis: {test_expr}")
        full_result = await agent.analyze(test_expr, memory_summary)
        
        if full_result:
            print(f"\n✅ FULL ANALYSIS SUCCESS!")
            print(f"📊 Expression: {full_result.expression}")
            print(f"📊 Final Result: {full_result.action.result}")
            print(f"📊 Overall Success: {full_result.success}")
            print(f"📊 Perception Complexity: {full_result.perception.complexity}")
            print(f"📊 Memory Strategy: {full_result.memory.strategy_recommendation}")
            print(f"📊 Decision Method: {full_result.decision.selected_method}")
            print(f"📊 Action Confidence: {full_result.action.confidence:.3f}")
        else:
            print("❌ Full analysis failed!")
        
        # Test 3: Individual phase testing
        print("\n" + "="*50)
        print("🧪 TEST 3: Individual Phase Testing")
        print("="*50)
        
        # test_expr = "100 ÷ 4"
        test_expr = input("📡 Enter expression for individual phase testing: ").strip()

        
        # Test perception
        print(f"\n📡 Testing Perception Phase: {test_expr}")
        from models import PerceptionInput
        perception_input = PerceptionInput(expression=test_expr)
        perception_result = await agent.perception.analyze(perception_input)
        
        print(f"✅ Perception Valid: {perception_result.is_valid}")
        print(f"📊 Complexity: {perception_result.complexity}")
        print(f"🎯 Difficulty: {perception_result.estimated_difficulty}/10")
        
        # Test memory consultation
        print(f"\n🧠 Testing Memory Phase:")
        from models import MemoryInput
        memory_input = MemoryInput(
            expression=test_expr,
            perception_data=perception_result,
            memory_summary="Agent has solved 3 problems with 100% success rate. Experienced with arithmetic operations."
        )
        memory_result = await agent.memory.consult(memory_input)
        
        print(f"🎯 Strategy Recommendation: {memory_result.strategy_recommendation}")
        print(f"📈 Confidence Modifier: {memory_result.confidence_modifier:.2f}")
        
        # Test decision making
        print(f"\n⚡ Testing Decision Phase:")
        from models import DecisionInput
        decision_input = DecisionInput(
            expression=test_expr,
            perception_data=perception_result,
            memory_data=memory_result
        )
        decision_result = await agent.decision.decide(decision_input)
        
        print(f"🎯 Selected Method: {decision_result.selected_method}")
        print(f"📊 Final Confidence: {decision_result.final_confidence:.3f}")
        print(f"🔍 Verification Level: {decision_result.verification_level}")
        
        # Test action execution
        print(f"\n🚀 Testing Action Phase:")
        from models import ActionInput
        action_input = ActionInput(
            expression=test_expr,
            perception_data=perception_result,
            decision_data=decision_result
        )
        action_result = await agent.action.execute(action_input)
        
        print(f"📊 Action Result: {action_result.result}")
        print(f"🎯 Action Confidence: {action_result.confidence:.3f}")
        print(f"📝 Steps Count: {len(action_result.steps)}")
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS COMPLETED!")
        print("✅ Cognitive Agent is working correctly!")
        print("💡 You can now use the full system with MCP server")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def interactive_standalone():
    """Interactive mode without MCP server"""
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        return
    
    try:
        print("\n🧠 STANDALONE INTERACTIVE MODE")
        print("=" * 50)
        print("🚀 No MCP server needed - pure cognitive agent")
        print("📝 Commands:")
        print("   • Enter math expression for analysis")
        print("   • 'quick <expr>' for quick solve")
        print("   • 'quit' to exit")
        print("-" * 50)
        
        # Initialize agent
        agent = CognitiveAgent(api_key=api_key)
        
        while True:
            user_input = input("\n🤖 Enter command: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower().startswith('quick '):
                expr = user_input[6:].strip()
                result = await agent.quick_solve(expr)
                print(f"📊 Result: {result.result}")
            elif user_input:
                memory_summary = "Fresh start - no previous experience."
                result = await agent.analyze(user_input, memory_summary)
                if result:
                    print(f"📊 Final Result: {result.action.result}")
                    print(f"🏆 Success: {'✅' if result.success else '❌'}")
            else:
                print("❓ Enter a math expression or 'quit'")
    
    except KeyboardInterrupt:
        print("\n👋 Session interrupted")
    except Exception as e:
        print(f"❌ Session failed: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'interactive':
        asyncio.run(interactive_standalone())
    else:
        asyncio.run(test_cognitive_phases())