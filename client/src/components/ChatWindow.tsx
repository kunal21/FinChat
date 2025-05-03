import React, { useState } from 'react';

interface Props {
  userId: number;
}

const ChatWindow: React.FC<Props> = ({ userId }) => {
  const [messages, setMessages] = useState<string[]>([]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim()) {
      setMessages([...messages, input]);
      setInput('');
    }
  };

  return (
    <div className="chatWindow">
      <div className="chatMessages">
        {messages.map((msg, index) => (
          <div key={index} className="chatMessage">
            {msg}
          </div>
        ))}
      </div>
      <div className="chatInput">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default ChatWindow;