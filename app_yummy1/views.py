import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.utils import timezone
from django.db.models import *

from .models import *
from .forms import *

def home(request):

    context = {
        'page_title': 'Home',
    }
    return render(request, 'home/home.html', context)







def listar_listas(request):
    """
    Lista todas as listas do usuário atual e retorna em formato JSON
    """
    # Obtém todas as listas do usuário atual
    listas = Lista.objects.filter(usuario=request.user).order_by('-data_criacao')
    
    # Adiciona informações extra para cada lista
    resultado = []
    for lista in listas:
        # Conta total de itens e itens concluídos
        total_itens = lista.itens.count()
        itens_concluidos = lista.itens.filter(status='concluido').count()
        
        # Calcula porcentagem concluída
        porcentagem = 0
        if total_itens > 0:
            porcentagem = int((itens_concluidos / total_itens) * 100)
        
        # Calcula dias restantes
        dias_restantes = None
        status_dias = ''
        if lista.data_objetivo:
            hoje = timezone.now().date()
            dias = (lista.data_objetivo - hoje).days
            dias_restantes = dias
            if dias < 0:
                status_dias = 'atrasada'
            elif dias == 0:
                status_dias = 'hoje'
            elif dias == 1:
                status_dias = 'amanhã'
            else:
                status_dias = f'em {dias} dias'
        
        # Obtém o número de itens por prioridade
        itens_alta = lista.itens.filter(prioridade='alta').count()
        itens_media = lista.itens.filter(prioridade='media').count()
        itens_baixa = lista.itens.filter(prioridade='baixa').count()
        
        # Cria dicionário com dados da lista e estatísticas
        lista_dict = {
            'id': lista.id,
            'nome': lista.nome,
            'objetivo': lista.objetivo,
            'status': lista.status,
            'status_display': lista.get_status_display(),
            'cor': lista.cor,
            'icone': lista.icone,
            'data_criacao': lista.data_criacao.strftime('%d/%m/%Y'),
            'data_objetivo': lista.data_objetivo.strftime('%d/%m/%Y') if lista.data_objetivo else None,
            'dias_restantes': dias_restantes,
            'status_dias': status_dias,
            'total_itens': total_itens,
            'itens_concluidos': itens_concluidos,
            'porcentagem': porcentagem,
            'itens_alta': itens_alta,
            'itens_media': itens_media,
            'itens_baixa': itens_baixa,
        }
        resultado.append(lista_dict)
    
    return JsonResponse({'listas': resultado})


def obter_lista(request, lista_id):
    """
    Obtém os detalhes de uma lista específica em formato JSON
    """
    # Verifica se a lista existe e pertence ao usuário atual
    lista = get_object_or_404(Lista, id=lista_id, usuario=request.user)
    
    # Obtém todos os itens da lista ordenados
    itens = Item.objects.filter(lista=lista).order_by('ordem', '-prioridade', 'data_hora')
    itens_lista = []
    
    for item in itens:
        # Formata a data e hora, se existir
        data_hora_formatada = None
        if item.data_hora:
            data_hora_formatada = item.data_hora.strftime('%d/%m/%Y %H:%M')
        
        # Adiciona o item à lista de itens
        itens_lista.append({
            'id': item.id,
            'nome': item.nome,
            'descricao': item.descricao,
            'status': item.status,
            'status_display': item.get_status_display(),
            'prioridade': item.prioridade,
            'prioridade_display': item.get_prioridade_display(),
            'data_hora': data_hora_formatada,
            'esta_atrasado': item.esta_atrasado(),
            'tempo_restante': item.tempo_restante(),
            'ordem': item.ordem,
        })
    
    # Calcula porcentagem de conclusão
    total_itens = len(itens)
    itens_concluidos = sum(1 for item in itens if item.status == 'concluido')
    porcentagem = 0
    if total_itens > 0:
        porcentagem = int((itens_concluidos / total_itens) * 100)
    
    # Prepara os dados da lista
    lista_dict = {
        'id': lista.id,
        'nome': lista.nome,
        'objetivo': lista.objetivo,
        'status': lista.status,
        'status_display': lista.get_status_display(),
        'cor': lista.cor,
        'icone': lista.icone,
        'data_criacao': lista.data_criacao.strftime('%d/%m/%Y'),
        'data_objetivo': lista.data_objetivo.strftime('%d/%m/%Y') if lista.data_objetivo else None,
        'dias_restantes': lista.dias_restantes(),
        'porcentagem': porcentagem,
        'total_itens': total_itens,
        'itens_concluidos': itens_concluidos,
        'itens': itens_lista,
    }
    
    return JsonResponse({'lista': lista_dict})


