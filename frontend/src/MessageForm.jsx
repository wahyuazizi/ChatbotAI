
import { useState } from 'react';
import axios from 'axios';

const api = axios.create({
  baseURL: "http://localhost:8000/",
  headers: {
    'Content-Type': 'application/json',
  }
});

export function TextareaWithButton() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log("Button clicked");

    if (!question.trim()) {
      return;
    }

    // Add user message to chat history immediately
    setChatHistory(prev => [
      ...prev, 
      { type: 'user', content: question }
    ]);
    
    // Save current question and clear input
    const currentQuestion = question;
    setQuestion("");

    setLoading(true);
    setError("");

    try {
      console.log("Sending request with message:", question);

      const response = await api.post("/chat", { message: question });
      console.log("Received response:", response.data);

      // Handle the answer text
      if (response.data.answer) {
        // Add bot response to chat history
        setChatHistory(prev => [
          ...prev, 
          { 
            type: 'bot', 
            content: response.data.answer,
            documents: response.data.documents && Array.isArray(response.data.documents) 
              ? response.data.documents 
              : []
          }
        ]);
      } else {
        setChatHistory(prev => [
          ...prev, 
          { type: 'bot', content: "No answer received", documents: [] }
        ]);
      }

      // Handle the documents
      if (response.data.documents && Array.isArray(response.data.documents)) {
        setDocuments(response.data.documents);
      } else {
        setDocuments([]);
      }
    } catch (err) {
      console.error("Error sending message:", err);

      // Provide better error feedback
      let errorMessage = "An unknown error occurred";
      
      if (err.response) {
        // The server responded with an error status
        errorMessage = err.response.data.error || 'Unknown server error';
        setError(`Error ${err.response.status}: ${errorMessage}`);
        console.error("Server error details:", err.response.data);
      } else if (err.request) {
        // The request was made but no response received
        errorMessage = "No response from server. Is the server running?";
        setError(errorMessage);
      } else {
        // Something else went wrong
        errorMessage = `Error: ${err.message}`;
        setError(errorMessage);
      }

      // Add error message to chat
      setChatHistory(prev => [
        ...prev, 
        { type: 'error', content: errorMessage }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Function to format document content for display
  const formatDocumentContent = (doc) => {
    if (!doc) return "No content";

    // Check if it's a document with page_content
    if (doc.page_content) {
      // Truncate long content
      const content = doc.page_content;
      return content.length > 100 ? content.substring(0, 100) + '...' : content;
    }

    // For other formats, convert to string and truncate
    const content = typeof doc === 'string' ? doc : JSON.stringify(doc);
    return content.length > 100 ? content.substring(0, 100) + '...' : content;
  };

  return (
    <div className="max-w-2xl mx-auto p-4 pb-20"> {/* Padding bawah untuk fixed input */}
      {/* Pesan Error */}
      {error && (
        <div className="text-red-500 w-full mb-4 p-2 border border-red-300 rounded">
          {error}
        </div>
      )}

      {/* Jawaban */}
      {answer && (
        <div className="w-full mb-4 p-4 border rounded ">
          <h2 className="text-lg font-semibold mb-2">Jawaban</h2>
          <p className="text-left whitespace-pre-wrap">{answer}</p>

          {/* {documents.length > 0 && (
        <div className="mt-4">
          <h3 className="text-md font-semibold mb-1">Sumber Informasi:</h3>
          <ul className="list-disc pl-5">
            {documents.map((doc, index) => (
              <li key={index} className="text-sm text-gray-700">
                {formatDocumentContent(doc)}
              </li>
            ))}
          </ul>
        </div>
      )} */}
        </div>
      )}

      {/* Input dengan tombol di dalamnya - versi alternatif */}
      <div className="fixed bottom-0 left-0 right-0 p-4 shadow-md">
        <div className="max-w-2xl mx-auto relative rounded-xl border focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Tanyakan sesuatu tentang Universitas Hamzanwadi..."
            disabled={loading}
            className="min-h-10 max-h-60 w-full p-3 pr-16 border-none focus:outline-none resize-none rounded-xl"
          />

          <button
            type='submit'
            onClick={handleSubmit}
            disabled={loading}
            className="absolute right-2 bottom-2.5 p-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors"
          >
            {loading ?
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg> :
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd" />
              </svg>
            }
          </button>
        </div>
      {/* Footer di bagian bawah layar */}
      <footer className="w-full py-2">
        <div className="max-w-2xl mx-auto text-center text-sm text-gray-500">
          Made with ❤️ and Dedication by Wahyu Azizi
        </div>
      </footer>
      </div>
    </div>
  );
}