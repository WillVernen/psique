# PsiQuê

Plataforma web de apoio ao trabalho clínico em psicologia.

Permite gerenciar pacientes, gravar sessões, transcrever e resumir com IA, acompanhar o humor ao longo do tempo e conversar com a base clínica via RAG — com isolamento de dados por usuário.

## Autor

**Francisco Will Vernen de Sousa Josino**

## Funcionalidades

- Cadastro e autenticação de psicólogos
- Pacientes vinculados ao usuário (ownership)
- Upload de gravações (áudio/vídeo), transcrição (Whisper) e resumo (GPT)
- Avaliação de humor e gráfico de evolução
- Chat com contexto clínico (LangChain + FAISS)
- Envio opcional de resumos via WhatsApp (Evolution API)
- Mídia clínica protegida (não pública)

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Django 5.2 |
| IA / LLM | OpenAI (GPT + Whisper) via LangChain |
| RAG | FAISS + embeddings OpenAI |
| Filas | Django-Q2 |
| Frontend | Tailwind CSS (CDN), Chart.js |
| WhatsApp | Evolution API (opcional) |
| Deploy | Docker, Gunicorn, WhiteNoise |

## Requisitos

- **Python 3.12 ou 3.13** (recomendado: 3.12). **Não use Python 3.14+** — várias dependências pinadas ainda não têm wheel pronto e a instalação falha.
- Conta OpenAI (chave de API)
- (Opcional) instância Evolution API para WhatsApp

Se o download no site python.org falhar (SSL/rede), no Windows use o winget:

```powershell
winget install --id Python.Python.3.12 -e --source winget --accept-package-agreements --accept-source-agreements
```

## Como rodar (local)

```bash
# 1. Ambiente virtual (force a versão correta no Windows)
py -3.12 -m venv venv
# se não tiver 3.12: py -3.13 -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
# python3.12 -m venv venv && source venv/bin/activate

# 2. Dependências
python -m pip install --upgrade pip
pip install -r requirements.txt

# Se aparecer erro SSL (CERTIFICATE_VERIFY_FAILED), use:
# pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
#
# Se a OpenAI/tiktoken falhar com CERTIFICATE_VERIFY_FAILED no Windows
# (antivírus/proxy), no .env defina: SSL_VERIFY=False  (somente em desenvolvimento)

# 3. Variáveis de ambiente
copy .env.example .env          # Windows
# cp .env.example .env          # Linux / macOS
# Edite .env e preencha pelo menos SECRET_KEY e OPENAI_API_KEY

# 4. Banco
python manage.py migrate

# 5. Servidor
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` (redireciona para pacientes; é preciso estar autenticado).

### Variáveis principais (`.env`)

| Variável | Obrigatória | Descrição |
|---|---|---|
| `SECRET_KEY` | Sim | Chave secreta do Django |
| `DEBUG` | Sim | `True` em desenvolvimento |
| `ALLOWED_HOSTS` | Sim | Ex.: `localhost,127.0.0.1` |
| `OPENAI_API_KEY` | Sim | Chave da OpenAI |
| `EVOLUTION_API_URL` | Não | URL da Evolution API |
| `EVOLUTION_API_KEY` | Não | Chave da Evolution API |
| `EVOLUTION_INSTANCE_NAME` | Não | Nome da instância WhatsApp |

## Docker (produção)

```bash
docker build -t psique .
docker run --env-file .env -p 8000:8000 psique
```

O `entrypoint.prod.sh` executa `migrate`, `collectstatic`, o worker `qcluster` e o `gunicorn`.

## Estrutura do repositório

```
.
├── core/           # Settings, URLs, WSGI/ASGI
├── usuarios/       # Auth, pacientes, mídia protegida
├── consultas/      # Gravações, IA, chat RAG, WhatsApp
├── prompts/        # Prompts usados pelos agentes
├── templates/      # Layout base e estáticos de origem
├── manage.py
├── Dockerfile
├── entrypoint.prod.sh
├── requirements.txt
└── .env.example
```

Código-fonte único na raiz deste repositório (`WillVernen/psique`).

## Documentação adicional

- [analise_sistema_psique.md](analise_sistema_psique.md) — análise técnica do sistema
- [relatorio_final.md](relatorio_final.md) — relatório de correções e hardening

## Licença

Distribuído sob a licença [MIT](LICENSE).
Copyright (c) 2026 Francisco Will Vernen de Sousa Josino.
