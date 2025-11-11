-- CRIAÇÃO DO BANCO E TABELAS (DDL)

CREATE DATABASE IF NOT EXISTS biblioteca_db;
USE biblioteca_db;

-- Tabela de Grupos (Requisito Obrigatório)
CREATE TABLE grupos_usuarios (
    grupo_id CHAR(10) PRIMARY KEY,
    nome_grupo VARCHAR(50) NOT NULL UNIQUE,
    permissoes JSON NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Usuários (Requisito Obrigatório)
CREATE TABLE usuarios (
    usuario_id CHAR(15) PRIMARY KEY,
    grupo_id CHAR(10) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    telefone VARCHAR(20),
    endereco TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('ativo', 'inativo', 'suspenso') DEFAULT 'ativo',
    FOREIGN KEY (grupo_id) REFERENCES grupos_usuarios(grupo_id)
);

-- Tabela de Autores
CREATE TABLE autores (
    autor_id CHAR(12) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    nacionalidade VARCHAR(50),
    data_nascimento DATE,
    biografia TEXT
);

-- Tabela de Editoras
CREATE TABLE editoras (
    editora_id CHAR(12) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    fundacao YEAR,
    pais VARCHAR(50)
);

-- Tabela de Categorias
CREATE TABLE categorias (
    categoria_id CHAR(10) PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,
    descricao TEXT
);

-- Tabela de Livros
CREATE TABLE livros (
    livro_id CHAR(15) PRIMARY KEY,
    isbn VARCHAR(20) UNIQUE,
    titulo VARCHAR(200) NOT NULL,
    autor_id CHAR(12) NOT NULL,
    editora_id CHAR(12) NOT NULL,
    categoria_id CHAR(10) NOT NULL,
    ano_publicacao YEAR,
    edicao INT DEFAULT 1,
    quantidade_total INT NOT NULL DEFAULT 0,
    quantidade_disponivel INT NOT NULL DEFAULT 0,
    sinopse TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (autor_id) REFERENCES autores(autor_id),
    FOREIGN KEY (editora_id) REFERENCES editoras(editora_id),
    FOREIGN KEY (categoria_id) REFERENCES categorias(categoria_id)
);

-- Tabela de Empréstimos
CREATE TABLE emprestimos (
    emprestimo_id CHAR(20) PRIMARY KEY,
    usuario_id CHAR(15) NOT NULL,
    livro_id CHAR(15) NOT NULL,
    data_emprestimo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_devolucao_prevista DATE NOT NULL,
    data_devolucao_real DATE NULL,
    status ENUM('ativo', 'devolvido', 'atrasado') DEFAULT 'ativo',
    multa DECIMAL(10,2) DEFAULT 0.00,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id),
    FOREIGN KEY (livro_id) REFERENCES livros(livro_id)
);

-- Tabela de Reservas
CREATE TABLE reservas (
    reserva_id CHAR(18) PRIMARY KEY,
    usuario_id CHAR(15) NOT NULL,
    livro_id CHAR(15) NOT NULL,
    data_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_expiracao DATE NOT NULL,
    status ENUM('ativa', 'cancelada', 'expirada', 'concluida') DEFAULT 'ativa',
    FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id),
    FOREIGN KEY (livro_id) REFERENCES livros(livro_id)
);

-- Tabela de Multas
CREATE TABLE multas (
    multa_id CHAR(16) PRIMARY KEY,
    usuario_id CHAR(15) NOT NULL,
    emprestimo_id CHAR(20) NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    data_multa DATE NOT NULL,
    data_pagamento DATE NULL,
    status ENUM('pendente', 'paga') DEFAULT 'pendente',
    FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id),
    FOREIGN KEY (emprestimo_id) REFERENCES emprestimos(emprestimo_id)
);

-- --------------------------------------------------------
-- 1.2: ÍNDICES (Otimização) e Justificativas
-- --------------------------------------------------------

-- Justificativa: Buscas frequentes por email durante login e recuperação de conta
CREATE INDEX idx_usuario_email ON usuarios(email);

-- Justificativa: Filtros constantes por status em relatórios e consultas administrativas
CREATE INDEX idx_usuario_status ON usuarios(status);

-- Justificativa: Buscas textuais por título são muito comuns no sistema
CREATE INDEX idx_livro_titulo ON livros(titulo);

-- Justificativa: Consultas frequentes para verificar disponibilidade de livros
CREATE INDEX idx_livro_disponivel ON livros(quantidade_disponivel);

-- Justificativa: Verificações diárias de empréstimos próximos do vencimento
CREATE INDEX idx_emprestimo_devolucao ON emprestimos(data_devolucao_prevista);

-- (Outros índices de FK e PK são criados automaticamente pelas definições de tabela)
CREATE INDEX idx_autor_nome ON autores(nome);
CREATE INDEX idx_editora_nome ON editoras(nome);
CREATE INDEX idx_livro_autor ON livros(autor_id);
CREATE INDEX idx_livro_categoria ON livros(categoria_id);
CREATE INDEX idx_emprestimo_usuario ON emprestimos(usuario_id);
CREATE INDEX idx_emprestimo_status ON emprestimos(status);
CREATE INDEX idx_reserva_status ON reservas(status);
CREATE INDEX idx_reserva_expiracao ON reservas(data_expiracao);
CREATE INDEX idx_multa_status ON multas(status);
CREATE INDEX idx_multa_data ON multas(data_multa);

