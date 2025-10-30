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