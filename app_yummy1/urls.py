from django.urls import path
from .views import *

app_name = 'app_yummy1'

urlpatterns = [
    path('', home, name='home'),

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),

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


    path('api/sub-itens/<int:item_id>/', listar_sub_itens, name='api_listar_sub_itens'),
    path('api/sub-itens/criar/', criar_sub_item, name='api_criar_sub_item'),
    path('api/sub-itens/<int:sub_item_id>/atualizar/', atualizar_sub_item, name='api_atualizar_sub_item'),
    path('api/sub-itens/<int:sub_item_id>/excluir/', excluir_sub_item, name='api_excluir_sub_item'),
    path('api/sub-itens/<int:sub_item_id>/concluido/', atualizar_status_concluido_sub_item, name='api_atualizar_status_concluido_sub_item'),


    # API para Comentários
    path('api/comentarios/<int:item_id>/', listar_comentarios, name='api_listar_comentarios'),
    path('api/comentarios/criar/', criar_comentario, name='api_criar_comentario'),
    path('api/comentarios/<int:comentario_id>/excluir/', excluir_comentario, name='api_excluir_comentario'),
    
    # API para Histórico
    path('api/historico/<int:item_id>/', listar_historico, name='api_listar_historico'),
    
    # API para Categorias
    path('api/categorias/', listar_categorias, name='api_listar_categorias'),
    path('api/categorias/criar/', criar_categoria, name='api_criar_categoria'),
    path('api/categorias/<int:categoria_id>/atualizar/', atualizar_categoria, name='api_atualizar_categoria'),
    path('api/categorias/<int:categoria_id>/excluir/', excluir_categoria, name='api_excluir_categoria'),
    path('api/listas/<int:lista_id>/categorias/', categorizar_lista, name='api_categorizar_lista'),
    path('api/itens/<int:item_id>/categorias/', categorizar_item, name='api_categorizar_item'),

    
]