# Complaint Processing API

A RESTful API for collecting and analyzing customer complaints using external services:
sentiment analysis, spam filtering, geolocation, and category classification.

---

## 📦 Features

- Accept complaints via POST requests (`/complaints`)
- Analyze sentiment using [APILayer Sentiment API](https://apilayer.com/marketplace/sentiment-analysis-api)
- Detect spam via [APILayer](https://apilayer.com/marketplace/spam-checker-api) or [API Ninjas](https://api-ninjas.com/api/spamcheck)
- Retrieve geolocation via [ip-api](http://ip-api.com/)
- Classify complaint categories using [OpenAI GPT-3.5 Turbo](https://platform.openai.com/docs/guides/gpt)

---

## 🚀 Getting Started with Docker

### 1. Clone the repository

```bash
git clone https://github.com/axnra/complaints_api.git
cd complaints-api
```

### 2. Create environment config

```bash
cp .env.example .env
```

Fill in required keys in `.env`.

### 3. Build and run

```bash
docker compose up --build
```

The API will be available at: `http://localhost:8000`

---

## 🔧 Endpoints

### `POST /complaints`

Submit a new complaint:

```json
{
  "text": "Не приходит SMS-код"
}
```

Response:

```json
{
  "id": 1,
  "status": "open",
  "sentiment": "neutral",
  "category": "техническая"
}
```

### `GET /complaints`

Optional query parameters:

- `status=open|closed`
- `since=<ISO-8601 datetime>`

---

## 🛠️ Environment Variables

See `.env.example` for required variables:

```dotenv
DATABASE_URL=sqlite:///./db.sqlite3
SENTIMENT_API_KEY=your_apilayer_key
APILAYER_SPAMCHECK_API_KEY=your_apilayer_key
NINJA_SPAMCHECK_API_KEY=your_ninja_key
OPENAI_API_KEY=your_openai_key
```


## 📎 Notes

- If external APIs are unavailable, sentiment is set to `"unknown"`
- If category cannot be determined, it defaults to `"другое"`

---

## 📄 License

MIT