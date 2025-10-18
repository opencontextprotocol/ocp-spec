"""
Stripe API Integration with OCP

Demonstrates OCP's context-aware API integration with payment processing APIs.
Shows automatic API discovery, tool validation, and persistent context management.
"""

import os
from ocp import OCPAgent, create_stripe_agent

def main():
    """
    Demo of OCP agent with Stripe API integration.
    """
    print("💳 OCP + Stripe API Demo")
    print("=" * 40)
    
    # Create Stripe agent
    print("\n📋 Creating Stripe agent...")
    stripe_agent = create_stripe_agent()
    stripe_agent.update_goal("Process payments and manage customer data")
    
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
    
    print(f"\n✨ OCP Advantages Demonstrated:")
    print(f"   • Zero infrastructure setup")
    print(f"   • Automatic API discovery")
    print(f"   • Persistent context tracking") 
    print(f"   • Context-aware API interactions")
    print(f"   • Works with any OpenAPI spec")

if __name__ == "__main__":
    main()