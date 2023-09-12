import os

import openai
import pinecone
from dotenv import load_dotenv, find_dotenv
from fastapi import APIRouter
from langchain.agents import AgentType
from langchain.agents import Tool
from langchain.agents import initialize_agent
from langchain.chains import ConversationChain
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationSummaryBufferMemory
from langchain.output_parsers import ResponseSchema
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.utilities import GoogleSerperAPIWrapper
from langchain.vectorstores import DocArrayInMemorySearch
from langchain.vectorstores import Pinecone

from application.services import load_firebase_documents, perform_news_sentiment, get_stock_data
from .schema import Message, NewsContent, QnA, DocMessage, StockAnalysisRequest

router = APIRouter()
MAX_TOKENS = 5000
timeout_seconds = 60
_ = load_dotenv(find_dotenv())
openai.api_key = os.environ['OPENAI_API_KEY']

embedding = OpenAIEmbeddings()
pinecone.init(
    api_key=os.environ['PINECONE_API_KEY'],
    environment=os.environ['PINECONE_ENV'],
)
index_name = "fd-market-pulse-2"


@router.post('/news-sentiment', response_model=None, response_description='Chat completion with ChatGPT')
async def news_sentiment(message: NewsContent):
    return perform_news_sentiment(message)


@router.post('/news-sentiment-translation', response_model=None, response_description='news translation with ChatGPT')
async def news_sentiment_translation(message: NewsContent):
    translation_schema = ResponseSchema(name='translation',
                                        description='translation of the news into english text and replace double '
                                                    'quotes with single quotes')
    return perform_news_sentiment(message, translation_schema)


@router.post('/chat-v2', response_model=None, response_description='Chat completion with ChatGPT and Google APIs')
async def chat_v2(message: Message):
    search = GoogleSerperAPIWrapper()
    tools = [
        Tool(
            name="Current Search",
            func=search.run,
            description="useful for when you don't know the answer"
        ),
    ]
    # memory = ConversationBufferMemory(memory_key="chat_history")

    llm = ChatOpenAI(temperature=0.0, model_name="gpt-4")
    memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=MAX_TOKENS, memory_key="chat_history")

    array_of_dicts = []
    for item in message.chat_history[2:]:
        array_of_dicts.append({"input": item.content if item.role == "user" else None,
                               "output": item.content if item.role == "assistant" else None})

    for item in array_of_dicts:
        user_message = item["input"]
        ai_message = item["output"]
        # memory.save_context({'input': item["input"]}, {'output': item["output"]})
        if user_message:
            memory.chat_memory.add_user_message(user_message)

        if ai_message:
            memory.chat_memory.add_ai_message(ai_message)

    agent_chain = initialize_agent(tools, llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=True,
                                   memory=memory)
    try:
        bot_reply = agent_chain.run(input=message.message)
    except ValueError as e:
        bot_reply = str(e)
        print(bot_reply)
        if not bot_reply.startswith("Could not parse LLM output: `"):
            raise e
        bot_reply = bot_reply.removeprefix("Could not parse LLM output: `").removesuffix("`")
    chat_history = [
        *[c.dict() for c in message.chat_history],
        {'role': 'user', 'content': message.message}
    ]

    return {
        'message': bot_reply,
        'chat_history': [*chat_history, {'role': 'assistant', 'content': bot_reply}]
    }


@router.post('/chat', response_model=None, response_description='Chat completion with ChatGPT')
async def chat(message: Message):
    llm = ChatOpenAI(temperature=0.0, openai_api_key=message.api_key, model_name="gpt-3.5-turbo")
    memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=MAX_TOKENS)

    if len(message.chat_history) > 1:
        input_memory = ''
        output_memory = ''
        for i in message.chat_history[1:]:
            if i.role == 'assistant':
                output_memory = i.content
            else:
                input_memory = i.content

        if input_memory != '' and output_memory != '':
            memory.save_context({'input': input_memory}, {'output': output_memory})

    conversation = ConversationChain(llm=llm, memory=memory)
    bot_reply = conversation.predict(input=message.message)

    chat_history = [
        *[c.dict() for c in message.chat_history],
        {'role': 'user', 'content': message.message}
    ]

    return {
        'message': bot_reply,
        'chat_history': [*chat_history, {'role': 'assistant', 'content': bot_reply}]
    }


