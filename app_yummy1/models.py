from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Lista(models.Model):
    """Modelo para listas de tarefas"""
    
    STATUS_CHOICES = [
        ('em_andamento', 'Em andamento'),
        ('concluida', 'Concluída'),
        ('arquivada', 'Arquivada'),
        ('pausada', 'Pausada'),
    ]
    
    nome = models.CharField(max_length=100)
    objetivo = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listas')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_objetivo = models.DateField(blank=True, null=True, help_text="Data para conclusão da lista (opcional)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='em_andamento')
    cor = models.CharField(max_length=20, blank=True, default='#FF4500', help_text="Cor de destaque da lista")
    icone = models.CharField(max_length=50, blank=True, default='fas fa-tasks', help_text="Classe de ícone FontAwesome")
    
    # NOVOS CAMPOS DE GEOLOCALIZAÇÃO
    endereco = models.CharField(max_length=255, blank=True, null=True, 
                               help_text="Endereço relacionado à lista")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, 
                                 help_text="Latitude da localização da lista")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True,
                                  help_text="Longitude da localização da lista")
    
    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Lista'
        verbose_name_plural = 'Listas'
    
    def __str__(self):
        return f"{self.nome} ({self.get_status_display()})"
    
    def porcentagem_concluida(self):
        """Calcula a porcentagem de itens concluídos"""
        total_itens = self.itens.count()
        if total_itens == 0:
            return 0
        
        itens_concluidos = self.itens.filter(status='concluido').count()
        return int((itens_concluidos / total_itens) * 100)
    
    def dias_restantes(self):
        """Retorna o número de dias restantes até a data objetivo"""
        if not self.data_objetivo:
            return None
            
        hoje = timezone.now().date()
        return (self.data_objetivo - hoje).days
    
    def tem_geolocalizacao(self):
        """Verifica se a lista possui geolocalização definida"""
        return self.latitude is not None and self.longitude is not None
    
    def itens_alta_prioridade(self):
        """Retorna a quantidade de itens de alta prioridade"""
        return self.itens.filter(prioridade='alta').count()
    
    def itens_media_prioridade(self):
        """Retorna a quantidade de itens de média prioridade"""
        return self.itens.filter(prioridade='media').count()
    
    def itens_baixa_prioridade(self):
        """Retorna a quantidade de itens de baixa prioridade"""
        return self.itens.filter(prioridade='baixa').count()


class Item(models.Model):
    """Modelo para os itens de tarefa dentro de uma lista"""
    
    PRIORIDADE_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Média'),
        ('baixa', 'Baixa'),
    ]
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em andamento'),
        ('concluido', 'Concluído'),
        ('adiado', 'Adiado'),
        ('cancelado', 'Cancelado'),
    ]
    
    TIPO_ITEM_CHOICES = [
        ('tarefa', 'Tarefa Regular'),
        ('compra', 'Item de Compra'),
        ('local', 'Local para Visitar'),
        ('outro', 'Outro'),
    ]
    
    lista = models.ForeignKey(Lista, on_delete=models.CASCADE, related_name='itens')
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_hora = models.DateTimeField(blank=True, null=True, help_text="Data e hora para conclusão (opcional)")
    prioridade = models.CharField(max_length=10, choices=PRIORIDADE_CHOICES, default='media')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    ordem = models.PositiveIntegerField(default=0, help_text="Ordem de exibição do item na lista")
    notas = models.TextField(blank=True, null=True, help_text="Notas adicionais sobre o item")
    
    # Campos para geolocalizacao e APIs de IAs
    tipo_item = models.CharField(max_length=20, choices=TIPO_ITEM_CHOICES, default='tarefa', 
                                help_text="Tipo do item para facilitar a integração com APIs")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, 
                                 help_text="Latitude do local associado ao item")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True,
                                  help_text="Longitude do local associado ao item")
    preco = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                              help_text="Preço estimado ou desejado do item/serviço")
    moeda = models.CharField(max_length=3, default='BRL', blank=True, null=True,
                           help_text="Código da moeda (ex: BRL, USD)")
    endereco = models.CharField(max_length=255, blank=True, null=True,
                              help_text="Endereço completo associado ao item")
    ultimo_check_preco = models.DateTimeField(blank=True, null=True,
                                            help_text="Data da última verificação de preços pela API")
    raio_busca = models.PositiveIntegerField(default=5000, blank=True, null=True,
                                          help_text="Raio de busca em metros para locais próximos")
    
    class Meta:
        ordering = ['ordem', 'prioridade', 'data_hora', 'data_criacao']
        verbose_name = 'Item'
        verbose_name_plural = 'Itens'
    
    def __str__(self):
        return self.nome
    
    def esta_atrasado(self):
        """Verifica se o item está atrasado"""
        if not self.data_hora or self.status == 'concluido':
            return False
            
        agora = timezone.now()
        return self.data_hora < agora
    
    def tempo_restante(self):
        """Retorna o tempo restante até a data limite"""
        if not self.data_hora:
            return None
            
        agora = timezone.now()
        if self.data_hora < agora:
            return "Atrasado"
            
        delta = self.data_hora - agora
        
        # Se for menos de 24h
        if delta.days == 0:
            horas = delta.seconds // 3600
            if horas == 0:
                minutos = delta.seconds // 60
                return f"{minutos} minutos"
            return f"{horas} horas"
        
        # Se for mais de 24h
        return f"{delta.days} dias"
    
    def tem_geolocalizacao(self):
        """Verifica se o item possui geolocalização definida"""
        return self.latitude is not None and self.longitude is not None



