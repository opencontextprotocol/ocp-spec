"""
Stripe API with OCP (Open Context Protocol) Integration

This example demonstrates how payment processing with Stripe can work with OCP context,
enabling AI agents to handle financial transactions while maintaining session continuity.

Key Benefits:
1. No Stripe Integration Changes: Use existing Stripe API endpoints
2. Context-Aware Payments: Track user payment history and preferences  
3. AI Agent Ready: Easy integration with LLMs for payment workflows
4. Secure by Default: Uses Stripe's existing security model

Example curl commands:

# Create Customer with Context
curl -X POST https://api.stripe.com/v1/customers \
  -H "Authorization: Bearer sk_test_..." \
  -H "OCP-Context-ID: payment-session-123" \
  -H "OCP-User: alice" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=alice@example.com&name=Alice Johnson"

# Create Payment Intent with Preserved Context  
curl -X POST https://api.stripe.com/v1/payment_intents \
  -H "Authorization: Bearer sk_test_..." \
  -H "OCP-Context-ID: payment-session-123" \
  -H "OCP-Session: eyJwYXltZW50X2hpc3RvcnkiOltdLCJjdXN0b21lcl9pZCI6ImN1c19hYmMxMjMifQ==" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "amount=2000&currency=usd&customer=cus_abc123"
"""
import stripe
import base64
import json
from datetime import datetime
from typing import Dict, List, Optional

class StripeOCP:
    """Stripe API client with OCP context support."""
    
    def __init__(self, api_key: str, context_id: str = None):
        stripe.api_key = api_key
        self.context = {
            "context_id": context_id or f"stripe-{datetime.now().isoformat()}",
            "user": None,
            "api_specs": ["https://raw.githubusercontent.com/stripe/openapi/refs/heads/master/openapi/spec3.json"],
            "session": {
                "history": [],
                "state": {
                    "payment_methods": [],
                    "customers": [],
                    "transactions": []
                }
            },
            "auth": {"tokens": {"stripe": api_key}},
            "created_at": datetime.now().isoformat()
        }
    
    def _add_interaction(self, action: str, details: Dict):
        """Add interaction to context history."""
        self.context["session"]["history"].append({
            "role": "payment_system",
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def create_customer(self, email: str, name: str = None, **kwargs) -> Dict:
        """Create a new customer with OCP context."""
        customer_data = {
            "email": email,
            "metadata": {
                "ocp_context_id": self.context["context_id"],
                "ocp_user": self.context.get("user", "")
            }
        }
        
        if name:
            customer_data["name"] = name
        customer_data.update(kwargs)
        
        customer = stripe.Customer.create(**customer_data)
        
        # Update context
        self.context["session"]["state"]["customers"].append({
            "id": customer.id,
            "email": email,
            "created": customer.created
        })
        
        self._add_interaction("create_customer", {
            "customer_id": customer.id,
            "email": email
        })
        
        return customer
    
    def create_payment_intent(self, amount: int, currency: str = "usd", 
                            customer: str = None, **kwargs) -> Dict:
        """Create payment intent with context tracking."""
        payment_data = {
            "amount": amount,
            "currency": currency,
            "metadata": {
                "ocp_context_id": self.context["context_id"],
                "ocp_user": self.context.get("user", "")
            }
        }
        
        if customer:
            payment_data["customer"] = customer
        payment_data.update(kwargs)
        
        intent = stripe.PaymentIntent.create(**payment_data)
        
        # Update context
        self.context["session"]["state"]["transactions"].append({
            "id": intent.id,
            "amount": amount,
            "currency": currency,
            "status": intent.status,
            "created": intent.created
        })
        
        self._add_interaction("create_payment_intent", {
            "payment_intent_id": intent.id,
            "amount": amount,
            "currency": currency,
            "customer": customer
        })
        
        return intent
    
    def list_payment_methods(self, customer: str, type: str = "card") -> List[Dict]:
        """List payment methods for customer."""
        methods = stripe.PaymentMethod.list(customer=customer, type=type)
        
        # Update context
        method_data = [{"id": pm.id, "type": pm.type} for pm in methods.data]
        self.context["session"]["state"]["payment_methods"] = method_data
        
        self._add_interaction("list_payment_methods", {
            "customer": customer,
            "count": len(methods.data)
        })
        
        return methods
    
    def get_payment_history(self) -> List[Dict]:
        """Get payment history from context."""
        return self.context["session"]["state"]["transactions"]
    
    def get_context_summary(self) -> Dict:
        """Get summary of context state."""
        state = self.context["session"]["state"]
        return {
            "context_id": self.context["context_id"],
            "user": self.context.get("user"),
            "customers_count": len(state["customers"]),
            "transactions_count": len(state["transactions"]),
            "payment_methods_count": len(state["payment_methods"]),
            "total_interactions": len(self.context["session"]["history"])
        }


def demo_stripe_ocp():
    """Demo Stripe API with OCP context."""
    
    # Initialize with Stripe test key
    api_key = "sk_test_your_key_here"  # Replace with real test key
    stripe_ocp = StripeOCP(api_key, context_id="payment-demo-123")
    stripe_ocp.context["user"] = "alice"
    
    print("=== Stripe API with OCP Demo ===\n")
    
    try:
        # Create customer
        print("1. Creating customer...")
        customer = stripe_ocp.create_customer(
            email="alice@example.com",
            name="Alice Johnson"
        )
        print(f"   Customer created: {customer.id}")
        
        # Create payment intent
        print("\n2. Creating payment intent...")
        intent = stripe_ocp.create_payment_intent(
            amount=2000,  # $20.00
            currency="usd",
            customer=customer.id,
            description="OCP Demo Payment"
        )
        print(f"   Payment Intent: {intent.id} (${intent.amount/100:.2f})")
        
        # Show context summary
        print("\n3. Context Summary:")
        summary = stripe_ocp.get_context_summary()
        for key, value in summary.items():
            print(f"   {key}: {value}")
        
        # Show interaction history
        print("\n4. Interaction History:")
        for i, interaction in enumerate(stripe_ocp.context["session"]["history"]):
            print(f"   {i+1}. {interaction['action']}: {interaction['details']}")
        
        print("\n✅ Demo completed successfully!")
        return stripe_ocp
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Make sure to set a valid Stripe test key!")
        return None


class StripeAI:
    """AI agent for Stripe operations using OCP."""
    
    def __init__(self, stripe_key: str, openai_key: str):
        self.stripe = StripeOCP(stripe_key)
        # self.openai = OpenAI(api_key=openai_key)  # Uncomment if using OpenAI
    
    def process_payment_request(self, user_message: str, user_email: str):
        """Process natural language payment requests."""
        
        # Example: "Charge Alice $50 for consulting services"
        # This would typically use an LLM to parse the intent
        
        # For demo, extract simple patterns
        import re
        
        amount_match = re.search(r'\$(\d+(?:\.\d{2})?)', user_message)
        if not amount_match:
            return "I couldn't find an amount in your request."
        
        amount_dollars = float(amount_match.group(1))
        amount_cents = int(amount_dollars * 100)
        
        # Create customer if needed
        try:
            customer = self.stripe.create_customer(email=user_email)
            intent = self.stripe.create_payment_intent(
                amount=amount_cents,
                customer=customer.id,
                description=f"Payment from: {user_message}"
            )
            
            return {
                "success": True,
                "message": f"Created payment intent for ${amount_dollars:.2f}",
                "payment_intent_id": intent.id,
                "context": self.stripe.get_context_summary()
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Payment failed: {str(e)}"
            }


if __name__ == "__main__":
    # Run the demo
    demo_stripe_ocp()