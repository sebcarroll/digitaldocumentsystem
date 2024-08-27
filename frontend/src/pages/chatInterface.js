import React, { useState, useEffect, useCallback, useRef } from 'react';
import './chatInterface.css';
import BotIcon from '../components/chatInterface/chatInterfaceSubComponents/botIcon.js';
import { sendQuery, uploadDocument, openDriveFile, clearChatHistory } from '../services/api';
import SendButton from '../components/drivePage/searchbarSubComponents/searchbarSendButton.js';
import AttachFileSharpIcon from '@mui/icons-material/AttachFileSharp';
import UploadPopup from '../components/chatInterface/uploadDocumentPopup.js';
import { useUploadDocument } from '../hooks/useUploadDocument';
import Message from './Message';

const ChatInterface = ({ initialQuery, onClose, getFileIcon }) => {
  console.log('ChatInterface rendering', { initialQuery });
  
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploadPopupOpen, setIsUploadPopupOpen] = useState(false);

  const messageListRef = useRef(null);

  const addMessage = useCallback((text, isUser) => {
    setMessages(prevMessages => [...prevMessages, { text, isUser }]);
  }, []);

  useEffect(() => {
    if (initialQuery) {
      addMessage(initialQuery, true);
      handleQuery(initialQuery);
    }

    return () => {
      clearChatHistory();
    };
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

  const scrollToBottom = () => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const setError = (errorMessage) => {
    console.error('Error in ChatInterface:', errorMessage);
    addMessage(`Error: ${errorMessage}`, false);
  };

  const uploadDocumentHook = useUploadDocument(setError);

  const handleFileIconClick = () => {
    console.log('File icon clicked, opening upload popup');
    setIsUploadPopupOpen(true);
    uploadDocumentHook.handleOpen();
  };

  const handleUploadPopupClose = () => {
    console.log('Closing upload popup');
    setIsUploadPopupOpen(false);
    uploadDocumentHook.handleClose();
  };

  const handleFileUpload = async (selectedFiles) => {
    console.log('Handling file upload', selectedFiles);
    for (const file of selectedFiles) {
      try {
        const fileDetails = await openDriveFile(file.id);
        await uploadDocument(fileDetails);
        setDocuments(prev => [...prev, fileDetails]);
        addMessage(`Document "${fileDetails.name}" uploaded and processed successfully.`, false);
      } catch (error) {
        console.error('Error uploading document:', error);
        addMessage(`Failed to upload document "${file.name}". Please try again.`, false);
      }
    }
    setIsUploadPopupOpen(false);
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <button onClick={onClose} className="close-button">×</button>
      </div>
      <div className="message-list" ref={messageListRef}>
        {messages.map((message, index) => (
          <Message key={index} text={message.text} isUser={message.isUser} />
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
        <div className="file-upload-label" onClick={handleFileIconClick}>
          <AttachFileSharpIcon />
        </div>
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
      <UploadPopup
        getFileIcon={getFileIcon}
        setError={setError}
        isOpen={isUploadPopupOpen}
        onClose={handleUploadPopupClose}
        onUpload={handleFileUpload}
        {...uploadDocumentHook}
      />
    </div>
  );
};

export default ChatInterface;