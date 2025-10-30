-- 1. Índice em usuarios.email
-- JUSTIFICATIVA: Buscas frequentes por email durante login e recuperação de conta
CREATE INDEX idx_usuario_email ON usuarios(email);

-- 2. Índice em usuarios.status  
-- JUSTIFICATIVA: Filtros constantes por status em relatórios e consultas administrativas
CREATE INDEX idx_usuario_status ON usuarios(status);

-- 3. Índice em livros.titulo
-- JUSTIFICATIVA: Buscas textuais por título são muito comuns no sistema
CREATE INDEX idx_livro_titulo ON livros(titulo);

-- 4. Índice em livros.quantidade_disponivel
-- JUSTIFICATIVA: Consultas frequentes para verificar disponibilidade
CREATE INDEX idx_livro_disponivel ON livros(quantidade_disponivel);

-- 5. Índice em emprestimos.data_devolucao_prevista
-- JUSTIFICATIVA: Verificações diárias de empréstimos próximos do vencimento
CREATE INDEX idx_emprestimo_devolucao ON emprestimos(data_devolucao_prevista);