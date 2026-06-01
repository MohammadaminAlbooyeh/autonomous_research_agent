# Autonomous Research Agent

A multi-agent research system that autonomously searches the web, analyzes content, verifies facts, and generates structured research reports.

## Architecture

```
User Input → ResearchAgent → WebSearcher → WebScraper → ContentAnalyzer → FactChecker → ReportGenerator → Report
```

### Components

- **Backend**: Python/FastAPI with SQLAlchemy, SQLite/PostgreSQL
- **Frontend**: React 18 with Vite
- **Agents**: Research orchestrator, web searcher, content analyzer, fact checker, report generator
- **Tools**: Google Search, web scraper, summarizer, citation manager, comparison engine, document parser

## Quick Start

### Backend

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys (optional - works with mock data)
uvicorn backend.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### API

The API runs at `http://localhost:8000`. Key endpoints:

- `POST /api/research` - Start research: `{"topic": "...", "depth": "shallow|medium|deep"}`
- `GET /api/research` - List all tasks
- `GET /api/research/{id}` - Get task details with sources, findings, report
- `GET /api/research/{id}/report` - Get report
- `GET /api/research/{id}/report/export?format=markdown|text` - Export report
- `GET /api/research/stats` - System statistics

### Docker

```bash
docker compose up
```

## Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | For LLM-powered summarization & reports | No |
| `GOOGLE_API_KEY` | For real web search results | No |
| `GOOGLE_CX` | Google Custom Search Engine ID | No |
| `DATABASE_URL` | Database connection string | No (defaults to SQLite) |

Without API keys, the system uses mock data and heuristic algorithms.

## Testing

```bash
pytest tests/ -v
```