@csrf_exempt
def criar_lista(request):
    """
    Cria uma nova lista a partir dos dados enviados via POST
    """
    if request.method == 'POST':
        try:
            # Obtém os dados do POST
            dados = json.loads(request.body)
            
            # Cria um formulário com os dados recebidos
            form = ListaForm(dados)
            
            if form.is_valid():
                # Salva a lista, mas não comita ainda
                lista = form.save(commit=False)
                # Define o usuário atual como dono da lista
                lista.usuario = request.user
                # Salva a lista
                lista.save()
                
                # Retorna resposta de sucesso
                return JsonResponse({
                    'status': 'success',
                    'message': 'Lista criada com sucesso!',
                    'lista': {
                        'id': lista.id,
                        'nome': lista.nome,
                        'status': lista.status,
                        'status_display': lista.get_status_display(),
                        'data_objetivo': lista.data_objetivo.strftime('%d/%m/%Y') if lista.data_objetivo else None,
                    }
                })
            else:
                # Retorna erros de validação
                return JsonResponse({
                    'status': 'error',
                    'message': 'Erro de validação nos dados!',
                    'errors': form.errors
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Dados inválidos. Verifique o formato JSON.'
            }, status=400)
    
    # Se não for uma requisição POST
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido. Use POST para criar uma lista.'
    }, status=405)


@csrf_exempt
def atualizar_lista(request, lista_id):
    """
    Atualiza uma lista existente a partir dos dados enviados via PUT
    """
    # Verifica se a lista existe e pertence ao usuário atual
    lista = get_object_or_404(Lista, id=lista_id, usuario=request.user)
    
    if request.method in ['PUT', 'POST']:
        try:
            # Obtém os dados do corpo da requisição
            dados = json.loads(request.body)
            
            # Cria um formulário com os dados recebidos
            form = ListaForm(dados, instance=lista)
            
            if form.is_valid():
                # Salva as alterações
                lista = form.save()
                
                # Retorna resposta de sucesso
                return JsonResponse({
                    'status': 'success',
                    'message': 'Lista atualizada com sucesso!',
                    'lista': {
                        'id': lista.id,
                        'nome': lista.nome,
                        'objetivo': lista.objetivo,
                        'status': lista.status,
                        'status_display': lista.get_status_display(),
                        'cor': lista.cor,
                        'icone': lista.icone,
                        'data_objetivo': lista.data_objetivo.strftime('%d/%m/%Y') if lista.data_objetivo else None,
                    }
                })
            else:
                # Retorna erros de validação
                return JsonResponse({
                    'status': 'error',
                    'message': 'Erro de validação nos dados!',
                    'errors': form.errors
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Dados inválidos. Verifique o formato JSON.'
            }, status=400)
    
    # Se não for uma requisição PUT ou POST
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido. Use PUT ou POST para atualizar uma lista.'
    }, status=405)


@csrf_exempt
def excluir_lista(request, lista_id):
    """
    Exclui uma lista existente
    """
    # Verifica se a lista existe e pertence ao usuário atual
    lista = get_object_or_404(Lista, id=lista_id, usuario=request.user)
    
    if request.method in ['DELETE', 'POST']:
        try:
            # Armazena o ID e nome da lista antes de excluí-la
            lista_info = {'id': lista.id, 'nome': lista.nome}
            
            # Exclui a lista
            lista.delete()
            
            # Retorna resposta de sucesso
            return JsonResponse({
                'status': 'success',
                'message': f'Lista "{lista_info["nome"]}" excluída com sucesso!',
                'lista_info': lista_info
            })
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Erro ao excluir lista: {str(e)}'
            }, status=500)
    
    # Se não for uma requisição DELETE ou POST
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido. Use DELETE ou POST para excluir uma lista.'
    }, status=405)


