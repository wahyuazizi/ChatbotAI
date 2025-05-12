from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_community.chat_models import AzureChatOpenAI
from langchain_openai import AzureOpenAI
from operator import itemgetter

from decouple import config
from src.my_qdrant import vector_store, embeddings


azure_openai_gpt_key = config("AZURE_OPENAI_GPT_API_KEY")
azure_openai_gpt_endpoint = config("AZURE_OPENAI_GPT_ENDPOINT")

model = AzureChatOpenAI(
    azure_deployment="gpt-35-turbo",
    api_version="2024-12-01-preview",
    endpoint=azure_openai_gpt_endpoint,
    api_key=azure_openai_gpt_key
)

prompt_design = """
Kamu berperan sebagai admin penyedia informasi untuk Universitas Hamzanwadi.
Kamu akan menjawab semua seputar pertanyaan kampus dan pendidikan yang ada di kampus Universitas Hamzanwadi.
Jawab berdasarkan konteks yang diberikan.

Context: {context}
Question: {question}
Answer:
"""

prompt = ChatPromptTemplate.from_template(prompt_design)

retriever = vector_store.as_retriever(search_kwargs={"k": 3})

def create_chain():
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