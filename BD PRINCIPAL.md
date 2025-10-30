-- Criar database
CREATE DATABASE IF NOT EXISTS biblioteca_db;
USE biblioteca_db;

-- Criando tabela dos grupos de usuários
CREATE TABLE grupos_usuarios (
    grupo_id CHAR(10) PRIMARY KEY,
    nome_grupo VARCHAR(50) NOT NULL UNIQUE,
    permissoes JSON NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de usuários
CREATE TABLE usuarios (
    usuario_id CHAR(15) PRIMARY KEY,
    grupo_id CHAR(10) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    telefone VARCHAR(20),
    endereco TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('ativo', 'inativo', 'suspenso') DEFAULT 'ativo',
    FOREIGN KEY (grupo_id) REFERENCES grupos_usuarios(grupo_id),
    INDEX idx_usuario_email (email),
    INDEX idx_usuario_status (status)
);

-- Tabela dos autores
CREATE TABLE autores (
    autor_id CHAR(12) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    nacionalidade VARCHAR(50),
    data_nascimento DATE,
    biografia TEXT,
    INDEX idx_autor_nome (nome)
);

-- Tabela das editoras
CREATE TABLE editoras (
    editora_id CHAR(12) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    fundacao YEAR,
    pais VARCHAR(50),
    INDEX idx_editora_nome (nome)
);

-- Tabela das categorias
CREATE TABLE categorias (
    categoria_id CHAR(10) PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,
    descricao TEXT
);

-- Tabela de livros
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
    FOREIGN KEY (categoria_id) REFERENCES categorias(categoria_id),
    INDEX idx_livro_titulo (titulo),
    INDEX idx_livro_autor (autor_id),
    INDEX idx_livro_categoria (categoria_id),
    INDEX idx_livro_disponivel (quantidade_disponivel)
);

-- Tabela de empréstimo
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
    FOREIGN KEY (livro_id) REFERENCES livros(livro_id),
    INDEX idx_emprestimo_usuario (usuario_id),
    INDEX idx_emprestimo_status (status),
    INDEX idx_emprestimo_devolucao (data_devolucao_prevista)
);

-- Tabela de reserva
CREATE TABLE reservas (
    reserva_id CHAR(18) PRIMARY KEY,
    usuario_id CHAR(15) NOT NULL,
    livro_id CHAR(15) NOT NULL,
    data_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_expiracao DATE NOT NULL,
    status ENUM('ativa', 'cancelada', 'expirada', 'concluida') DEFAULT 'ativa',
    FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id),
    FOREIGN KEY (livro_id) REFERENCES livros(livro_id),
    INDEX idx_reserva_status (status),
    INDEX idx_reserva_expiracao (data_expiracao)
);

-- Tabela das multas dos emprestimos atrasados
CREATE TABLE multas (
    multa_id CHAR(16) PRIMARY KEY,
    usuario_id CHAR(15) NOT NULL,
    emprestimo_id CHAR(20) NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    data_multa DATE NOT NULL,
    data_pagamento DATE NULL,
    status ENUM('pendente', 'paga') DEFAULT 'pendente',
    FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id),
    FOREIGN KEY (emprestimo_id) REFERENCES emprestimos(emprestimo_id),
    INDEX idx_multa_status (status),
    INDEX idx_multa_data (data_multa)
);