@csrf_exempt
def atualizar_status_lista(request, lista_id):
    """
    Atualiza apenas o status de uma lista existente
    """
    # Verifica se a lista existe e pertence ao usuário atual
    lista = get_object_or_404(Lista, id=lista_id, usuario=request.user)
    
    if request.method == 'POST':
        try:
            # Obtém os dados do corpo da requisição
            dados = json.loads(request.body)
            
            # Verifica se o status foi fornecido
            if 'status' not in dados:
                return JsonResponse({
                    'status': 'error',
                    'message': 'O status da lista é obrigatório!'
                }, status=400)
            
            # Verifica se o status é válido
            novo_status = dados['status']
            if novo_status not in [choice[0] for choice in Lista.STATUS_CHOICES]:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Status inválido!'
                }, status=400)
            
            # Atualiza o status da lista
            lista.status = novo_status
            lista.save()
            
            # Retorna resposta de sucesso
            return JsonResponse({
                'status': 'success',
                'message': 'Status da lista atualizado com sucesso!',
                'lista': {
                    'id': lista.id,
                    'nome': lista.nome,
                    'status': lista.status,
                    'status_display': lista.get_status_display(),
                }
            })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Dados inválidos. Verifique o formato JSON.'
            }, status=400)
    
    # Se não for uma requisição POST
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido. Use POST para atualizar o status da lista.'
    }, status=405)


def estatisticas_listas(request):
    """
    Retorna estatísticas sobre as listas do usuário
    """
    # Obtém todas as listas do usuário atual
    listas = Lista.objects.filter(usuario=request.user)
    
    # Estatísticas das listas
    total_listas = listas.count()
    listas_concluidas = listas.filter(status='concluida').count()
    listas_em_andamento = listas.filter(status='em_andamento').count()
    listas_arquivadas = listas.filter(status='arquivada').count()
    listas_pausadas = listas.filter(status='pausada').count()
    
    # Estatísticas dos itens
    itens = Item.objects.filter(lista__usuario=request.user)
    total_itens = itens.count()
    itens_concluidos = itens.filter(status='concluido').count()
    itens_pendentes = itens.filter(status='pendente').count()
    itens_em_andamento = itens.filter(status='em_andamento').count()
    
    # Itens por prioridade
    itens_alta = itens.filter(prioridade='alta').count()
    itens_media = itens.filter(prioridade='media').count()
    itens_baixa = itens.filter(prioridade='baixa').count()
    
    # Itens atrasados
    hoje = timezone.now()
    itens_atrasados = itens.filter(
        data_hora__lt=hoje,
        status__in=['pendente', 'em_andamento']
    ).count()
    
    # Listas com prazo
    listas_com_prazo = listas.filter(data_objetivo__isnull=False).count()
    listas_atrasadas = listas.filter(
        data_objetivo__lt=timezone.now().date(),
        status='em_andamento'
    ).count()
    
    # Prepara o resultado
    resultado = {
        'total_listas': total_listas,
        'listas_concluidas': listas_concluidas,
        'listas_em_andamento': listas_em_andamento,
        'listas_arquivadas': listas_arquivadas,
        'listas_pausadas': listas_pausadas,
        'porcentagem_listas_concluidas': int((listas_concluidas / total_listas) * 100) if total_listas > 0 else 0,
        
        'total_itens': total_itens,
        'itens_concluidos': itens_concluidos,
        'itens_pendentes': itens_pendentes,
        'itens_em_andamento': itens_em_andamento,
        'itens_alta': itens_alta,
        'itens_media': itens_media,
        'itens_baixa': itens_baixa,
        'itens_atrasados': itens_atrasados,
        'porcentagem_itens_concluidos': int((itens_concluidos / total_itens) * 100) if total_itens > 0 else 0,
        
        'listas_com_prazo': listas_com_prazo,
        'listas_atrasadas': listas_atrasadas,
    }
    
    return JsonResponse(resultado)