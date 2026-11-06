"""Pré-carrega encoding do tiktoken e limpa fila Django-Q órfã (dev)."""
import hashlib
import os
import sys
import tempfile

import django
import requests
import urllib3

urllib3.disable_warnings()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()


def cache_tiktoken():
    url = "https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken"
    cache_dir = os.path.join(tempfile.gettempdir(), "data-gym-cache")
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, hashlib.sha1(url.encode()).hexdigest())
    print("cache_path:", cache_path)

    if not os.path.exists(cache_path):
        resp = requests.get(url, verify=False, timeout=120)
        resp.raise_for_status()
        with open(cache_path, "wb") as f:
            f.write(resp.content)
        print("baixado:", len(resp.content), "bytes")
    else:
        print("já em cache:", os.path.getsize(cache_path), "bytes")

    import tiktoken

    enc = tiktoken.get_encoding("cl100k_base")
    print("tiktoken OK, tokens=", len(enc.encode("teste")))


def clear_stale_queue():
    from django_q.models import Failure, OrmQ, Success
    from consultas.models import Gravacoes

    existing = set(Gravacoes.objects.values_list("id", flat=True))
    print("gravacoes existentes:", sorted(existing))

    pending = OrmQ.objects.count()
    OrmQ.objects.all().delete()
    Failure.objects.all().delete()
    print(f"fila limpa (pending={pending}). Failures apagados.")
    print("Sucessos mantidos:", Success.objects.count())


def test_openai():
    from django.conf import settings
    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    try:
        models = list(client.models.list())[:3]
        print("openai API OK:", [m.id for m in models])
    except Exception as e:
        print("openai API FAIL:", type(e).__name__, e)


if __name__ == "__main__":
    cache_tiktoken()
    clear_stale_queue()
    test_openai()
