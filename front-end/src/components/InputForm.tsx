import React, { useState } from "react";
import axios from "axios";

interface InputFormProps {
  onNewMessage: (sender: string, content: string, type: "user") => void;
  onNewAssistantMessage: (content: string, type: "assistant") => void;
  onError: (message: string) => void;
}

const InputForm: React.FC<InputFormProps> = ({
  onNewMessage,
  onNewAssistantMessage,
  onError,
}) => {
  const [prompt, setPrompt] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim() === "") return;

    onNewMessage("You", prompt, "user");
    setPrompt("");
    setLoading(true);

    const formData = new FormData();
    formData.append("prompt", prompt);
    if (apiKey.trim() !== "") {
      formData.append("llm_api_key", apiKey);
    }

    try {
      const response = await axios.post("/api/chat", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      if (response.data.status === "success") {
        // For simplicity, we'll assume the assistant's response is immediately available.
        // In a real-world scenario, you might implement streaming or polling.
        // Here, you can fetch the latest response or modify the backend to return it directly.
        // As per the current backend setup, it doesn't return the assistant's response,
        // so you might need to adjust the backend to return it.
        // For now, we'll leave it as is.
      } else {
        onError(response.data.message);
      }
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        onError(error.message);
      } else {
        onError("An unknown error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      className="flex flex-col sm:flex-row mt-4 space-y-2 sm:space-y-0 sm:space-x-2"
      onSubmit={handleSubmit}
    >
      <input
        type="text"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Type your message here..."
        className="flex-1 p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        required
      />
      <input
        type="text"
        value={apiKey}
        onChange={(e) => setApiKey(e.target.value)}
        placeholder="LLM API Key (optional)"
        className="flex-1 p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        type="submit"
        className={`p-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
          loading ? "opacity-50 cursor-not-allowed" : ""
        }`}
        disabled={loading}
      >
        {loading ? "Sending..." : "Send"}
      </button>
    </form>
  );
};

export default InputForm;
