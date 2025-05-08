from django.shortcuts import render

def home(request):
    """View para a página inicial do Yummy"""
    context = {
        'page_title': 'Home',
        'featured_recipes': [
            {'name': 'Pizza Caseira', 'category': 'Italiana'},
            {'name': 'Feijoada', 'category': 'Brasileira'},
            {'name': 'Sushi', 'category': 'Japonesa'},
        ]
    }
    return render(request, 'home/home.html', context)