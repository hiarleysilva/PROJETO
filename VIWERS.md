CREATE VIEW vw_livros_disponiveis AS
SELECT 
    l.livro_id,
    l.titulo,
    a.nome as autor,
    e.nome as editora,
    c.nome as categoria,
    l.ano_publicacao,
    l.quantidade_disponivel as copias_disponiveis
FROM livros l
JOIN autores a ON l.autor_id = a.autor_id
JOIN editoras e ON l.editora_id = e.editora_id
JOIN categorias c ON l.categoria_id = c.categoria_id
WHERE l.quantidade_disponivel > 0
ORDER BY l.titulo;

-- JUSTIFICATIVA: Esta view é essencial para usuários buscarem livros disponíveis
-- sem precisar conhecer a complexidade das junções entre tabelas

CREATE VIEW vw_emprestimos_ativos AS
SELECT 
    e.emprestimo_id,
    u.nome as usuario,
    l.titulo as livro,
    e.data_emprestimo,
    e.data_devolucao_prevista,
    DATEDIFF(e.data_devolucao_prevista, CURDATE()) as dias_restantes,
    CASE 
        WHEN DATEDIFF(e.data_devolucao_prevista, CURDATE()) < 0 THEN 'Atrasado'
        WHEN DATEDIFF(e.data_devolucao_prevista, CURDATE()) <= 3 THEN 'Próximo do vencimento'
        ELSE 'No prazo'
    END as status_emprestimo
FROM emprestimos e
JOIN usuarios u ON e.usuario_id = u.usuario_id
JOIN livros l ON e.livro_id = l.livro_id
WHERE e.status = 'ativo'
ORDER BY e.data_devolucao_prevista ASC;

-- JUSTIFICATIVA: Fornece uma visão consolidada para gestão de empréstimos,
-- facilitando acompanhamento de prazos e identificação de possíveis atrasos