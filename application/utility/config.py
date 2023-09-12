import os
import pinecone
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

pinecone.init(
    api_key=os.environ['PINECONE_API_KEY'],
    environment=os.environ['PINECONE_ENV']
)



MAX_TOKENS = 5000
index_name = "fd-market-pulse-2"
