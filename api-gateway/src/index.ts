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

// 3. Body parsing (Hardened with size limits to prevent payload DoS)
app.use(express.json({ limit: '10kb' }));

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

  // Enforce a hard length limit on the query itself
  if (query.length > 1000) {
    return res.status(400).json({ error: 'Query exceeds maximum allowed length (1000 characters).' });
  }

  try {
    const startTime = Date.now();
    
    // Forward the request to the Python AI Service with a strict timeout
    // Prevent the gateway from hanging indefinitely if the AI service stalls
    const aiResponse = await axios.post(`${AI_SERVICE_URL}/api/chat`, { query }, {
      timeout: 25000 // 25 seconds max
    });
    const { answer, metadata } = aiResponse.data;
    
    const durationMs = Date.now() - startTime;

    // 6. Output Filtering Guardrail
    // Fallback in case the LLM disobeys the prompt and attempts to leak instructions
    const lowerAnswer = answer.toLowerCase();
    if (lowerAnswer.includes("you are docent") || lowerAnswer.includes("security guardrails") || lowerAnswer.includes("untrusted user data")) {
      console.warn(JSON.stringify({
        timestamp: new Date().toISOString(),
        level: 'WARN',
        event: 'prompt_leak_prevented',
        query: query
      }));
      return res.status(403).json({ error: 'I cannot fulfill that request due to security constraints.' });
    }

    // Structured Security Logging
    // Phase 8 dictates we retain query text, retrieved chunk IDs, and the final response.
    console.log(JSON.stringify({
      timestamp: new Date().toISOString(),
      level: 'INFO',
      event: 'chat_query_processed',
      query: query,
      answer: answer, // Log the final response
      durationMs,
      metadata: metadata 
    }));

    // We only return the sanitized answer to the frontend.
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

// Only start the server if we aren't running tests
if (process.env.NODE_ENV !== 'test') {
  app.listen(PORT, () => {
    console.log(`API Gateway listening on port ${PORT}`);
  });
}

export default app;
