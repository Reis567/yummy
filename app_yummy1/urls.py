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
]