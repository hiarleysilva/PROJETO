-- Criar usuários específicos (NUNCA usar root)
CREATE USER 'bib_admin'@'localhost' IDENTIFIED BY 'SenhaAdmin123!';
CREATE USER 'bib_funcionario'@'localhost' IDENTIFIED BY 'SenhaFunc123!';
CREATE USER 'bib_usuario'@'localhost' IDENTIFIED BY 'SenhaUser123!';
CREATE USER 'bib_relatorio'@'localhost' IDENTIFIED BY 'SenhaRel123!';

-- Permissões para Administrador (acesso total)
GRANT ALL PRIVILEGES ON biblioteca_db.* TO 'bib_admin'@'localhost';

-- Permissões para Funcionário (operações do dia a dia)
GRANT SELECT, INSERT, UPDATE ON biblioteca_db.usuarios TO 'bib_funcionario'@'localhost';
GRANT SELECT, INSERT, UPDATE ON biblioteca_db.emprestimos TO 'bib_funcionario'@'localhost';
GRANT SELECT ON biblioteca_db.livros TO 'bib_funcionario'@'localhost';
GRANT SELECT ON biblioteca_db.vw_livros_disponiveis TO 'bib_funcionario'@'localhost';
GRANT SELECT ON biblioteca_db.vw_emprestimos_ativos TO 'bib_funcionario'@'localhost';
GRANT EXECUTE ON PROCEDURE biblioteca_db.sp_realizar_emprestimo TO 'bib_funcionario'@'localhost';

-- Permissões para Usuário (acesso limitado)
GRANT SELECT ON biblioteca_db.vw_livros_disponiveis TO 'bib_usuario'@'localhost';
GRANT SELECT ON biblioteca_db.autores TO 'bib_usuario'@'localhost';
GRANT SELECT ON biblioteca_db.editoras TO 'bib_usuario'@'localhost';

-- Permissões para Relatórios (somente leitura)
GRANT SELECT ON biblioteca_db.* TO 'bib_relatorio'@'localhost';

FLUSH PRIVILEGES;