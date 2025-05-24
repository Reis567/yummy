from django import forms
from django.utils import timezone
from .models import Lista, Item, Categoria, SubItem
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from decimal import Decimal, InvalidOperation

class RegisterForm(UserCreationForm):
    """Formulário personalizado para criação de usuários"""
    
    first_name = forms.CharField(
        max_length=30, 
        required=False, 
        label="Nome",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome'
        })
    )
    
    last_name = forms.CharField(
        max_length=30, 
        required=False, 
        label="Sobrenome",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu sobrenome'
        })
    )
    
    email = forms.EmailField(
        max_length=254, 
        required=True, 
        label="E-mail",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'exemplo@email.com'
        })
    )
    
    username = forms.CharField(
        max_length=150,
        required=True,
        label="Nome de usuário",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Escolha um nome de usuário'
        })
    )
    
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Crie uma senha forte'
        })
    )
    
    password2 = forms.CharField(
        label="Confirme a senha",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme sua senha'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def clean_email(self):
        """Valida se o e-mail já está em uso"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está em uso. Por favor, use outro.")
        return email




class ListaForm(forms.ModelForm):
    """Formulário para criar e editar listas"""
    
    class Meta:
        model = Lista
        fields = ['nome', 'objetivo', 'data_objetivo', 'status', 'cor', 'icone', 
                 'endereco', 'latitude', 'longitude']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nome da lista'
            }),
            'objetivo': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Objetivo desta lista'
            }),
            'data_objetivo': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'cor': forms.TextInput(attrs={
                'class': 'form-control', 
                'type': 'color'
            }),
            'icone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Classe do ícone (ex: fas fa-tasks)'
            }),
            'endereco': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Endereço relacionado à lista'
            }),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
    
    def clean_data_objetivo(self):
        """Valida a data objetivo"""
        data_objetivo = self.cleaned_data.get('data_objetivo')
        if data_objetivo and data_objetivo < timezone.now().date():
            raise forms.ValidationError("A data objetivo não pode ser no passado!")
        return data_objetivo
    
    def clean_nome(self):
        """Valida o nome da lista"""
        nome = self.cleaned_data.get('nome')
        if not nome or not nome.strip():
            raise forms.ValidationError("O nome da lista é obrigatório!")
        return nome.strip()
    
    def clean_latitude(self):
        """Valida a latitude"""
        latitude = self.cleaned_data.get('latitude')
        if latitude is not None:
            try:
                lat_decimal = Decimal(str(latitude))
                if not (-90 <= lat_decimal <= 90):
                    raise forms.ValidationError("Latitude deve estar entre -90 e 90 graus.")
                return lat_decimal
            except (InvalidOperation, TypeError, ValueError):
                raise forms.ValidationError("Latitude inválida.")
        return latitude
    
    def clean_longitude(self):
        """Valida a longitude"""
        longitude = self.cleaned_data.get('longitude')
        if longitude is not None:
            try:
                lng_decimal = Decimal(str(longitude))
                if not (-180 <= lng_decimal <= 180):
                    raise forms.ValidationError("Longitude deve estar entre -180 e 180 graus.")
                return lng_decimal
            except (InvalidOperation, TypeError, ValueError):
                raise forms.ValidationError("Longitude inválida.")
        return longitude
    
    def clean(self):
        """Validação cruzada dos campos"""
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        endereco = cleaned_data.get('endereco')
        
        # Se há coordenadas, ambas devem estar presentes
        if (latitude is not None and longitude is None) or (longitude is not None and latitude is None):
            raise forms.ValidationError("Se definir coordenadas, tanto latitude quanto longitude são obrigatórias.")
        
        # Se há coordenadas mas não há endereço, é válido (usuário pode ter clicado no mapa)
        # Se há endereço mas não há coordenadas, também é válido (usuário pode ter digitado apenas)
        
        return cleaned_data


class ItemForm(forms.ModelForm):
    """Formulário para criar e editar itens de lista"""
    
    class Meta:
        model = Item
        fields = ['nome', 'descricao', 'data_hora', 'prioridade', 'status', 'notas']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da tarefa'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição da tarefa'}),
            'data_hora': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'prioridade': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notas adicionais'}),
        }
    
    def clean_data_hora(self):
        data_hora = self.cleaned_data.get('data_hora')
        # Só valida se foi fornecida uma data (já que o campo é opcional)
        if data_hora and data_hora < timezone.now():
            raise forms.ValidationError("A data e hora não podem ser no passado!")
        return data_hora


class CategoriaForm(forms.ModelForm):
    """Formulário para criar e editar categorias"""
    
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao', 'cor', 'icone']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da categoria'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição breve'}),
            'cor': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'icone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Classe do ícone (ex: fas fa-tag)'}),
        }


class SubItemForm(forms.ModelForm):
    """Formulário para criar e editar sub-itens"""
    
    class Meta:
        model = SubItem
        fields = ['nome', 'concluido']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do sub-item'}),
            'concluido': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ComentarioForm(forms.Form):
    """Formulário para adicionar comentários a um item"""
    
    texto = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Adicione um comentário...'
        }),
        label='',
    )


class PesquisaForm(forms.Form):
    """Formulário para pesquisa de itens e listas"""
    
    termo = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Pesquisar...'
        })
    )
    
    STATUS_CHOICES = [
        ('', 'Todos os status'),
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em andamento'),
        ('concluido', 'Concluído'),
        ('adiado', 'Adiado'),
        ('cancelado', 'Cancelado'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('', 'Todas as prioridades'),
        ('alta', 'Alta'),
        ('media', 'Média'),
        ('baixa', 'Baixa'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    prioridade = forms.ChoiceField(
        choices=PRIORIDADE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.none(),  # Será definido no __init__
        required=False,
        empty_label="Todas as categorias",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super(PesquisaForm, self).__init__(*args, **kwargs)
        
        if usuario:
            self.fields['categoria'].queryset = Categoria.objects.filter(usuario=usuario)


class ItemImportanteForm(forms.Form):
    """Formulário para marcar rapidamente um item como importante"""
    
    nome = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Adicione um item urgente...'
        })
    )
    
    lista = forms.ModelChoiceField(
        queryset=Lista.objects.none(),  # Será definido no __init__
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super(ItemImportanteForm, self).__init__(*args, **kwargs)
        
        if usuario:
            self.fields['lista'].queryset = Lista.objects.filter(
                usuario=usuario, 
                status='em_andamento'
            )






class UserRegisterForm(UserCreationForm):
    """
    Formulário de registro estendido com campos adicionais
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome',
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sobrenome',
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        
        # Personalizando os widgets dos campos padrão
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nome de usuário',
        })
        
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Senha',
        })
        
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar senha',
        })
        
        # Tornando o help_text mais amigável
        self.fields['username'].help_text = 'Necessário. 150 caracteres ou menos. Letras, números e @/./+/-/_ apenas.'
        self.fields['password1'].help_text = 'Sua senha deve conter pelo menos 8 caracteres, não pode ser muito comum e não pode ser totalmente numérica.'
        self.fields['password2'].help_text = 'Digite a mesma senha novamente, para verificação.'
    
    def clean_email(self):
        """
        Valida se o email já existe no sistema
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email já está em uso. Por favor, use outro email.")
        return email