-- --------------------------------------------------------
-- 1.3: LÓGICA DE BANCO - FUNCTIONS (Geração de IDs)
-- --------------------------------------------------------

-- Função para gerar ID de Usuário
DELIMITER //
CREATE FUNCTION fn_gerar_id_usuario(nome VARCHAR(100))
RETURNS CHAR(15)
DETERMINISTIC
BEGIN
    DECLARE novo_id CHAR(15);
    DECLARE sequencia INT;
    
    SET @base_id = CONCAT(
        UPPER(SUBSTRING(REPLACE(nome, ' ', ''), 1, 3)),
        DATE_FORMAT(NOW(), '%y')
    );
    
    SELECT COUNT(*) + 1 INTO sequencia 
    FROM usuarios 
    WHERE usuario_id LIKE CONCAT(@base_id, '%');
    
    SET novo_id = CONCAT(@base_id, 'U', LPAD(sequencia, 6, '0'));
    RETURN novo_id;
END//
DELIMITER ;

-- Função para gerar ID de Autor
DELIMITER //
CREATE FUNCTION fn_gerar_id_autor(nome VARCHAR(100))
RETURNS CHAR(12)
DETERMINISTIC
BEGIN
    DECLARE novo_id CHAR(12);
    DECLARE sequencia INT;
    
    SET @base_id = UPPER(SUBSTRING(REPLACE(nome, ' ', ''), 1, 4));
    
    SELECT COUNT(*) + 1 INTO sequencia 
    FROM autores 
    WHERE autor_id LIKE CONCAT(@base_id, '%');
    
    SET novo_id = CONCAT(@base_id, 'A', LPAD(sequencia, 5, '0'));
    RETURN novo_id;
END//
DELIMITER ;

-- Função para gerar ID de Livro
DELIMITER //
CREATE FUNCTION fn_gerar_id_livro(titulo VARCHAR(200), ano YEAR)
RETURNS CHAR(15)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE novo_id CHAR(15);
    DECLARE sequencia INT;
    
    SET @base_id = CONCAT(
        UPPER(SUBSTRING(REPLACE(titulo, ' ', ''), 1, 3)),
        RIGHT(ano, 2)
    );
    
    SELECT COUNT(*) + 1 INTO sequencia 
    FROM livros 
    WHERE livro_id LIKE CONCAT(@base_id, '%');
    
    SET novo_id = CONCAT(@base_id, 'L', LPAD(sequencia, 6, '0'));
    
    RETURN novo_id;
END//
DELIMITER ;

-- --------------------------------------------------------
-- 1.4: LÓGICA DE BANCO - TRIGGERS (Mínimo de 2)
-- --------------------------------------------------------

-- Trigger 1: Atualizar estoque ao realizar empréstimo (INSERT)
DELIMITER //
CREATE TRIGGER after_emprestimo_insert
AFTER INSERT ON emprestimos
FOR EACH ROW
BEGIN
    -- Diminuir quantidade disponível quando um livro é emprestado
    UPDATE livros 
    SET quantidade_disponivel = quantidade_disponivel - 1 
    WHERE livro_id = NEW.livro_id;
END//
DELIMITER ;


-- Trigger 2: Atualizar estoque e gerar multa na devolução (UPDATE)
DELIMITER //
CREATE TRIGGER after_emprestimo_update
AFTER UPDATE ON emprestimos
FOR EACH ROW
BEGIN
    -- Se o status mudar para 'devolvido'
    IF NEW.status = 'devolvido' AND OLD.status != 'devolvido' THEN
        -- Aumentar quantidade disponível
        UPDATE livros 
        SET quantidade_disponivel = quantidade_disponivel + 1 
        WHERE livro_id = NEW.livro_id;
        
        -- Calcular multa se houve atraso
        IF NEW.data_devolucao_real > NEW.data_devolucao_prevista THEN
            SET @dias_atraso = DATEDIFF(NEW.data_devolucao_real, NEW.data_devolucao_prevista);
            SET @valor_multa = @dias_atraso * 1.00; -- 1 REAL por dia de multa.
            
            -- Inserir registro de multa
            INSERT INTO multas (multa_id, usuario_id, emprestimo_id, valor, data_multa, status)
            VALUES (
                CONCAT('MUL', DATE_FORMAT(NOW(), '%Y%m%d'), LPAD(NEW.emprestimo_id, 8, '0')),
                NEW.usuario_id,
                NEW.emprestimo_id,
                @valor_multa,
                CURDATE(),
                'pendente'
            );
        END IF;
    END IF;
END//
DELIMITER ;

-- --------------------------------------------------------
-- 1.5: LÓGICA DE BANCO - VIEWS (Mínimo de 2)
-- --------------------------------------------------------

-- View 1: Livros disponíveis para consulta pública
-- Justificativa: Essencial para usuários buscarem livros disponíveis sem precisar conhecer as junções complexas das tabelas.
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

