import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import rateLimit from 'express-rate-limit';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 4000;
const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000';

// 1. Security Headers (Best Practice)
app.use(helmet());

// 2. CORS (Restrict to frontend domain in production)
app.use(cors({
  origin: process.env.FRONTEND_URL || '*',
  methods: ['POST', 'GET']
}));

// 3. Body parsing
app.use(express.json());

// 4. Rate Limiting (Protects the expensive AI Service from abuse)
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 30, // Limit each IP to 30 requests per window
  message: { error: 'Too many requests, please try again later.' }
});

// 5. Request Logging
app.use(morgan('tiny'));

// Chat Endpoint (BFF - Backend For Frontend)
app.post('/api/chat', apiLimiter, async (req, res) => {
  const { query } = req.body;

  if (!query || typeof query !== 'string') {
    return res.status(400).json({ error: 'Valid query string is required.' });
  }

  try {
    const startTime = Date.now();
    
    // Forward the request to the Python AI Service
    const aiResponse = await axios.post(`${AI_SERVICE_URL}/api/chat`, { query });
    const { answer, metadata } = aiResponse.data;
    
    const durationMs = Date.now() - startTime;

    // Phase 3 Requirement: Structured Logging
    // We log the query, duration, and the metadata (rerank scores, chunk sources) provided by Python
    console.log(JSON.stringify({
      timestamp: new Date().toISOString(),
      level: 'INFO',
      event: 'chat_query_processed',
      query: query,
      durationMs,
      metadata: metadata 
    }));

    // We only return the answer to the frontend. The metadata stays strictly in our backend logs.
    res.json({ answer });
  } catch (error: any) {
    // Structured error logging
    console.error(JSON.stringify({
      timestamp: new Date().toISOString(),
      level: 'ERROR',
      event: 'ai_service_failure',
      message: error.message
    }));

    // Sane error handling: Don't leak internal Python stack traces to the public frontend
    res.status(503).json({ error: 'AI Assistant is temporarily unavailable. Please try again later.' });
  }
});

// Health check (For CI/CD & Kubernetes)
app.get('/health', (req, res) => {
  res.json({ status: 'gateway_healthy' });
});

app.listen(PORT, () => {
  console.log(`API Gateway listening on port ${PORT}`);
});
