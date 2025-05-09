from django.urls import path
from .views import *
app_name = 'app_yummy1'

urlpatterns = [
    path('', home, name='home'),


    # API para Listas (CRUD)
    path('api/listas/', listar_listas, name='api_listar_listas'),
    path('api/listas/<int:lista_id>/', obter_lista, name='api_obter_lista'),
    path('api/listas/criar/', criar_lista, name='api_criar_lista'),
    path('api/listas/<int:lista_id>/atualizar/', atualizar_lista, name='api_atualizar_lista'),
    path('api/listas/<int:lista_id>/excluir/', excluir_lista, name='api_excluir_lista'),
    path('api/listas/<int:lista_id>/status/', atualizar_status_lista, name='api_atualizar_status_lista'),
    path('api/listas/estatisticas/', estatisticas_listas, name='api_estatisticas_listas'),


    path('api/itens/criar/', criar_item, name='api_criar_item'),
    path('api/itens/<int:item_id>/', obter_item, name='api_obter_item'),
    path('api/itens/<int:item_id>/atualizar/', atualizar_item, name='api_atualizar_item'),
    path('api/itens/<int:item_id>/excluir/', excluir_item, name='api_excluir_item'),
    path('api/itens/<int:item_id>/status/', atualizar_status_item, name='api_atualizar_status_item'),
    path('api/itens/<int:item_id>/prioridade/', atualizar_prioridade_item, name='api_atualizar_prioridade_item'),
    path('api/listas/<int:lista_id>/itens/', listar_itens_da_lista, name='api_listar_itens_da_lista'),
    
]