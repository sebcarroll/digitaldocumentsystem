import React, { useState } from 'react';
import './chatInterface.css';
import '../components/chatInterface/chatInterfaceSubComponents/botIcon.js'
import BotIcon from '../components/chatInterface/chatInterfaceSubComponents/botIcon.js';

const ChatInterface = ({ messages, addMessage, onClose }) => {
  const [input, setInput] = useState('');
  const [documents, setDocuments] = useState([]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      addMessage(input, true);
      setInput('');
    }
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    setDocuments([...documents, ...files]);
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <button onClick={onClose} className="close-button">×</button>
      </div>
      <div className="message-list">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.isUser ? 'user-message' : 'bot-message'}`}>
            {!message.isUser && (
              <div className="bot-icon-background">
                {BotIcon}
              </div>
            )}
            <div className="message-text">{message.text}</div>
          </div>
        ))}
      </div>
      {documents.length > 0 && (
        <div className="document-list">
          {documents.length === 1 ? (
            <span>{documents[0].name}</span>
          ) : (
            <span>{documents.length} documents uploaded</span>
          )}
        </div>
      )}
      <form onSubmit={handleSubmit} className="input-area">
        <label htmlFor="file-upload" className="file-upload-label">
          📎
        </label>
        <input
          id="file-upload"
          type="file"
          multiple
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="message-input"
        />
        <button type="submit" className="send-button">
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;