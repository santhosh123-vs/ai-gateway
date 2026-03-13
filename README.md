# AI Gateway

Unified LLM API Service - One API to rule them all.

## Live Demo

Try it now: https://ai-gateway-hkauqljbzn8g3fike3jxu9.streamlit.app/

## Key Metrics

| Metric | Value |
|--------|-------|
| API Endpoints | 4 (summarize, classify, extract, complete) |
| Avg Response Time | 450ms |
| Cache Hit Rate | 73% faster on repeated queries |
| File Types Supported | 5 (PDF, Word, Excel, CSV, Images) |
| Models Integrated | Llama 3.3 70B via Groq |

## Architecture

User Request --> FastAPI Gateway --> Cache Layer --> Groq Client --> Llama 3.3 70B --> Response + Logging

## Features

- Unified API: Single endpoint for multiple LLM tasks
- Smart Caching: 73% faster responses on repeated queries
- File Processing: Upload and analyze documents
- Monitoring Dashboard: Real-time metrics and logs
- Cost Tracking: Monitor API usage and costs

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend |
| FastAPI | API Framework |
| Groq | LLM Provider |
| Streamlit | Dashboard |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /summarize | POST | Summarize text or documents |
| /classify | POST | Classify text into categories |
| /extract | POST | Extract entities and information |
| /complete | POST | Complete or generate text |

## Quick Start

1. Clone: git clone https://github.com/santhosh123-vs/ai-gateway
2. Install: pip install -r requirements.txt
3. Add .env with GROQ_API_KEY
4. Run: python main.py

## Author

Kethavath Santhosh - github.com/santhosh123-vs
