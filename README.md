# complaints_api

A FastAPI-based backend for collecting, analyzing, and categorizing customer complaints.  
Includes sentiment analysis, category detection using OpenAI, optional spam filtering, and automation via n8n.

## Features

- Accepts user complaints via API
- Analyzes sentiment using [APILayer Sentiment Analysis](https://apilayer.com/marketplace/sentiment-api)
- Detects category (technical / payment / other) using OpenAI GPT-3.5
- Optional spam filtering via API Layer or API Ninjas (API keys required; enable manually in code)
- Stores complaints in SQLite
- Exposes REST API with OpenAPI docs
- Integrated automation via n8n

## Technologies

- **FastAPI**
- **SQLite**
- **Docker & Docker Compose**
- **n8n** (automation via web interface)
- **External APIs:**
  - [APILayer Sentiment API](https://apilayer.com/marketplace/sentiment-api)
  - [OpenAI GPT-3.5 Turbo](https://platform.openai.com/)
  - [IP-API](http://ip-api.com/)
  - [API Layer Spam Checker](https://apilayer.com/marketplace/spamcheck-api)
  - [API Ninjas Spam Checker](https://api-ninjas.com/api/spamcheck)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/axnra/complaints_api.git
cd complaints_api
```

### 2. Create `.env`

Create a file named `.env` in the root directory and fill in your API keys:

```
DATABASE_URL=sqlite:///./db_data/db.sqlite3

OPENAI_API_KEY=your_openai_key
SENTIMENT_API_KEY=your_apilayer_sentiment_key

APILAYYER_SPAMCHECK_API_KEY=optional_apilayer_spam_key
NINJA_SPAMCHECK_API_KEY=optional_ninja_spam_key
```

> ⚠️ `TELEGRAM_BOT_TOKEN` and Google Service Account credentials **cannot** be passed through `.env` unless you're on **n8n Enterprise**. Set them manually in the n8n web interface.

### 3. Build and start the system

```bash
docker compose up --build -d
```

- FastAPI will be available at: http://localhost:8015/docs
- n8n will be available at: http://localhost:8020

## API Endpoints

### Submit a complaint

```http
POST /complaints
```

**Request Body:**
```json
{
  "text": "My payment failed again!"
}
```

**Response:**
```json
{
  "id": 1,
  "status": "open",
  "sentiment": "negative",
  "category": "оплата"
}
```

### Get complaints (with filters)

```http
GET /complaints?status=open&since=2025-04-17T12:00:00
```

### Update status

```http
PATCH /complaints/{id}/status?new_status=closed
```

## Example via `curl`

```bash
curl -X POST http://localhost:8015/complaints      -H "Content-Type: application/json"      -d '{"text": "The SMS never arrived"}'
```

## Database Schema (SQLite)

| Field     | Type    | Description                        |
|-----------|---------|------------------------------------|
| id        | int     | Auto-increment primary key         |
| text      | string  | Complaint text                     |
| status    | string  | "open" or "closed" (default: open) |
| timestamp | datetime| UTC time of creation               |
| sentiment | string  | positive / negative / neutral      |
| category  | string  | техническая / оплата / другое      |

## Automation with n8n

Automation is implemented via **n8n’s web interface** (GUI workflow builder).


### Notes:

- **Authorization to Google Sheets** requires manual login via OAuth2 in n8n GUI
- **Telegram bot token** must be set in the interface (not `.env`) unless using n8n Enterprise

## Limitations

- Free-tier APIs have daily/monthly limits (see respective providers)
- n8n cloud environment variable injection is limited without Enterprise license
- Google Sheets integration requires manual OAuth via browser

## License

MIT

## Author

Built with spite and love by [axnra](https://github.com/axnra)