// frontend/src/App.tsx

import React, { useState } from "react";
import ChatBox from "./components/ChatBox";
import InputForm from "./components/InputForm";
import axios from "axios";

interface Message {
  sender: string;
  content: string;
  type: "user" | "assistant" | "system" | "error";
}

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);

  const handleNewMessage = (sender: string, content: string, type: "user") => {
    setMessages((prev) => [...prev, { sender, content, type }]);
  };

  const handleNewAssistantMessage = (
    content: string,
    type: "assistant" | "system"
  ) => {
    setMessages((prev) => [...prev, { sender: "Assistant", content, type }]);
  };

  const handleError = (message: string) => {
    setMessages((prev) => [
      ...prev,
      { sender: "Error", content: message, type: "error" },
    ]);
  };

  const handleForget = async () => {
    try {
      const response = await axios.post("/api/forget");
      if (response.data.status === "success") {
        handleNewAssistantMessage("Last conversation forgotten.", "system");
      } else {
        handleError(response.data.message);
      }
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        handleError(error.message);
      } else {
        handleError("An unexpected error occurred.");
      }
    }
  };

  const handleRecall = async (prompt: string) => {
    try {
      const formData = new FormData();
      formData.append("prompt", prompt);

      const response = await axios.post("/api/recall", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      if (response.data.status === "success") {
        const assistantResponse = response.data.response;
        handleNewAssistantMessage(assistantResponse, "assistant");
      } else {
        handleError(response.data.message);
      }
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        handleError(error.message);
      } else {
        handleError("An unexpected error occurred.");
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-white shadow-md rounded-md p-6">
        <h1 className="text-2xl font-bold mb-4 text-center">
          RAG AI Assistant
        </h1>
        <ChatBox messages={messages} />
        <InputForm
          onNewMessage={handleNewMessage}
          onNewAssistantMessage={handleNewAssistantMessage}
          onError={handleError}
        />
        <div className="flex justify-end mt-4 space-x-2">
          <button
            onClick={handleForget}
            className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500"
          >
            Forget Last Conversation
          </button>
          <button
            onClick={() => handleRecall("Your prompt here")}
            className="px-4 py-2 bg-yellow-500 text-white rounded-md hover:bg-yellow-600 focus:outline-none focus:ring-2 focus:ring-yellow-500"
          >
            Recall
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;
