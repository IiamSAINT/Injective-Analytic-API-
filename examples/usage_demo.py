#!/usr/bin/env python3
"""
Example Usage Script for Injective Market Intelligence API

This script demonstrates how to interact with the API endpoints.
Make sure the API is running locally before executing this script:
    uvicorn app.main:app --reload
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)


def format_json(data: dict) -> str:
    """Format JSON for display."""
    return json.dumps(data, indent=2, default=str)


def example_health_check():
    """Example: Check API health."""
    print_section("Health Check")
    
    # Basic health
    response = requests.get(f"{BASE_URL}/api/v1/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {format_json(response.json())}")
    
    # Injective connectivity
    print("\n--- Injective Connectivity ---")
    response = requests.get(f"{BASE_URL}/api/v1/health/injective")
    print(f"Response: {format_json(response.json())}")


def example_list_markets():
    """Example: List all markets."""
    print_section("List Markets")
    
    # Get all markets
    response = requests.get(f"{BASE_URL}/api/v1/markets")
    data = response.json()
    
    print(f"Total Markets: {data['total']}")
    print(f"Spot Markets: {data['spot_count']}")
    print(f"Derivative Markets: {data['derivative_count']}")
    
    # Show first 5 markets
    print("\n--- First 5 Markets ---")
    for market in data['markets'][:5]:
        print(f"  • {market['ticker']} ({market['market_type']}) - ID: {market['market_id'][:20]}...")
    
    # Filter by type
    print("\n--- Spot Markets Only ---")
    response = requests.get(f"{BASE_URL}/api/v1/markets", params={"market_type": "spot"})
    data = response.json()
    print(f"Spot Markets Count: {data['total']}")


def example_get_market_detail(market_id: str):
    """Example: Get market details."""
    print_section(f"Market Detail: {market_id[:20]}...")
    
    response = requests.get(f"{BASE_URL}/api/v1/markets/{market_id}")
    
    if response.status_code == 200:
        print(f"Response: {format_json(response.json())}")
    else:
        print(f"Error: {response.status_code} - {response.json()}")


def example_get_orderbook(market_id: str):
    """Example: Get orderbook."""
    print_section(f"Orderbook: {market_id[:20]}...")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/markets/{market_id}/orderbook",
        params={"depth": 5}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Market ID: {data['market_id'][:20]}...")
        print(f"Timestamp: {data['timestamp']}")
        print(f"Spread: {data.get('spread', 'N/A')}")
        print(f"Mid Price: {data.get('mid_price', 'N/A')}")
        
        print("\n--- Top 3 Bids ---")
        for bid in data['bids'][:3]:
            print(f"  Price: {bid['price']:.6f}  Qty: {bid['quantity']:.4f}")
        
        print("\n--- Top 3 Asks ---")
        for ask in data['asks'][:3]:
            print(f"  Price: {ask['price']:.6f}  Qty: {ask['quantity']:.4f}")
    else:
        print(f"Error: {response.status_code}")


def example_analytics_overview():
    """Example: Get analytics overview."""
    print_section("Analytics Overview")
    
    response = requests.get(f"{BASE_URL}/api/v1/analytics/overview")
    data = response.json()
    
    stats = data['stats']
    print(f"Total Markets: {stats['total_markets']}")
    print(f"Active Spot: {stats['active_spot_markets']}")
    print(f"Active Derivatives: {stats['active_derivative_markets']}")
    print(f"Total 24h Volume: ${stats['total_volume_24h']:,.2f}")
    
    print("\n--- Top Gainers ---")
    for gainer in data['top_gainers'][:3]:
        print(f"  • {gainer['ticker']}: +{gainer['price_change_24h']:.2f}%")
    
    print("\n--- Top Losers ---")
    for loser in data['top_losers'][:3]:
        print(f"  • {loser['ticker']}: {loser['price_change_24h']:.2f}%")


def example_volatility(market_id: str):
    """Example: Get volatility metrics."""
    print_section(f"Volatility: {market_id[:20]}...")
    
    response = requests.get(f"{BASE_URL}/api/v1/analytics/{market_id}/volatility")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Ticker: {data['ticker']}")
        print(f"Period: {data['period']}")
        print(f"Volatility: {data['volatility']:.4f}")
        print(f"Volatility %: {data['volatility_percentage']:.2f}%")
        print(f"24h Range: {data['low']:.4f} - {data['high']:.4f}")
    else:
        print(f"Error: {response.status_code}")


def example_liquidity(market_id: str):
    """Example: Get liquidity metrics."""
    print_section(f"Liquidity: {market_id[:20]}...")
    
    response = requests.get(f"{BASE_URL}/api/v1/analytics/{market_id}/liquidity")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Ticker: {data['ticker']}")
        print(f"Liquidity Score: {data['liquidity_score']}/100")
        print(f"Bid Depth: ${data['bid_depth']:,.2f}")
        print(f"Ask Depth: ${data['ask_depth']:,.2f}")
        print(f"Spread (bps): {data['spread_bps']:.2f}")
    else:
        print(f"Error: {response.status_code}")


def example_market_health(market_id: str):
    """Example: Get market health."""
    print_section(f"Market Health: {market_id[:20]}...")
    
    response = requests.get(f"{BASE_URL}/api/v1/analytics/{market_id}/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Ticker: {data['ticker']}")
        print(f"Health Score: {data['health_score']}/100")
        print(f"Status: {data['status'].upper()}")
        print(f"Components:")
        print(f"  - Liquidity: {data['liquidity_component']:.2f}")
        print(f"  - Volatility: {data['volatility_component']:.2f}")
        print(f"  - Activity: {data['activity_component']:.2f}")
    else:
        print(f"Error: {response.status_code}")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print(" INJECTIVE MARKET INTELLIGENCE API - USAGE EXAMPLES")
    print("="*60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    
    try:
        # Health check first
        example_health_check()
        
        # List markets and get first market ID
        response = requests.get(f"{BASE_URL}/api/v1/markets")
        markets = response.json().get('markets', [])
        
        example_list_markets()
        
        if markets:
            market_id = markets[0]['market_id']
            
            example_get_market_detail(market_id)
            example_get_orderbook(market_id)
            example_analytics_overview()
            example_volatility(market_id)
            example_liquidity(market_id)
            example_market_health(market_id)
        else:
            print("\n⚠️  No markets found. Analytics examples skipped.")
        
        print("\n" + "="*60)
        print(" EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("   Make sure the API is running: uvicorn app.main:app --reload\n")


if __name__ == "__main__":
    main()
