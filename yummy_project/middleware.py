from django.shortcuts import redirect
from django.urls import reverse

class RedirectUnauthenticatedUsersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verifica se o usuário não está autenticado e não está tentando acessar a página de login ou de registro
        if not request.user.is_authenticated:
            # Lista de URLs permitidas para usuários não autenticados
            allowed_paths = [
                reverse('app_yummy1:login'),
                reverse('app_yummy1:register'),
                '/admin/login/',  # Adicione o caminho para a página de login do admin
            ]
            
            # Verifica se o caminho atual está na lista de permitidos
            is_allowed = any(request.path.startswith(path) for path in allowed_paths)
            
            # Se não estiver nos caminhos permitidos, redireciona para login
            if not is_allowed:
                return redirect('app_yummy1:login')
                
        return self.get_response(request)