import React, { useState, useEffect, useCallback } from 'react';
import './chatInterface.css';
import BotIcon from '../components/chatInterface/chatInterfaceSubComponents/botIcon.js';

/**
 * ChatInterface component
 * Renders a self-contained chat interface with message history and input
 * @param {Object} props - Component props
 * @param {string} props.initialQuery - Initial query to start the chat
 * @param {Function} props.onClose - Function to close the chat interface
 * @returns {JSX.Element} The rendered ChatInterface component
 */
const ChatInterface = ({ initialQuery, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [documents, setDocuments] = useState([]);

  /**
   * Adds a new message to the chat
   * @param {string} text - The message text
   * @param {boolean} isUser - Whether the message is from the user
   */
  const addMessage = useCallback((text, isUser) => {
    setMessages(prevMessages => [...prevMessages, { text, isUser }]);
  }, []);

  useEffect(() => {
    if (initialQuery) {
      addMessage(initialQuery, true);
    }
  }, [initialQuery, addMessage]);

  /**
   * Handles form submission
   * @param {Event} e - The form submit event
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      addMessage(input, true);
      setInput('');
      // Here you would typically call an API to get the bot's response
      // For now, we'll just simulate a response
      setTimeout(() => {
        addMessage("I'm a simulated response from the AI.", false);
      }, 1000);
    }
  };

  /**
   * Handles file input change
   * @param {Event} e - The file input change event
   */
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
                <BotIcon />
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