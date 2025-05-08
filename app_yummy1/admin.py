from django.contrib import admin
from .models import Lista, Item, Categoria, CategorizacaoLista, CategorizacaoItem, SubItem, Comentario, Historico


class SubItemInline(admin.TabularInline):
    model = SubItem
    extra = 1


class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0
    readonly_fields = ('usuario', 'data_criacao')


class HistoricoInline(admin.TabularInline):
    model = Historico
    extra = 0
    readonly_fields = ('usuario', 'acao', 'detalhes', 'data')
    can_delete = False


class ItemAdmin(admin.ModelAdmin):
    list_display = ('nome', 'lista', 'prioridade', 'status', 'data_hora', 'esta_atrasado')
    list_filter = ('status', 'prioridade', 'lista__usuario')
    search_fields = ('nome', 'descricao', 'lista__nome')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    fieldsets = (
        (None, {
            'fields': ('lista', 'nome', 'descricao')
        }),
        ('Detalhes', {
            'fields': ('prioridade', 'status', 'ordem', 'data_hora')
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao', 'notas'),
            'classes': ('collapse',),
        }),
    )
    inlines = [SubItemInline, ComentarioInline, HistoricoInline]


class ItemInline(admin.TabularInline):
    model = Item
    extra = 1
    fields = ('nome', 'prioridade', 'status', 'data_hora')
    show_change_link = True


class CategorizacaoListaInline(admin.TabularInline):
    model = CategorizacaoLista
    extra = 1


class ListaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'usuario', 'status', 'data_criacao', 'data_objetivo', 'porcentagem_concluida')
    list_filter = ('status', 'usuario')
    search_fields = ('nome', 'objetivo', 'usuario__username')
    readonly_fields = ('porcentagem_concluida', 'data_criacao')
    fieldsets = (
        (None, {
            'fields': ('nome', 'objetivo', 'usuario')
        }),
        ('Detalhes', {
            'fields': ('status', 'data_objetivo', 'cor', 'icone')
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'porcentagem_concluida'),
            'classes': ('collapse',),
        }),
    )
    inlines = [ItemInline, CategorizacaoListaInline]


class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'usuario', 'descricao', 'cor')
    list_filter = ('usuario',)
    search_fields = ('nome', 'descricao')


class CategorizacaoListaAdmin(admin.ModelAdmin):
    list_display = ('lista', 'categoria')
    list_filter = ('categoria', 'lista__usuario')


class CategorizacaoItemAdmin(admin.ModelAdmin):
    list_display = ('item', 'categoria')
    list_filter = ('categoria', 'item__lista__usuario')


class SubItemAdmin(admin.ModelAdmin):
    list_display = ('nome', 'item', 'concluido', 'ordem')
    list_filter = ('concluido', 'item__lista')
    search_fields = ('nome', 'item__nome')


class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('item', 'usuario', 'texto_curto', 'data_criacao')
    list_filter = ('usuario', 'data_criacao')
    search_fields = ('texto', 'item__nome')
    readonly_fields = ('data_criacao',)
    
    def texto_curto(self, obj):
        return obj.texto[:50] + '...' if len(obj.texto) > 50 else obj.texto
    texto_curto.short_description = 'Texto'


class HistoricoAdmin(admin.ModelAdmin):
    list_display = ('item', 'usuario', 'acao', 'detalhes_curtos', 'data')
    list_filter = ('acao', 'usuario', 'data')
    search_fields = ('detalhes', 'item__nome')
    readonly_fields = ('data',)
    
    def detalhes_curtos(self, obj):
        if not obj.detalhes:
            return '-'
        return obj.detalhes[:50] + '...' if len(obj.detalhes) > 50 else obj.detalhes
    detalhes_curtos.short_description = 'Detalhes'


# Registrar os modelos no admin
admin.site.register(Lista, ListaAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(CategorizacaoLista, CategorizacaoListaAdmin)
admin.site.register(CategorizacaoItem, CategorizacaoItemAdmin)
admin.site.register(SubItem, SubItemAdmin)
admin.site.register(Comentario, ComentarioAdmin)
admin.site.register(Historico, HistoricoAdmin)