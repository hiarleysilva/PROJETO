DELIMITER //
CREATE FUNCTION fn_gerar_id_livro(titulo VARCHAR(200), ano YEAR)
RETURNS CHAR(15)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE novo_id CHAR(15);
    DECLARE sequencia INT;
    
    -- Gerar base do ID: 3 primeiras letras do título + ano + sequência
    SET @base_id = CONCAT(
        UPPER(SUBSTRING(REPLACE(titulo, ' ', ''), 1, 3)),
        RIGHT(ano, 2)
    );
    
    -- Verificar quantos IDs já existem com essa base
    SELECT COUNT(*) + 1 INTO sequencia 
    FROM livros 
    WHERE livro_id LIKE CONCAT(@base_id, '%');
    
    -- Formatar ID final
    SET novo_id = CONCAT(@base_id, 'L', LPAD(sequencia, 6, '0'));
    
    RETURN novo_id;
END//
DELIMITER ;

-- EXPLICAÇÃO DE USO: Garante IDs únicos e significativos para livros,
-- evitando dependência do AUTO_INCREMENT

-- ====================================

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
    
    -- Verificar status do usuário
    SELECT status INTO v_usuario_status FROM usuarios WHERE usuario_id = p_usuario_id;
    IF v_usuario_status != 'ativo' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Usuário não está ativo';
    END IF;
    
    -- Verificar disponibilidade do livro
    SELECT quantidade_disponivel INTO v_disponivel FROM livros WHERE livro_id = p_livro_id;
    IF v_disponivel <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Livro não disponível para empréstimo';
    END IF;
    
    -- Verificar se usuário já tem muitos empréstimos
    SELECT COUNT(*) INTO v_emprestimos_ativos 
    FROM emprestimos 
    WHERE usuario_id = p_usuario_id AND status = 'ativo';
    
    IF v_emprestimos_ativos >= 5 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Limite de empréstimos atingido';
    END IF;
    
    -- Gerar ID do empréstimo
    SET v_novo_emprestimo_id = CONCAT(
        'EMP', 
        DATE_FORMAT(NOW(), '%Y%m%d'), 
        LPAD(FLOOR(RAND() * 1000000), 6, '0')
    );
    
    -- Inserir empréstimo
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

-- EXPLICAÇÃO DE USO: Centraliza toda a lógica de empréstimo com validações,
-- garantindo consistência e evitando empréstimos inválidos
