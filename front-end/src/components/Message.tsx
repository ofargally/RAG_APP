import React from "react";

interface MessageProps {
  sender: string;
  content: string;
  type: "user" | "assistant" | "system" | "error";
}

const Message: React.FC<MessageProps> = ({ sender, content, type }) => {
  const baseStyle = "p-2 rounded-md";
  const senderStyles = {
    user: "bg-blue-100 text-blue-800 self-end",
    assistant: "bg-green-100 text-green-800 self-start",
    system: "bg-gray-200 text-gray-800 text-center",
    error: "bg-red-100 text-red-800 text-center",
  };

  return (
    <div
      className={`flex ${
        type !== "system" && type !== "error"
          ? type === "user"
            ? "justify-end"
            : "justify-start"
          : "justify-center"
      } mb-2`}
    >
      <div className={`${baseStyle} ${senderStyles[type]} max-w-xs`}>
        <strong>{sender}:</strong> {content}
      </div>
    </div>
  );
};

export default Message;
