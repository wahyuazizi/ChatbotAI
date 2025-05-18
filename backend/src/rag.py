# from langchain_core.prompts.chat import ChatPromptTemplate
# from langchain_core.runnables import RunnablePassthrough, RunnableParallel
# from langchain_openai import AzureChatOpenAI
# from langchain_openai import AzureOpenAI
# from operator import itemgetter

# from decouple import config
# from src.my_qdrant import vector_store
# import logging


# azure_openai_gpt_key = config("AZURE_OPENAI_GPT_API_KEY")
# azure_openai_gpt_endpoint = config("AZURE_OPENAI_GPT_ENDPOINT")

# model = AzureChatOpenAI(
#     azure_deployment="gpt-4o-mini",
#     api_version="2024-12-01-preview",
#     azure_endpoint=azure_openai_gpt_endpoint,
#     api_key=azure_openai_gpt_key
# )

# PROMPT_DESIGN = """
# Kamu berperan sebagai admin penyedia informasi untuk Universitas Hamzanwadi.
# Kamu akan menjawab semua seputar pertanyaan kampus dan pendidikan yang ada di kampus Universitas Hamzanwadi.
# Jawab berdasarkan konteks yang diberikan.

# Context: {context}
# Question: {question}
# Answer:
# """

# prompt = ChatPromptTemplate.from_template(PROMPT_DESIGN)

# retriever = vector_store.as_retriever(search_kwargs={"k": 3})


# def create_chain():
#     """
#     Create a chain that retrieves context and generates a response.
#     """
#     chain = (
#         {
#             "context": retriever.with_config(
#                 return_only_outputs=True,
#                 run_name="retriever",
#                 top_k=3,
#             ),
#             "question": RunnablePassthrough().with_config(
#                 run_name="question",
#             ),
#         }
#         | RunnableParallel(
#             {
#                 "response": prompt | model,
#                 "context": itemgetter("context"),
#             }
#         )
#     )

#     return chain


# def get_answer_and_docs(question: str):
#     """
#     Get the answer and documents for a given question.
#     """
#     # Log incoming question for debugging
#     logger.info(f"Processing question: {question}")

#     # Make sure question is a string
#     if not isinstance(question, str):
#         # If we received a Message object instead of string
#         if hasattr(question, 'message'):
#             question = question.message
#         else:
#             question = str(question)

#     chain = create_chain()
#     result = chain.invoke(question)
#     answer = result["response"]
#     context = result["context"]

#     return {
#         "answer": answer,
#         "context": context
#     }

# # response = get_answer_and_docs("Apa itu Universitas Hamzanwadi?")
# # print(response["answer"])


from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAI
from operator import itemgetter
import logging

from decouple import config
from src.my_qdrant import vector_store

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load OpenAI API credentials
azure_openai_gpt_key = config("AZURE_OPENAI_GPT_API_KEY")
azure_openai_gpt_endpoint = config("AZURE_OPENAI_GPT_ENDPOINT")

model = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    api_version="2024-12-01-preview",
    azure_endpoint=azure_openai_gpt_endpoint,
    api_key=azure_openai_gpt_key
)

PROMPT_DESIGN = """
Kamu berperan sebagai admin penyedia informasi untuk Universitas Hamzanwadi yang friendly.
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

def get_answer_and_docs(question):
    """
    Get the answer and documents for a given question.
    
    Args:
        question: String containing the user's question
        
    Returns:
        Dictionary with answer and context documents
    """
    try:
        # Log incoming question for debugging
        logger.info("Processing question: %s", question)
        
        # Make sure question is a string
        if not isinstance(question, str):
            # If we received a Message object instead of string
            if hasattr(question, 'message'):
                question = question.message
            else:
                question = str(question)
                
        # Create and invoke the chain
        chain = create_chain()
        result = chain.invoke(question)
        
        # Log the result structure to help with debugging
        logger.info("Result keys: %s", result.keys())
        
        # Get the answer from the response
        answer = result["response"]
        logger.info("Answer type: %s", type(answer))
        
        # Get the context documents
        context = result["context"]
        logger.info("Context type: %s", type(context))
        
        # Format documents for better debugging
        doc_summary = []
        for i, doc in enumerate(context):
            if hasattr(doc, "page_content"):
                # Truncate long content for logging
                content_preview = doc.page_content[:50] + "..." if len(doc.page_content) > 50 else doc.page_content
                doc_summary.append(f"Doc {i}: {content_preview}")
        
        logger.info("Documents: %s", doc_summary)
        
        return {
            "answer": answer,
            "context": context
        }
    except Exception as e:
        # Log the full exception with traceback
        logger.error("Error in get_answer_and_docs: %s", str(e), exc_info=True)
        
        # Return a formatted error response rather than letting the exception propagate
        class ErrorMessage:
            def __init__(self, error):
                self.content = f"Error: {error}"
        
        return {
            "answer": ErrorMessage(str(e)),
            "context": []
        }