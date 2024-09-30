import React, { useEffect, useRef } from "react";
import Message from "./Message";

interface ChatBoxProps {
  messages: {
    sender: string;
    content: string;
    type: "user" | "assistant" | "system" | "error";
  }[];
}

const ChatBox: React.FC<ChatBoxProps> = ({ messages }) => {
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col h-96 overflow-y-scroll border border-gray-300 p-4 bg-gray-50 rounded-md">
      {messages.map((msg, index) => (
        <Message
          key={index}
          sender={msg.sender}
          content={msg.content}
          type={msg.type}
        />
      ))}
      <div ref={chatEndRef} />
    </div>
  );
};

export default ChatBox;
