import os

import firebase_admin
import openai
import pinecone
from dotenv import load_dotenv, find_dotenv
from fastapi import APIRouter
from firebase_admin import credentials, storage
from langchain.chains import ConversationChain
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationSummaryBufferMemory
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import DocArrayInMemorySearch
from langchain.vectorstores import Pinecone

from .schema import Message, NewsContent, QnA, DocMessage

router = APIRouter()

# Maximum allowed tokens for the chosen model
MAX_TOKENS = 5000

_ = load_dotenv(find_dotenv())
openai.api_key = os.environ['OPENAI_API_KEY']
embedding = OpenAIEmbeddings()
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),  # find at app.pinecone.io
    environment=os.getenv("PINECONE_ENV"),  # next to api key in console
)

index_name = "fd-market-pulse"


def ensure_triple_backticks(s):
    if not s.startswith('```'):
        s = '```' + s
    if not s.endswith('```'):
        s = s + '```'
    return s


def perform_news_sentiment(message: NewsContent, translation_schema=None):
    gpt_chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.0, openai_api_key=message.api_key)
    template_string = """Consider the following text that is delimited by triple backticks. text:```{news_text}``` 
    {format_instructions}"""

    response_schemas = [
        translation_schema if translation_schema else None,
        ResponseSchema(name='sentiment', description='sentiment of the news , is it positive, negative or neutral'),
        ResponseSchema(name='sentimentScore',
                       description='from -5 to 5 where higher is more positive and lower is more negative'),
        ResponseSchema(name='direction',
                       description='what is the direction of the investor, whether it is buy, sell, hold or no action'),
        ResponseSchema(name='stocksTagList', description='extract the stocks tickers in array format'),
        ResponseSchema(name='sentimentSummary', description='summary of the news not more than 20 words')
    ]
    output_parser = StructuredOutputParser.from_response_schemas([s for s in response_schemas if s])
    format_instructions = output_parser.get_format_instructions()
    prompt_template = ChatPromptTemplate.from_template(template_string)
    customer_messages = prompt_template.format_messages(news_text=message.message,
                                                        format_instructions=format_instructions)
    customer_response = gpt_chat(customer_messages)

    return output_parser.parse(ensure_triple_backticks(customer_response.content))


@router.post('/news-sentiment', response_model=None, response_description='Chat completion with ChatGPT')
async def news_sentiment(message: NewsContent):
    return perform_news_sentiment(message)


@router.post('/news-sentiment-translation', response_model=None, response_description='news translation with ChatGPT')
async def news_sentiment_translation(message: NewsContent):
    translation_schema = ResponseSchema(name='translation',
                                        description='translation of the text into english text and replace double quotes with single quotes')
    return perform_news_sentiment(message, translation_schema)


@router.post('/chat', response_model=None, response_description='Chat completion with ChatGPT')
async def chat(message: Message):
    llm = ChatOpenAI(temperature=0.0, openai_api_key=message.api_key)
    memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=5000)

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
    llm = ChatOpenAI(temperature=0.0)
    loader = PyPDFLoader(message.url)
    documents = loader.load()
    embeddings = OpenAIEmbeddings()
    db = DocArrayInMemorySearch.from_documents(
        documents,
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
        # if index_name in pinecone.list_indexes():
        #     pinecone.delete_index(index_name)
        cred = credentials.Certificate("application/routers/chat_gpt/fd-market-pulse-firebase-adminsdk.json")
        try:
            firebase_admin.get_app()
        except ValueError as e:
            firebase_admin.initialize_app(cred)

        bucket = storage.bucket("fd-market-pulse.appspot.com")

        blobs = bucket.list_blobs(prefix='doc_chatbot/')

        documents_url_list = []
        for blob in blobs:
            if not blob.name.endswith('/'):  # Ignore directories
                blob.make_public()
                documents_url_list.append(blob.public_url)

        documents = []
        for i in documents_url_list:
            print("document loading start ")
            loader = PyPDFLoader(i)
            doc_i = loader.load()
            print("document loading end ")
            for j in doc_i:
                j.metadata['file_name'] = i
            documents.extend(doc_i)
            print("document extend end")

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

    general_system_template = r"""Use the following pieces of context to answer the question at the end. If you don't 
    know the answer, just say that you don't know, don't try to make up an answer. Keep the answer as detail as 
    possible. Always say "thanks for asking!" at the end of the answer. ---- 
    {context} ----"""
    general_user_template = "Question:```{question}```"
    messages = [
        SystemMessagePromptTemplate.from_template(general_system_template),
        HumanMessagePromptTemplate.from_template(general_user_template)
    ]
    qa_prompt = ChatPromptTemplate.from_messages(messages)
    qa = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0),
        chain_type="stuff",
        retriever=docsearch.as_retriever(search_type="similarity", search_kwargs={'k': 4}),
        combine_docs_chain_kwargs={'prompt': qa_prompt}
        # condense_question_prompt=prompt
        # return_source_documents=True,
        # return_generated_question=True,
    )

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
