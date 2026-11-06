from django.shortcuts import get_object_or_404
from .models import Gravacoes
from langchain_core.documents import Document
from .agents import RAGContext, SummaryAgent, EvaluationAgent
from .openai_client import get_openai_client

def transcribe_recording(id_recording):
    recording = get_object_or_404(Gravacoes, id=id_recording)
    client = get_openai_client()

    with open(recording.video.path, "rb") as f:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
            language="pt",
        )
    recording.transcricao = transcription.text

    segmentos = []
    for segment in transcription.segments:
        segmentos.append({
            "inicio": segment.start,
            "fim": segment.end,
            "texto": segment.text
        })

    recording.segmentos = segmentos
    recording.save()
    return 'Ok'

def summary_recording(id_recording):
    recording = get_object_or_404(Gravacoes, id=id_recording)
    if not (recording.transcricao or '').strip():
        raise ValueError(
            f'Gravação {id_recording} sem transcrição. '
            'Verifique créditos/cota da OpenAI e se a tarefa de transcrição concluiu.'
        )
    recording.resumo = SummaryAgent().run(transcription=recording.transcricao).summaries
    recording.humor = EvaluationAgent().run(transcription=recording.transcricao).evaluation
    recording.save()


def task_rag(id_recording):
    recording = get_object_or_404(Gravacoes, id=id_recording)
    texto = (recording.transcricao or '').strip()
    if not texto:
        raise ValueError(
            f'Gravação {id_recording} sem transcrição para indexar no FAISS. '
            'A transcrição precisa concluir antes do RAG.'
        )

    docs = [Document(
        page_content=texto,
        metadata={"date": recording.data.strftime("%d/%m/%Y"), 'id_recording': id_recording},
    )]
    RAGContext().train(docs, recording.paciente.id)