-- View 2: Empréstimos ativos e status de atraso
-- Justificativa: Fornece uma visão gerencial para facilitar o acompanhamento de prazos e identificação de atrasos.
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

-- --------------------------------------------------------
-- 1.6: LÓGICA DE BANCO - PROCEDURE (Lógica de Negócio)
-- --------------------------------------------------------

-- Procedure para realizar empréstimo com validações
-- Justificativa: Centraliza toda a lógica de empréstimo (validações de disponibilidade, status do usuário, limite) em um único local seguro.
DELIMITER //
CREATE PROCEDURE sp_realizar_emprestimo(
    IN p_usuario_id CHAR(15),
    IN p_livro_id CHAR(15),
    IN p_dias_emprestimo INT
)
BEGIN
    DECLARE v_disponivel INT;
    DECLARE v_emprestimos_ativos INT;
    DECLARE v_usuario_status VARCHAR(20);
    DECLARE v_novo_emprestimo_id CHAR(20);
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
    -- 1. Verificar status do usuário
    SELECT status INTO v_usuario_status FROM usuarios WHERE usuario_id = p_usuario_id;
    IF v_usuario_status != 'ativo' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Usuário não está ativo';
    END IF;
    
    -- 2. Verificar disponibilidade do livro
    SELECT quantidade_disponivel INTO v_disponivel FROM livros WHERE livro_id = p_livro_id;
    IF v_disponivel <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Livro não disponível para empréstimo';
    END IF;
    
    -- 3. Verificar limite de empréstimos do usuário
    SELECT COUNT(*) INTO v_emprestimos_ativos 
    FROM emprestimos 
    WHERE usuario_id = p_usuario_id AND status = 'ativo';
    
    IF v_emprestimos_ativos >= 5 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Limite de empréstimos atingido';
    END IF;
    
    -- 4. Gerar ID do empréstimo (regra própria)
    SET v_novo_emprestimo_id = CONCAT(
        'EMP', 
        DATE_FORMAT(NOW(), '%Y%m%d'), 
        LPAD(FLOOR(RAND() * 1000000), 6, '0')
    );
    
    -- 5. Inserir empréstimo
    INSERT INTO emprestimos (
        emprestimo_id, 
        usuario_id, 
        livro_id, 
        data_devolucao_prevista,
        status
    ) VALUES (
        v_novo_emprestimo_id,
        p_usuario_id,
        p_livro_id,
        DATE_ADD(CURDATE(), INTERVAL p_dias_emprestimo DAY),
        'ativo'
    );
    
    COMMIT;
    
    SELECT 'Empréstimo realizado com sucesso' as mensagem, v_novo_emprestimo_id as emprestimo_id;
    
END//
DELIMITER ;

-- --------------------------------------------------------
-- 1.7: SEGURANÇA - USUÁRIOS E CONTROLE DE ACESSO (DCL)
-- --------------------------------------------------------
-- Justificativa: Criação de níveis de acesso para garantir que o usuário 'root' não seja usado e que cada perfil de usuário tenha apenas as permissões mínimas necessárias.

-- Criar usuários específicos
CREATE USER 'bib_admin'@'localhost' IDENTIFIED BY 'SenhaAdmin123!';
CREATE USER 'bib_funcionario'@'localhost' IDENTIFIED BY 'SenhaFunc123!';
CREATE USER 'bib_usuario'@'localhost' IDENTIFIED BY 'SenhaUser123!';
CREATE USER 'bib_relatorio'@'localhost' IDENTIFIED BY 'SenhaRel123!';

-- Nível 1: Administrador (acesso total ao DB)
GRANT ALL PRIVILEGES ON biblioteca_db.* TO 'bib_admin'@'localhost';

-- Nível 2: Funcionário (operações do dia a dia)
GRANT SELECT, INSERT, UPDATE ON biblioteca_db.usuarios TO 'bib_funcionario'@'localhost';
GRANT SELECT, INSERT, UPDATE ON biblioteca_db.emprestimos TO 'bib_funcionario'@'localhost';
GRANT SELECT ON biblioteca_db.livros TO 'bib_funcionario'@'localhost';
GRANT SELECT ON biblioteca_db.vw_livros_disponiveis TO 'bib_funcionario'@'localhost';
GRANT SELECT ON biblioteca_db.vw_emprestimos_ativos TO 'bib_funcionario'@'localhost';
GRANT EXECUTE ON PROCEDURE biblioteca_db.sp_realizar_emprestimo TO 'bib_funcionario'@'localhost';

-- Nível 3: Usuário (acesso público limitado)
GRANT SELECT ON biblioteca_db.vw_livros_disponiveis TO 'bib_usuario'@'localhost';
GRANT SELECT ON biblioteca_db.autores TO 'bib_usuario'@'localhost';
GRANT SELECT ON biblioteca_db.editoras TO 'bib_usuario'@'localhost';

-- Nível 4: Relatórios (somente leitura de tudo)
GRANT SELECT ON biblioteca_db.* TO 'bib_relatorio'@'localhost';

FLUSH PRIVILEGES;