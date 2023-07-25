import openai
from fastapi import APIRouter
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from langchain.prompts import ChatPromptTemplate

from .schema import Message, NewsContent

router = APIRouter()

# Maximum allowed tokens for the chosen model
MAX_TOKENS = 5000


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
        ResponseSchema(name='sentimentScore', description='from -5 to 5 where higher is more positive and lower is more negative'),
        ResponseSchema(name='direction', description='what is the direction of the investor, whether it is buy, sell, hold or no action'),
        ResponseSchema(name='stocksTagList', description='extract the stocks tickers in array format'),
        ResponseSchema(name='sentimentSummary', description='summary of the news not more than 20 words')
    ]
    output_parser = StructuredOutputParser.from_response_schemas([s for s in response_schemas if s])
    format_instructions = output_parser.get_format_instructions()
    prompt_template = ChatPromptTemplate.from_template(template_string)
    customer_messages = prompt_template.format_messages(news_text=message.message, format_instructions=format_instructions)
    customer_response = gpt_chat(customer_messages)

    return output_parser.parse(ensure_triple_backticks(customer_response.content))

@router.post('/news-sentiment', response_model=None, response_description='Chat completion with ChatGPT')
async def news_sentiment(message: NewsContent):
    return perform_news_sentiment(message)

@router.post('/news-sentiment-translation', response_model=None, response_description='news translation with ChatGPT')
async def news_sentiment_translation(message: NewsContent):
    translation_schema = ResponseSchema(name='translation', description='translation of the text into english text and replace double quotes with single quotes')
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