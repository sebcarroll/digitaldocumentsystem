import React, { useEffect, useRef } from 'react';
import BotIcon from '../chatInterface/chatInterfaceSubComponents/botIcon.js';
import DOMPurify from 'dompurify';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css'; // Choose a style
import './message.css';

function Message({ text, isUser }) {
  const messageRef = useRef(null);

  useEffect(() => {
    if (messageRef.current) {
      messageRef.current.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightBlock(block);
      });
    }
  }, [text]);

  return (
    <div className={`message ${isUser ? 'user-message' : 'bot-message'}`}>
      {!isUser && (
        <div className="bot-icon-background">
          <BotIcon />
        </div>
      )}
        <div 
          ref={messageRef}
          className="message-text"
          dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(text) }}
        />
      </div>
  );
}

export default Message;