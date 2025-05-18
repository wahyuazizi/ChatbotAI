# from fastapi import FastAPI
# from fastapi.responses import JSONResponse
# from src.rag import get_answer_and_docs
# from src.my_qdrant import upload_website_to_collection
# from pydantic import BaseModel

# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI(
#     title="Chatbot Artificial Intelligence",
#     description="Chatbot AI API",
#     version="1.0.0",
# )

# origins = [
#     "http://localhost:5173",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class Message(BaseModel):
#     message: str

# @app.post("/chat")
# def chat(message: Message):
#     message_text = message.message
#     response = get_answer_and_docs(message)
#     response_content = {
#         "question": message,
#         "answer": str(response["answer"]),
#         "documents": [doc.dict() for doc in response["context"]]
#     }
#     return JSONResponse(content=response_content, status_code=200)

# @app.post("/indexing")
# def indexing(url:str):
#     try:
#         response = upload_website_to_collection(url)
#         return JSONResponse(content={"response":response}, status_code=200)
#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=400)

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from src.rag import get_answer_and_docs
from src.my_qdrant import upload_website_to_collection
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Chatbot Artificial Intelligence",
    description="Chatbot AI API",
    version="1.0.0",
)

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    message: str

@app.post("/chat")
def chat(message: Message):
    try:
        # Extract message string from the Message object
        message_text = message.message
        logger.info("Received message: %s", message_text)
        
        # Get response from RAG system
        response = get_answer_and_docs(message_text)
        
        # The answer is a langchain_core.messages.AIMessage object
        # which has a 'content' attribute with the actual text
        answer_text = ""
        if response and "answer" in response:
            answer = response["answer"]
            # Check if answer has a 'content' attribute
            if hasattr(answer, "content"):
                answer_text = answer.content
            else:
                # If it's a string or has __str__
                answer_text = str(answer)
        
        # Process context documents
        documents = []
        if "context" in response and response["context"]:
            for doc in response["context"]:
                if hasattr(doc, "page_content") and hasattr(doc, "metadata"):
                    # Standard Document object
                    doc_dict = {
                        "page_content": doc.page_content,
                        "metadata": doc.metadata
                    }
                    documents.append(doc_dict)
                elif hasattr(doc, "dict"):
                    # Object with dict method
                    documents.append(doc.dict())
                elif isinstance(doc, dict):
                    # Already a dictionary
                    documents.append(doc)
                else:
                    # Fallback for other types
                    documents.append({
                        "page_content": str(doc),
                        "metadata": {}
                    })
        
        response_content = {
            "question": message_text,
            "answer": answer_text,
            "documents": documents
        }
        
        logger.info("Prepared response content: %s", response_content)
        return JSONResponse(content=response_content, status_code=200)
    
    except Exception as e:
        logger.error("Error processing chat request: %s", str(e), exc_info=True)
        return JSONResponse(
            content={"error": f"Failed to process request: {str(e)}"},
            status_code=500
        )

@app.post("/indexing")
def indexing(url: str):
    try:
        response = upload_website_to_collection(url)
        return JSONResponse(content={"response": response}, status_code=200)
    except Exception as e:
        logger.error("Error processing indexing request: %s", str(e), exc_info=True)
        return JSONResponse(content={"error": str(e)}, status_code=400)