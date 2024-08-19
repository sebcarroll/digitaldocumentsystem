import React, { useState, useEffect, useCallback } from 'react';
import './chatInterface.css';
import BotIcon from '../components/chatInterface/chatInterfaceSubComponents/botIcon.js';
import { sendQuery, addDocument, updateDocument, deleteDocument } from '../services/api.js';

const ChatInterface = ({ initialQuery, onClose }) => {
  console.log('ChatInterface rendering', { initialQuery });
  
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const addMessage = useCallback((text, isUser) => {
    setMessages(prevMessages => [...prevMessages, { text, isUser }]);
  }, []);

  useEffect(() => {
    if (initialQuery) {
      addMessage(initialQuery, true);
      handleQuery(initialQuery);
    }
  }, [initialQuery, addMessage]);

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

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      addMessage(input, true);
      handleQuery(input);
      setInput('');
    }
  };

  const handleFileChange = async (e) => {
    const files = Array.from(e.target.files);
    setDocuments(prevDocuments => [...prevDocuments, ...files]);

    for (const file of files) {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const content = e.target.result;
        try {
          const document = {
            id: file.name,
            content: content,
            type: file.type,
          };
          await addDocument(document);
          addMessage(`Document "${file.name}" uploaded and processed successfully.`, false);
        } catch (error) {
          console.error('Error uploading document:', error);
          addMessage(`Failed to upload document "${file.name}". Please try again.`, false);
        }
      };
      reader.readAsText(file);
    }
  };

  const handleUpdateDocument = async (documentId, newContent) => {
    try {
      await updateDocument({ id: documentId, content: newContent });
      addMessage(`Document "${documentId}" updated successfully.`, false);
    } catch (error) {
      console.error('Error updating document:', error);
      addMessage(`Failed to update document "${documentId}". Please try again.`, false);
    }
  };

  const handleDeleteDocument = async (documentId) => {
    try {
      await deleteDocument(documentId);
      setDocuments(prevDocuments => prevDocuments.filter(doc => doc.name !== documentId));
      addMessage(`Document "${documentId}" deleted successfully.`, false);
    } catch (error) {
      console.error('Error deleting document:', error);
      addMessage(`Failed to delete document "${documentId}". Please try again.`, false);
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
          {documents.map((doc, index) => (
            <div key={index} className="document-item">
              <span>{doc.name}</span>
              <button onClick={() => handleDeleteDocument(doc.name)}>Delete</button>
            </div>
          ))}
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