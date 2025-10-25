# Stripe API with OCP

This example demonstrates using the Stripe API with OCP context headers for persistent payment agent sessions.

## Overview

- **API Registration**: Automatically discovers Stripe API endpoints from OpenAPI specification
- **Context Tracking**: Maintains payment session state across multiple API interactions
- **Tool Discovery**: Finds and validates available Stripe operations
- **HTTP Client**: Context-aware requests with automatic header injection

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Stripe Secret Key**
   ```bash
   export STRIPE_SECRET_KEY="sk_test_your_key_here"
   ```

3. **Run Example**
   ```bash
   python main.py
   ```

## Code Structure

```python
from ocp import OCPAgent, wrap_api

# Create agent with context
agent = OCPAgent(
    agent_type="payment_processor",
    workspace="stripe-demo", 
    agent_goal="Process payments and manage customer data"
)

# Register Stripe API from OpenAPI spec
api_spec = agent.register_api(
    name="stripe",
    spec_url="https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json"
)

# Create context-aware HTTP client
stripe_client = wrap_api(
    "https://api.stripe.com", 
    agent.context,
    auth="Bearer sk_test_your_key_here"
)
```

## Features Demonstrated

- **OpenAPI Discovery**: Automatic tool extraction from Stripe's OpenAPI specification
- **Context Persistence**: Payment session state maintained across API calls
- **Tool Validation**: Schema-based validation of payment operations
- **HTTP Enhancement**: Standard HTTP clients enhanced with OCP headers
- **Session Tracking**: Persistent payment history and customer interactions

## HTTP Headers

OCP adds these headers to all Stripe API requests:

```
OCP-Context-ID: ocp-12345678
OCP-Agent-Type: payment_processor
OCP-Version: 1.0
OCP-Goal: Process payments and manage customer data
OCP-Session: eyJjb250ZXh0X2lkIjoi...
```

## Requirements

- Python 3.8+
- Stripe test secret key
- Internet connection for OpenAPI spec retrieval

## Python Usage

```python
from stripe_ocp import StripeOCP

# Initialize with your Stripe test key
stripe = StripeOCP("sk_test_your_key_here")
stripe.context["user"] = "alice"

# Create customer with context tracking
customer = stripe.create_customer(
    email="alice@example.com",
    name="Alice Johnson"
)

# Create payment intent - context flows automatically  
intent = stripe.create_payment_intent(
    amount=2000,  # $20.00
    currency="usd",
    customer=customer.id,
    description="OCP Demo Payment"
)

# Check context state
summary = stripe.get_context_summary()
print(f"Context: {summary}")
```

## AI Agent Integration

```python
from stripe_ocp import StripeAI

# AI agent that can process payment requests
ai = StripeAI(stripe_key="sk_test_...", openai_key="sk-...")

# Natural language payment processing
result = ai.process_payment_request(
    "Charge Alice $50 for consulting services",
    user_email="alice@example.com"
)

print(result)
# {
#   "success": True,
#   "message": "Created payment intent for $50.00", 
#   "payment_intent_id": "pi_abc123",
#   "context": {...}
# }
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Get a Stripe test key from [dashboard.stripe.com](https://dashboard.stripe.com)

3. **Bonus**: Check out Stripe's actual OpenAPI spec that this example references:
   ```bash
   curl https://raw.githubusercontent.com/stripe/openapi/refs/heads/master/openapi/spec3.json
   ```

4. Run the demo:
   ```python
   python stripe_ocp.py
   ```

## Context Flow

The OCP context tracks:
- **Payment History**: All transactions in session
- **Customer Data**: Created customers and their details  
- **Payment Methods**: Stored payment methods
- **Interaction Log**: Complete audit trail of operations

This enables AI agents to:
- Remember previous payments in the conversation
- Provide personalized payment experiences
- Handle complex multi-step payment workflows
- Maintain state across multiple API calls

## Security Notes

- Always use Stripe test keys for development
- OCP context includes payment metadata but not sensitive card details
- Stripe's security model remains unchanged
- Context can be encrypted before transmission if needed

## Benefits Over Traditional Integration

| Traditional Approach | OCP Approach |
|---------------------|--------------|
| ❌ Stateless API calls | ✅ Context-aware transactions |
| ❌ No session continuity | ✅ Persistent session state |
| ❌ Manual history tracking | ✅ Automatic interaction logging |
| ❌ Complex AI integration | ✅ Simple AI agent workflows |