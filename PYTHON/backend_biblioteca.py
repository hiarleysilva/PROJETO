import os
import random
import string
import time
from datetime import datetime, date, timedelta
from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error as MySQLError
from pymongo import MongoClient, errors as MongoError

# ======================================================================
# CONFIGURAÇÕES DE AMBIENTE E CONEXÃO
# ATENÇÃO: SUBSTITUA COM SUAS PRÓPRIAS CREDENCIAIS
# ======================================================================

# Configuração do MySQL (Usando o perfil de Funcionário para operações CRUD)
MYSQL_CONFIG = {
    'host': 'localhost',
    'database': 'biblioteca_db',
    'user': 'bib_funcionario',
    'password': 'SenhaFunc123!'
}

# Configuração do MongoDB
MONGO_URI = 'mongodb://localhost:27017/'
MONGO_DB_NAME = 'biblioteca_db'
MONGO_LOG_COLLECTION = 'atividade_logs'

app = Flask(__name__)

# ======================================================================
# FUNÇÕES DE CONEXÃO COM BANCOS DE DADOS
# ======================================================================

def get_mysql_connection():
    """Tenta estabelecer e retornar uma conexão MySQL."""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn
    except MySQLError as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

def get_mongo_collection():
    """Tenta estabelecer conexão MongoDB e retorna a coleção de logs."""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping') # Verifica a conexão
        db = client[MONGO_DB_NAME]
        # Cria a coleção Capped se não existir (apenas para inicialização)
        if MONGO_LOG_COLLECTION not in db.list_collection_names():
            # Esta parte é idealmente executada no Shell, mas está aqui para segurança
            print("AVISO: Coleção de logs do MongoDB não encontrada. Criando...")
            db.create_collection(
                MONGO_LOG_COLLECTION,
                capped=True,
                size=5242880, # 5MB
                max= 5000
            )
        return db[MONGO_LOG_COLLECTION]
    except MongoError as e:
        print(f"Erro ao conectar ao MongoDB: {e}")
        return None

# ======================================================================
# LÓGICA DE NEGÓCIO - REPLICANDO FUNÇÕES DE GERAÇÃO DE ID DO MYSQL
# As regras customizadas de ID são recriadas no Python para inserção.
# ======================================================================

def generate_custom_id(name, prefix, length_name, length_seq, separator, table_name):
    """
    Função genérica para replicar a lógica de geração de IDs customizados.
    Necessita de uma consulta ao MySQL para obter a sequência.
    """
    conn = get_mysql_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        # 1. Cria a base do ID
        base_name = name.upper().replace(' ', '')
        base_id = base_name[:length_name]

        # 2. Constrói o padrão LIKE para contar IDs existentes
        search_pattern = f"{base_id}%{separator}%"

        # 3. Consulta a sequência atual (count + 1)
        query = f"SELECT COUNT(*) as count FROM {table_name} WHERE {table_name[:-1]}_id LIKE '{search_pattern}';"
        cursor.execute(query)
        result = cursor.fetchone()
        sequence = result['count'] + 1

        # 4. Formata o novo ID
        sequence_padded = str(sequence).zfill(length_seq)
        new_id = f"{base_id}{separator}{sequence_padded}"
        return new_id
    except MySQLError as e:
        print(f"Erro ao gerar ID customizado para {table_name}: {e}")
        return None
    finally:
        conn.close()

def generate_user_id(name):
    """Gera ID de usuário (Ex: JOA25U000001) - Replica fn_gerar_id_usuario"""
    base_name = name.upper().replace(' ', '')[:3]
    year = datetime.now().strftime('%y')
    separator = 'U'
    
    conn = get_mysql_connection()
    if not conn: return None

    try:
        cursor = conn.cursor(dictionary=True)
        search_pattern = f"{base_name}{year}{separator}%"
        
        # Consulta a sequência atual
        query = f"SELECT COUNT(*) AS count FROM usuarios WHERE usuario_id LIKE '{search_pattern}';"
        cursor.execute(query)
        result = cursor.fetchone()
        sequence = result['count'] + 1
        
        sequence_padded = str(sequence).zfill(6) # 6 dígitos de sequência
        new_id = f"{base_name}{year}{separator}{sequence_padded}"
        return new_id
    except MySQLError as e:
        print(f"Erro ao gerar ID de usuário: {e}")
        return None
    finally:
        conn.close()

