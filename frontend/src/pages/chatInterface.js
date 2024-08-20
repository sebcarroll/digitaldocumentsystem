import React, { useState, useEffect, useCallback } from 'react';
import './chatInterface.css';
import BotIcon from '../components/chatInterface/chatInterfaceSubComponents/botIcon.js';
import { sendQuery, uploadDocument } from '../services/api'
import SendButton from '../components/drivePage/searchbarSubComponents/searchbarSendButton.js';
import AttachFileSharpIcon from '@mui/icons-material/AttachFileSharp';

/**
 * ChatInterface component
 * Renders a self-contained chat interface with message history, input, and file upload functionality.
 * It interacts with an LLM backend for processing queries and documents.
 *
 * @component
 * @param {Object} props - Component props
 * @param {string} props.initialQuery - Initial query to start the chat
 * @param {Function} props.onClose - Function to close the chat interface
 * @returns {JSX.Element} The rendered ChatInterface component
 */
const ChatInterface = ({ initialQuery, onClose }) => {
  console.log('ChatInterface rendering', { initialQuery });
  
  // State declarations
  const [messages, setMessages] = useState([]); // Stores chat messages
  const [input, setInput] = useState(''); // Stores current input text
  const [documents, setDocuments] = useState([]); // Stores uploaded documents
  const [isLoading, setIsLoading] = useState(false); // Indicates if a query is being processed

  /**
   * Adds a new message to the chat history
   * @param {string} text - The message text
   * @param {boolean} isUser - Whether the message is from the user (true) or the AI (false)
   */
  const addMessage = useCallback((text, isUser) => {
    setMessages(prevMessages => [...prevMessages, { text, isUser }]);
  }, []);

  // Effect to handle initial query
  useEffect(() => {
    if (initialQuery) {
      addMessage(initialQuery, true);
      handleQuery(initialQuery);
    }
  }, [initialQuery, addMessage]);

  /**
   * Handles sending a query to the LLM backend and processing the response
   * @param {string} query - The query to send to the LLM
   */
  const handleQuery = async (query) => {
    setIsLoading(true);
    try {
      const response = await sendQuery(query);
      addMessage(response.response, false);
    } catch (error) {
      console.error('Error processing query:', error);
      addMessage("Sorry, I couldn't process your request. Please try again.", false);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handles form submission when the user sends a message
   * @param {Event} e - The form submit event
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      addMessage(input, true);
      handleQuery(input);
      setInput('');
    }
  };

  /**
   * Handles file input change when the user uploads documents
   * @param {Event} e - The file input change event
   */
  const handleFileChange = async (e) => {
    const files = Array.from(e.target.files);
    setDocuments([...documents, ...files]);

    for (const file of files) {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const content = e.target.result;
        try {
          await uploadDocument({
            id: file.name,
            content: content,
            type: file.type,
          });
          addMessage(`Document "${file.name}" uploaded and processed successfully.`, false);
        } catch (error) {
          console.error('Error uploading document:', error);
          addMessage(`Failed to upload document "${file.name}". Please try again.`, false);
        }
      };
      reader.readAsText(file);
    }
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
        {isLoading && <div className="loading-indicator">Processing...</div>}
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
          <AttachFileSharpIcon />
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
          <SendButton />
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;