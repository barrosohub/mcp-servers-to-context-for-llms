# -*- coding: utf-8 -*-
import asyncio
import json
import requests
import time
from datetime import datetime

def test_health_endpoint():
    """Tests the health check endpoint"""
    print("🧪 Testing health endpoint...")
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Health check: {data['status']}")
        print(f"📊 Server: {data['server']} v{data['version']}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False



def test_mcp_endpoint(service: str, tool: str, payload: dict):
    """Tests a generic MCP endpoint."""
    print(f"🧪 Testing MCP endpoint: {service}/{tool}...")
    url = f"http://127.0.0.1:8000/mcp/{service}/{tool}"
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"✅ {service.capitalize()} {tool.capitalize()} successful: {data.get('status')}")
        return True
    except Exception as e:
        print(f"❌ {service.capitalize()} {tool.capitalize()} failed: {e}")
        return False

def test_all_endpoints():
    """Runs all tests in sequence"""
    print("🚀 Starting FastAPI MCP test suite")
    print("=" * 50)
    
    # Health check test
    if not test_health_endpoint():
        print("⚠️  Server is not responding. Run: python main.py")
        return False
    
    print("\n" + "-" * 50)
    
    # DeepWiki tests
    deepwiki_tools_ok = test_mcp_endpoint("deepwiki", "tools", {})
    deepwiki_analyze_ok = test_mcp_endpoint("deepwiki", "analyze", {"repository": "test/repo"})

    print("\n" + "-" * 50)

    # Context7 tests
    context7_tools_ok = test_mcp_endpoint("context7", "tools", {})
    context7_docs_ok = test_mcp_endpoint("context7", "docs", {"library": "/test/library"})
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"   Health Check: {'✅' if True else '❌'}")
    print(f"   DeepWiki Tools: {'✅' if deepwiki_tools_ok else '❌'}")
    print(f"   DeepWiki Analyze: {'✅' if deepwiki_analyze_ok else '❌'}")
    print(f"   Context7 Tools: {'✅' if context7_tools_ok else '❌'}")
    print(f"   Context7 Docs: {'✅' if context7_docs_ok else '❌'}")
    
    all_ok = deepwiki_tools_ok and deepwiki_analyze_ok and context7_tools_ok and context7_docs_ok
    print(f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if all_ok else '❌ SOME TESTS FAILED'}")
    
    return all_ok

def interactive_test():
    """Interactive test to choose specific endpoints"""
    print("🚀 FastAPI MCP - Interactive Test")
    print("=" * 40)
    print("1. Health Check")
    print("2. DeepWiki - List Tools")
    print("3. DeepWiki - Analyze Repo")
    print("4. Context7 - List Tools")
    print("5. Context7 - Get Library Docs")
    print("6. Run All Tests")
    print("7. Exit")
    print("=" * 40)
    
    while True:
        try:
            choice = input("\nChoose an option (1-7): ").strip()
            
            if choice == '1':
                test_health_endpoint()
            elif choice == '2':
                test_mcp_endpoint("deepwiki", "tools", {})
            elif choice == '3':
                test_mcp_endpoint("deepwiki", "analyze", {"repository": "test/repo"})
            elif choice == '4':
                test_mcp_endpoint("context7", "tools", {})
            elif choice == '5':
                test_mcp_endpoint("context7", "docs", {"library": "/test/library"})
            elif choice == '6':
                test_all_endpoints()
            elif choice == '7':
                print("👋 Exiting tests...")
                break
            else:
                print("❌ Invalid option")
                
        except KeyboardInterrupt:
            print("\n🛑 Tests interrupted by user")
            break
        except EOFError:
            print("\n👋 Exiting tests...")
            break

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Automatic mode
        test_all_endpoints()
    else:
        # Interactive mode
        interactive_test()