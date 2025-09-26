import os
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.core.constants import DEFAULT_TEMPERATURE
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.llms.bedrock import Bedrock
from typing import Dict
from llama_index.core.settings import Settings
load_dotenv()

class Config:
    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USER = os.getenv("NEO4J_USERNAME")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    DB_PROVIDER = os.getenv("DB_PROVIDER", "neo4j")
    QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")
    COLLECTION_EXPERIENCE = os.getenv("COLLECTION_EXPERIENCE")
    COLLECTION_PROGRAMMING_LANGUAGES = os.getenv("COLLECTION_PROGRAMMING_LANGUAGES")
    COLLECTION_FRAMEWORK = os.getenv("COLLECTION_FRAMEWORK")
    COLLECTION_SKILLS = os.getenv("COLLECTION_SKILLS")
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    API_VERSION = os.getenv("API_VERSION")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
settings = Config()

def init_settings():
    model_provider = os.getenv("MODEL_PROVIDER")
    match model_provider:
        case "bedrock":
            init_bedrock()
        case "azure-openai":
            init_azure_openai()
        case "gemini":
            init_gemini()
        case _:
            raise ValueError(f"Invalid model provider: {model_provider}")

    Settings.chunk_size = 8191
    Settings.chunk_overlap = 0

def init_azure_openai():
    llm_deployment = os.environ["MODEL"]
    embedding_deployment = os.environ["EMBEDDING_MODEL"]
    max_tokens = os.getenv("LLM_MAX_TOKENS")
    temperature = os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE)

    azure_config = {
        "api_key": os.environ["AZURE_OPENAI_KEY"],
        "azure_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"],
        "api_version": os.getenv("API_VERSION")
        or os.getenv("API_VERSION"),
    }

    Settings.llm = AzureOpenAI(
        model=os.getenv("MODEL"),
        max_tokens=int(max_tokens) if max_tokens is not None else None,
        temperature=float(temperature),
        deployment_name=llm_deployment,
        **azure_config,
    )

    Settings.embed_model = AzureOpenAIEmbedding(
        model=os.getenv("EMBEDDING_MODEL"),
        deployment_name=embedding_deployment,
        **azure_config,
    )
    print("Settings Azure Openai susscess!") 

def init_bedrock():

    Settings.llm = Bedrock(
        model=os.getenv("MODEL_LLM"),
        aws_access_key_id=os.getenv("aws_access_key_id"),
        aws_secret_access_key=os.getenv("aws_secret_access_key"),
        region_name=os.getenv("region_name")
    )

    Settings.embed_model = BedrockEmbedding(
        model_name=os.getenv("MODEL_ID"),
        aws_access_key_id=os.getenv("aws_access_key_id"),
        aws_secret_access_key=os.getenv("aws_secret_access_key"),
        region_name=os.getenv("region_name")
    )
    print("Settings bedrock susscess!")
def init_gemini():
    
    from llama_index.llms.gemini import Gemini
    from llama_index.embeddings.gemini import GeminiEmbedding
    Settings.llm = Gemini(
        api_key=os.getenv("GEMINI_API_KEY"),
        model="gemini-2.5-flash"
    )
    Settings.embed_model = GeminiEmbedding(
        api_key=os.getenv("GEMINI_API_KEY"),
        model_name='text-embedding-004'
    )
    print("Settings Gemini susscess!")

