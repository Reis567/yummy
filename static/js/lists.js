/**
 * Arquivo JS para manipulação das listas
 * Este script gerencia todas as operações CRUD para listas no frontend
 */

// Objeto principal para operações com listas
const ListaManager = {
    // URL base para as APIs de lista
    apiUrls: {
        listar: '/api/listas/',
        obter: (id) => `/api/listas/${id}/`,
        criar: '/api/listas/criar/',
        atualizar: (id) => `/api/listas/${id}/atualizar/`,
        excluir: (id) => `/api/listas/${id}/excluir/`,
        atualizarStatus: (id) => `/api/listas/${id}/status/`,
        estatisticas: '/api/listas/estatisticas/'
    },
    
    // Método para obter o token CSRF
    getCSRFToken: function() {
        return document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    },
    
    // Inicializa o gerenciador de listas
    init: function() {
        // Registra os eventos de clique
        this.registrarEventos();
        
        // Carrega as listas ao iniciar a página
        this.carregarListas();
        
        // Carrega as estatísticas
        this.carregarEstatisticas();
        
        console.log('ListaManager inicializado');
    },
    
    // Registra eventos para interações com as listas
    registrarEventos: function() {
        // Modal de criação de lista
        document.getElementById('btnCriarLista')?.addEventListener('click', this.abrirModalCriarLista.bind(this));
        document.getElementById('formCriarLista')?.addEventListener('submit', this.criarLista.bind(this));
        
        // Pesquisa e filtros
        document.getElementById('pesquisaListas')?.addEventListener('input', this.filtrarListas.bind(this));
        document.getElementById('filtroStatusListas')?.addEventListener('change', this.filtrarListas.bind(this));
        
        // Atualização do container de listas para eventos delegados
        const listaContainer = document.getElementById('listaContainer');
        if (listaContainer) {
            // Delegação de eventos para os botões de cada lista
            listaContainer.addEventListener('click', (e) => {
                // Clique no botão de editar lista
                if (e.target.matches('.btn-editar-lista') || e.target.closest('.btn-editar-lista')) {
                    const listaId = e.target.closest('.lista-card').dataset.listaId;
                    this.abrirModalEditarLista(listaId);
                }
                
                // Clique no botão de excluir lista
                if (e.target.matches('.btn-excluir-lista') || e.target.closest('.btn-excluir-lista')) {
                    const listaId = e.target.closest('.lista-card').dataset.listaId;
                    const listaNome = e.target.closest('.lista-card').dataset.listaNome;
                    this.confirmarExclusaoLista(listaId, listaNome);
                }
                
                // Clique no botão de mudar status da lista
                if (e.target.matches('.dropdown-status-lista .dropdown-item') || e.target.closest('.dropdown-status-lista .dropdown-item')) {
                    const listaId = e.target.closest('.lista-card').dataset.listaId;
                    const novoStatus = e.target.dataset.status || e.target.closest('.dropdown-item').dataset.status;
                    this.mudarStatusLista(listaId, novoStatus);
                }
                
                // Clique para abrir a lista (visualizar detalhes)
                if (e.target.matches('.lista-card-link') || e.target.closest('.lista-card-link')) {
                    if (!e.target.closest('.dropdown-menu') && !e.target.closest('button')) {
                        const listaId = e.target.closest('.lista-card').dataset.listaId;
                        this.abrirLista(listaId);
                    }
                }
            });
        }
        
        // Modal de edição de lista
        document.getElementById('formEditarLista')?.addEventListener('submit', this.atualizarLista.bind(this));
    },
    
    // Carrega todas as listas do usuário
    carregarListas: async function() {
        const listaContainer = document.getElementById('listaContainer');
        if (!listaContainer) return;
        
        try {
            // Mostrar loading
            listaContainer.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">Carregando listas...</p></div>';
            
            // Fazer a requisição
            const response = await fetch(this.apiUrls.listar);
            
            // Verificar se a requisição foi bem-sucedida
            if (!response.ok) {
                throw new Error('Erro ao carregar listas');
            }
            
            // Converter a resposta para JSON
            const data = await response.json();
            
            // Verificar se existem listas
            if (data.listas.length === 0) {
                listaContainer.innerHTML = `
                    <div class="text-center py-5">
                        <div class="empty-state">
                            <i class="fas fa-clipboard-list fa-3x text-muted mb-3"></i>
                            <h4>Você ainda não tem listas</h4>
                            <p class="text-muted">Crie sua primeira lista para começar a organizar suas tarefas</p>
                            <button id="btnCriarListaEmpty" class="btn btn-primary">
                                <i class="fas fa-plus me-2"></i>Criar Lista
                            </button>
                        </div>
                    </div>
                `;
                
                // Adicionar evento ao botão de criar lista no estado vazio
                document.getElementById('btnCriarListaEmpty')?.addEventListener('click', this.abrirModalCriarLista.bind(this));
                
                return;
            }
            
            // Renderizar as listas
            listaContainer.innerHTML = data.listas.map(lista => this.renderizarCardLista(lista)).join('');
            
        } catch (error) {
            console.error('Erro ao carregar listas:', error);
            listaContainer.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Ocorreu um erro ao carregar suas listas. Por favor, tente novamente.
                </div>
            `;
        }
    },
    
    // Filtra as listas com base na pesquisa e nos filtros selecionados
    filtrarListas: function() {
        const termoPesquisa = document.getElementById('pesquisaListas')?.value.toLowerCase() || '';
        const filtroStatus = document.getElementById('filtroStatusListas')?.value || '';
        
        // Seleciona todos os cards de lista
        const listaCards = document.querySelectorAll('.lista-card');
        
        // Para cada card, verifica se deve ser exibido ou ocultado
        listaCards.forEach(card => {
            const nome = card.dataset.listaNome.toLowerCase();
            const objetivo = card.dataset.listaObjetivo?.toLowerCase() || '';
            const status = card.dataset.listaStatus;
            
            // Verifica se o card atende aos critérios de pesquisa e filtro
            const atendeTermoPesquisa = nome.includes(termoPesquisa) || objetivo.includes(termoPesquisa);
            const atendeFiltroStatus = filtroStatus === '' || status === filtroStatus;
            
            // Exibe ou oculta o card com base nos critérios
            if (atendeTermoPesquisa && atendeFiltroStatus) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
        
        // Verifica se há listas visíveis após a filtragem
        const listasVisiveis = document.querySelectorAll('.lista-card[style="display: block"]');
        const containerVazio = document.getElementById('listaContainerVazio');
        
        if (listasVisiveis.length === 0) {
            // Não há listas visíveis, mostra mensagem
            if (!containerVazio) {
                const listaContainer = document.getElementById('listaContainer');
                const mensagemVazia = document.createElement('div');
                mensagemVazia.id = 'listaContainerVazio';
                mensagemVazia.className = 'text-center py-4 mt-3';
                mensagemVazia.innerHTML = `
                    <i class="fas fa-search fa-2x text-muted mb-3"></i>
                    <h5>Nenhuma lista encontrada</h5>
                    <p class="text-muted">Tente ajustar seus filtros ou criar uma nova lista</p>
                `;
                listaContainer.appendChild(mensagemVazia);
            }
        } else {
            // Há listas visíveis, remove a mensagem se existir
            if (containerVazio) {
                containerVazio.remove();
            }
        }
    },
    
    // Carrega estatísticas das listas
    carregarEstatisticas: async function() {
        const estatisticasContainer = document.getElementById('estatisticasContainer');
        if (!estatisticasContainer) return;
        
        try {
            // Fazer a requisição
            const response = await fetch(this.apiUrls.estatisticas);
            
            // Verificar se a requisição foi bem-sucedida
            if (!response.ok) {
                throw new Error('Erro ao carregar estatísticas');
            }
            
            // Converter a resposta para JSON
            const stats = await response.json();
            
            // Atualiza estatísticas no container
            estatisticasContainer.innerHTML = `
                <div class="row g-3">
                    <div class="col-md-3 col-6">
                        <div class="stat-card bg-white rounded shadow-sm p-3">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="text-muted mb-1">Total de Listas</h6>
                                    <h4>${stats.total_listas}</h4>
                                </div>
                                <div class="stat-icon rounded-circle d-flex align-items-center justify-content-center">
                                    <i class="fas fa-clipboard-list"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3 col-6">
                        <div class="stat-card bg-white rounded shadow-sm p-3">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="text-muted mb-1">Listas Concluídas</h6>
                                    <h4>${stats.listas_concluidas}</h4>
                                </div>
                                <div class="stat-icon rounded-circle bg-success text-white d-flex align-items-center justify-content-center">
                                    <i class="fas fa-check"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3 col-6">
                        <div class="stat-card bg-white rounded shadow-sm p-3">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="text-muted mb-1">Total de Tarefas</h6>
                                    <h4>${stats.total_itens}</h4>
                                </div>
                                <div class="stat-icon rounded-circle bg-info text-white d-flex align-items-center justify-content-center">
                                    <i class="fas fa-tasks"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3 col-6">
                        <div class="stat-card bg-white rounded shadow-sm p-3">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="text-muted mb-1">Tarefas Atrasadas</h6>
                                    <h4>${stats.itens_atrasados}</h4>
                                </div>
                                <div class="stat-icon rounded-circle bg-danger text-white d-flex align-items-center justify-content-center">
                                    <i class="fas fa-exclamation-triangle"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-3">
                    <div class="col-md-6">
                        <div class="bg-white rounded shadow-sm p-3">
                            <h6 class="mb-3">Progresso das Listas</h6>
                            <div class="progress mb-2" style="height: 20px;">
                                <div class="progress-bar bg-success" role="progressbar" style="width: ${stats.porcentagem_listas_concluidas}%;" 
                                    aria-valuenow="${stats.porcentagem_listas_concluidas}" aria-valuemin="0" aria-valuemax="100">
                                    ${stats.porcentagem_listas_concluidas}%
                                </div>
                            </div>
                            <div class="d-flex justify-content-between text-muted small">
                                <span>Concluídas: ${stats.listas_concluidas}</span>
                                <span>Total: ${stats.total_listas}</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="bg-white rounded shadow-sm p-3">
                            <h6 class="mb-3">Progresso das Tarefas</h6>
                            <div class="progress mb-2" style="height: 20px;">
                                <div class="progress-bar bg-success" role="progressbar" style="width: ${stats.porcentagem_itens_concluidos}%;" 
                                    aria-valuenow="${stats.porcentagem_itens_concluidos}" aria-valuemin="0" aria-valuemax="100">
                                    ${stats.porcentagem_itens_concluidos}%
                                </div>
                            </div>
                            <div class="d-flex justify-content-between text-muted small">
                                <span>Concluídas: ${stats.itens_concluidos}</span>
                                <span>Total: ${stats.total_itens}</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-3">
                    <div class="col-md-12">
                        <div class="bg-white rounded shadow-sm p-3">
                            <h6 class="mb-3">Tarefas por Prioridade</h6>
                            <div class="d-flex justify-content-between mb-2">
                                <span>Alta</span>
                                <span>${stats.itens_alta}</span>
                            </div>
                            <div class="progress mb-3" style="height: 8px;">
                                <div class="progress-bar bg-danger" role="progressbar" 
                                    style="width: ${stats.total_itens > 0 ? (stats.itens_alta / stats.total_itens) * 100 : 0}%;">
                                </div>
                            </div>
                            <div class="d-flex justify-content-between mb-2">
                                <span>Média</span>
                                <span>${stats.itens_media}</span>
                            </div>
                            <div class="progress mb-3" style="height: 8px;">
                                <div class="progress-bar bg-warning" role="progressbar" 
                                    style="width: ${stats.total_itens > 0 ? (stats.itens_media / stats.total_itens) * 100 : 0}%;">
                                </div>
                            </div>
                            <div class="d-flex justify-content-between mb-2">
                                <span>Baixa</span>
                                <span>${stats.itens_baixa}</span>
                            </div>
                            <div class="progress mb-3" style="height: 8px;">
                                <div class="progress-bar bg-success" role="progressbar" 
                                    style="width: ${stats.total_itens > 0 ? (stats.itens_baixa / stats.total_itens) * 100 : 0}%;">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
        } catch (error) {
            console.error('Erro ao carregar estatísticas:', error);
            estatisticasContainer.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Ocorreu um erro ao carregar as estatísticas.
                </div>
            `;
        }
    },
    
    // Renderiza um card para uma lista
    renderizarCardLista: function(lista) {
        // Define a cor de fundo com base no status
        let statusClass = '';
        let statusBadge = '';
        
        switch (lista.status) {
            case 'concluida':
                statusClass = 'border-success';
                statusBadge = '<span class="badge bg-success">Concluída</span>';
                break;
            case 'arquivada':
                statusClass = 'border-secondary opacity-75';
                statusBadge = '<span class="badge bg-secondary">Arquivada</span>';
                break;
            case 'pausada':
                statusClass = 'border-warning';
                statusBadge = '<span class="badge bg-warning text-dark">Pausada</span>';
                break;
            default:
                statusClass = '';
                statusBadge = lista.data_objetivo ? 
                    '<span class="badge bg-info">Em andamento</span>' : 
                    '<span class="badge bg-primary">Em andamento</span>';
        }
        
        // Template para o card da lista
        return `
            <div class="lista-card ${statusClass} mb-3" 
                data-lista-id="${lista.id}" 
                data-lista-nome="${lista.nome}" 
                data-lista-objetivo="${lista.objetivo || ''}" 
                data-lista-status="${lista.status}">
                <div class="card lista-card-link" style="border-left: 5px solid ${lista.cor};">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h5 class="card-title mb-0">
                                <i class="${lista.icone} me-2" style="color: ${lista.cor};"></i>
                                ${lista.nome}
                            </h5>
                            <div class="dropdown">
                                <button class="btn btn-sm btn-light" type="button" data-bs-toggle="dropdown">
                                    <i class="fas fa-ellipsis-v"></i>
                                </button>
                                <ul class="dropdown-menu dropdown-menu-end">
                                    <li>
                                        <button class="dropdown-item btn-editar-lista">
                                            <i class="fas fa-edit me-2"></i>Editar
                                        </button>
                                    </li>
                                    <li>
                                        <button class="dropdown-item" data-bs-toggle="dropdown" data-bs-auto-close="outside">
                                            <i class="fas fa-tag me-2"></i>Status
                                        </button>
                                        <ul class="dropdown-menu dropdown-menu-end dropdown-status-lista">
                                            <li><button class="dropdown-item" data-status="em_andamento">
                                                <i class="fas fa-play-circle me-2 text-primary"></i>Em andamento
                                            </button></li>
                                            <li><button class="dropdown-item" data-status="concluida">
                                                <i class="fas fa-check-circle me-2 text-success"></i>Concluída
                                            </button></li>
                                            <li><button class="dropdown-item" data-status="pausada">
                                                <i class="fas fa-pause-circle me-2 text-warning"></i>Pausada
                                            </button></li>
                                            <li><button class="dropdown-item" data-status="arquivada">
                                                <i class="fas fa-archive me-2 text-secondary"></i>Arquivada
                                            </button></li>
                                        </ul>
                                    </li>
                                    <li><hr class="dropdown-divider"></li>
                                    <li>
                                        <button class="dropdown-item text-danger btn-excluir-lista">
                                            <i class="fas fa-trash-alt me-2"></i>Excluir
                                        </button>
                                    </li>
                                </ul>
                            </div>
                        </div>
                        
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <div>
                                ${statusBadge}
                                ${lista.dias_restantes !== null && lista.status !== 'concluida' ? 
                                    `<span class="badge ${lista.status_dias === 'atrasada' ? 'bg-danger' : 'bg-light text-dark'}">
                                        <i class="far fa-calendar-alt me-1"></i>${lista.status_dias}
                                    </span>` : ''}
                            </div>
                            <small class="text-muted">${lista.total_itens} tarefa${lista.total_itens !== 1 ? 's' : ''}</small>
                        </div>
                        
                        ${lista.objetivo ? `<p class="card-text small text-muted mb-2">${lista.objetivo.substring(0, 100)}${lista.objetivo.length > 100 ? '...' : ''}</p>` : ''}
                        
                        <div class="progress mt-2" style="height: 8px;">
                            <div class="progress-bar" style="width: ${lista.porcentagem}%; background-color: ${lista.cor};" role="progressbar" 
                                aria-valuenow="${lista.porcentagem}" aria-valuemin="0" aria-valuemax="100">
                            </div>
                        </div>
                        <div class="d-flex justify-content-between mt-1">
                            <small class="text-muted">${lista.porcentagem}% concluído</small>
                            <small class="text-muted">${lista.itens_concluidos}/${lista.total_itens}</small>
                        </div>
                        
                        ${lista.total_itens > 0 ? `
                        <div class="d-flex justify-content-center mt-3">
                            <div class="badge bg-danger me-2" title="Alta Prioridade">
                                <i class="fas fa-arrow-up me-1"></i>${lista.itens_alta}
                            </div>
                            <div class="badge bg-warning text-dark me-2" title="Média Prioridade">
                                <i class="fas fa-minus me-1"></i>${lista.itens_media}
                            </div>
                            <div class="badge bg-success" title="Baixa Prioridade">
                                <i class="fas fa-arrow-down me-1"></i>${lista.itens_baixa}
                            </div>
                        </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    },
    
    // Abre o modal para criação de uma nova lista
    abrirModalCriarLista: function() {
        // Resetar o formulário
        document.getElementById('formCriarLista')?.reset();
        
        // Abrir o modal
        const modal = new bootstrap.Modal(document.getElementById('modalCriarLista'));
        modal.show();
    },
    
    // Processa o formulário de criação de lista
    criarLista: async function(event) {
        event.preventDefault();
        
        // Obter os dados do formulário
        const formData = new FormData(event.target);
        const dados = {
            nome: formData.get('nome'),
            objetivo: formData.get('objetivo'),
            data_objetivo: formData.get('data_objetivo'),
            cor: formData.get('cor'),
            icone: formData.get('icone')
        };
        
        try {
            // Mostrar loading
            const btnSubmit = event.target.querySelector('button[type="submit"]');
            const btnText = btnSubmit.innerHTML;
            btnSubmit.disabled = true;
            btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Salvando...';
            
            // Fazer a requisição
            const response = await fetch(this.apiUrls.criar, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(dados)
            });
            
            // Obter a resposta em JSON
            const responseData = await response.json();
            
            // Verificar se houve erro
            if (!response.ok) {
                throw new Error(responseData.message || 'Erro ao criar lista');
            }
            
            // Fechar o modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalCriarLista'));
            modal.hide();
            
            // Mostrar mensagem de sucesso
            this.mostrarAlerta('success', 'Lista criada com sucesso!');
            
            // Recarregar as listas
            this.carregarListas();
            
            // Recarregar estatísticas
            this.carregarEstatisticas();
            
        } catch (error) {
            console.error('Erro ao criar lista:', error);
            this.mostrarAlerta('danger', 'Erro ao criar lista. Por favor, tente novamente.');
        } finally {
            // Restaurar o botão
            const btnSubmit = event.target.querySelector('button[type="submit"]');
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = 'Criar Lista';
        }
    },
    
    // Abre o modal para edição de uma lista existente
    abrirModalEditarLista: async function(listaId) {
        try {
            // Mostrar loading
            const modal = new bootstrap.Modal(document.getElementById('modalEditarLista'));
            modal.show();
            
            document.getElementById('loadingEditarLista').style.display = 'flex';
            document.getElementById('conteudoEditarLista').style.display = 'none';
            
            // Fazer a requisição
            const response = await fetch(this.apiUrls.obter(listaId));
            
            // Verificar se a requisição foi bem-sucedida
            if (!response.ok) {
                throw new Error('Erro ao obter detalhes da lista');
            }
            
            // Converter a resposta para JSON
            const data = await response.json();
            
            // Preencher o formulário
            const form = document.getElementById('formEditarLista');
            form.dataset.listaId = listaId;
            
            form.querySelector('input[name="nome"]').value = data.lista.nome;
            form.querySelector('textarea[name="objetivo"]').value = data.lista.objetivo || '';
            
            if (data.lista.data_objetivo) {
                // Converter a data para o formato YYYY-MM-DD para o input type="date"
                const partes = data.lista.data_objetivo.split('/');
                const dataFormatada = `${partes[2]}-${partes[1]}-${partes[0]}`;
                form.querySelector('input[name="data_objetivo"]').value = dataFormatada;
            } else {
                form.querySelector('input[name="data_objetivo"]').value = '';
            }
            
            form.querySelector('select[name="status"]').value = data.lista.status;
            form.querySelector('input[name="cor"]').value = data.lista.cor;
            form.querySelector('input[name="icone"]').value = data.lista.icone;
            
            // Exibir informações da lista
            document.getElementById('editarListaNome').textContent = data.lista.nome;
            
            // Esconder loading e mostrar conteúdo
            document.getElementById('loadingEditarLista').style.display = 'none';
            document.getElementById('conteudoEditarLista').style.display = 'block';
            
        } catch (error) {
            console.error('Erro ao abrir modal de edição:', error);
            // Fechar o modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalEditarLista'));
            modal.hide();
            
            // Mostrar mensagem de erro
            this.mostrarAlerta('danger', 'Erro ao carregar dados da lista. Por favor, tente novamente.');
        }
    },
    
// Processa o formulário de edição de lista
atualizarLista: async function(event) {
    event.preventDefault();
    
    // Obter o ID da lista
    const listaId = event.target.dataset.listaId;
    
    // Obter os dados do formulário
    const formData = new FormData(event.target);
    const dados = {
        nome: formData.get('nome'),
        objetivo: formData.get('objetivo'),
        data_objetivo: formData.get('data_objetivo'),
        status: formData.get('status'),
        cor: formData.get('cor'),
        icone: formData.get('icone')
    };
    
    try {
        // Mostrar loading
        const btnSubmit = event.target.querySelector('button[type="submit"]');
        const btnText = btnSubmit.innerHTML;
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Salvando...';
        
        // Fazer a requisição
        const response = await fetch(this.apiUrls.atualizar(listaId), {
            method: 'POST', // Alguns servidores não suportam PUT, então usamos POST
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify(dados)
        });
        
        // Obter a resposta em JSON
        const responseData = await response.json();
        
        // Verificar se houve erro
        if (!response.ok) {
            throw new Error(responseData.message || 'Erro ao atualizar lista');
        }
        
        // Fechar o modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalEditarLista'));
        modal.hide();
        
        // Mostrar mensagem de sucesso
        this.mostrarAlerta('success', 'Lista atualizada com sucesso!');
        
        // Recarregar as listas
        this.carregarListas();
        
        // Recarregar estatísticas
        this.carregarEstatisticas();
        
    } catch (error) {
        console.error('Erro ao atualizar lista:', error);
        this.mostrarAlerta('danger', 'Erro ao atualizar lista. Por favor, tente novamente.');
    } finally {
        // Restaurar o botão
        const btnSubmit = event.target.querySelector('button[type="submit"]');
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = 'Salvar Alterações';
    }
},

// Abre um diálogo de confirmação para excluir uma lista
confirmarExclusaoLista: function(listaId, listaNome) {
    // Criar um modal de confirmação usando Bootstrap
    const modalHtml = `
        <div class="modal fade" id="modalConfirmarExclusao" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title">Confirmar Exclusão</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p>Você tem certeza que deseja excluir a lista <strong>"${listaNome}"</strong>?</p>
                        <p class="text-danger"><i class="fas fa-exclamation-triangle me-2"></i>Esta ação não pode ser desfeita e todos os itens da lista serão excluídos.</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-danger" id="btnConfirmarExclusao">
                            <i class="fas fa-trash-alt me-2"></i>Excluir Lista
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Adicionar o modal ao corpo do documento
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Obter o modal
    const modalElement = document.getElementById('modalConfirmarExclusao');
    
    // Adicionar listener para remover o modal do DOM quando for fechado
    modalElement.addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
    
    // Adicionar listener para o botão de confirmar exclusão
    document.getElementById('btnConfirmarExclusao').addEventListener('click', () => {
        // Fechar o modal
        const modal = bootstrap.Modal.getInstance(modalElement);
        modal.hide();
        
        // Excluir a lista
        this.excluirLista(listaId);
    });
    
    // Abrir o modal
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
},

// Exclui uma lista
excluirLista: async function(listaId) {
    try {
        // Mostrar loading
        this.mostrarAlerta('info', '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Excluindo lista...', false);
        
        // Fazer a requisição
        const response = await fetch(this.apiUrls.excluir(listaId), {
            method: 'POST', // Alguns servidores não suportam DELETE, então usamos POST
            headers: {
                'X-CSRFToken': this.getCSRFToken()
            }
        });
        
        // Obter a resposta em JSON
        const responseData = await response.json();
        
        // Verificar se houve erro
        if (!response.ok) {
            throw new Error(responseData.message || 'Erro ao excluir lista');
        }
        
        // Mostrar mensagem de sucesso
        this.mostrarAlerta('success', responseData.message || 'Lista excluída com sucesso!');
        
        // Recarregar as listas
        this.carregarListas();
        
        // Recarregar estatísticas
        this.carregarEstatisticas();
        
    } catch (error) {
        console.error('Erro ao excluir lista:', error);
        this.mostrarAlerta('danger', 'Erro ao excluir lista. Por favor, tente novamente.');
    }
},

// Altera o status de uma lista
mudarStatusLista: async function(listaId, novoStatus) {
    try {
        // Mostrar loading
        this.mostrarAlerta('info', '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Atualizando status...', false);
        
        // Fazer a requisição
        const response = await fetch(this.apiUrls.atualizarStatus(listaId), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({ status: novoStatus })
        });
        
        // Obter a resposta em JSON
        const responseData = await response.json();
        
        // Verificar se houve erro
        if (!response.ok) {
            throw new Error(responseData.message || 'Erro ao atualizar status');
        }
        
        // Mostrar mensagem de sucesso
        this.mostrarAlerta('success', 'Status atualizado com sucesso!');
        
        // Recarregar as listas
        this.carregarListas();
        
        // Recarregar estatísticas
        this.carregarEstatisticas();
        
    } catch (error) {
        console.error('Erro ao atualizar status:', error);
        this.mostrarAlerta('danger', 'Erro ao atualizar status. Por favor, tente novamente.');
    }
},

// Abre a página de detalhes de uma lista
abrirLista: function(listaId) {
    // Redirecionar para a página de detalhes da lista
    window.location.href = `/lista/${listaId}/`;
},

// Exibe um alerta na tela
mostrarAlerta: function(tipo, mensagem, autoDesaparecer = true) {
    // Remover alertas existentes
    const alertasExistentes = document.querySelectorAll('.alert-flutuante');
    alertasExistentes.forEach(alerta => alerta.remove());
    
    // Criar o alerta
    const alerta = document.createElement('div');
    alerta.className = `alert alert-${tipo} alert-flutuante shadow-sm`;
    alerta.innerHTML = `
        ${mensagem}
        <button type="button" class="btn-close btn-close-white" aria-label="Close"></button>
    `;
    
    // Adicionar o alerta ao corpo do documento
    document.body.appendChild(alerta);
    
    // Adicionar evento de clique para fechar o alerta
    alerta.querySelector('.btn-close').addEventListener('click', () => {
        alerta.remove();
    });
    
    // Fazer o alerta desaparecer após 5 segundos
    if (autoDesaparecer) {
        setTimeout(() => {
            alerta.classList.add('fechar');
            setTimeout(() => {
                alerta.remove();
            }, 300);
        }, 5000);
    }
}
};

// Inicializar o gerenciador de listas quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
ListaManager.init();
});

// Estilo CSS para alertas flutuantes
document.head.insertAdjacentHTML('beforeend', `
<style>
    .alert-flutuante {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        padding-right: 40px;
        animation: slide-in 0.3s ease-out;
    }
    
    .alert-flutuante .btn-close {
        position: absolute;
        top: 0.5rem;
        right: 0.5rem;
    }
    
    .alert-flutuante.fechar {
        animation: slide-out 0.3s ease-in forwards;
    }
    
    @keyframes slide-in {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slide-out {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .stat-icon {
        width: 50px;
        height: 50px;
        background-color: rgba(0, 0, 0, 0.05);
    }
    
    .dropdown-menu .dropdown-menu {
        position: absolute;
        left: 100%;
        top: 0;
    }
</style>
`);