def generate_livro_id(title, year):
    """Gera ID de Livro (Ex: ASO24L000001) - Replica fn_gerar_id_livro"""
    base_title = title.upper().replace(' ', '')[:3]
    year_suffix = str(year)[-2:]
    separator = 'L'
    
    conn = get_mysql_connection()
    if not conn: return None

    try:
        cursor = conn.cursor(dictionary=True)
        search_pattern = f"{base_title}{year_suffix}{separator}%"
        
        query = f"SELECT COUNT(*) AS count FROM livros WHERE livro_id LIKE '{search_pattern}';"
        cursor.execute(query)
        result = cursor.fetchone()
        sequence = result['count'] + 1
        
        sequence_padded = str(sequence).zfill(6) # 6 dígitos de sequência
        new_id = f"{base_title}{year_suffix}{separator}{sequence_padded}"
        return new_id
    except MySQLError as e:
        print(f"Erro ao gerar ID de livro: {e}")
        return None
    finally:
        conn.close()

def generate_autor_id(name):
    """Gera ID de Autor (Ex: TOLLIA00001) - Replica fn_gerar_id_autor"""
    base_name = name.upper().replace(' ', '')[:4]
    separator = 'A'
    
    conn = get_mysql_connection()
    if not conn: return None

    try:
        cursor = conn.cursor(dictionary=True)
        search_pattern = f"{base_name}{separator}%"
        
        query = f"SELECT COUNT(*) AS count FROM autores WHERE autor_id LIKE '{search_pattern}';"
        cursor.execute(query)
        result = cursor.fetchone()
        sequence = result['count'] + 1
        
        sequence_padded = str(sequence).zfill(5) # 5 dígitos de sequência
        new_id = f"{base_name}{separator}{sequence_padded}"
        return new_id
    except MySQLError as e:
        print(f"Erro ao gerar ID de autor: {e}")
        return None
    finally:
        conn.close()


# ======================================================================
# FUNÇÃO DE LOG (INTEGRAÇÃO COM MONGODB)
# ======================================================================

def log_activity(usuario_id: str, acao: str, detalhes: dict):
    """Insere um log de atividade na coleção MongoDB (Capped Collection)."""
    log_collection = get_mongo_collection()
    if not log_collection:
        print("AVISO: Falha ao conectar ao MongoDB. Log não salvo.")
        return

    log_document = {
        'timestamp': datetime.now(),
        'usuario_id': usuario_id, # ID do MySQL (ex: MAR25U000003)
        'acao': acao,             # Ex: 'LOGIN_SUCESSO', 'EMPRESTIMO_REALIZADO'
        'detalhes': detalhes,
        # Adicionar o ID do atendente logado/API Key se houver
        'responsavel': MYSQL_CONFIG['user'] 
    }
    
    try:
        log_collection.insert_one(log_document)
    except Exception as e:
        print(f"Erro ao inserir log no MongoDB: {e}")


# ======================================================================
# ROTAS DA API (FLASK)
# ======================================================================

# Simulação de ID de Usuário Logado para Logs
# Em um sistema real, este seria obtido via token de autenticação.
API_USER_ID = 'FUNC24U000001' # ID fictício para logs

@app.route('/usuarios', methods=['POST'])
def criar_usuario():
    """Cria um novo usuário na tabela 'usuarios'."""
    data = request.get_json()
    required_fields = ['nome', 'email', 'grupo_id', 'senha_hash']

    if not all(field in data for field in required_fields):
        log_activity(API_USER_ID, 'ERRO_API', {'endpoint': '/usuarios', 'erro': 'Campos obrigatórios faltando'})
        return jsonify({"erro": "Campos obrigatórios faltando: nome, email, grupo_id, senha_hash"}), 400

    # 1. Gerar ID customizado usando a lógica Python
    new_user_id = generate_user_id(data['nome'])
    if not new_user_id:
        return jsonify({"erro": "Falha ao gerar ID customizado"}), 500

    conn = get_mysql_connection()
    if not conn:
        return jsonify({"erro": "Falha na conexão com o MySQL"}), 500

    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO usuarios (usuario_id, grupo_id, nome, email, senha_hash)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            new_user_id, 
            data['grupo_id'], 
            data['nome'], 
            data['email'], 
            data['senha_hash']
        ))
        conn.commit()
        
        log_activity(API_USER_ID, 'USUARIO_CRIADO', {
            'usuario_id': new_user_id, 
            'email': data['email']
        })
        return jsonify({
            "mensagem": "Usuário criado com sucesso",
            "usuario_id": new_user_id
        }), 201
    except MySQLError as e:
        conn.rollback()
        error_msg = f"Erro MySQL: {e}"
        log_activity(API_USER_ID, 'ERRO_BD', {'endpoint': '/usuarios', 'erro': error_msg})
        return jsonify({"erro": error_msg}), 500
    finally:
        conn.close()


