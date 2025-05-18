// import { useState } from 'react'
// import { Button } from "@/components/ui/button"
// import { Textarea } from "@/components/ui/textarea"
// import axios from 'axios'

// const api = axios.create({
//     baseURL: "http://localhost:8000/"
// })

// export function MessageWithButton() {
//     const [question, setQuestion] = useState("");
//     const [answer, setAnswer] = useState("");

//     const handleSubmit = async (e) => {
//         e.preventDefault();
//         console.log("Button clicked");
//         const response = await api.post("/chat", {message: question})
//         setAnswer(response.data.answer)
//     }

//     return (
//         <div className="grid items-center justify-center gap-2">
//             <Textarea value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Type your message here." />
//             <Button type='submit' onClick={handleSubmit} >Kirim</Button>
//             <div>
//                 <h1>Answer</h1>
//                 <p>{answer}</p>
//             </div>
//         </div>
//     )
// }
import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import axios from 'axios';

const api = axios.create({ 
  baseURL: "http://localhost:8000/",
  headers: {
    'Content-Type': 'application/json',
  }
});

export function MessageWithButton() {
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
    
    setLoading(true);
    setError("");
    
    try {
      console.log("Sending request with message:", question);
      
      const response = await api.post("/chat", { message: question });
      console.log("Received response:", response.data);
      
      // Handle the answer text
      if (response.data.answer) {
        setAnswer(response.data.answer);
      } else {
        setAnswer("No answer received");
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
      if (err.response) {
        // The server responded with an error status
        const errorMessage = err.response.data.error || 'Unknown server error';
        setError(`Error ${err.response.status}: ${errorMessage}`);
        console.error("Server error details:", err.response.data);
      } else if (err.request) {
        // The request was made but no response received
        setError("No response from server. Is the server running?");
      } else {
        // Something else went wrong
        setError(`Error: ${err.message}`);
      }
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
    <div className="grid items-center justify-center gap-2 p-4 max-w-2xl mx-auto">
      <h3 className="text-xl font-bold mb-2 text-center">Universitas Hamzanwadi Chatbot</h3>
      
      <Textarea 
        value={question} 
        onChange={(e) => setQuestion(e.target.value)} 
        placeholder="Tanyakan sesuatu tentang Universitas Hamzanwadi..."
        disabled={loading}
        className="min-h-20 "
      />
      
      <Button 
        type='submit' 
        onClick={handleSubmit}
        disabled={loading}
        className="w-full"
      >
        {loading ? "Mengirim..." : "Kirim"}
      </Button>
      
      {error && (
        <div className="text-red-500 mt-2 p-2 border border-red-300 rounded">
          {error}
        </div>
      )}
      
      {answer && (
        <div className="mt-4 p-4 border rounded bg-gray-50">
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
    </div>
  );
}