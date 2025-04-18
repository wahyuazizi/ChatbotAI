from fastapi import FastAPI
from fastapi.responses import JSONResponse


app = FastAPI(
    title="ChatbotAI RAG",
    description="ChatbotAI dengan teknik RAG untuk menyelesaikan Skripsi",
    version="0.1.0"
)

@app.post('/chat')
def chat(message: str):
    return JSONResponse(content={
        "pesanmu": message
    },
    status_code=200
    )