@app.route('/livros', methods=['POST'])
def adicionar_livro():
    """Adiciona um novo livro, autor e editora se não existirem."""
    data = request.get_json()
    # Campos obrigatórios para o livro
    required_fields = ['titulo', 'autor_nome', 'editora_nome', 'categoria_id', 'ano_publicacao', 'quantidade_total']

    if not all(field in data for field in required_fields):
        return jsonify({"erro": "Campos obrigatórios faltando"}), 400

    conn = get_mysql_connection()
    if not conn:
        return jsonify({"erro": "Falha na conexão com o MySQL"}), 500

    autor_id = None
    editora_id = None
    
    try:
        cursor = conn.cursor(dictionary=True)

        # 1. Encontrar/Criar Autor
        cursor.execute("SELECT autor_id FROM autores WHERE nome = %s", (data['autor_nome'],))
        autor = cursor.fetchone()
        if autor:
            autor_id = autor['autor_id']
        else:
            autor_id = generate_autor_id(data['autor_nome'])
            if not autor_id: raise Exception("Falha ao gerar ID de autor")
            cursor.execute("INSERT INTO autores (autor_id, nome) VALUES (%s, %s)", (autor_id, data['autor_nome']))

        # 2. Encontrar/Criar Editora
        cursor.execute("SELECT editora_id FROM editoras WHERE nome = %s", (data['editora_nome'],))
        editora = cursor.fetchone()
        if editora:
            editora_id = editora['editora_id']
        else:
            editora_id = generate_custom_id(data['editora_nome'], 'EDI', 4, 5, 'E', 'editoras')
            if not editora_id: raise Exception("Falha ao gerar ID de editora")
            cursor.execute("INSERT INTO editoras (editora_id, nome) VALUES (%s, %s)", (editora_id, data['editora_nome']))

        # 3. Gerar ID e Inserir Livro
        livro_id = generate_livro_id(data['titulo'], data['ano_publicacao'])
        if not livro_id: raise Exception("Falha ao gerar ID de livro")

        sql_livro = """
            INSERT INTO livros (livro_id, titulo, autor_id, editora_id, categoria_id, ano_publicacao, 
                                quantidade_total, quantidade_disponivel, sinopse, isbn)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_livro, (
            livro_id, data['titulo'], autor_id, editora_id, data['categoria_id'], 
            data['ano_publicacao'], data['quantidade_total'], data['quantidade_total'], 
            data.get('sinopse'), data.get('isbn')
        ))

        conn.commit()
        
        log_activity(API_USER_ID, 'LIVRO_ADICIONADO', {
            'livro_id': livro_id, 
            'titulo': data['titulo']
        })
        return jsonify({
            "mensagem": "Livro, autor e editora processados com sucesso",
            "livro_id": livro_id
        }), 201

    except MySQLError as e:
        conn.rollback()
        error_msg = f"Erro MySQL ao adicionar livro: {e}"
        log_activity(API_USER_ID, 'ERRO_BD', {'endpoint': '/livros', 'erro': error_msg})
        return jsonify({"erro": error_msg}), 500
    except Exception as e:
        conn.rollback()
        error_msg = str(e)
        return jsonify({"erro": error_msg}), 500
    finally:
        conn.close()


@app.route('/emprestimo', methods=['POST'])
def realizar_emprestimo():
    """
    Executa a PROCEDURE sp_realizar_emprestimo para garantir a lógica
    de negócio e as validações (limite, disponibilidade, status).
    """
    data = request.get_json()
    required_fields = ['usuario_id', 'livro_id', 'dias_emprestimo']

    if not all(field in data for field in required_fields):
        return jsonify({"erro": "Campos obrigatórios faltando: usuario_id, livro_id, dias_emprestimo"}), 400
    
    conn = get_mysql_connection()
    if not conn:
        return jsonify({"erro": "Falha na conexão com o MySQL"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        # 1. Chamar a Stored Procedure
        args = (data['usuario_id'], data['livro_id'], data['dias_emprestimo'])
        
        # A procedure retorna um resultado (mensagem e emprestimo_id)
        cursor.callproc('sp_realizar_emprestimo', args)
        
        # Obter o resultado da procedure
        result = [res.fetchall() for res in cursor.stored_results()]
        
        conn.commit()
        
        emprestimo_info = result[0][0] # Primeiro resultado é a mensagem/ID
        
        log_activity(API_USER_ID, 'EMPRESTIMO_REALIZADO', {
            'usuario_id': data['usuario_id'],
            'livro_id': data['livro_id'],
            'emprestimo_id': emprestimo_info['emprestimo_id']
        })
        
        return jsonify(emprestimo_info), 200

    except MySQLError as e:
        conn.rollback()
        # Captura erros gerados pelo SIGNAL da Stored Procedure
        if e.errno == 1644: # MySQL error code for SIGNAL
            error_msg = str(e).split(':')[-1].strip()
        else:
            error_msg = f"Erro interno do Banco de Dados: {e}"

        log_activity(API_USER_ID, 'ERRO_EMPRESTIMO', {
            'usuario_id': data['usuario_id'],
            'livro_id': data['livro_id'],
            'erro': error_msg
        })
        return jsonify({"erro": error_msg}), 400
    finally:
        conn.close()


@app.route('/devolucao', methods=['POST'])
def realizar_devolucao():
    """
    Atualiza o empréstimo como 'devolvido'. Isso aciona o TRIGGER
    'after_emprestimo_update' no MySQL, que calcula e insere a multa.
    """
    data = request.get_json()
    required_fields = ['emprestimo_id']

    if not all(field in data for field in required_fields):
        return jsonify({"erro": "Campo 'emprestimo_id' obrigatório"}), 400
    
    conn = get_mysql_connection()
    if not conn:
        return jsonify({"erro": "Falha na conexão com o MySQL"}), 500

    try:
        cursor = conn.cursor()
        
        # Data de devolução real é hoje.
        sql = """
            UPDATE emprestimos SET
            status = 'devolvido',
            data_devolucao_real = CURDATE()
            WHERE emprestimo_id = %s AND status = 'ativo'
        """
        cursor.execute(sql, (data['emprestimo_id'],))
        
        if cursor.rowcount == 0:
            return jsonify({"aviso": "Empréstimo não encontrado ou já devolvido"}), 404

        conn.commit()
        
        # O TRIGGER MySQL executa a lógica de estoque e multa aqui.
        
        log_activity(API_USER_ID, 'DEVOLUCAO_REALIZADA', {
            'emprestimo_id': data['emprestimo_id']
        })
        return jsonify({"mensagem": "Devolução registrada. Multa (se houver) processada."}), 200

    except MySQLError as e:
        conn.rollback()
        error_msg = f"Erro MySQL ao registrar devolução: {e}"
        log_activity(API_USER_ID, 'ERRO_BD', {'endpoint': '/devolucao', 'erro': error_msg})
        return jsonify({"erro": error_msg}), 500
    finally:
        conn.close()


@app.route('/logs', methods=['GET'])
def buscar_logs():
    """
    Busca os últimos logs de atividade no MongoDB (NoSQL).
    Demonstra a leitura de dados não-estruturados.
    """
    log_collection = get_mongo_collection()
    if not log_collection:
        return jsonify({"erro": "Falha na conexão com o MongoDB"}), 500
    
    try:
        # Consulta: Busca os 50 logs mais recentes, ordenados por timestamp decrescente
        recent_logs = list(log_collection.find().sort("timestamp", -1).limit(50))

        # O ObjectId e o datetime precisam ser convertidos para string/JSON
        # para serem serializados pelo Flask
        serialized_logs = []
        for log in recent_logs:
            log['_id'] = str(log['_id'])
            log['timestamp'] = log['timestamp'].isoformat()
            serialized_logs.append(log)

        return jsonify(serialized_logs), 200

    except Exception as e:
        error_msg = f"Erro ao buscar logs no MongoDB: {e}"
        log_activity(API_USER_ID, 'ERRO_MONGODB', {'endpoint': '/logs', 'erro': error_msg})
        return jsonify({"erro": error_msg}), 500


if __name__ == '__main__':
    print("Iniciando o Backend da Biblioteca...")
    print(f"MySQL DB: {MYSQL_CONFIG['database']} - User: {MYSQL_CONFIG['user']}")
    print(f"MongoDB Collection: {MONGO_LOG_COLLECTION}")
    # Nota: Use port 5000 para evitar conflito com outros serviços
    app.run(debug=True, port=5000)