import React, { useState, useEffect, useRef, useMemo } from 'react';
import '../index.scss';
import '../App.scss';
import { motion, AnimatePresence } from 'framer-motion';
import { useMessages } from '../services/messages.tsx';
interface Props {
  userId: number;
}


const ChatWindow: React.FC<Props> = ({ userId }) => {
    interface Message {
        id: number;
        text: string;
        author: string;
    }

    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const listRef = useRef<HTMLDivElement>(null);
    const timeoutRef = useRef(null);
    const { messagesById, getMessagesByUser, sendMessage, deleteAllMessagesByUser } = useMessages();

    useEffect(() => {
        const sorted = Object.values(messagesById).sort((a, b) => a.id - b.id);
        setMessages(sorted);
    },[messagesById]);

    // When a new bot message arrives, clear typing
    useEffect(() => {
        const last = messages[messages.length - 1];
        console.log("last = ", last)
        if (last && last.author === 'bot') {
            setIsTyping(false);
        }
    }, [messages]);

    useEffect(() => {
      if (listRef.current) {
        listRef.current.scrollTop = listRef.current.scrollHeight;
      }
    }, [messages]);

    useEffect(() => {
        getMessagesByUser(userId);
    }, [getMessagesByUser, userId]);
  
    useEffect(() => () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    }, []);
  
    const handleClear = () => {
        deleteAllMessagesByUser(userId);
    };

    const handleSend = () => {
        const text = input.trim();
        if (!text) return;
        setInput('');
        setIsTyping(true);
        sendMessage(userId, text);
    };
  
    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    };
  
    return (
      <div className="App">
        <div ref={listRef} className="transactions-body">
          <AnimatePresence initial={false}>
            {messages.map(msg => (
              <motion.div key={msg.id.toString()} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                  <div style={{ display: 'flex', justifyContent: msg.author === 'user' ? 'flex-end' : 'flex-start', marginBottom: '1rem' }}>
                    <div className="box" style={{ backgroundColor: msg.author === 'user' ? '#D1E8FF' : '#FFFFFF', maxWidth: '60%', padding: '1rem' }}>
                      <p>{msg.text}</p>
                    </div>
                  </div>
              </motion.div>
            ))}
            {isTyping && (
              <motion.div key="typing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '1rem' }}>
                  <div className="box" style={{ maxWidth: '60%', padding: '1rem', opacity: 0.7 }}>
                    <p className="heading">Typing...</p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        <div className="box" style={{ padding: '1rem' }}>
          <textarea
            rows={2}
            placeholder="Type a message"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            style={{ width: '100%', resize: 'none' }}
          />
          <button className="btnWithMargin" onClick={handleSend} style={{ marginTop: '0.5rem' }}>
            Send
          </button>
        </div>
        <button className="btnWithMargin" onClick={handleClear} style={{ margin: '1rem' }}>
            Clear Chat
        </button>
      </div>
    );
};

function TypingIndicator() {
    return (
      <div style={{ fontStyle: 'italic' }}>
        <p>Typing...</p>
      </div>
    );
}
  

export default ChatWindow;