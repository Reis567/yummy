# Generated by Django 4.2.3 on 2025-05-20 09:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_yummy1', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='endereco',
            field=models.CharField(blank=True, help_text='Endereço completo associado ao item', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, help_text='Latitude do local associado ao item', max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, help_text='Longitude do local associado ao item', max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='moeda',
            field=models.CharField(blank=True, default='BRL', help_text='Código da moeda (ex: BRL, USD)', max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='preco',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Preço estimado ou desejado do item/serviço', max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='raio_busca',
            field=models.PositiveIntegerField(blank=True, default=5000, help_text='Raio de busca em metros para locais próximos', null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='tipo_item',
            field=models.CharField(choices=[('tarefa', 'Tarefa Regular'), ('compra', 'Item de Compra'), ('local', 'Local para Visitar'), ('outro', 'Outro')], default='tarefa', help_text='Tipo do item para facilitar a integração com APIs', max_length=20),
        ),
        migrations.AddField(
            model_name='item',
            name='ultimo_check_preco',
            field=models.DateTimeField(blank=True, help_text='Data da última verificação de preços pela API', null=True),
        ),
        migrations.CreateModel(
            name='LocalSugerido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('endereco', models.CharField(max_length=255)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('preco', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('distancia', models.DecimalField(blank=True, decimal_places=2, help_text='Distância em metros do local de referência', max_digits=10, null=True)),
                ('detalhes', models.JSONField(blank=True, help_text='Dados adicionais fornecidos pela API (horários, avaliações, etc)', null=True)),
                ('data_consulta', models.DateTimeField(auto_now_add=True)),
                ('selecionado', models.BooleanField(default=False, help_text='Indica se este local foi selecionado pelo usuário')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locais_sugeridos', to='app_yummy1.item')),
            ],
            options={
                'verbose_name': 'Local Sugerido',
                'verbose_name_plural': 'Locais Sugeridos',
                'ordering': ['distancia', '-data_consulta'],
            },
        ),
        migrations.CreateModel(
            name='ConsultaAPI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_api', models.CharField(choices=[('claude', 'Claude AI'), ('maps', 'Google Maps'), ('precos', 'API de Preços'), ('outro', 'Outra API')], default='claude', max_length=20)),
                ('parametros', models.JSONField(help_text='Parâmetros enviados na consulta')),
                ('resposta', models.JSONField(blank=True, help_text='Resposta recebida da API', null=True)),
                ('data_consulta', models.DateTimeField(auto_now_add=True)),
                ('sucesso', models.BooleanField(default=True)),
                ('erro', models.TextField(blank=True, null=True)),
                ('tempo_resposta', models.PositiveIntegerField(blank=True, help_text='Tempo de resposta em ms', null=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consultas_api', to='app_yummy1.item')),
            ],
            options={
                'verbose_name': 'Consulta API',
                'verbose_name_plural': 'Consultas API',
                'ordering': ['-data_consulta'],
            },
        ),
    ]
