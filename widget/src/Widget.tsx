import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { MessageSquare, X, Send, RotateCcw } from 'lucide-react';
import './index.css';

interface Message {
  id: string;
  role: 'user' | 'bot';
  content: string;
}

export default function Widget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Session memory persisted in localStorage
  useEffect(() => {
    const saved = localStorage.getItem('docent_chat_session');
    if (saved) {
      try {
        setMessages(JSON.parse(saved));
      } catch (e) {
        console.error("Failed to parse saved chat session.");
      }
    } else {
      setMessages([
        { id: '1', role: 'bot', content: 'Hello! I am Docent, your AI assistant. How can I help you today?' }
      ]);
    }
  }, []);

  // Save to localStorage on change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('docent_chat_session', JSON.stringify(messages));
    }
  }, [messages]);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { id: Date.now().toString(), role: 'user', content: input.trim() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Connect to the API Gateway (BFF), NOT the Python service directly
      const response = await fetch('http://127.0.0.1:4000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage.content })
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      
      const botMessage: Message = { id: (Date.now() + 1).toString(), role: 'bot', content: data.answer };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error(error);
      const errorMsg: Message = { id: (Date.now() + 1).toString(), role: 'bot', content: "I'm having trouble connecting to the server. Please try again later." };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearSession = () => {
    localStorage.removeItem('docent_chat_session');
    setMessages([
      { id: '1', role: 'bot', content: 'Hello! I am Docent, your AI assistant. How can I help you today?' }
    ]);
  };

  return (
    <>
      {/* Floating Action Button */}
      {!isOpen && (
        <button 
          className="docent-fab" 
          onClick={() => setIsOpen(true)}
          aria-label="Open AI Assistant"
        >
          <MessageSquare size={24} />
        </button>
      )}

      {/* Chat Panel */}
      {isOpen && (
        <div className="docent-panel">
          {/* Header */}
          <div className="docent-header">
            <h3>Docent AI</h3>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button className="docent-header-btn" onClick={clearSession} title="Reset Chat">
                <RotateCcw size={18} />
              </button>
              <button className="docent-header-btn" onClick={() => setIsOpen(false)} title="Close">
                <X size={20} />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="docent-messages">
            {messages.map((msg) => (
              <div key={msg.id} className={`docent-message ${msg.role}`}>
                {msg.role === 'bot' ? (
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                ) : (
                  msg.content
                )}
              </div>
            ))}
            
            {/* Realistic loading state */}
            {isLoading && (
              <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="docent-input-area">
            <input 
              type="text" 
              className="docent-input" 
              placeholder="Ask me anything..." 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={isLoading}
            />
            <button 
              className="docent-send-btn" 
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
            >
              <Send size={18} style={{ marginLeft: '2px' }} />
            </button>
          </div>
        </div>
      )}
    </>
  );
}
