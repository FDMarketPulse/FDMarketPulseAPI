from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser
from langchain.output_parsers import ResponseSchema
from langchain.prompts import ChatPromptTemplate
from ..routers.chat_gpt.schema import NewsContent


def perform_news_sentiment(message: NewsContent, translation_schema=None):
    gpt_chat = ChatOpenAI(model_name='gpt-3.5-turbo-16k', temperature=0.0, openai_api_key=message.api_key)
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
        ResponseSchema(name='sentimentSummary', description='summary of the news in less than 50 words')
    ]
    output_parser = StructuredOutputParser.from_response_schemas([s for s in response_schemas if s])
    format_instructions = output_parser.get_format_instructions()
    prompt_template = ChatPromptTemplate.from_template(template_string)
    customer_messages = prompt_template.format_messages(news_text=message.message,
                                                        format_instructions=format_instructions)
    customer_response = gpt_chat(customer_messages)

    return output_parser.parse(ensure_triple_backticks(customer_response.content))


def ensure_triple_backticks(s):
    if not s.startswith('```'):
        s = '```' + s
    if not s.endswith('```'):
        s = s + '```'
    return s
