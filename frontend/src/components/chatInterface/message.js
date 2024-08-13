import React from 'react';
import Icon from './Icon';

function Message({ text, isUser }) {
  return (
    <div className={`message ${isUser ? 'user-message' : 'bot-message'}`}>
      {!isUser && (
        <div className="bot-icon-background">
          <Icon />
        </div>
      )}
      <div className="message-text">{text}</div>
    </div>
  );
}

export default Message;