class LocalSugerido(models.Model):
    """Modelo para armazenar locais sugeridos pela API para um item"""
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='locais_sugeridos')
    nome = models.CharField(max_length=200)
    endereco = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    preco = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    distancia = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                                  help_text="Distância em metros do local de referência")
    detalhes = models.JSONField(blank=True, null=True, 
                              help_text="Dados adicionais fornecidos pela API (horários, avaliações, etc)")
    data_consulta = models.DateTimeField(auto_now_add=True)
    selecionado = models.BooleanField(default=False, 
                                    help_text="Indica se este local foi selecionado pelo usuário")
    
    class Meta:
        ordering = ['distancia', '-data_consulta']
        verbose_name = 'Local Sugerido'
        verbose_name_plural = 'Locais Sugeridos'
    
    def __str__(self):
        return f"{self.nome} ({self.distancia}m de {self.item.nome})"
    


class ConsultaAPI(models.Model):
    """Modelo para registrar consultas à API externa"""
    
    TIPO_API_CHOICES = [
        ('claude', 'Claude AI'),
        ('maps', 'Google Maps'),
        ('precos', 'API de Preços'),
        ('outro', 'Outra API'),
    ]
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='consultas_api')
    tipo_api = models.CharField(max_length=20, choices=TIPO_API_CHOICES, default='claude')
    parametros = models.JSONField(help_text="Parâmetros enviados na consulta")
    resposta = models.JSONField(blank=True, null=True, help_text="Resposta recebida da API")
    data_consulta = models.DateTimeField(auto_now_add=True)
    sucesso = models.BooleanField(default=True)
    erro = models.TextField(blank=True, null=True)
    tempo_resposta = models.PositiveIntegerField(help_text="Tempo de resposta em ms", blank=True, null=True)
    
    class Meta:
        ordering = ['-data_consulta']
        verbose_name = 'Consulta API'
        verbose_name_plural = 'Consultas API'
    
    def __str__(self):
        return f"Consulta {self.tipo_api} para {self.item.nome} em {self.data_consulta}"


class Categoria(models.Model):
    """Modelo para categorizar listas ou itens"""
    nome = models.CharField(max_length=50)
    descricao = models.CharField(max_length=200, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categorias')
    cor = models.CharField(max_length=20, default='#007bff')
    icone = models.CharField(max_length=50, blank=True, default='fas fa-tag')
    
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']
        unique_together = ['nome', 'usuario']  # Evita categorias duplicadas para o mesmo usuário
    
    def __str__(self):
        return self.nome


class CategorizacaoLista(models.Model):
    """Relação entre Listas e Categorias"""
    lista = models.ForeignKey(Lista, on_delete=models.CASCADE, related_name='categorizacoes')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='listas')
    
    class Meta:
        verbose_name = 'Categorização de Lista'
        verbose_name_plural = 'Categorizações de Listas'
        unique_together = ['lista', 'categoria']  # Evita duplicatas
    
    def __str__(self):
        return f"{self.lista.nome} - {self.categoria.nome}"


class CategorizacaoItem(models.Model):
    """Relação entre Itens e Categorias"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='categorizacoes')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='itens')
    
    class Meta:
        verbose_name = 'Categorização de Item'
        verbose_name_plural = 'Categorizações de Itens'
        unique_together = ['item', 'categoria']  # Evita duplicatas
    
    def __str__(self):
        return f"{self.item.nome} - {self.categoria.nome}"


class SubItem(models.Model):
    """Modelo para sub-tarefas de um item"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='sub_itens')
    nome = models.CharField(max_length=200)
    concluido = models.BooleanField(default=False)
    ordem = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['ordem']
        verbose_name = 'Sub-Item'
        verbose_name_plural = 'Sub-Itens'
    
    def __str__(self):
        return self.nome


class Comentario(models.Model):
    """Modelo para comentários em itens"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'
    
    def __str__(self):
        return f"Comentário de {self.usuario.username} em {self.item.nome}"


class Historico(models.Model):
    """Modelo para registrar o histórico de alterações em itens"""
    ACAO_CHOICES = [
        ('criacao', 'Criação'),
        ('atualizacao', 'Atualização'),
        ('conclusao', 'Conclusão'),
        ('remocao', 'Remoção'),
        ('mudanca_status', 'Mudança de Status'),
        ('mudanca_prioridade', 'Mudança de Prioridade'),
    ]
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='historico')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    acao = models.CharField(max_length=20, choices=ACAO_CHOICES)
    detalhes = models.TextField(blank=True, null=True)
    data = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-data']
        verbose_name = 'Histórico'
        verbose_name_plural = 'Históricos'
    
    def __str__(self):
        return f"{self.get_acao_display()} de {self.item.nome} por {self.usuario.username}"