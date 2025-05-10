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
    """
    Página inicial que mostra as listas do usuário
    """
    # Obtém todas as listas do usuário atual
    listas = Lista.objects.filter(usuario=request.user).order_by('-data_criacao')
    
    # Cria um formulário para nova lista
    form_lista = ListaForm()
    
    # Cria contexto para o template
    context = {
        'page_title': 'Home',
        'listas': listas,
        'form_lista': form_lista,
        # Adiciona estatísticas básicas
        'total_listas': listas.count(),
        'listas_concluidas': listas.filter(status='concluida').count(),
        'listas_em_andamento': listas.filter(status='em_andamento').count(),
    }
    
    return render(request, 'home/home.html', context)






### INICIO ITENS 

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



### FIM LISTAS



### INICIO ITENS 

def listar_itens_da_lista(request, lista_id):
    """
    Lista todos os itens de uma lista específica e retorna em formato JSON
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
            'notas': item.notas,
        })
    
    return JsonResponse({'itens': itens_lista})


def obter_item(request, item_id):
    """
    Obtém os detalhes de um item específico em formato JSON
    """
    # Verifica se o item existe e pertence a uma lista do usuário atual
    item = get_object_or_404(Item, id=item_id, lista__usuario=request.user)
    
    # Formata a data e hora, se existir
    data_hora_formatada = None
    if item.data_hora:
        data_hora_formatada = item.data_hora.strftime('%d/%m/%Y %H:%M')
    
    # Prepara os dados do item
    item_dict = {
        'id': item.id,
        'lista_id': item.lista.id,
        'lista_nome': item.lista.nome,
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
        'notas': item.notas,
        'data_criacao': item.data_criacao.strftime('%d/%m/%Y %H:%M'),
        'data_atualizacao': item.data_atualizacao.strftime('%d/%m/%Y %H:%M'),
    }
    
    # Adiciona os sub-itens, se houver
    sub_itens = SubItem.objects.filter(item=item).order_by('ordem')
    sub_itens_lista = []
    
    for sub_item in sub_itens:
        sub_itens_lista.append({
            'id': sub_item.id,
            'nome': sub_item.nome,
            'concluido': sub_item.concluido,
            'ordem': sub_item.ordem,
        })
    
    item_dict['sub_itens'] = sub_itens_lista
    
    return JsonResponse({'item': item_dict})


@csrf_exempt
def criar_item(request):
    """
    Cria um novo item a partir dos dados enviados via POST
    """
    if request.method == 'POST':
        try:
            # Obtém os dados do POST
            dados = json.loads(request.body)
            
            # Verifica se a lista existe e pertence ao usuário atual
            lista_id = dados.get('lista')
            if not lista_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'ID da lista é obrigatório!'
                }, status=400)
            
            lista = get_object_or_404(Lista, id=lista_id, usuario=request.user)
            
            # Cria um formulário com os dados recebidos
            form = ItemForm(dados)
            
            if form.is_valid():
                # Salva o item, mas não comita ainda
                item = form.save(commit=False)
                # Define a lista correta
                item.lista = lista
                # Salva o item
                item.save()
                
                # Registra no histórico
                Historico.objects.create(
                    item=item,
                    usuario=request.user,
                    acao='criacao',
                    detalhes=f'Item criado com status {item.get_status_display()}'
                )
                
                # Verifica se o status da lista precisa ser atualizado
                verificar_status_lista(lista)
                
                # Retorna resposta de sucesso
                return JsonResponse({
                    'status': 'success',
                    'message': 'Item criado com sucesso!',
                    'item': {
                        'id': item.id,
                        'nome': item.nome,
                        'status': item.status,
                        'status_display': item.get_status_display(),
                        'prioridade': item.prioridade,
                        'prioridade_display': item.get_prioridade_display(),
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
        'message': 'Método não permitido. Use POST para criar um item.'
    }, status=405)


@csrf_exempt
def atualizar_item(request, item_id):
    """
    Atualiza um item existente a partir dos dados enviados via PUT ou POST
    """
    # Verifica se o item existe e pertence a uma lista do usuário atual
    item = get_object_or_404(Item, id=item_id, lista__usuario=request.user)
    
    if request.method in ['PUT', 'POST']:
        try:
            # Obtém os dados do corpo da requisição
            dados = json.loads(request.body)
            
            # Armazena o status atual antes de atualizar
            status_anterior = item.status
            prioridade_anterior = item.prioridade
            
            # Verifica se a lista foi alterada e se a nova lista pertence ao usuário
            nova_lista_id = dados.get('lista')
            if nova_lista_id and nova_lista_id != item.lista.id:
                nova_lista = get_object_or_404(Lista, id=nova_lista_id, usuario=request.user)
                dados['lista'] = nova_lista.id
            
            # Cria um formulário com os dados recebidos
            form = ItemForm(dados, instance=item)
            
            if form.is_valid():
                # Salva as alterações
                item = form.save()
                
                # Registra alterações significativas no histórico
                detalhes = []
                
                if status_anterior != item.status:
                    detalhes.append(f'Status alterado de {dict(Item.STATUS_CHOICES)[status_anterior]} para {item.get_status_display()}')
                    Historico.objects.create(
                        item=item,
                        usuario=request.user,
                        acao='mudanca_status',
                        detalhes=detalhes[-1]
                    )
                
                if prioridade_anterior != item.prioridade:
                    detalhes.append(f'Prioridade alterada de {dict(Item.PRIORIDADE_CHOICES)[prioridade_anterior]} para {item.get_prioridade_display()}')
                    Historico.objects.create(
                        item=item,
                        usuario=request.user,
                        acao='mudanca_prioridade',
                        detalhes=detalhes[-1]
                    )
                
                if detalhes:
                    Historico.objects.create(
                        item=item,
                        usuario=request.user,
                        acao='atualizacao',
                        detalhes='; '.join(detalhes)
                    )
                
                # Verifica se o status da lista precisa ser atualizado
                verificar_status_lista(item.lista)
                
                # Retorna resposta de sucesso
                return JsonResponse({
                    'status': 'success',
                    'message': 'Item atualizado com sucesso!',
                    'item': {
                        'id': item.id,
                        'nome': item.nome,
                        'status': item.status,
                        'status_display': item.get_status_display(),
                        'prioridade': item.prioridade,
                        'prioridade_display': item.get_prioridade_display(),
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
        'message': 'Método não permitido. Use PUT ou POST para atualizar um item.'
    }, status=405)


@csrf_exempt
def excluir_item(request, item_id):
    """
    Exclui um item existente
    """
    # Verifica se o item existe e pertence a uma lista do usuário atual
    item = get_object_or_404(Item, id=item_id, lista__usuario=request.user)
    lista = item.lista  # Guarda a referência da lista antes de excluir o item
    
    if request.method in ['DELETE', 'POST']:
        try:
            # Armazena o ID e nome do item antes de excluí-lo
            item_info = {'id': item.id, 'nome': item.nome}
            
            # Registra no histórico antes de excluir o item
            Historico.objects.create(
                item=item,
                usuario=request.user,
                acao='remocao',
                detalhes=f'Item "{item.nome}" removido'
            )
            
            # Exclui o item
            item.delete()
            
            # Verifica se o status da lista precisa ser atualizado
            verificar_status_lista(lista)
            
            # Retorna resposta de sucesso
            return JsonResponse({
                'status': 'success',
                'message': f'Item "{item_info["nome"]}" excluído com sucesso!',
                'item_info': item_info
            })
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Erro ao excluir item: {str(e)}'
            }, status=500)
    
    # Se não for uma requisição DELETE ou POST
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido. Use DELETE ou POST para excluir um item.'
    }, status=405)


@csrf_exempt
def atualizar_status_item(request, item_id):
    """
    Atualiza apenas o status de um item existente
    """
    # Verifica se o item existe e pertence a uma lista do usuário atual
    item = get_object_or_404(Item, id=item_id, lista__usuario=request.user)
    
    if request.method == 'POST':
        try:
            # Obtém os dados do corpo da requisição
            dados = json.loads(request.body)
            
            # Verifica se o status foi fornecido
            if 'status' not in dados:
                return JsonResponse({
                    'status': 'error',
                    'message': 'O status do item é obrigatório!'
                }, status=400)
            
            # Verifica se o status é válido
            novo_status = dados['status']
            if novo_status not in [choice[0] for choice in Item.STATUS_CHOICES]:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Status inválido!'
                }, status=400)
            
            # Armazena o status atual
            status_anterior = item.status
            
            # Atualiza o status do item
            item.status = novo_status
            item.save()
            
            # Registra no histórico
            if status_anterior != novo_status:
                Historico.objects.create(
                    item=item,
                    usuario=request.user,
                    acao='mudanca_status',
                    detalhes=f'Status alterado de {dict(Item.STATUS_CHOICES)[status_anterior]} para {item.get_status_display()}'
                )
            
            # Verifica se o status da lista precisa ser atualizado
            verificar_status_lista(item.lista)
            
            # Retorna resposta de sucesso
            return JsonResponse({
                'status': 'success',
                'message': 'Status do item atualizado com sucesso!',
                'item': {
                    'id': item.id,
                    'nome': item.nome,
                    'status': item.status,
                    'status_display': item.get_status_display(),
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
        'message': 'Método não permitido. Use POST para atualizar o status do item.'
    }, status=405)


@csrf_exempt
def atualizar_prioridade_item(request, item_id):
    """
    Atualiza apenas a prioridade de um item existente
    """
    # Verifica se o item existe e pertence a uma lista do usuário atual
    item = get_object_or_404(Item, id=item_id, lista__usuario=request.user)
    
    if request.method == 'POST':
        try:
            # Obtém os dados do corpo da requisição
            dados = json.loads(request.body)
            
            # Verifica se a prioridade foi fornecida
            if 'prioridade' not in dados:
                return JsonResponse({
                    'status': 'error',
                    'message': 'A prioridade do item é obrigatória!'
                }, status=400)
            
            # Verifica se a prioridade é válida
            nova_prioridade = dados['prioridade']
            if nova_prioridade not in [choice[0] for choice in Item.PRIORIDADE_CHOICES]:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Prioridade inválida!'
                }, status=400)
            
            # Armazena a prioridade atual
            prioridade_anterior = item.prioridade
            
            # Atualiza a prioridade do item
            item.prioridade = nova_prioridade
            item.save()
            
            # Registra no histórico
            if prioridade_anterior != nova_prioridade:
                Historico.objects.create(
                    item=item,
                    usuario=request.user,
                    acao='mudanca_prioridade',
                    detalhes=f'Prioridade alterada de {dict(Item.PRIORIDADE_CHOICES)[prioridade_anterior]} para {item.get_prioridade_display()}'
                )
            
            # Retorna resposta de sucesso
            return JsonResponse({
                'status': 'success',
                'message': 'Prioridade do item atualizada com sucesso!',
                'item': {
                    'id': item.id,
                    'nome': item.nome,
                    'prioridade': item.prioridade,
                    'prioridade_display': item.get_prioridade_display(),
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
        'message': 'Método não permitido. Use POST para atualizar a prioridade do item.'
    }, status=405)


def verificar_status_lista(lista):
    """
    Verifica e atualiza o status da lista com base no status de seus itens
    """
    # Conta o total de itens e itens concluídos
    total_itens = lista.itens.count()
    itens_concluidos = lista.itens.filter(status='concluido').count()
    
    # Se não houver itens, não altera o status da lista
    if total_itens == 0:
        return
    
    # Se todos os itens estiverem concluídos, marca a lista como concluída
    if total_itens == itens_concluidos:
        # Só atualiza se o status atual não for 'concluida'
        if lista.status != 'concluida':
            lista.status = 'concluida'
            lista.save()
    # Se a lista estiver concluída mas nem todos os itens estiverem concluídos, 
    # volta o status da lista para 'em_andamento'
    elif lista.status == 'concluida':
        lista.status = 'em_andamento'
        lista.save()


### FIM ITENS



### INICIO SUBITENS


def listar_sub_itens(request, item_id):
    """
    Lista todos os sub-itens de um item específico e retorna em formato JSON
    """
    # Verifica se o item existe e pertence a uma lista do usuário atual
    item = get_object_or_404(Item, id=item_id, lista__usuario=request.user)
    
    # Obtém todos os sub-itens do item ordenados
    sub_itens = SubItem.objects.filter(item=item).order_by('ordem')
    sub_itens_lista = []
    
    for sub_item in sub_itens:
        sub_itens_lista.append({
            'id': sub_item.id,
            'nome': sub_item.nome,
            'concluido': sub_item.concluido,
            'ordem': sub_item.ordem,
        })
    
    return JsonResponse({'sub_itens': sub_itens_lista})


@csrf_exempt
def criar_sub_item(request):
    """
    Cria um novo sub-item a partir dos dados enviados via POST
    """
    if request.method == 'POST':
        try:
            # Obtém os dados do POST
            dados = json.loads(request.body)
            
            # Verifica se o ID do item foi fornecido
            if 'item' not in dados:
                return JsonResponse({
                    'status': 'error',
                    'message': 'ID do item é obrigatório!'
                }, status=400)
            
            # Verifica se o item existe e pertence a uma lista do usuário atual
            item_id = dados.get('item')
            item = get_object_or_404(Item, id=item_id, lista__usuario=request.user)
            
            # Cria um novo sub-item
            sub_item = SubItem(
                item=item,
                nome=dados.get('nome', ''),
                concluido=dados.get('concluido', False),
                ordem=dados.get('ordem', 0)
            )
            sub_item.save()
            
            # Retorna resposta de sucesso
            return JsonResponse({
                'status': 'success',
                'message': 'Sub-item criado com sucesso!',
                'sub_item': {
                    'id': sub_item.id,
                    'nome': sub_item.nome,
                    'concluido': sub_item.concluido,
                    'ordem': sub_item.ordem,
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
        'message': 'Método não permitido. Use POST para criar um sub-item.'
    }, status=405)


@csrf_exempt
def atualizar_sub_item(request, sub_item_id):
    """
    Atualiza um sub-item existente a partir dos dados enviados via PUT ou POST
    """
    # Verifica se o sub-item existe e pertence a um item de uma lista do usuário atual
    sub_item = get_object_or_404(SubItem, id=sub_item_id, item__lista__usuario=request.user)
    
    if request.method in ['PUT', 'POST']:
        try:
            # Obtém os dados do corpo da requisição
            dados = json.loads(request.body)
            
            # Atualiza os campos do sub-item
            if 'nome' in dados:
                sub_item.nome = dados['nome']
            if 'concluido' in dados:
                sub_item.concluido = dados['concluido']
            if 'ordem' in dados:
                sub_item.ordem = dados['ordem']
            
            # Salva as alterações
            sub_item.save()
            
            # Retorna resposta de sucesso
            return JsonResponse({
                'status': 'success',
                'message': 'Sub-item atualizado com sucesso!',
                'sub_item': {
                    'id': sub_item.id,
                    'nome': sub_item.nome,
                    'concluido': sub_item.concluido,
                    'ordem': sub_item.ordem,
                }
            })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Dados inválidos. Verifique o formato JSON.'
            }, status=400)
    
    # Se não for uma requisição PUT ou POST
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido. Use PUT ou POST para atualizar um sub-item.'
    }, status=405)


@csrf_exempt
def excluir_sub_item(request, sub_item_id):
    """
    Exclui um sub-item existente
    """
    # Verifica se o sub-item existe e pertence a um item de uma lista do usuário atual
    sub_item = get_object_or_404(SubItem, id=sub_item_id, item__lista__usuario=request.user)
    
    if request.method in ['DELETE', 'POST']:
        try:
            # Armazena o ID e nome do sub-item antes de excluí-lo
            sub_item_info = {'id': sub_item.id, 'nome': sub_item.nome}
            
            # Exclui o sub-item
            sub_item.delete()
            
            # Retorna resposta de sucesso
            return JsonResponse({
                'status': 'success',
                'message': f'Sub-item "{sub_item_info["nome"]}" excluído com sucesso!',
                'sub_item_info': sub_item_info
            })
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Erro ao excluir sub-item: {str(e)}'
            }, status=500)
    
    # Se não for uma requisição DELETE ou POST
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido. Use DELETE ou POST para excluir um sub-item.'
    }, status=405)


@csrf_exempt
def atualizar_status_concluido_sub_item(request, sub_item_id):
    """
    Atualiza apenas o status 'concluido' de um sub-item existente
    """
    # Verifica se o sub-item existe e pertence a um item de uma lista do usuário atual
    sub_item = get_object_or_404(SubItem, id=sub_item_id, item__lista__usuario=request.user)
    
    if request.method == 'POST':
        try:
            # Obtém os dados do corpo da requisição
            dados = json.loads(request.body)
            
            # Verifica se o status 'concluido' foi fornecido
            if 'concluido' not in dados:
                return JsonResponse({
                    'status': 'error',
                    'message': 'O status concluido do sub-item é obrigatório!'
                }, status=400)
            
            # Atualiza o status 'concluido' do sub-item
            sub_item.concluido = dados['concluido']
            sub_item.save()
            
            # Verifica se todos os sub-itens estão concluídos
            if sub_item.item.sub_itens.exists():
                todos_concluidos = all(si.concluido for si in sub_item.item.sub_itens.all())
                
                # Se todos os sub-itens estiverem concluídos, marca o item como concluído
                if todos_concluidos and sub_item.item.status != 'concluido':
                    sub_item.item.status = 'concluido'
                    sub_item.item.save()
                    
                    # Registra no histórico
                    Historico.objects.create(
                        item=sub_item.item,
                        usuario=request.user,
                        acao='conclusao',
                        detalhes='Item concluído automaticamente após conclusão de todos os sub-itens'
                    )
                    
                    # Verifica se o status da lista precisa ser atualizado
                    verificar_status_lista(sub_item.item.lista)
            
            # Retorna resposta de sucesso
            return JsonResponse({
                'status': 'success',
                'message': 'Status do sub-item atualizado com sucesso!',
                'sub_item': {
                    'id': sub_item.id,
                    'nome': sub_item.nome,
                    'concluido': sub_item.concluido,
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
        'message': 'Método não permitido. Use POST para atualizar o status do sub-item.'
    }, status=405)



### FIM SUBITENS 



### INICIO COMENTARIOS 

def listar_comentarios(request, item_id):
    """
    Lista todos os comentários de um item específico e retorna em formato JSON
    """
    # Verifica se o item existe e pertence a uma lista do usuário atual
    item = get_object_or_404(Item, id=item_id, lista__usuario=request.user)
    
    # Obtém todos os comentários do item ordenados por data de criação (mais recentes primeiro)
    comentarios = Comentario.objects.filter(item=item).order_by('-data_criacao')
    comentarios_lista = []
    
    for comentario in comentarios:
        comentarios_lista.append({
            'id': comentario.id,
            'texto': comentario.texto,
            'usuario': comentario.usuario.username,
            'data_criacao': comentario.data_criacao.strftime('%d/%m/%Y %H:%M'),
            'e_meu': comentario.usuario.id == request.user.id,
        })
    
    return JsonResponse({'comentarios': comentarios_lista})


@csrf_exempt
def criar_comentario(request):
    """
    Cria um novo comentário a partir dos dados enviados via POST
    """
    if request.method == 'POST':
        try:
            # Obtém os dados do POST
            dados = json.loads(request.body)
            
            # Verifica se o ID do item foi fornecido
            if 'item' not in dados:
                return JsonResponse({
                    'status': 'error',
                    'message': 'ID do item é obrigatório!'
                }, status=400)
            
            # Verifica se o texto foi fornecido
            if 'texto' not in dados or not dados['texto'].strip():
                return JsonResponse({
                    'status': 'error',
                    'message': 'O texto do comentário é obrigatório!'
                }, status=400)
            
            # Verifica se o item existe e pertence a uma lista do usuário atual
            item_id = dados.get('item')
            item = get_object_or_404(Item, id=item_id, lista__usuario=request.user)
            
            # Cria um novo comentário
            comentario = Comentario(
                item=item,
                usuario=request.user,
                texto=dados.get('texto').strip()
            )
            comentario.save()
            
            # Retorna resposta de sucesso
            return JsonResponse({
                'status': 'success',
                'message': 'Comentário adicionado com sucesso!',
                'comentario': {
                    'id': comentario.id,
                    'texto': comentario.texto,
                    'usuario': comentario.usuario.username,
                    'data_criacao': comentario.data_criacao.strftime('%d/%m/%Y %H:%M'),
                    'e_meu': True,
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
        'message': 'Método não permitido. Use POST para criar um comentário.'
    }, status=405)


@csrf_exempt
def excluir_comentario(request, comentario_id):
    """
    Exclui um comentário existente
    """
    # Verifica se o comentário existe e foi criado pelo usuário atual
    comentario = get_object_or_404(Comentario, id=comentario_id, usuario=request.user)
    
    if request.method in ['DELETE', 'POST']:
        try:
            # Armazena o ID do comentário antes de excluí-lo
            comentario_info = {'id': comentario.id}
            
            # Exclui o comentário
            comentario.delete()
            
            # Retorna resposta de sucesso
            return JsonResponse({
                'status': 'success',
                'message': 'Comentário excluído com sucesso!',
                'comentario_info': comentario_info
            })
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Erro ao excluir comentário: {str(e)}'
            }, status=500)
    
    # Se não for uma requisição DELETE ou POST
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido. Use DELETE ou POST para excluir um comentário.'
    }, status=405)


### FIM COMENTARIOS 


### HISTORICO

def listar_historico(request, item_id):
    """
    Lista todo o histórico de um item específico e retorna em formato JSON
    """
    # Verifica se o item existe e pertence a uma lista do usuário atual
    item = get_object_or_404(Item, id=item_id, lista__usuario=request.user)
    
    # Obtém todo o histórico do item ordenado por data (mais recentes primeiro)
    historicos = Historico.objects.filter(item=item).order_by('-data')
    historicos_lista = []
    
    for historico in historicos:
        historicos_lista.append({
            'id': historico.id,
            'acao': historico.acao,
            'acao_display': historico.get_acao_display(),
            'detalhes': historico.detalhes,
            'usuario': historico.usuario.username,
            'data': historico.data.strftime('%d/%m/%Y %H:%M'),
        })
    
    return JsonResponse({'historico': historicos_lista})

### FIM HISTORICO



### CATEGORIAS

def listar_categorias(request):
    """
    Lista todas as categorias do usuário atual e retorna em formato JSON
    """
    # Obtém todas as categorias do usuário atual
    categorias = Categoria.objects.filter(usuario=request.user).order_by('nome')
    categorias_lista = []
    
    for categoria in categorias:
        categorias_lista.append({
            'id': categoria.id,
            'nome': categoria.nome,
            'descricao': categoria.descricao,
            'cor': categoria.cor,
            'icone': categoria.icone,
            'total_listas': categoria.listas.count(),
            'total_itens': categoria.itens.count(),
        })
    
    return JsonResponse({'categorias': categorias_lista})


@csrf_exempt
def criar_categoria(request):
    """
    Cria uma nova categoria a partir dos dados enviados via POST
    """
    if request.method == 'POST':
        try:
            # Obtém os dados do POST
            dados = json.loads(request.body)
            
            # Verifica se o nome foi fornecido
            if 'nome' not in dados or not dados['nome'].strip():
                return JsonResponse({
                    'status': 'error',
                    'message': 'O nome da categoria é obrigatório!'
                }, status=400)
            
            # Verifica se já existe uma categoria com o mesmo nome para o usuário
            nome = dados.get('nome').strip()
            if Categoria.objects.filter(usuario=request.user, nome=nome).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Já existe uma categoria com esse nome!'
                }, status=400)
            
            # Cria uma nova categoria
            categoria = Categoria(
                usuario=request.user,
                nome=nome,
                descricao=dados.get('descricao', ''),
                cor=dados.get('cor', '#007bff'),
                icone=dados.get('icone', 'fas fa-tag')
            )
            categoria.save()
            
            # Retorna resposta de sucesso
            return JsonResponse({
                'status': 'success',
                'message': 'Categoria criada com sucesso!',
                'categoria': {
                    'id': categoria.id,
                    'nome': categoria.nome,
                    'descricao': categoria.descricao,
                    'cor': categoria.cor,
                    'icone': categoria.icone,
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
        'message': 'Método não permitido. Use POST para criar uma categoria.'
    }, status=405)


@csrf_exempt
def atualizar_categoria(request, categoria_id):
    """
    Atualiza uma categoria existente a partir dos dados enviados via PUT ou POST
    """
    # Verifica se a categoria existe e pertence ao usuário atual
    categoria = get_object_or_404(Categoria, id=categoria_id, usuario=request.user)
    
    if request.method in ['PUT', 'POST']:
        try:
            # Obtém os dados do corpo da requisição
            dados = json.loads(request.body)
            
            # Verifica se o nome foi fornecido
            if 'nome' in dados and not dados['nome'].strip():
                return JsonResponse({
                    'status': 'error',
                    'message': 'O nome da categoria não pode ser vazio!'
                }, status=400)
            
            # Verifica se já existe uma categoria com o mesmo nome para o usuário (excluindo a atual)
            if 'nome' in dados:
                nome = dados.get('nome').strip()
                if Categoria.objects.filter(usuario=request.user, nome=nome).exclude(id=categoria.id).exists():
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Já existe uma categoria com esse nome!'
                    }, status=400)
                categoria.nome = nome
            
            # Atualiza os demais campos da categoria
            if 'descricao' in dados:
                categoria.descricao = dados['descricao']
            if 'cor' in dados:
                categoria.cor = dados['cor']
            if 'icone' in dados:
                categoria.icone = dados['icone']
            
            # Salva as alterações
            categoria.save()
            
            # Retorna resposta de sucesso
            return JsonResponse({
                'status': 'success',
                'message': 'Categoria atualizada com sucesso!',
                'categoria': {
                    'id': categoria.id,
                    'nome': categoria.nome,
                    'descricao': categoria.descricao,
                    'cor': categoria.cor,
                    'icone': categoria.icone,
                }
            })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Dados inválidos. Verifique o formato JSON.'
            }, status=400)
    
    # Se não for uma requisição PUT ou POST
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido. Use PUT ou POST para atualizar uma categoria.'
    }, status=405)


@csrf_exempt
def excluir_categoria(request, categoria_id):
    """
    Exclui uma categoria existente
    """
    # Verifica se a categoria existe e pertence ao usuário atual
    categoria = get_object_or_404(Categoria, id=categoria_id, usuario=request.user)
    
    if request.method in ['DELETE', 'POST']:
        try:
            # Armazena o ID e nome da categoria antes de excluí-la
            categoria_info = {'id': categoria.id, 'nome': categoria.nome}
            
            # Exclui a categoria
            categoria.delete()
            
            # Retorna resposta de sucesso
            return JsonResponse({
                'status': 'success',
                'message': f'Categoria "{categoria_info["nome"]}" excluída com sucesso!',
                'categoria_info': categoria_info
            })
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Erro ao excluir categoria: {str(e)}'
            }, status=500)
    
    # Se não for uma requisição DELETE ou POST
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido. Use DELETE ou POST para excluir uma categoria.'
    }, status=405)


@csrf_exempt
def categorizar_lista(request, lista_id):
    """
    Associa ou desassocia categorias a uma lista
    """
    # Verifica se a lista existe e pertence ao usuário atual
    lista = get_object_or_404(Lista, id=lista_id, usuario=request.user)
    
    if request.method == 'POST':
        try:
            # Obtém os dados do corpo da requisição
            dados = json.loads(request.body)
            
            # Verifica se as categorias foram fornecidas
            if 'categorias' not in dados or not isinstance(dados['categorias'], list):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Lista de IDs de categorias é obrigatória!'
                }, status=400)
            
            # Limpa as categorizações atuais
            CategorizacaoLista.objects.filter(lista=lista).delete()
            
            # Adiciona as novas categorias
            categorias_adicionadas = []
            for categoria_id in dados['categorias']:
                try:
                    # Verifica se a categoria existe e pertence ao usuário atual
                    categoria = get_object_or_404(Categoria, id=categoria_id, usuario=request.user)
                    
                    # Cria a associação
                    CategorizacaoLista.objects.create(lista=lista, categoria=categoria)
                    
                    categorias_adicionadas.append({
                        'id': categoria.id,
                        'nome': categoria.nome,
                    })
                except:
                    # Ignora categorias inválidas
                    pass
            
            # Retorna resposta de sucesso
            return JsonResponse({
                'status': 'success',
                'message': 'Categorias associadas com sucesso!',
                'lista': {
                    'id': lista.id,
                    'nome': lista.nome,
                },
                'categorias': categorias_adicionadas
            })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Dados inválidos. Verifique o formato JSON.'
            }, status=400)
    
    # Se não for uma requisição POST
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido. Use POST para associar categorias.'
    }, status=405)


@csrf_exempt
def categorizar_item(request, item_id):
    """
    Associa ou desassocia categorias a um item
    """
    # Verifica se o item existe e pertence a uma lista do usuário atual
    item = get_object_or_404(Item, id=item_id, lista__usuario=request.user)
    
    if request.method == 'POST':
        try:
            # Obtém os dados do corpo da requisição
            dados = json.loads(request.body)
            
            # Verifica se as categorias foram fornecidas
            if 'categorias' not in dados or not isinstance(dados['categorias'], list):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Lista de IDs de categorias é obrigatória!'
                }, status=400)
            
            # Limpa as categorizações atuais
            CategorizacaoItem.objects.filter(item=item).delete()
            
            # Adiciona as novas categorias
            categorias_adicionadas = []
            for categoria_id in dados['categorias']:
                try:
                    # Verifica se a categoria existe e pertence ao usuário atual
                    categoria = get_object_or_404(Categoria, id=categoria_id, usuario=request.user)
                    
                    # Cria a associação
                    CategorizacaoItem.objects.create(item=item, categoria=categoria)
                    
                    categorias_adicionadas.append({
                        'id': categoria.id,
                        'nome': categoria.nome,
                    })
                except:
                    # Ignora categorias inválidas
                    pass
            
            # Retorna resposta de sucesso
            return JsonResponse({
                'status': 'success',
                'message': 'Categorias associadas com sucesso!',
                'item': {
                    'id': item.id,
                    'nome': item.nome,
                },
                'categorias': categorias_adicionadas
            })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Dados inválidos. Verifique o formato JSON.'
            }, status=400)
    
    # Se não for uma requisição POST
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido. Use POST para associar categorias.'
    }, status=405)

### CATEGORIAS