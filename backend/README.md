# CulturalOS API Documentation

![CulturalOS](https://img.shields.io/badge/CulturalOS-MVP-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)
![Python](https://img.shields.io/badge/Python-3.12+-3776ab.svg)
![Gemini AI](https://img.shields.io/badge/Gemini-AI%20Powered-orange.svg)

> **Enterprise-grade Cultural Intelligence Platform API**  
> Discover, analyze, and predict cultural trends with AI-powered insights.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL
- **Google Gemini API Key (REQUIRED)**

### Installation
```bash
# Clone repository
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables (REQUIRED)
export GOOGLE_GEMINI_API_KEY="your_api_key_here"

# Start the server
python main.py
```

### Access Documentation
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📊 API Overview

The CulturalOS API provides comprehensive cultural intelligence analysis with AI-powered insights. The system analyzes user cultural profiles, music listening patterns, and generates personalized recommendations with explanations powered by Google Gemini.

### Core Capabilities
- **Cultural Intelligence Scoring** - Quantified cultural engagement metrics
- **AI-Powered Explanations** - Gemini-generated insights for every recommendation
- **Trend Predictions** - Cultural trend forecasting with confidence scores
- **Smart Todo Generation** - Actionable cultural discovery tasks
- **Enterprise Analytics** - Team performance and market intelligence
- **Music Analysis** - Listening history and pattern recognition

## 🎯 Key Endpoints

### Cultural Intelligence API (`/api/cultural-mock/`)

#### Users Management
```http
GET /api/cultural-mock/users
```
Returns list of available users for cultural analysis.

**Response Example:**
```json
[
  {
    "id": "1",
    "name": "Alex Chen",
    "email": "alex.chen@example.com",
    "location": "San Francisco, CA",
    "joinDate": "2024-01-15",
    "status": "active"
  }
]
```

#### Cultural Analysis
```http
GET /api/cultural-mock/analyze/{user_id}
```
Comprehensive cultural intelligence analysis with AI explanations.

**Key Features:**
- Cultural score and diversity index calculation
- Platform engagement metrics (Spotify, Instagram, TikTok)
- AI-powered trend predictions with explanations
- Cultural insights with confidence scores
- Personalized recommendations with Gemini AI reasoning

**Response Structure:**
```json
{
  "user_id": "1",
  "cultural_score": 89,
  "diversity_index": 94,
  "platforms": {
    "spotify": {
      "connected": true,
      "tracks": 3066,
      "genres": 23,
      "daily_hours": 4.2
    }
  },
  "predictions": [
    {
      "nextTrend": "K-Pop x Latin Collaborations",
      "probability": 84,
      "timeframe": "2-3 weeks",
      "category": "music",
      "reasoning": "Strong K-Pop engagement correlates with Latin fusion trends",
      "ai_explanation": "Your K-Pop interest aligns perfectly with the emerging Latin collaboration trend..."
    }
  ],
  "insights": [
    {
      "category": "Music Evolution",
      "finding": "Your taste spans 4 genres, indicating high musical curiosity",
      "confidence": 87,
      "ai_explanation": "Your diverse musical preferences demonstrate exceptional cultural curiosity..."
    }
  ],
  "recommendations": [
    {
      "category": "Music Discovery",
      "title": "K-Electronic Fusion Artists",
      "description": "Explore artists blending K-Pop with electronic elements",
      "cultural_impact": 85,
      "ai_explanation": "This fusion perfectly matches your cultural profile..."
    }
  ]
}
```

#### Music Listening History
```http
GET /api/cultural-mock/listening-history/{user_id}?days=30
```
Retrieve user's music listening patterns for cultural analysis.

**Parameters:**
- `days`: Number of days of history to analyze (default: 30)

#### Smart Todo Generation
```http
POST /api/cultural-mock/todo-analysis/{user_id}
```
Generate personalized cultural discovery tasks based on listening history.

**Response Example:**
```json
{
  "user_id": "1",
  "analysis_type": "music_based_todos",
  "total_recommendations": 5,
  "todos": [
    {
      "category": "Music Discovery",
      "priority": "medium",
      "title": "Explore Electronic Music",
      "description": "Discover new artists and tracks in electronic based on your cultural profile",
      "estimated_time": "30 minutes",
      "cultural_impact": 60,
      "specific_actions": [
        "Listen to 3 new electronic artists",
        "Create a electronic playlist",
        "Read about electronic cultural origins"
      ],
      "due_date": "2024-08-05T19:55:59.787063",
      "reasoning": "Your listening history shows limited exposure to electronic...",
      "ai_explanation": "Electronic music exploration will complement your existing preferences..."
    }
  ],
  "analysis_metadata": {
    "based_on_days": 30,
    "cultural_score_impact": 22,
    "estimated_total_time": 145
  }
}
```

### Enterprise API (`/api/enterprise/`)

#### Team Analytics
```http
GET /api/enterprise/team-analytics
```
Comprehensive team cultural performance metrics.

**Features:**
- Organization-wide cultural scores
- Team performance comparisons
- Collaboration matrix analysis
- Cultural trend adoption rates

#### Market Intelligence
```http
GET /api/enterprise/market-intelligence
```
Global market analysis and competitive landscape.

**Includes:**
- Market penetration and growth rates
- Cultural alignment scores by region
- Competitive positioning analysis
- Revenue opportunity projections

#### Cultural Initiatives
```http
GET /api/enterprise/cultural-initiatives
```
Organization-wide cultural development programs.

#### Report Generation
```http
POST /api/enterprise/generate-report?report_type=comprehensive
```
Generate custom enterprise reports.

**Report Types:**
- `comprehensive` - Complete analysis with recommendations
- `team_performance` - Team-focused cultural analytics
- `market_analysis` - Market intelligence report
- `cultural_trends` - Trend analysis and predictions

## 🤖 AI Integration

### Google Gemini Integration
The API leverages Google Gemini for intelligent explanations:

- **Recommendation Explanations** - Personalized reasoning for cultural suggestions
- **Insight Analysis** - Deep cultural pattern explanations
- **Trend Predictions** - Contextual trend relevance explanations
- **Todo Justifications** - AI-powered task recommendations

### Required Configuration
- Gemini API key is mandatory for all AI-powered explanations
- Server will not start without valid Gemini API key
- 10-second timeout optimization for production reliability

## 🏗 Architecture

### Tech Stack
- **FastAPI** - High-performance async web framework
- **Pydantic** - Data validation and serialization
- **PostgreSQL** - Primary database
- **aiohttp** - Async HTTP client for AI services
- **Google Gemini** - AI explanation generation

### Response Models
All endpoints use strongly-typed Pydantic models:
- `CulturalAnalysisResponse` - Complete cultural analysis
- `TodoAnalysisResponse` - Smart todo recommendations
- `ListeningHistoryResponse` - Music pattern analysis
- `TrendPrediction` - Cultural trend forecasting
- `CulturalInsight` - AI-powered insights

### Error Handling
- Comprehensive HTTP status codes
- Detailed error messages
- Graceful AI service failures
- Production-ready exception handling

## 📈 Sample Users

The API includes 4 diverse user profiles for demonstration:

1. **Alex Chen** (San Francisco) - K-pop, Electronic, Indie, Jazz enthusiast
2. **Maria Rodriguez** (Mexico City) - Reggaeton, Pop Latino, Electronic lover
3. **Kenji Tanaka** (Tokyo) - J-pop, City Pop, Electronic, Ambient fan
4. **Emma Thompson** (London) - Indie, Brit-pop, Electronic, World Music explorer

Each user has realistic:
- Music preferences and listening patterns
- Language capabilities
- Geographic cultural interests
- Social media engagement metrics

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/culturaldb

# AI Services
GOOGLE_GEMINI_API_KEY=your_gemini_api_key_here

# CORS (for frontend integration)
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"]
```

### API Settings
- **Base URL**: `http://localhost:8000`
- **Timeout**: 10 seconds for AI calls
- **Rate Limiting**: Not implemented (production consideration)
- **Authentication**: Disabled for MVP (enterprise feature)

## 🧪 Testing

### Manual Testing
Use the interactive documentation at `/docs` to test all endpoints with real-time responses.

### Sample API Calls
```bash
# Get users
curl "http://localhost:8000/api/cultural-mock/users"

# Analyze user culture
curl "http://localhost:8000/api/cultural-mock/analyze/1"

# Generate todos
curl -X POST "http://localhost:8000/api/cultural-mock/todo-analysis/1"

# Team analytics
curl "http://localhost:8000/api/enterprise/team-analytics"
```

## 🚀 Production Considerations

### Performance
- Async/await architecture for high concurrency
- Optimized AI call timeouts
- Efficient database queries
- Response caching opportunities

### Scalability
- Stateless API design
- Horizontal scaling ready
- Database connection pooling
- Load balancer compatible

### Security
- Input validation with Pydantic
- SQL injection protection
- CORS configuration
- Rate limiting (recommended)
- Authentication system (enterprise feature)

### Monitoring
- Health check endpoint
- Structured logging
- Error tracking integration points
- Performance metrics collection

## 📋 API Response Codes

- **200** - Success
- **404** - User/Resource not found
- **422** - Validation error
- **500** - Internal server error
- **503** - AI service unavailable (Gemini required)

## 🔮 Future Enhancements

- **Real Spotify Integration** - Live music data
- **WebSocket Support** - Real-time cultural updates
- **Advanced Analytics** - ML-powered insights
- **Multi-language Support** - Global cultural analysis
- **Authentication System** - User management
- **Rate Limiting** - Production API governance
- **Caching Layer** - Performance optimization

## 🤝 Contributing

This is an MVP demonstration. For production deployment:

1. Add authentication and authorization
2. Implement rate limiting
3. Add comprehensive testing suite
4. Set up monitoring and logging
5. Configure production database
6. Add caching layer
7. Implement CI/CD pipeline

## 📞 Support

For API questions or enterprise inquiries:
- Interactive Documentation: http://localhost:8000/docs
- Health Status: http://localhost:8000/health
- Version Info: v1.0.0 MVP

---

**Built with ❤️ for cultural discovery and intelligence.**