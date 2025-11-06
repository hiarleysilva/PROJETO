-- Índice em usuarios.email = Buscas frequentes por email durante login e recuperação de conta

CREATE INDEX idx_usuario_email ON usuarios(email);

-- Índice em usuarios.status = Filtros constantes por status em relatórios e consultas administrativas

CREATE INDEX idx_usuario_status ON usuarios(status);

-- Índice em livros.titulo = Buscas textuais por título são muito comuns no sistema

CREATE INDEX idx_livro_titulo ON livros(titulo);

-- Índice em livros.quantidade_disponivel = Consultas frequentes para verificar disponibilidade

CREATE INDEX idx_livro_disponivel ON livros(quantidade_disponivel);

-- Índice em emprestimos = Verificações diárias de empréstimos próximos do vencimento

data_devolucao_prevista
CREATE INDEX idx_emprestimo_devolucao ON emprestimos(data_devolucao_prevista);