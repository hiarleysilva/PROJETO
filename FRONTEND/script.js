// Ponto Central da API: Onde seu backend Python está rodando
const API_URL = 'http://127.0.0.1:5000';

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
                // A sua API retorna 'result.erro' (da procedure)
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

});