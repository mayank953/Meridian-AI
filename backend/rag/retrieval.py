
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from rag.vector_store import vector_store
from rag.llm import get_llm
from logger import GLOBAL_LOGGER as log
# ==========================================
# 4. Building the RAG Chain
# ==========================================
def ask_question(query: str):
    """Retrieves context and generates an answer using Gemini."""
    log.info("RAG query received", query=query)

    llm = get_llm()

    # Create a retriever from the vector store (fetch top 3 most relevant chunks)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # Define the system prompt to guide the LLM's behavior
    system_prompt = (
        "You are a helpful assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer based on the context, say that you don't know. "
        "Keep the answer concise and accurate."
        "\n\n"
        "Context: {context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # Chain 1: Formats the prompt with retrieved documents and passes to the LLM
    question_answer_chain = create_stuff_documents_chain(llm, prompt)

    # Chain 2: Orchestrates the retrieval step and the QA step
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    # Execute the chain
    response = rag_chain.invoke({"input": query})

    log.info("RAG answer generated", answer=response["answer"])

# ==========================================
# Execution
# ==========================================
# if __name__ == "__main__":
    # 1. Ingest the data into the database
    # (You only need to run this once to populate your Vector Search collection)
    # ingest_data()

    # 2. Query the RAG system
    # ask_question("What all countries does acme manufacturing operates in?")
    # ask_question("How much percentage of the manufacturing workface will retire in next five years?")
    # ask_question("What is the COGS in FY2024")
    # ask_question("What is the Revenue  in FY2022")