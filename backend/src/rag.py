from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAI
from operator import itemgetter

from decouple import config
from src.my_qdrant import vector_store


azure_openai_gpt_key = config("AZURE_OPENAI_GPT_API_KEY")
azure_openai_gpt_endpoint = config("AZURE_OPENAI_GPT_ENDPOINT")

model = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    api_version="2024-12-01-preview",
    azure_endpoint=azure_openai_gpt_endpoint,
    api_key=azure_openai_gpt_key
)

PROMPT_DESIGN = """
Kamu berperan sebagai admin penyedia informasi untuk Universitas Hamzanwadi.
Kamu akan menjawab semua seputar pertanyaan kampus dan pendidikan yang ada di kampus Universitas Hamzanwadi.
Jawab berdasarkan konteks yang diberikan.

Context: {context}
Question: {question}
Answer:
"""

prompt = ChatPromptTemplate.from_template(PROMPT_DESIGN)

retriever = vector_store.as_retriever(search_kwargs={"k": 3})

def create_chain():
    """
    Create a chain that retrieves context and generates a response.
    """
    chain = (
        {
            "context": retriever.with_config(
                return_only_outputs=True,
                run_name="retriever",
                top_k=3,
            ),
            "question": RunnablePassthrough().with_config(
                run_name="question",
            ),
        }
        | RunnableParallel(
            {
                "response": prompt | model,
                "context": itemgetter("context"),
            }
        )
    )

    return chain

def get_answer_and_docs(question:str):
    """
    Get the answer and documents for a given question.
    """
    chain = create_chain()
    result = chain.invoke(question)
    answer = result["response"]
    context = result["context"]
    
    return {
        "answer": answer,
        "context": context
    }

# response = get_answer_and_docs("Apa itu Universitas Hamzanwadi?")
# print(response["answer"])