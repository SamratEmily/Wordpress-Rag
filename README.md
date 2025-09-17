# WordPress Documentation RAG API

A FastAPI-based API for querying WordPress documentation using RAG (Retrieval-Augmented Generation). This project provides an intelligent search and question-answering system for WordPress documentation.

## Features

- FastAPI-based REST API
- React-based modern frontend
- RAG (Retrieval-Augmented Generation) for intelligent document querying
- Rate limiting and CORS support
- Comprehensive error handling
- Logging with rotation
- Health check endpoint
- API versioning

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── exceptions.py
│   │   │   ├── logging.py
│   │   │   └── middleware.py
│   │   ├── models/
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   └── rag_service.py
│   │   ├── utils/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── manifest.json
│   ├── src/
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

## Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API key
- Virtual environment (recommended)

## Installation

### Backend Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install backend dependencies:
```bash
pip install -r backend/requirements.txt
```

3. Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_api_key_here
DEBUG=False
```

### Frontend Setup

1. Install frontend dependencies:
```bash
cd frontend
npm install
```

## Usage

### Running the Backend

1. Start the API server:
```bash
cd backend
uvicorn app.main:app --reload
```

2. The API will be available at `http://localhost:8000`

3. API Documentation will be available at:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Running the Frontend

1. Start the development server:
```bash
cd frontend
npm start
```

2. The frontend will be available at `http://localhost:3000`

## API Endpoints

### POST /api/v1/ask
Query the RAG system with a question about WordPress documentation.

Request body:
```json
{
    "question": "How do I create a custom post type?",
    "context": "Optional additional context"
}
```

Response:
```json
{
    "answer": "To create a custom post type...",
    "sources": ["source1", "source2"],
    "confidence": 0.8
}
```

### GET /api/v1/health
Check API health status.

Response:
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "model": "gpt-3.5-turbo",
    "uptime": 3600
}
```

## Development

### Backend Testing
```bash
pytest backend/tests
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Code Style
The project uses Black for Python code formatting:
```bash
black .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI
- React
- Material-UI
- LangChain
- OpenAI
- ChromaDB 