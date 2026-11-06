from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import StreamingHttpResponse, JsonResponse
from django.contrib.humanize.templatetags.humanize import naturaltime
from usuarios.models import Pacientes
from .models import Gravacoes, Pergunta
from .agents import RAGContext
from .wrapper_evolutionapi import SendMessage

@login_required
def consultas(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
    if request.method == 'GET':
        gravacoes = Gravacoes.objects.filter(paciente__id=id).order_by('data')
        datas = [naturaltime(item['data']) for item in gravacoes.values('data')]
        humores = [item['humor'] for item in gravacoes.values('humor')]
     
        return render(request, 'consultas.html', {'paciente': paciente, 'gravacoes': gravacoes, 'datas': datas, 'humores': humores})
    elif request.method == 'POST':
        gravacao = request.FILES.get('gravacao')
        data = request.POST.get('data')
        transcript = request.POST.get('transcript') == 'on'

        gravacao = Gravacoes(
            video=gravacao,
            data=data,  
            transcrever=transcript,
            paciente=paciente,
        )
        gravacao.save()

        return redirect(reverse('consultas', kwargs={'id': id}))

@login_required
def gravacao(request, id):
    gravacao = get_object_or_404(Gravacoes, id=id)
    # Calcular humor médio de todas as gravações do paciente
    gravacoes_paciente = Gravacoes.objects.filter(paciente=gravacao.paciente, humor__gt=0)
    if gravacoes_paciente.exists():
        humor_medio = round(sum(g.humor for g in gravacoes_paciente) / gravacoes_paciente.count(), 1)
    else:
        humor_medio = 0
    return render(request, 'gravacao.html', {'gravacao': gravacao, 'humor_medio': humor_medio})

@login_required
def excluir_gravacao(request, id):
    gravacao = get_object_or_404(Gravacoes, id=id)
    paciente_id = gravacao.paciente.id
    gravacao.delete()
    return redirect(reverse('consultas', kwargs={'id': paciente_id}))

@login_required
@csrf_exempt
def chat(request, id):
    if request.method == 'GET':
        paciente = get_object_or_404(Pacientes, id=id)
        return render(request, 'chat.html', {'paciente': paciente})
    elif request.method == 'POST':
        pergunta_user = request.POST.get('pergunta')
        pergunta = Pergunta(
            pergunta=pergunta_user
        )
        pergunta.save()
        return JsonResponse({'id': pergunta.id})

@login_required
@csrf_exempt
def stream_response(request, id):
    id_pergunta = request.POST.get('id_pergunta')
    return StreamingHttpResponse(RAGContext().retrieval(id_pergunta, id))

@login_required
def ver_referencias(request, id):
    pergunta = get_object_or_404(Pergunta, id=id)
    data_treinamento = pergunta.data_treinamento.all()
    gravacoes = Gravacoes.objects.filter(datatreinamento__in=data_treinamento).distinct()

    return render(request, 'ver_referencia.html', {'pergunta': pergunta, 'data_treinamento': data_treinamento, 'gravacoes': gravacoes})

@login_required
def send_message(request, id):
    gravacao = get_object_or_404(Gravacoes, id=id)
    for g in gravacao.resumo:
        SendMessage().send_message({'number': gravacao.paciente.telefone, 'textMessage': {'text': g}})
    return redirect(f'/consultas/gravacao/{id}')