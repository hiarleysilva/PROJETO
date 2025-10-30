-- TRIGERS ==================================================================
-- Atualizar quantidade disponível ao emprestar
DELIMITER //
CREATE TRIGGER after_emprestimo_insert
AFTER INSERT ON emprestimos
FOR EACH ROW
BEGIN
    -- Diminuir quantidade disponível quando um livro é emprestado
    UPDATE livros 
    SET quantidade_disponivel = quantidade_disponivel - 1 
    WHERE livro_id = NEW.livro_id;
    
    -- Atualizar status para atrasado se já passou da data que era para devolver.
    IF NEW.data_devolucao_prevista < CURDATE() THEN
        UPDATE emprestimos 
        SET status = 'atrasado' 
        WHERE emprestimo_id = NEW.emprestimo_id;
    END IF;
END//
DELIMITER ;

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
                CONCAT('MUL', DATE_FORMAT(NOW(), '%Y%m%d'), LPAD(LAST_INSERT_ID(), 8, '0')),
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
-- =============================================================