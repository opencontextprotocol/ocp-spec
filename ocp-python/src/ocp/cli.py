#!/usr/bin/env python3
"""
OCP CLI - Command line interface for testing OCP functionality.

This provides basic commands for working with OCP context and making
test API calls to validate the implementation.
"""

import argparse
import json
import os
import sys
from typing import Optional, Dict, Any

# Add src to path for running from development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from ocp import AgentContext, wrap_api, create_ocp_headers, validate_context
    from ocp.headers import OCPHeaders
except ImportError as e:
    print(f"❌ Error importing OCP modules: {e}")
    print("Make sure you've installed the package: pip install -e .")
    sys.exit(1)


def cmd_create_context(args):
    """Create a new OCP context."""
    print("🆕 Creating OCP Context")
    print("=" * 30)
    
    context = AgentContext(
        agent_type=args.agent_type,
        user=args.user,
        workspace=args.workspace,
        current_file=args.file
    )
    
    if args.goal:
        context.update_goal(args.goal)
    
    print(f"✅ Created context: {context.context_id}")
    print(f"   Agent Type: {context.agent_type}")
    print(f"   User: {context.user or 'None'}")
    print(f"   Workspace: {context.workspace or 'None'}")
    print(f"   Goal: {context.current_goal or 'None'}")
    
    # Save context to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(context.to_dict(), f, indent=2)
        print(f"💾 Saved to: {args.output}")
    
    return context


def cmd_validate_context(args):
    """Validate an OCP context file."""
    print("✅ Validating OCP Context")
    print("=" * 30)
    
    try:
        with open(args.file, 'r') as f:
            context_data = json.load(f)
        
        # Validate the context
        result = validate_context(AgentContext.from_dict(context_data))
        
        if result.valid:
            print("✅ Context is valid!")
        else:
            print("❌ Context validation failed:")
            for error in result.errors:
                print(f"   • {error}")
            return False
        
        # Show context summary
        context = AgentContext.from_dict(context_data)
        print(f"\n📋 Context Summary:")
        print(f"   ID: {context.context_id}")
        print(f"   Type: {context.agent_type}")
        print(f"   Goal: {context.current_goal or 'None'}")
        print(f"   Interactions: {len(context.history)}")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ File not found: {args.file}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def cmd_test_headers(args):
    """Test OCP header encoding/decoding."""
    print("🧪 Testing OCP Headers")
    print("=" * 25)
    
    # Create test context
    context = AgentContext(
        agent_type="test_agent",
        user="test_user",
        workspace="test_workspace",
        current_goal="test_headers"
    )
    
    # Add some history
    context.add_interaction("test_action", "test_endpoint", "test_result")
    
    print(f"📤 Original Context ID: {context.context_id}")
    print(f"   Agent Type: {context.agent_type}")
    print(f"   History: {len(context.history)} interactions")
    
    # Encode to headers
    headers = create_ocp_headers(context)
    
    print(f"\n🔗 Generated Headers:")
    for key, value in headers.items():
        if len(value) > 50:
            print(f"   {key}: {value[:47]}...")
        else:
            print(f"   {key}: {value}")
    
    # Decode back
    decoded_context = OCPHeaders.decode_context(headers)
    
    if decoded_context:
        print(f"\n📥 Decoded Context ID: {decoded_context.context_id}")
        print(f"   Agent Type: {decoded_context.agent_type}")
        print(f"   History: {len(decoded_context.history)} interactions")
        
        # Verify round-trip
        if (context.context_id == decoded_context.context_id and 
            context.agent_type == decoded_context.agent_type and
            len(context.history) == len(decoded_context.history)):
            print("\n✅ Round-trip encoding/decoding successful!")
            return True
        else:
            print("\n❌ Round-trip verification failed!")
            return False
    else:
        print("\n❌ Failed to decode headers!")
        return False


