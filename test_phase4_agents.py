#!/usr/bin/env python3
"""
Phase 4 Testing - Multi-Agent Library
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_agent_library_loading():
    """Test loading the agent library"""
    print("\n" + "="*60)
    print("TEST: Agent Library Loading")
    print("="*60)
    
    try:
        from aurelius.agents.agent_library import library
        
        print(f"✅ PASS | Loaded {len(library)} agents")
        print(f"   └─ Available agents:")
        for name in library.keys():
            print(f"      • {name}")
        return True
        
    except Exception as e:
        print(f"❌ FAIL | Agent Library Loading")
        print(f"   └─ Error: {e}")
        return False


def test_agent_profiles():
    """Test that each agent has required fields"""
    print("\n" + "="*60)
    print("TEST: Agent Profiles Validation")
    print("="*60)
    
    try:
        from aurelius.agents.agent_library import library
        
        required_fields = ['name', 'profile']
        results = {}
        
        for name, agent in library.items():
            has_required = all(field in agent for field in required_fields)
            has_toolkits = 'toolkits' in agent
            
            if has_required:
                toolkit_count = len(agent.get('toolkits', []))
                results[name] = {
                    'valid': True,
                    'has_tools': has_toolkits,
                    'tool_count': toolkit_count
                }
            else:
                results[name] = {'valid': False}
        
        all_valid = all(r['valid'] for r in results.values())
        
        print(f"{'✅ PASS' if all_valid else '❌ FAIL'} | Agent Profiles")
        for name, info in results.items():
            tool_info = f"({info['tool_count']} tools)" if info.get('has_tools') else "(no tools)"
            status = "✓" if info['valid'] else "✗"
            print(f"   {status} {name} {tool_info}")
        
        return all_valid
        
    except Exception as e:
        print(f"❌ FAIL | Agent Profiles Validation")
        print(f"   └─ Error: {e}")
        return False


def test_market_analyst_tools():
    """Test Market Analyst agent's tools"""
    print("\n" + "="*60)
    print("TEST: Market Analyst Tools")
    print("="*60)
    
    try:
        from aurelius.agents.agent_library import library
        
        market_analyst = library.get('Market_Analyst')
        if not market_analyst:
            print("❌ FAIL | Market_Analyst not found")
            return False
        
        tools = market_analyst.get('toolkits', [])
        print(f"✅ PASS | Market Analyst has {len(tools)} tools")
        
        for tool in tools:
            tool_name = tool.__name__ if hasattr(tool, '__name__') else str(tool)
            print(f"   └─ {tool_name}")
        
        return len(tools) > 0
        
    except Exception as e:
        print(f"❌ FAIL | Market Analyst Tools")
        print(f"   └─ Error: {e}")
        return False


def test_expert_investor_tools():
    """Test Expert Investor agent's tools"""
    print("\n" + "="*60)
    print("TEST: Expert Investor Tools")
    print("="*60)
    
    try:
        from aurelius.agents.agent_library import library
        
        expert_investor = library.get('Expert_Investor')
        if not expert_investor:
            print("❌ FAIL | Expert_Investor not found")
            return False
        
        tools = expert_investor.get('toolkits', [])
        print(f"✅ PASS | Expert Investor has {len(tools)} tools")
        
        for tool in tools:
            if hasattr(tool, '__name__'):
                tool_name = tool.__name__
            elif hasattr(tool, '__class__'):
                tool_name = tool.__class__.__name__
            else:
                tool_name = str(tool)
            print(f"   └─ {tool_name}")
        
        return len(tools) > 0
        
    except Exception as e:
        print(f"❌ FAIL | Expert Investor Tools")
        print(f"   └─ Error: {e}")
        return False


def test_agent_profile_content():
    """Test that agent profiles have meaningful content"""
    print("\n" + "="*60)
    print("TEST: Agent Profile Content")
    print("="*60)
    
    try:
        from aurelius.agents.agent_library import library
        
        min_profile_length = 50
        results = {}
        
        for name, agent in library.items():
            profile = agent.get('profile', '')
            profile_length = len(profile)
            is_valid = profile_length >= min_profile_length
            results[name] = {
                'length': profile_length,
                'valid': is_valid
            }
        
        all_valid = all(r['valid'] for r in results.values())
        
        print(f"{'✅ PASS' if all_valid else '❌ FAIL'} | Profile Content Check")
        for name, info in results.items():
            status = "✓" if info['valid'] else "✗"
            print(f"   {status} {name}: {info['length']} chars")
        
        return all_valid
        
    except Exception as e:
        print(f"❌ FAIL | Agent Profile Content")
        print(f"   └─ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "🔬 PHASE 4 TESTING: MULTI-AGENT LIBRARY".center(60))
    print("=" * 60)
    
    results = {
        "Agent Library Loading": test_agent_library_loading(),
        "Agent Profiles Validation": test_agent_profiles(),
        "Market Analyst Tools": test_market_analyst_tools(),
        "Expert Investor Tools": test_expert_investor_tools(),
        "Agent Profile Content": test_agent_profile_content(),
    }
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} | {test}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All Phase 4 Agent tests passed!")
    else:
        print("⚠️  Some tests failed - review output above")

