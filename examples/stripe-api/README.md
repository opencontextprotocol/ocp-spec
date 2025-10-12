# Stripe API with OCP

This example demonstrates how payment processing with Stripe can work with OCP context, enabling AI agents to handle financial transactions while maintaining session continuity.

## Key Benefits

1. **No Stripe Integration Changes**: Use existing Stripe API endpoints
2. **Context-Aware Payments**: Track user payment history and preferences
3. **AI Agent Ready**: Easy integration with LLMs for payment workflows
4. **Secure by Default**: Uses Stripe's existing security model
5. **⚠️ Current Status**: Stripe doesn't read OCP headers yet - context is managed client-side

## How It Works Today vs Future

### **Current Reality (Phase 1)**
- Stripe API **ignores** OCP headers (which is fine!)
- Client (your agent) **manages context** locally  
- Payment history and user preferences stored in OCP context
- Context flows between payment operations

### **Future Enhancement (Phase 2)**
- Stripe could optionally **read** OCP headers
- Provide **personalized payment experiences** based on context
- Example: Auto-suggest payment methods based on previous transactions in the session

## Example: Payment Processing Flow

### 1. Create Customer with Context

```bash
curl -X POST https://api.stripe.com/v1/customers \
  -H "Authorization: Bearer sk_test_..." \
  -H "OCP-Context-ID: payment-session-123" \
  -H "OCP-User: alice" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=alice@example.com&name=Alice Johnson"
```

### 2. Create Payment Intent with Preserved Context

```bash
curl -X POST https://api.stripe.com/v1/payment_intents \
  -H "Authorization: Bearer sk_test_..." \
  -H "OCP-Context-ID: payment-session-123" \
  -H "OCP-Session: eyJwYXltZW50X2hpc3RvcnkiOltdLCJjdXN0b21lcl9pZCI6ImN1c19hYmMxMjMifQ==" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "amount=2000&currency=usd&customer=cus_abc123"
```

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