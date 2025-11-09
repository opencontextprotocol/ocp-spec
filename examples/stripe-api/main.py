"""
Stripe API Integration with OCP

Demonstrates OCP's context-aware API integration with payment processing APIs.
Shows automatic API discovery, tool validation, and persistent context management.
"""

import os
from ocp import OCPAgent, wrap_api

def main():
    """
    Demo of OCP agent with Stripe API integration.
    """
    print("💳 OCP + Stripe API Demo")
    print("=" * 40)
    
    # Create Stripe agent using generic OCP approach
    print("\n📋 Creating Stripe agent...")
    stripe_agent = OCPAgent(
        agent_type="payment_processor",
        workspace="stripe-demo", 
        agent_goal="Process payments and manage customer data"
    )
    
    # Register Stripe API
    print("🔗 Registering Stripe API...")
    try:
        api_spec = stripe_agent.register_api(
            name="stripe",
            spec_url="https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json"
        )
        print(f"✅ Stripe API registered: {api_spec.title} v{api_spec.version}")
    except Exception as e:
        print(f"⚠️  Stripe API registration failed: {e}")
        print("   (This indicates a network issue or invalid OpenAPI spec)")
        return
    
    # List discovered tools
    tools = stripe_agent.list_tools("stripe")
    print(f"🔧 Discovered {len(tools)} Stripe API tools")
    
    # Search for payment tools
    payment_tools = stripe_agent.search_tools("payment")
    print(f"💰 Found {len(payment_tools)} payment-related tools:")
    for tool in payment_tools[:5]:  # Show first 5
        print(f"   • {tool.name}: {tool.description[:50]}...")
    
    # Search for customer tools
    customer_tools = stripe_agent.search_tools("customer")
    print(f"👥 Found {len(customer_tools)} customer-related tools:")
    for tool in customer_tools[:3]:  # Show first 3
        print(f"   • {tool.name}: {tool.description[:50]}...")
    
    # Show tool documentation
    if payment_tools:
        print(f"\n📖 Documentation for '{payment_tools[0].name}':")
        doc = stripe_agent.get_tool_documentation(payment_tools[0].name)
        print(doc[:300] + "..." if len(doc) > 300 else doc)
    
    # Show context tracking
    print(f"\n🧠 Agent Context:")
    print(f"   Session ID: {stripe_agent.context.context_id}")
    print(f"   Goal: {stripe_agent.context.current_goal}")
    print(f"   Interactions: {len(stripe_agent.context.history)}")
    
    # Demonstrate OCP HTTP client
    print(f"\n🌐 OCP HTTP Client Demo:")
    stripe_http = wrap_api(
        "https://api.stripe.com", 
        stripe_agent.context,
        headers={"Authorization": f"Bearer {os.getenv('STRIPE_SECRET_KEY', 'sk_test_your_key_here')}"}
    )
    print("   • Context-aware HTTP client created")
    print("   • Automatic OCP headers added to requests")
    print("   • All interactions tracked in agent context")
    
    print(f"\n✨ OCP Advantages Demonstrated:")
    print(f"   • Zero infrastructure setup")
    print(f"   • Automatic API discovery")
    print(f"   • Persistent context tracking") 
    print(f"   • Context-aware API interactions")
    print(f"   • Works with any OpenAPI spec")
    print(f"   • Generic framework - no hardcoded APIs")

if __name__ == "__main__":
    main()