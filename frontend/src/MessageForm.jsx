import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const api = axios.create({
  baseURL: "http://localhost:8000/",
  headers: {
    'Content-Type': 'application/json',
  }
});

export function TextareaWithButton() {
  const [question, setQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  // Ubah dari chatContainerRef menjadi messagesEndRef
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Add a CSS rule to show scrollbars without layout shift
    const style = document.createElement('style');
    style.textContent = `
      html {
        overflow-y: scroll;
      }
      
      body {
        overflow-x: hidden;
        padding-right: 0 !important; /* Prevent padding shifts */
      }
      
      /* For Firefox */
      * {
        scrollbar-width: thin;
      }
      
      /* For Webkit browsers */
      ::-webkit-scrollbar {
        width: 6px;
      }
      
      ::-webkit-scrollbar-track {
        background: transparent;
      }
      
      ::-webkit-scrollbar-thumb {
        background-color: rgba(155, 155, 155, 0.5);
        border-radius: 20px;
      }
    `;
    document.head.appendChild(style);

    return () => {
      document.head.removeChild(style);
    };
  }, []);

  // Perbaikan auto-scroll menggunakan scrollIntoView
  useEffect(() => {
    // Gunakan timeout untuk memastikan DOM telah diupdate sebelum scroll
    const timeoutId = setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 100);

    return () => clearTimeout(timeoutId);
  }, [chatHistory, loading]);

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
      console.log("Sending request with message:", currentQuestion);

      const response = await api.post("/chat", { message: currentQuestion });
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
    <div className="max-w-2xl mx-auto p-4 pb-20">
      {/* Error Banner (if needed outside of chat) */}
      {error && (
        <div className="alert alert-error mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{error}</span>
        </div>
      )}

      {/* Chat History - tanpa ref pada container utama */}
      <div className="mb-16 flex flex-col space-y-3">
        {/* Welcome Message */}
        {chatHistory.length === 0 && (
          <div className="text-center p-6 text-gray-500">
            <h1 style={{ fontFamily: 'Faculty Glyphic, sans-serif' }} className="text-3xl font-bold mb-2">Selamat Datang!</h1>

            <h3 className='font-semibold text-xl'>Tanyakan sesuatu tentang Universitas Hamzanwadi</h3>
          </div>
        )}

        {/* Messages */}
        {chatHistory.map((msg, index) => (
          <div key={index} className={`chat ${msg.type === 'user' ? 'chat-end' : 'chat-start'}`}>
            <div className={`chat-bubble rounded-2xl ${msg.type === 'error'
                ? 'chat-bubble-error'
                : msg.type === 'user'
                  ? 'chat-bubble-success'
                  : ''
              }`}>
              <div className="whitespace-pre-wrap text-left">{msg.content}</div>

              {/* Show documents sources if available */}
              {msg.documents && msg.documents.length > 0 && (
                <div className="mt-2 opacity-70 text-xs">
                  <details className="collapse collapse-arrow bg-base-200 bg-opacity-40">
                    <summary className="collapse-title py-1 px-2 min-h-0">Sumber Informasi</summary>
                    <div className="collapse-content text-left">
                      <ul className="list-disc list-inside">
                        {msg.documents.map((doc, idx) => (
                          <li key={idx} className="text-xs">
                            {formatDocumentContent(doc)}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </details>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading indicator as a message bubble */}
        {loading && (
          <div className="chat chat-start">
            <div className="chat-bubble">
              <div className="flex items-center gap-2">
                <span className="loading loading-dots loading-sm"></span>
                <span>Memikirkan jawaban...</span>
              </div>
            </div>
          </div>
        )}

        {/* Elemen kosong untuk target scrollIntoView */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input with button */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-base-100 shadow-md">
        <div className="max-w-2xl mx-auto">
          <form onSubmit={handleSubmit} className="relative">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Tanyakan sesuatu tentang Universitas Hamzanwadi..."
              disabled={loading}
              className="textarea textarea-bordered border-2 w-full pr-14 min-h-12 resize-none rounded-2xl"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />
            <button
              type="submit"
              disabled={loading || !question.trim()}
              className="btn btn-soft btn-success absolute right-2 bottom-2 rounded-2xl"
            >
              {loading ? (
                <span className="loading loading-spinner loading-sm"></span>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd" />
                </svg>
              )}
            </button>
          </form>

          {/* Footer */}
          <footer className="w-full py-2">
            <div className="text-center text-sm text-gray-500">
              Made with ❤️ and Dedication by Wahyu Azizi
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}