def cmd_make_request(args):
    """Make an HTTP request with OCP context."""
    print(f"🌐 Making OCP Request to {args.url}")
    print("=" * 50)
    
    # Load context if provided
    context = None
    if args.context:
        try:
            with open(args.context, 'r') as f:
                context_data = json.load(f)
            context = AgentContext.from_dict(context_data)
            print(f"📋 Using context: {context.context_id}")
        except Exception as e:
            print(f"⚠️ Could not load context: {e}")
    
    # Create default context if none provided
    if context is None:
        context = AgentContext(
            agent_type="cli_agent",
            user="cli_user",
            current_goal="test_api_call"
        )
        print(f"📋 Created default context: {context.context_id}")
    
    # Set up authentication if provided
    auth_header = None
    if args.auth:
        if args.auth.startswith(('token ', 'Bearer ', 'Basic ')):
            auth_header = args.auth
        else:
            auth_header = f"token {args.auth}"
    
    # Make request
    try:
        import requests
        
        # Prepare headers
        headers = create_ocp_headers(context)
        if auth_header:
            headers['Authorization'] = auth_header
        
        print(f"\n📤 Request Details:")
        print(f"   Method: {args.method}")
        print(f"   URL: {args.url}")
        print(f"   OCP Headers: {len([k for k in headers.keys() if k.startswith('OCP')])}")
        
        # Make request
        response = requests.request(args.method, args.url, headers=headers)
        
        print(f"\n📥 Response:")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {len(response.headers)}")
        
        # Show response body (truncated)
        if response.text:
            body = response.text
            if len(body) > 200:
                print(f"   Body: {body[:200]}...")
            else:
                print(f"   Body: {body}")
        
        # Update context with interaction
        context.add_interaction(
            f"api_call_{args.method.lower()}",
            f"{args.method} {args.url}",
            f"HTTP {response.status_code}"
        )
        
        print(f"\n✅ Request completed! Context updated with interaction.")
        
        # Save updated context if file was provided
        if args.context and os.path.exists(args.context):
            with open(args.context, 'w') as f:
                json.dump(context.to_dict(), f, indent=2)
            print(f"💾 Updated context saved to: {args.context}")
        
        return response.status_code < 400
        
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OCP CLI - Test and work with Open Context Protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ocp create --agent-type ide_copilot --user alice --workspace myapp
  ocp validate context.json
  ocp test-headers
  ocp request GET https://api.github.com/user --auth token ghp_xxx
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create context command
    create_parser = subparsers.add_parser('create', help='Create new OCP context')
    create_parser.add_argument('--agent-type', default='generic_agent', 
                              help='Type of agent (default: generic_agent)')
    create_parser.add_argument('--user', help='User identifier')
    create_parser.add_argument('--workspace', help='Workspace name')
    create_parser.add_argument('--file', help='Current file')
    create_parser.add_argument('--goal', help='Initial goal')
    create_parser.add_argument('--output', '-o', help='Output file for context')
    
    # Validate context command
    validate_parser = subparsers.add_parser('validate', help='Validate OCP context file')
    validate_parser.add_argument('file', help='Context JSON file to validate')
    
    # Test headers command
    test_parser = subparsers.add_parser('test-headers', help='Test header encoding/decoding')
    
    # Make request command
    request_parser = subparsers.add_parser('request', help='Make HTTP request with OCP context')
    request_parser.add_argument('method', choices=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
                               help='HTTP method')
    request_parser.add_argument('url', help='URL to request')
    request_parser.add_argument('--context', '-c', help='Context JSON file to use')
    request_parser.add_argument('--auth', '-a', help='Authorization header value')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Run command
    success = False
    if args.command == 'create':
        success = cmd_create_context(args) is not None
    elif args.command == 'validate':
        success = cmd_validate_context(args)
    elif args.command == 'test-headers':
        success = cmd_test_headers(args)
    elif args.command == 'request':
        success = cmd_make_request(args)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()