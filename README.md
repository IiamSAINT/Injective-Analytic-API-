<div align="center">

# Injective Market & Network Data API

**REST API for Injective Protocol market data, analytics, and network economics**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Injective](https://img.shields.io/badge/Injective-00F2FE?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxMCIgZmlsbD0id2hpdGUiLz48L3N2Zz4=&logoColor=black)](https://injective.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

[**Explore the Docs →**](http://localhost:8000/docs) · [**Quick Start**](#installation) · [**API Reference**](#api-reference)

</div>

---

## Overview

A unified REST API that provides **clean, normalized market data** and **computed analytics** for the Injective Protocol ecosystem. Instead of wrestling with multiple raw blockchain endpoints, get structured data and actionable metrics through a single interface.

```bash
curl http://localhost:8000/api/v1/analytics/overview
```

```json
{
  "total_markets": 203,
  "spot_markets": 136,
  "derivative_markets": 67,
  "top_gainers": ["..."],
  "top_losers": ["..."]
}
```

---

## Features

<table>
<tr>
<td width="50%">

### 📊 Market Data
Access **200+ markets** through unified endpoints
- Spot & derivative markets
- Real-time orderbooks
- Trade history

</td>
<td width="50%">

### 📈 Analytics
Computed metrics not available elsewhere
- Volatility scores
- Liquidity ratings (0–100)
- Market health indicators

</td>
</tr>
<tr>
<td width="50%">

### 💰 Supply & Economics
Macro-economic data for the ecosystem
- Real-time supply: Total / Staked / Burned
- Inflation rate & minting parameters
- Burn address tracking

</td>
<td width="50%">

### 🥷 Ninja Analytics
Community tracking and analysis
- Active participant detection from blocks
- Address tagging (CEX, Whale, etc.)
- Per-address lookup

</td>
</tr>
<tr>
<td width="50%">

### ⚡ Performance
Built for speed
- Intelligent caching (10–30s TTL)
- Fully async architecture
- Connection pooling

</td>
<td width="50%">

### 🔒 Premium (Gated)
High-value data for subscribers
- Whale Watch: large transaction feed
- API key authentication
- Admin tagging endpoints

</td>
</tr>
</table>

---

## Installation

### Local Development

```bash
git clone https://github.com/IiamSAINT/inj_API.git
cd inj_API

python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

### Docker

```bash
docker build -t injective-api .
docker run -p 8000:8000 injective-api
```

**Access Points:**

| Resource | URL |
|----------|-----|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| API Base | http://localhost:8000/api/v1 |

---

## API Reference

### Markets

| Endpoint | Description |
|----------|-------------|
| `GET /markets` | List all 200+ markets |
| `GET /markets?market_type=spot` | Filter by type |
| `GET /markets/{id}` | Market details |
| `GET /markets/{id}/orderbook` | Live orderbook |

### Analytics

| Endpoint | Description |
|----------|-------------|
| `GET /analytics/overview` | Global market stats |
| `GET /analytics/top-movers` | Gainers & losers |
| `GET /analytics/{id}/volatility` | Price volatility |
| `GET /analytics/{id}/liquidity` | Liquidity score |
| `GET /analytics/{id}/health` | Market health |

### Supply & Economics

| Endpoint | Description |
|----------|-------------|
| `GET /analytics/supply/overview` | Total/Staked/Burned supply |
| `GET /analytics/supply/inflation` | Inflation rate & mint params |

### Ninja Analytics

| Endpoint | Description |
|----------|-------------|
| `GET /analytics/ninja/active` | Top active addresses |
| `GET /analytics/ninja/check/{addr}` | Check address tags/labels |

### Premium (API Key Required)

| Endpoint | Description |
|----------|-------------|
| `GET /premium/whales` | Large transaction feed |
| `POST /premium/tags` | Admin: Add address tags |

### Health

| Endpoint | Description |
|----------|-------------|
| `GET /health` | API status |
| `GET /health/injective` | Network connectivity |
| `GET /health/detailed` | Full diagnostics |

---

## How Analytics Work

### Liquidity Score (0–100)

| Component | Weight | What It Measures |
|-----------|--------|------------------|
| Depth | 40% | Total orderbook value |
| Spread | 40% | Gap between best bid/ask |
| Balance | 20% | Bid vs ask symmetry |

**Interpretation:** 80+ = Excellent · 60–79 = Good · 40–59 = Moderate · <40 = Low

### Volatility

Uses the Parkinson estimator based on 24h high/low range.

| Range | Risk Level |
|-------|------------|
| 0–2% | Low |
| 2–5% | Moderate |
| 5–10% | High |
| 10%+ | Extreme |

### Health Score (0–100)

Composite metric: Liquidity (40%) + Volatility (30%) + Activity (30%).

| Score | Status |
|-------|--------|
| 70–100 | ✅ Healthy |
| 40–69 | ⚠️ Moderate |
| 0–39 | ❌ Weak |

---

## Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Client    │ ───▶ │   FastAPI   │ ───▶ │  Injective  │
│             │      │   + Cache   │      │  Mainnet    │
└─────────────┘      └─────────────┘      └─────────────┘
```

**Stack:** FastAPI · httpx · Pydantic v2 · cachetools

```
app/
├── main.py          # Application entry point
├── config.py        # Environment-based settings
├── routers/         # API endpoint definitions
├── services/        # Business logic & data processing
├── models/          # Pydantic response schemas
└── utils/           # Caching & authentication
```

---

## Testing

```bash
pytest tests/ -v
```

---

## Configuration

All settings can be overridden via environment variables or a `.env` file.

| Variable | Default | Description |
|----------|---------|-------------|
| `INJECTIVE_LCD_URL` | `https://sentry.lcd.injective.network:443` | LCD endpoint |
| `MARKET_CACHE_TTL` | `10` | Market cache TTL (seconds) |
| `ANALYTICS_CACHE_TTL` | `30` | Analytics cache TTL (seconds) |
| `PREMIUM_API_KEY` | `secret_ninja_key` | API key for premium endpoints |

See [`.env.example`](.env.example) for all available options.

---

## License

[MIT](LICENSE)

---

<div align="center">

**Built for the Injective Ecosystem**

[Documentation](http://localhost:8000/docs) · [Report Bug](https://github.com/IiamSAINT/inj_API/issues) · [Request Feature](https://github.com/IiamSAINT/inj_API/issues)

</div>
