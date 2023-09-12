import os
import openai
import yfinance as yf
from langchain import OpenAI
from langchain.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI

openai.api_key = os.environ['OPENAI_API_KEY']


def get_stock_data(tickers, start, end):
    tickers_str = " ".join(tickers)  # Convert list of tickers to space-separated string
    data = yf.download(tickers_str, group_by='Ticker', period="12mo", start=start, end=end)
    # agent = create_pandas_dataframe_agent(
    #     ChatOpenAI(temperature=0, model="gpt-4"),
    #     data.reset_index(),
    #     verbose=True,
    #     agent_type=AgentType.OPENAI_FUNCTIONS,
    # )
    agent = create_pandas_dataframe_agent(ChatOpenAI(temperature=0.0, model_name="gpt-3.5-turbo-16k"), data.reset_index(),
                                          verbose=True)
    print(data.shape)
    return agent

# # Example of how to use the class:
# yf_analysis = YfStockAnalysis()
# tickers = ["SPY", "AAPL", "TSLA", "MSFT"]
# stock_data_agent = yf_analysis.get_stock_data(tickers)
