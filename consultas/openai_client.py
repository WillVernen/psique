"""Clientes OpenAI/LangChain com suporte a SSL_VERIFY (útil em redes com proxy/antivírus)."""
from functools import lru_cache

import httpx
from django.conf import settings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from openai import OpenAI


@lru_cache(maxsize=1)
def _http_client() -> httpx.Client:
    return httpx.Client(verify=settings.SSL_VERIFY, timeout=120.0)


def get_openai_client() -> OpenAI:
    return OpenAI(api_key=settings.OPENAI_API_KEY, http_client=_http_client())


def get_chat_llm(**kwargs) -> ChatOpenAI:
    return ChatOpenAI(
        openai_api_key=settings.OPENAI_API_KEY,
        http_client=_http_client(),
        **kwargs,
    )


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        openai_api_key=settings.OPENAI_API_KEY,
        http_client=_http_client(),
    )
