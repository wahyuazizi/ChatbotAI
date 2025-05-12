from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.rag import get_answer_and_docs
from src.my_qdrant import upload_website_to_collection

app = FastAPI(
    title="Chatbot Artificial Intelligence",
    description="Chatbot AI API",
    version="1.0.0",
)

@app.post("/chat")
def chat(message: str):
    response = get_answer_and_docs(message)
    response_content = {
        "question": message,
        "answer": response["answer"].content,
        "documents": [doc.dict() for doc in response["context"]]
    }
    return JSONResponse(content=response_content, status_code=200)

@app.post("/indexing")
def indexing(url:str):
    try:
        response = upload_website_to_collection(url)
        return JSONResponse(content={"response":response}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)