@router.post('/qna', response_model=None, response_description='simple question answer with ChatGPT')
async def chat(message: QnA):
    _ = load_dotenv(find_dotenv())  # read local .env file
    llm = ChatOpenAI(temperature=0.0, model_name="gpt-3.5-turbo")
    loader = PyPDFLoader(message.url)
    documents = loader.load_and_split()
    embeddings = OpenAIEmbeddings()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    db = DocArrayInMemorySearch.from_documents(
        docs,
        embeddings
    )
    retriever = db.as_retriever()
    qa_stuff = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        verbose=False
    )

    response = qa_stuff.run(message.message)

    return dict(resp=response)


@router.post('/chat-docs', response_model=None, response_description='Chat completion with docs')
async def chat(message: DocMessage):
    # initialize pinecone

    if message.delete_index:
        documents = load_firebase_documents("fd-market-pulse.appspot.com", 'doc_chatbot/')
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = text_splitter.split_documents(documents)
        # First, check if our index already exists. If it doesn't, we create it
        if index_name not in pinecone.list_indexes():
            # we create a new index
            pinecone.create_index(
                name=index_name,
                metric='cosine',
                dimension=1536
            )
        docsearch = Pinecone.from_documents(docs, embedding, index_name=index_name)
    else:
        docsearch = Pinecone.from_existing_index(index_name, embedding)

    metadata_field_info = [
        AttributeInfo(
            name="file_name",
            description="The document the chunk is from",
            type="string",
        ),
        AttributeInfo(
            name="page",
            description="The page from the document",
            type="integer",
        ),
    ]

    general_system_template = r"""Use the following pieces of context to answer the question at the end. If you don't 
    know the answer, just say that you don't know, don't try to make up an answer. Keep the answer with as much 
    detail as possible. Always say "thanks for asking!" at the end of the answer. ---- {context} ----"""
    general_user_template = "Question:```{question}```"
    messages = [
        SystemMessagePromptTemplate.from_template(general_system_template),
        HumanMessagePromptTemplate.from_template(general_user_template)
    ]
    qa_prompt = ChatPromptTemplate.from_messages(messages)
    document_content_description = "files"
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0)
    retriever = SelfQueryRetriever.from_llm(
        llm,
        docsearch,
        document_content_description,
        metadata_field_info,
        verbose=True
    )
    qa = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0),
        chain_type="stuff",
        retriever=docsearch.as_retriever(search_type="similarity", search_kwargs={'k': 20}),
        combine_docs_chain_kwargs={'prompt': qa_prompt}
    )
    # qa = ConversationalRetrievalChain.from_llm(
    #     llm=ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0),
    #     chain_type="map_reduce",
    #     retriever=retriever,
    #     # combine_docs_chain_kwargs={'prompt': qa_prompt}
    # )

    result = qa({"question": message.message, "chat_history": message.doc_history})
    message.doc_history.extend([(message.message, result["answer"])])

    chat_history = [
        *[c.dict() for c in message.chat_history],
        {'role': 'user', 'content': message.message}
    ]

    return {
        'message': result["answer"],
        'chat_history': [*chat_history, {'role': 'assistant', 'content': result["answer"]}],
        'doc_history': message.doc_history,
        'delete_index': message.delete_index
    }


@router.post("/stock_analysis", response_model=None, response_description='Chat completion with docs')
async def stock_analysis(request: StockAnalysisRequest):
    stock_data_agent = get_stock_data(request.tickers, request.start, request.end)
    return {"result": stock_data_agent(request.query), "tickers": request.tickers}
