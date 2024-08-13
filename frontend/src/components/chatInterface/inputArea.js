import React, { useState } from 'react';

function InputArea({ onSendMessage, onUploadDocuments }) {
  const [input, setInput] = useState('');

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
  );
}

export default InputArea;