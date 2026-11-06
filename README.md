# PsiQuê

App de apoio ao trabalho clínico em psicologia: pacientes, gravações de sessão, transcrição, resumos, humor e chat com contexto clínico.

## Autor

**Francisco Will Vernen de Sousa Josino**

## Stack

- Django 5
- LangChain + OpenAI
- FAISS (RAG)
- Docker / Gunicorn
- Evolution API (WhatsApp, opcional)

## Como rodar

```bash
python -m venv venv
# Windows
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # preencha SECRET_KEY, OPENAI_API_KEY, etc.
python manage.py migrate
python manage.py runserver
```

Em produção (Docker), o `entrypoint.prod.sh` executa migrate, collectstatic, qcluster e gunicorn.

## Estrutura

Código-fonte único na raiz do repositório (`core/`, `usuarios/`, `consultas/`, …).

## Licença

Ver [LICENSE](LICENSE).
