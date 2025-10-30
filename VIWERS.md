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