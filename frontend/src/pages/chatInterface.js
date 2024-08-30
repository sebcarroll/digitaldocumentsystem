import React, { useState, useEffect, useCallback, useRef } from 'react';
import './chatInterface.css';
import { sendQuery, uploadDocument, openDriveFile, clearChatHistory, uploadSelectedDocuments, updateDocumentSelection } from '../services/api';
import SendButton from '../components/drivePage/searchbarSubComponents/searchbarSendButton.js';
import AttachFileSharpIcon from '@mui/icons-material/AttachFileSharp';
import UploadPopup from '../components/chatInterface/uploadDocumentPopup.js';
import { useUploadDocument } from '../hooks/useUploadDocument';
import Message from '../components/chatInterface/message.js';
import SelectedDocuments from '../components/chatInterface/documentList.js';

const ChatInterface = ({ initialQuery, onClose, getFileIcon }) => {
  console.log('ChatInterface rendering', { initialQuery });
  
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploadPopupOpen, setIsUploadPopupOpen] = useState(false);
  const [selectedDocuments, setSelectedDocuments] = useState([]);

  const messageListRef = useRef(null);
  const textareaRef = useRef(null);

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

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      const newHeight = Math.max(scrollHeight, parseInt(getComputedStyle(textareaRef.current).getPropertyValue('min-height')));
      textareaRef.current.style.height = `${newHeight}px`;
      
      // Show scrollbar only when content exceeds max height
      if (scrollHeight > 150) {
        textareaRef.current.style.overflowY = 'auto';
      } else {
        textareaRef.current.style.overflowY = 'hidden';
      }
    }
  }, [input]);

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
    try {
      const result = await uploadSelectedDocuments(selectedFiles);
      setSelectedDocuments(prevDocs => [...prevDocs, ...selectedFiles]);
      addMessage(`${result.successful_uploads} out of ${result.total_files} document(s) uploaded and processed successfully.`, false);
    } catch (error) {
      console.error('Error uploading documents:', error);
      addMessage(`Failed to upload documents. Please try again.`, false);
    }
    handleUploadPopupClose();
  };

  const handleRemoveDocument = async (docId) => {
    try {
      await updateDocumentSelection(docId, false);
      setSelectedDocuments(prev => prev.filter(doc => doc.id !== docId));
      addMessage(`Document removed from selection.`, false);
    } catch (error) {
      console.error('Error removing document:', error);
      addMessage(`Failed to remove document. Please try again.`, false);
    }
  };

  const handleClose = () => {
    clearChatHistory();
    onClose();
  };
  

  return (
    <div className="chat-interface">
      <div className="chat-header">
      <button onClick={handleClose} className="close-button">×</button>
      </div>
      <div className="message-list" ref={messageListRef}>
        {messages.map((message, index) => (
          <Message key={index} text={message.text} isUser={message.isUser} />
        ))}
        {isLoading && <div className="loading-indicator">Processing...</div>}
      </div>
      <SelectedDocuments 
        documents={selectedDocuments} 
        onRemove={handleRemoveDocument} 
      />
      <form onSubmit={handleSubmit} className="input-area">
        <div className="file-upload-label" onClick={handleFileIconClick}>
          <AttachFileSharpIcon />
        </div>
        <textarea
          ref={textareaRef}
          value={input}
          onChange={handleInputChange}
          placeholder="Type your message..."
          className="message-input"
          rows="1"
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