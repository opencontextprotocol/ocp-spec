#!/usr/bin/env python3
"""Populate the registry with sample API entries for testing and demonstration."""

import asyncio
import json
import sys
from pathlib import Path

# Add the registry module to the path
sys.path.insert(0, str(Path(__file__).parent))

from ocp_registry.database import db_manager
from ocp_registry.service import RegistryService
from ocp_registry.models import APIRegistration, AuthConfig, APICategory, AuthType


# Sample API configurations
SAMPLE_APIS = [
    {
        "name": "github",
        "display_name": "GitHub API",
        "description": "GitHub REST API for repository management, issues, pull requests, and collaboration",
        "openapi_url": "https://api.github.com/rest/openapi.json",
        "base_url": "https://api.github.com",
        "category": APICategory.development,
        "auth_config": AuthConfig(
            type=AuthType.bearer_token,
            header_name="Authorization",
            instructions="Use 'Bearer ghp_xxxxxxxxxxxx' with a GitHub personal access token"
        ),
        "tags": ["git", "repositories", "collaboration", "version-control"],
        "documentation_url": "https://docs.github.com/en/rest",
        "rate_limit": "5000 requests/hour (authenticated)"
    },
    {
        "name": "stripe",
        "display_name": "Stripe API",
        "description": "Stripe payment processing API for handling payments, subscriptions, and billing",
        "openapi_url": "https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json",
        "base_url": "https://api.stripe.com",
        "category": APICategory.finance,
        "auth_config": AuthConfig(
            type=AuthType.bearer_token,
            header_name="Authorization",
            instructions="Use 'Bearer sk_test_xxxxxxxxxxxx' with your Stripe secret key"
        ),
        "tags": ["payments", "billing", "subscriptions", "ecommerce"],
        "documentation_url": "https://stripe.com/docs/api",
        "rate_limit": "100 requests/second"
    },
    {
        "name": "openweather",
        "display_name": "OpenWeatherMap API",
        "description": "Weather data and forecasting API with current conditions and historical data",
        "openapi_url": "https://api.openweathermap.org/data/2.5/openapi.json",
        "base_url": "https://api.openweathermap.org",
        "category": APICategory.other,
        "auth_config": AuthConfig(
            type=AuthType.api_key,
            query_param="appid",
            instructions="Sign up at openweathermap.org to get your API key"
        ),
        "tags": ["weather", "forecast", "climate", "location"],
        "documentation_url": "https://openweathermap.org/api",
        "rate_limit": "1000 requests/day (free tier)"
    },
    {
        "name": "slack",
        "display_name": "Slack API",
        "description": "Slack communication platform API for messaging, channels, and workspace management",
        "openapi_url": "https://api.slack.com/specs/openapi/v2/slack_web.json",
        "base_url": "https://slack.com/api",
        "category": APICategory.communication,
        "auth_config": AuthConfig(
            type=AuthType.bearer_token,
            header_name="Authorization",
            instructions="Use 'Bearer xoxb-xxxxxxxxxxxx' with your Slack bot token"
        ),
        "tags": ["messaging", "collaboration", "chat", "notifications"],
        "documentation_url": "https://api.slack.com/",
        "rate_limit": "Tier-based rate limits"
    },
    {
        "name": "notion",
        "display_name": "Notion API",
        "description": "Notion productivity API for managing pages, databases, and workspace content",
        "openapi_url": "https://developers.notion.com/reference/openapi.json",
        "base_url": "https://api.notion.com",
        "category": APICategory.productivity,
        "auth_config": AuthConfig(
            type=AuthType.bearer_token,
            header_name="Authorization",
            instructions="Use 'Bearer secret_xxxxxxxxxxxx' with your Notion integration token"
        ),
        "tags": ["productivity", "notes", "database", "knowledge-management"],
        "documentation_url": "https://developers.notion.com/",
        "rate_limit": "3 requests/second"
    },
    {
        "name": "httpbin",
        "display_name": "HTTPBin Testing Service",
        "description": "HTTP testing service for debugging and testing HTTP requests and responses",
        "openapi_url": "https://httpbin.org/spec.json",
        "base_url": "https://httpbin.org",
        "category": APICategory.development,
        "auth_config": AuthConfig(
            type=AuthType.none,
            instructions="No authentication required"
        ),
        "tags": ["testing", "debugging", "http", "development"],
        "documentation_url": "https://httpbin.org/",
        "rate_limit": "No rate limits"
    }
]


async def populate_registry():
    """Populate the registry with sample APIs."""
    print("🚀 Populating OCP Registry with sample APIs...")
    
    # Initialize database
    db_manager.create_tables()
    
    # Get database session
    db = next(db_manager.get_session())
    service = RegistryService(db)
    
    registered_count = 0
    failed_count = 0
    
    for api_data in SAMPLE_APIS:
        try:
            print(f"📝 Registering {api_data['display_name']}...")
            
            # Create registration object
            registration = APIRegistration(**api_data)
            
            # Register API (this will trigger validation)
            api_entry = await service.register_api(registration)
            
            print(f"   ✅ Registered '{api_entry.name}' (Status: {api_entry.status})")
            if api_entry.tool_count:
                print(f"   🔧 Discovered {api_entry.tool_count} tools")
            if api_entry.validation_error:
                print(f"   ⚠️  Validation warning: {api_entry.validation_error}")
                
            registered_count += 1
            
        except Exception as e:
            print(f"   ❌ Failed to register {api_data['display_name']}: {e}")
            failed_count += 1
    
    print(f"\n📊 Registration Summary:")
    print(f"   ✅ Successfully registered: {registered_count}")
    print(f"   ❌ Failed: {failed_count}")
    print(f"   📈 Total APIs in registry: {registered_count}")
    
    # Show some statistics
    stats = service.get_stats()
    print(f"\n📈 Registry Statistics:")
    print(f"   Total APIs: {stats.total_apis}")
    print(f"   Active APIs: {stats.active_apis}")
    print(f"   Categories: {len(stats.categories)}")
    
    db.close()
    print("\n🎉 Registry population complete!")


if __name__ == "__main__":
    asyncio.run(populate_registry())