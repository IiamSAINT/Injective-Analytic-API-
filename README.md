<div align="center">

# Injective Market Intelligence API

**Transform complex blockchain data into actionable trading insights**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Injective](https://img.shields.io/badge/Injective-00F2FE?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxMCIgZmlsbD0id2hpdGUiLz48L3N2Zz4=&logoColor=black)](https://injective.com)

[**Explore the Docs →**](http://localhost:8000/docs) · [**View Demo**](#quick-demo) · [**Get Started**](#installation)

---

🏆 *Built for the [Ninja API Forge](https://xsxo494365r.typeform.com/to/iiNKwjI8) Contest*

</div>

---

## The Challenge

Building on Injective means wrestling with:
- **Complex APIs** — Multiple endpoints, different formats for spot vs derivatives
- **Raw Data** — No computed analytics, just raw orderbooks and trades  
- **Performance** — No caching, every request hits the blockchain

## Our Solution

One simple API that gives you **clean data** and **computed analytics** instantly.

```bash
# Before: Multiple calls, manual calculations, complex parsing
# After: One call, instant insights

curl http://localhost:8000/api/v1/analytics/overview
```

```json
{
  "total_markets": 203,
  "spot_markets": 136,
  "derivative_markets": 67,
  "top_gainers": [...],
  "top_losers": [...]
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
Computed metrics that don't exist elsewhere
- Volatility scores
- Liquidity ratings (0-100)
- Market health indicators

</td>
</tr>
<tr>
<td width="50%">

### ⚡ Performance
Built for speed
- Intelligent caching (10-30s TTL)
- Async architecture
- Connection pooling

</td>
<td width="50%">

### 🛡️ Reliability
Production-ready
- 20 automated tests
- Graceful error handling
- Health monitoring

</td>
</tr>
</table>

---

## Quick Demo

### Check Market Health
```bash
GET /api/v1/analytics/{market_id}/health
```
```json
{
  "ticker": "INJ/USDT",
  "health_score": 78.5,
  "status": "healthy",
  "liquidity_component": 31.4,
  "volatility_component": 25.0,
  "activity_component": 22.1
}
```

### Get Liquidity Score
```bash
GET /api/v1/analytics/{market_id}/liquidity
```
```json
{
  "ticker": "BTC/USDT PERP",
  "liquidity_score": 85.2,
  "bid_depth": 125000.00,
  "ask_depth": 118000.00,
  "spread_bps": 12.5
}
```

### Market Overview
```bash
GET /api/v1/analytics/overview
```
```json
{
  "total_markets": 203,
  "active_spot_markets": 136,
  "active_derivative_markets": 67,
  "top_gainers": ["INJ/USDT +5.2%", "ATOM/USDT +3.1%"],
  "volume_leaders": ["BTC/USDT PERP", "ETH/USDT PERP"]
}
```

---

## Installation

### Option 1: Local Development

```bash
git clone https://github.com/IiamSAINT/inj_API.git
cd inj_API

python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

### Option 2: Docker

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

### Health

| Endpoint | Description |
|----------|-------------|
| `GET /health` | API status |
| `GET /health/injective` | Network connectivity |
| `GET /health/detailed` | Full diagnostics |

---

## How Analytics Work

### Liquidity Score (0-100)

Measures ease of trading without moving the price.

| Component | Weight | What It Measures |
|-----------|--------|------------------|
| Depth | 40% | Total orderbook value |
| Spread | 40% | Gap between best bid/ask |
| Balance | 20% | Bid vs ask symmetry |

**Interpretation:** 80+ = Excellent · 60-79 = Good · 40-59 = Moderate · <40 = Low

### Volatility

Uses the Parkinson estimator based on 24h high/low range.

| Range | Risk Level |
|-------|------------|
| 0-2% | Low |
| 2-5% | Moderate |
| 5-10% | High |
| 10%+ | Extreme |

### Health Score (0-100)

Composite metric combining liquidity, volatility, and activity.

| Score | Status |
|-------|--------|
| 70-100 | ✅ Healthy |
| 40-69 | ⚠️ Moderate |
| 0-39 | ❌ Weak |

---

## Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Client    │ ───▶ │   FastAPI   │ ───▶ │  Injective  │
│             │      │   + Cache   │      │  Mainnet    │
└─────────────┘      └─────────────┘      └─────────────┘
```

**Stack:** FastAPI · httpx · Pydantic v2 · cachetools

**Structure:**
```
app/
├── main.py          # Entry point
├── config.py        # Settings
├── routers/         # API endpoints
├── services/        # Business logic
├── models/          # Data schemas
└── utils/           # Caching
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Current status
✅ 20/20 tests passing
```

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `INJECTIVE_LCD_URL` | `sentry.lcd.injective.network` | LCD endpoint |
| `MARKET_CACHE_TTL` | `10` | Market cache (seconds) |
| `ANALYTICS_CACHE_TTL` | `30` | Analytics cache (seconds) |

---

## License

MIT — Use it freely in your projects.

---

<div align="center">

**Built with ❤️ for the Injective Ecosystem**

[Documentation](http://localhost:8000/docs) · [Report Bug](https://github.com/IiamSAINT/inj_API/issues) · [Request Feature](https://github.com/IiamSAINT/inj_API/issues)

</div>
