# Generated by Django 5.2.1 on 2025-05-08 18:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('data_atualizacao', models.DateTimeField(auto_now=True)),
                ('data_hora', models.DateTimeField(blank=True, help_text='Data e hora para conclusão (opcional)', null=True)),
                ('prioridade', models.CharField(choices=[('alta', 'Alta'), ('media', 'Média'), ('baixa', 'Baixa')], default='media', max_length=10)),
                ('status', models.CharField(choices=[('pendente', 'Pendente'), ('em_andamento', 'Em andamento'), ('concluido', 'Concluído'), ('adiado', 'Adiado'), ('cancelado', 'Cancelado')], default='pendente', max_length=20)),
                ('ordem', models.PositiveIntegerField(default=0, help_text='Ordem de exibição do item na lista')),
                ('notas', models.TextField(blank=True, help_text='Notas adicionais sobre o item', null=True)),
            ],
            options={
                'verbose_name': 'Item',
                'verbose_name_plural': 'Itens',
                'ordering': ['ordem', 'prioridade', 'data_hora', 'data_criacao'],
            },
        ),
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50)),
                ('descricao', models.CharField(blank=True, max_length=200)),
                ('cor', models.CharField(default='#007bff', max_length=20)),
                ('icone', models.CharField(blank=True, default='fas fa-tag', max_length=50)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categorias', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Categoria',
                'verbose_name_plural': 'Categorias',
                'ordering': ['nome'],
                'unique_together': {('nome', 'usuario')},
            },
        ),
        migrations.CreateModel(
            name='Historico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acao', models.CharField(choices=[('criacao', 'Criação'), ('atualizacao', 'Atualização'), ('conclusao', 'Conclusão'), ('remocao', 'Remoção'), ('mudanca_status', 'Mudança de Status'), ('mudanca_prioridade', 'Mudança de Prioridade')], max_length=20)),
                ('detalhes', models.TextField(blank=True, null=True)),
                ('data', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historico', to='app_yummy1.item')),
            ],
            options={
                'verbose_name': 'Histórico',
                'verbose_name_plural': 'Históricos',
                'ordering': ['-data'],
            },
        ),
        migrations.CreateModel(
            name='Comentario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.TextField()),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comentarios', to='app_yummy1.item')),
            ],
            options={
                'verbose_name': 'Comentário',
                'verbose_name_plural': 'Comentários',
                'ordering': ['-data_criacao'],
            },
        ),
        migrations.CreateModel(
            name='Lista',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('objetivo', models.TextField(blank=True, null=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('data_objetivo', models.DateField(blank=True, help_text='Data para conclusão da lista (opcional)', null=True)),
                ('status', models.CharField(choices=[('em_andamento', 'Em andamento'), ('concluida', 'Concluída'), ('arquivada', 'Arquivada'), ('pausada', 'Pausada')], default='em_andamento', max_length=20)),
                ('cor', models.CharField(blank=True, default='#FF4500', help_text='Cor de destaque da lista', max_length=20)),
                ('icone', models.CharField(blank=True, default='fas fa-tasks', help_text='Classe de ícone FontAwesome', max_length=50)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Lista',
                'verbose_name_plural': 'Listas',
                'ordering': ['-data_criacao'],
            },
        ),
        migrations.AddField(
            model_name='item',
            name='lista',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens', to='app_yummy1.lista'),
        ),
        migrations.CreateModel(
            name='SubItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('concluido', models.BooleanField(default=False)),
                ('ordem', models.PositiveIntegerField(default=0)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_itens', to='app_yummy1.item')),
            ],
            options={
                'verbose_name': 'Sub-Item',
                'verbose_name_plural': 'Sub-Itens',
                'ordering': ['ordem'],
            },
        ),
        migrations.CreateModel(
            name='CategorizacaoItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens', to='app_yummy1.categoria')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categorizacoes', to='app_yummy1.item')),
            ],
            options={
                'verbose_name': 'Categorização de Item',
                'verbose_name_plural': 'Categorizações de Itens',
                'unique_together': {('item', 'categoria')},
            },
        ),
        migrations.CreateModel(
            name='CategorizacaoLista',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listas', to='app_yummy1.categoria')),
                ('lista', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categorizacoes', to='app_yummy1.lista')),
            ],
            options={
                'verbose_name': 'Categorização de Lista',
                'verbose_name_plural': 'Categorizações de Listas',
                'unique_together': {('lista', 'categoria')},
            },
        ),
    ]
