# CulturalOS API - Quick Reference

🚀 **MVP Demo Ready** | FastAPI Documentation: http://localhost:8000/docs

## 🎯 Essential MVP Endpoints

### 1. Get Available Users
```http
GET /api/cultural-mock/users
```
**Use Case:** See which users are available for cultural analysis  
**Demo Value:** Shows 4 diverse cultural profiles

### 2. Complete Cultural Analysis ⭐ **MVP HIGHLIGHT**
```http
GET /api/cultural-mock/analyze/1
```
**Use Case:** Full cultural intelligence analysis with AI explanations  
**Demo Value:** Showcases core AI-powered cultural insights  
**Features:**
- Cultural score (0-100)
- Diversity index
- Platform engagement metrics
- AI-generated trend predictions
- Personalized recommendations with Gemini explanations

### 3. Smart Todo Generation ⭐ **MVP HIGHLIGHT**
```http
POST /api/cultural-mock/todo-analysis/1
```
**Use Case:** Generate actionable cultural discovery tasks  
**Demo Value:** Shows practical application of cultural analysis  
**Features:**
- Music-based cultural todos
- AI explanations for each recommendation
- Cultural impact scores
- Specific action steps

### 4. Enterprise Team Analytics ⭐ **MVP HIGHLIGHT**
```http
GET /api/enterprise/team-analytics
```
**Use Case:** Organization-wide cultural intelligence metrics  
**Demo Value:** Enterprise scalability demonstration  
**Features:**
- Team performance comparison
- Cultural trend adoption
- Collaboration metrics

### 5. Global Market Intelligence
```http
GET /api/enterprise/market-intelligence
```
**Use Case:** Market expansion cultural insights  
**Demo Value:** B2B enterprise features  
**Features:**
- Market penetration analysis
- Cultural alignment scores
- Revenue projections

## 🎭 Sample Users (for testing)

| ID | Name | Location | Cultural Profile |
|----|------|----------|------------------|
| 1 | Alex Chen | San Francisco | K-pop, Electronic, Multilingual |
| 2 | Maria Rodriguez | Mexico City | Reggaeton, Latin culture |
| 3 | Kenji Tanaka | Tokyo | J-pop, Minimalist |
| 4 | Emma Thompson | London | Indie, World music |

## 🤖 AI Features (Gemini Integration)

Every recommendation includes AI-generated explanations:
- **Why** it's relevant to the user
- **How** it enhances cultural intelligence
- **What** specific benefits it provides

**Required:** Gemini API key must be configured or server will not start

## 💼 MVP Presentation Tips

### For Investors/Clients:
1. **Start with:** `/docs` - Professional API documentation
2. **Show Cultural Analysis:** `/analyze/1` - Core AI capabilities
3. **Demonstrate Actionable Value:** `/todo-analysis/1` - Practical applications
4. **Scale to Enterprise:** `/team-analytics` - B2B potential

### Key Value Props:
- ✅ **AI-Powered** - Every insight includes Gemini explanations
- ✅ **Actionable** - Not just analysis, but specific next steps
- ✅ **Scalable** - Individual to enterprise-level analytics
- ✅ **Cultural Focus** - Unique positioning in cultural intelligence
- ✅ **Production Ready** - Professional documentation, error handling

## 🔗 Quick Test Commands

```bash
# Health check
curl http://localhost:8000/health

# Get users
curl http://localhost:8000/api/cultural-mock/users | jq

# Full cultural analysis (Alex Chen)
curl http://localhost:8000/api/cultural-mock/analyze/1 | jq

# Generate smart todos
curl -X POST http://localhost:8000/api/cultural-mock/todo-analysis/1 | jq

# Enterprise analytics
curl http://localhost:8000/api/enterprise/team-analytics | jq
```

## 📊 Response Highlights

### Cultural Analysis Response includes:
- `cultural_score`: 0-100 intelligence rating
- `predictions[]`: Trend forecasts with AI explanations
- `insights[]`: Cultural patterns with confidence scores
- `recommendations[]`: Personalized suggestions with Gemini reasoning

### Todo Analysis Response includes:
- `todos[]`: Actionable cultural tasks
- `ai_explanation`: Gemini-generated reasoning
- `cultural_impact`: Potential score improvement
- `analysis_metadata`: Performance metrics

---

**Ready for Demo:** http://localhost:8000/docs