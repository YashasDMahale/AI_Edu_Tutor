import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, User, Loader2 } from 'lucide-react';

export default function ChatWindow() {
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Hello! I am your AI Education Tutor. Upload your materials and ask me any questions.' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const url = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await axios.post(`${url}/query`, {
        question: input
      });

      const aiResponse = { 
        role: 'ai', 
        content: response.data.answer,
        sources: response.data.sources
      };
      
      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'ai', content: "An error occurred while generating the answer. Check if your backend and AI models are running." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="panel chat-panel glass-effect">
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message-wrapper ${msg.role}`}>
            <div className={`avatar ${msg.role}`}>
              {msg.role === 'ai' ? <Bot size={20} /> : <User size={20} />}
            </div>
            <div className="message-content">
              <p>{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div className="sources-box">
                  <strong>Sources:</strong>
                  <ul>
                    {msg.sources.map((s, i) => (
                      <li key={i}>{s.file_name} ({s.source_type}) - Score: {s.score?.toFixed(2)}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message-wrapper ai loading">
            <div className="avatar ai"><Bot size={20} /></div>
            <div className="message-content">
              <Loader2 className="spinner" size={20} />
              <span>Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="chat-input-area">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Ask a question..."
          rows="2"
        />
        <button className="btn-send" onClick={handleSend} disabled={isLoading || !input.trim()}>
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}
