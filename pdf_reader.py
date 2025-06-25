# pdf_reader.pys

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain_together import ChatTogether
# from langchain-together import ChatTogether
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda

def format_docs(retrieved_docs):
    return "\n\n".join(doc.page_content for doc in retrieved_docs)

def build_qa_chain(pdf_path):
    # Load & split PDF
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)

    # Embed & vector store
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embedding=embeddings)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    # LLM + prompt
    llm = ChatTogether(model="deepseek-ai/DeepSeek-V3", temperature=0.2)
    prompt = PromptTemplate(
        template="""
        You are a helpful assistant.
        Answer ONLY from the provided document context.
        If the context is insufficient, just say you don't know about that but know everything about the pdf you uploaded.
        but if they greet you, greet them back. if they ask what should they ask or what you can do, tell them they can ask anything from the document and you will answer that.
        {context}
        Question: {question}
        """,
        input_variables=['context', 'question']
    )

    # Chain
    parallel_chain = RunnableParallel({
        "context": retriever | RunnableLambda(format_docs),
        "question": RunnablePassthrough()
    })
    parser = StrOutputParser()

    full_chain = parallel_chain | prompt | llm | parser
    return full_chain
