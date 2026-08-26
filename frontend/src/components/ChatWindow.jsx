import React, { useState, useEffect, useRef } from 'react';

export default function ChatWindow({ messages, onSendMessage, loading }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const samplePrompts = [
    "I need ANC wireless headphones under INR 5,000.",
    "Show laptop under INR 70,000 with upsells.",
    "Trigger test failure demo to show recovery."
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    onSendMessage(input);
    setInput('');
  };

  const handleChipClick = (prompt) => {
    onSendMessage(prompt);
  };

  return (
    <div className="chat-section">
      <div className="chat-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '1.2rem' }}>🤖</span>
          <div>
            <div style={{ fontWeight: '600', fontSize: '0.95rem' }}>AI Commerce Agent</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Powered by Gemini / Groq Tool Calling</div>
          </div>
        </div>
      </div>

      <div className="messages-container">
        {messages.map((msg, index) => (
          <div key={index} className={`message-bubble ${msg.sender}`}>
            <div style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</div>
            <div style={{ fontSize: '0.7rem', opacity: 0.6, marginTop: '0.4rem', textAlign: 'right' }}>
              {msg.time}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message-bubble agent" style={{ opacity: 0.7 }}>
            ⚡ Agent is searching catalog, checking policy bounds & building cart...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <div className="prompt-suggestions">
          {samplePrompts.map((p, idx) => (
            <button key={idx} className="chip-btn" onClick={() => handleChipClick(p)}>
              {p}
            </button>
          ))}
        </div>

        <form className="input-box-wrapper" onSubmit={handleSubmit}>
          <input
            type="text"
            className="chat-input"
            placeholder="Type your natural language request (e.g. 'I need headphones under INR 5,000')..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button type="submit" className="send-btn" disabled={loading}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
