from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_community.chat_models import ChatOpenAI
from langchain_openai import AzureOpenAI
from operator import itemgetter

from decouple import config
# from qdrant import vectorstore
from qdrant import embeddings

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
Jika tidak ada dalam dokumen, jawab tidak ada dengan bahasa yang baik.

Context: {context}
Question: {question}
Answer:
"""

prompt = ChatPromptTemplate.from_template(prompt_design)