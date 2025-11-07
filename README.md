Projeto de Banco de Dados: Criação de um sistema de Biblioteca.

Este é o meu projeto para a disciplina de Banco de Dados. O objetivo era criar um sistema de biblioteca usando tanto MySQL quanto MongoDB como a parte funcional.
Deveria conter também back-end e front-end para a ligação e organização de todo os sistema.

MySQL: Foi usado para guardar os dados principais e transacionais, como usuários, livros, empréstimos e multas.
MongoDB: Usei para uma finalidade secundária, que no caso escolhi ser o armazenamento de logs de atividade e auditoria do sistema.

Requisitos Cumpridos

O projeto segue os requisitos que foram pedidos:

No MySQL:
Criação de tabelas e seus relacionamentos (`FOREIGN KEY`).
Tabelas obrigatórias `usuarios` e `grupos_usuarios`.
Índices para otimizar as consultas.
Dois Triggers (um para `INSERT` em empréstimo, outro para `UPDATE`).
Duas Views (uma para livros disponíveis, outra para empréstimos ativos, deixando mais fácil de visualizar as tabelas).
Procedures e Funções (incluindo as de geração de ID).
Criação de usuários com diferentes níveis de acesso (para não usar `root`, e poder acessar de outros lugares como criando outro usuario no workbanch).
Funções próprias para gerar IDs (ex: `fn_gerar_id_usuario`).

No NoSQL (MongoDB):
Deveria ter o porque da escolha do MongoDB.
Explicação de como ele funciona.
Justificativa e demonstração de uso (para salvar logs de forma flexível).

Como Executar o Projeto:
É preciso configurar os dois bancos de dados separadamente.

1. Configuração do MySQL (Usei o Workbench)
    Antes de começar, é provável que você precise rodar este comando (como `root`) para permitir a criação das funções que usam `NOW()` ou `RAND()`.
    Quando estava testando houve esse erro e quebrei a cabeça para tentar resolver, mas no fim deu tudo certo utilizando a linha de código abaixo:
    
    `SET GLOBAL log_bin_trust_function_creators = 1;`
    
    Após isso deve ser criado todo o banco de dados.
    Depois toda a lógica: Índices, Funções, Views, Triggers e a Procedure.
   Após isso, os usuários e todas as suas permissões, como por exemplo não deixar dar um drop no banco de dados.

2. Configuração do MongoDB (No mongo shell)
   Após abrir o mongo no prompt, devemos criar a coleção.
