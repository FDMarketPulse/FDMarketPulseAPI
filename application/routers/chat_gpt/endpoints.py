import json
from typing import List

import openai
from fastapi import APIRouter

from .schema import Message, RoleMessage, NewsContent

router = APIRouter()

# Maximum allowed tokens for the chosen model
MAX_TOKENS = 1000


def get_completion(prompt, model="gpt-3.5-turbo", temperature=0):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]


@router.post("/news-sentiment", response_model=None, response_description="Chat completion with ChatGPT")
async def news_sentiment(message: NewsContent):
    openai.api_key = message.api_key
    news_format = {"sentiment": "positive,negative,neutral",
                   "sentiment point": "from -5 to 5 where higher is more positive",
                   "direction": "buy,sell",
                   "stocks tag list": ["give me the stock tag list inside"],
                   "sentiment summary": "less than 15 words"}
    input_prompt = f"""Consider the following text:-------{message.message}-------Put this message with the correct 
    infos to JSON Array Text with double quotes in the following JSON structure:------{news_format}------"""

    a = get_completion(prompt=input_prompt)
    return json.loads(a)


@router.post("/chat", response_model=None, response_description="Chat completion with ChatGPT")
async def chat(message: Message):
    openai.api_key = message.api_key

    # Truncate the chat history if it exceeds the maximum token limit
    truncated_chat_history = truncate_chat_history(message.chat_history, MAX_TOKENS - 4)

    chat_history = [
        {"role": "system", "content": "You are a cute pikachu"},
        *[c.dict() for c in truncated_chat_history],
        {"role": "user", "content": message.message}
    ]

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_history,
        max_tokens=MAX_TOKENS - 4,
        temperature=0.6
    )

    bot_reply = completion.choices[0].message.content.strip()

    response = {
        "message": bot_reply,
        "chat_history": [*truncated_chat_history,
                         {"role": "assistant", "content": bot_reply}]
    }

    return response


def truncate_chat_history(chat_history: List[RoleMessage], max_tokens: int) -> List[RoleMessage]:
    """
    Truncates the chat history to ensure it doesn't exceed the maximum token limit.
    """
    total_tokens = 0
    truncated_history = []

    for msg in chat_history:
        msg_tokens = len(msg.content.split())
        if total_tokens + msg_tokens <= max_tokens:
            truncated_history.append(msg)
            total_tokens += msg_tokens
        else:
            break

    return truncated_history
