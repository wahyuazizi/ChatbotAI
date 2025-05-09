from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Chatbot Artificial Intelligence",
    description="Chatbot AI API",
    version="1.0.0",
)

@app.post("/chat")
def chat(message: str):
    return JSONResponse(content={"Your message": message}, status_code=200)