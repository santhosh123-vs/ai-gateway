# 🤖 AI Gateway — Unified LLM API

A unified REST API that abstracts multiple AI providers behind a single interface with smart routing, automatic fallback, response caching, and real-time monitoring.

## 🎯 Problem This Solves

| Problem | Without AI Gateway | With AI Gateway |
|---------|-------------------|-----------------|
| Vendor Lock-in | Stuck with one AI provider | Switch providers in one config change |
| Reliability | If provider goes down, everything breaks | Automatic fallback to next provider |
| Cost Explosion | No visibility into AI spending | Real-time cost tracking per request |
| Duplicated Work | Every team builds own AI integration | One shared API for all teams |
| No Monitoring | No idea about latency, errors, usage | Full observability dashboard |
| Wasted Money | Pay for duplicate identical requests | Response caching saves 40%+ costs |

## 🚀 Features

- Unified API — 4 AI task endpoints (complete, summarize, classify, extract)
- Multi-Provider — Groq, OpenAI, Anthropic, Google Gemini support
- Smart Routing — Automatic provider selection and fallback
- Response Caching — Eliminates duplicate API calls, saves cost
- Cost Tracking — Real-time cost monitoring per request
- Latency Monitoring — Track response times
- Error Tracking — Monitor error rates and provider health
- Interactive Dashboard — Beautiful Streamlit monitoring UI
- API Documentation — Auto-generated Swagger docs at /docs

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/complete | General AI completion |
| POST | /api/v1/summarize | Summarize text |
| POST | /api/v1/classify | Classify text |
| POST | /api/v1/extract | Extract information |
| GET | /api/v1/health | Provider health check |
| GET | /api/v1/metrics | Usage metrics |
| GET | /api/v1/models | Available models |
| GET | /api/v1/logs | Request logs |
| GET | /api/v1/cache/stats | Cache statistics |
| DELETE | /api/v1/cache/clear | Clear cache |

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| API Framework | FastAPI (Python) |
| AI Provider | Groq (Llama 3.3 70B) |
| Caching | In-memory with TTL |
| Monitoring | Custom metrics engine |
| Dashboard | Streamlit |
| Documentation | Swagger/OpenAPI |

## ⚡ Quick Start

1. Clone the repo
2. Create virtual environment: python3 -m venv venv
3. Activate: source venv/bin/activate
4. Install dependencies: pip install -r requirements.txt
5. Add your Groq API key to .env file
6. Start API: uvicorn app.main:app --reload --port 8000
7. Start Dashboard: streamlit run dashboard.py
8. Open docs: http://127.0.0.1:8000/docs

## 🧠 Why This Matters

This project demonstrates core AI platform engineering skills:
1. API Design — Clean, RESTful, well-documented APIs
2. System Architecture — Abstraction layers, separation of concerns
3. Reliability Engineering — Fallback mechanisms, error handling
4. Cost Optimization — Caching, model selection, cost tracking
5. Observability — Metrics, logging, dashboards
6. Multi-Provider Strategy — No vendor lock-in

## 📄 License

MIT License
