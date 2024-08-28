import React, { useState, useRef, useEffect } from 'react';
import '../../pages/chatInterface.css';

function InputArea({ onSendMessage, onUploadDocuments }) {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      onSendMessage(input, true);
      setInput('');
    }
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    onUploadDocuments(files);
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  return (
    <form className="input-area" onSubmit={handleSubmit}>
      <label htmlFor="file-upload" className="file-upload-label">
        <i className="paperclip-icon"></i>
      </label>
      <input
        id="file-upload"
        type="file"
        multiple
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />
      <textarea
        ref={textareaRef}
        value={input}
        onChange={handleInputChange}
        placeholder="Type your message..."
        className="message-input"
        rows="1"
      />
      <button type="submit" className="send-button">
        Send
      </button>
    </form>
  );
}

export default InputArea;