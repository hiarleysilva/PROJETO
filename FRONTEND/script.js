// Local que o back roda
const API_URL = 'http://127.0.0.1:5000';

// --- FUNÇÃO HELPER PARA VERIFICAR ATRASO ---
function isOverdue(dueDateString) {
    // dueDateString é esperado no formato DD/MM/AAAA (vindo do MySQL)
    const parts = dueDateString.split('/');
    // Cria a data no formato AAAA, MM (0-11), DD
    const dueDate = new Date(parts[2], parts[1] - 1, parts[0]);
    const today = new Date();
    // Zera a hora para comparar apenas a data
    today.setHours(0, 0, 0, 0);
    return dueDate < today;
}

// Espera o HTML carregar antes de rodar o script
document.addEventListener('DOMContentLoaded', () => {

    // Seleciona todos os elementos interativos
    const formEmprestimo = document.getElementById('form-emprestimo');
    const formDevolucao = document.getElementById('form-devolucao');
    const formUsuario = document.getElementById('form-usuario');
    const formLivro = document.getElementById('form-livro');
    const btnGetLogs = document.getElementById('btn-get-logs');
    const logsOutput = document.getElementById('logs-output');
    const statusMessage = document.getElementById('status-message');
    const btnGetUsuarios = document.getElementById('btn-get-usuarios');
    const usuariosOutput = document.getElementById('usuarios-output');
    const btnGetLivros = document.getElementById('btn-get-livros');
    const livrosOutput = document.getElementById('livros-output');
    const btnGetEmprestimos = document.getElementById('btn-get-emprestimos');
    const emprestimosOutput = document.getElementById('emprestimos-output');

    // --- FUNÇÃO HELPER PARA MOSTRAR STATUS ---
    /**
     * Mostra uma mensagem de sucesso ou erro na tela.
     * @param {string} message - A mensagem para exibir.
     * @param {boolean} isError - True se for erro (vermelho), false para sucesso (verde).
     */
    function showStatus(message, isError = false) {
        statusMessage.textContent = message;
        statusMessage.className = isError ? 'status-error' : 'status-success';
        
        // Esconde a mensagem depois de 5 segundos
        setTimeout(() => {
            statusMessage.className = '';
            statusMessage.textContent = '';
        }, 5000);
    }

    // --- FUNÇÃO HELPER GENÉRICA PARA POST (envio de dados) ---
    /**
     * Função reutilizável para fazer requisições POST para a API.
     * @param {string} endpoint - A rota da API (ex: '/emprestimo')
     * @param {object} formData - Os dados do formulário
     * @param {HTMLFormElement} formElement - O elemento do formulário (para limpar)
     */
    async function handlePostForm(endpoint, formData, formElement) {
        const data = Object.fromEntries(formData.entries());
        showStatus('Processando requisição...', false);

        try {
            const response = await fetch(`${API_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (!response.ok) {
                // Se a API retornar um erro (ex: 400, 500), joga o erro
                throw new Error(result.erro || result.aviso || 'Erro desconhecido');
            }

            // A sua API retorna 'result.mensagem'
            showStatus(result.mensagem || 'Operação realizada com sucesso!', false);
            formElement.reset(); // Limpa o formulário

        } catch (error) {
            console.error(`Erro ao fazer POST para ${endpoint}:`, error);
            showStatus(`Erro: ${error.message}`, true);
        }
    }


    // --- 1. LÓGICA DE EMPRÉSTIMO ---
    formEmprestimo.addEventListener('submit', (e) => {
        e.preventDefault(); // Impede o recarregamento da página
        const formData = new FormData(e.target);
        handlePostForm('/emprestimo', formData, e.target);
    });

    // --- 2. LÓGICA DE DEVOLUÇÃO ---
    formDevolucao.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        handlePostForm('/devolucao', formData, e.target);
    });

    // --- 3. LÓGICA DE ADICIONAR USUÁRIO ---
    formUsuario.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        handlePostForm('/usuarios', formData, e.target);
    });

    // --- 4. LÓGICA DE ADICIONAR LIVRO ---
    formLivro.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        handlePostForm('/livros', formData, e.target);
    });

    // --- 5. LÓGICA DE BUSCAR LOGS (GET) ---
    btnGetLogs.addEventListener('click', async () => {
        showStatus('Buscando logs no MongoDB...', false);
        logsOutput.textContent = 'Carregando...';

        try {
            const response = await fetch(`${API_URL}/logs`);
            
            if (!response.ok) {
                throw new Error(`Falha na rede: ${response.statusText}`);
            }
            
            const logs = await response.json();
            
            // Formata o JSON para exibição "bonita"
            logsOutput.textContent = JSON.stringify(logs, null, 2);
            showStatus('Logs carregados com sucesso.', false);

        } catch (error) {
            console.error('Erro ao buscar logs:', error);
            logsOutput.textContent = 'Falha ao carregar os logs.';
            showStatus(`Erro: ${error.message}`, true);
        }
    });

    // --- 6. LÓGICA DE LISTAR USUÁRIOS (GET) ---
    btnGetUsuarios.addEventListener('click', async () => {
        showStatus('Buscando usuários...', false);
        usuariosOutput.innerHTML = '<tr><td colspan="4">Carregando...</td></tr>';

        try {
            const response = await fetch(`${API_URL}/usuarios`);
            
            if (!response.ok) {
                // Se o servidor der erro, o 'erro' vem no JSON
                const errorResult = await response.json();
                throw new Error(errorResult.erro || `Falha na rede: ${response.statusText}`);
            }
            
            const usuarios = await response.json();
            usuariosOutput.innerHTML = ''; // Limpa o "Carregando..."

            if (usuarios.length === 0) {
                usuariosOutput.innerHTML = '<tr><td colspan="4">Nenhum usuário encontrado.</td></tr>';
                showStatus('Nenhum usuário cadastrado.', false);
                return;
            }

            // Preenche a tabela com os dados
            usuarios.forEach(usuario => {
                const row = document.createElement('tr');
                // Usamos innerHTML para criar as células
                row.innerHTML = `
                    <td>${usuario.usuario_id}</td>
                    <td>${usuario.nome}</td>
                    <td>${usuario.email}</td>
                    <td>${usuario.status}</td>
                `;
                usuariosOutput.appendChild(row);
            });

            showStatus(`Total de ${usuarios.length} usuários carregados.`, false);

        } catch (error) {
            console.error('Erro ao buscar usuários:', error);
            usuariosOutput.innerHTML = '<tr><td colspan="4">Falha ao carregar usuários.</td></tr>';
            showStatus(`Erro: ${error.message}`, true);
        }
    });

    // --- 7. LÓGICA DE LISTAR LIVROS (GET) ---
    btnGetLivros.addEventListener('click', async () => {
        showStatus('Buscando livros disponíveis...', false);
        livrosOutput.innerHTML = '<tr><td colspan="5">Carregando...</td></tr>'; // 5 colunas

        try {
            const response = await fetch(`${API_URL}/livros`);
            
            if (!response.ok) {
                const errorResult = await response.json();
                throw new Error(errorResult.erro || `Falha na rede: ${response.statusText}`);
            }
            
            const livros = await response.json();
            livrosOutput.innerHTML = ''; 

            if (livros.length === 0) {
                livrosOutput.innerHTML = '<tr><td colspan="5">Nenhum livro disponível encontrado.</td></tr>';
                showStatus('Nenhum livro disponível no momento.', false);
                return;
            }

            // Preenche a tabela com os dados
            livros.forEach(livro => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${livro.livro_id}</td>
                    <td>${livro.titulo}</td>
                    <td>${livro.autor}</td>
                    <td>${livro.editora}</td>
                    <td>${livro.copias_disponiveis}</td>
                `;
                livrosOutput.appendChild(row);
            });

            showStatus(`Total de ${livros.length} livros carregados.`, false);

        } catch (error) {
            console.error('Erro ao buscar livros:', error);
            livrosOutput.innerHTML = '<tr><td colspan="5">Falha ao carregar livros.</td></tr>';
            showStatus(`Erro: ${error.message}`, true);
        }
    });

    // --- 8. LÓGICA DE LISTAR EMPRÉSTIMOS ATIVOS (GET) ---
    btnGetEmprestimos.addEventListener('click', async () => {
        showStatus('Buscando empréstimos ativos...', false);
        emprestimosOutput.innerHTML = '<tr><td colspan="5">Carregando...</td></tr>'; // 5 colunas

        try {
            const response = await fetch(`${API_URL}/emprestimos`);
            
            if (!response.ok) {
                const errorResult = await response.json();
                throw new Error(errorResult.erro || `Falha na rede: ${response.statusText}`);
            }
            
            const emprestimos = await response.json();
            emprestimosOutput.innerHTML = ''; 

            if (emprestimos.length === 0) {
                emprestimosOutput.innerHTML = '<tr><td colspan="5">Nenhum empréstimo ativo encontrado.</td></tr>';
                showStatus('Nenhum empréstimo pendente no momento.', false);
                return;
            }

            // Preenche a tabela com os dados
            emprestimos.forEach(emprestimo => {
                // Adiciona a lógica de atraso para o CSS
                const isLate = isOverdue(emprestimo.data_vencimento);
                const row = document.createElement('tr');
                
                row.innerHTML = `
                    <td>${emprestimo.emprestimo_id}</td>
                    <td>${emprestimo.nome_usuario}</td>
                    <td>${emprestimo.titulo_livro}</td>
                    <td>${emprestimo.data_emprestimo}</td>
                    <td class="${isLate ? 'overdue' : ''}">${emprestimo.data_vencimento}</td>
                `;
                emprestimosOutput.appendChild(row);
            });

            showStatus(`Total de ${emprestimos.length} empréstimos pendentes carregados.`, false);

        } catch (error) {
            console.error('Erro ao buscar empréstimos:', error);
            emprestimosOutput.innerHTML = '<tr><td colspan="5">Falha ao carregar empréstimos.</td></tr>';
            showStatus(`Erro: ${error.message}`, true);
        }
    });
    
});