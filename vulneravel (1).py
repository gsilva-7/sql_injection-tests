"""
DEMO DE VULNERABILIDADE: SQL Injection (SQLi)
ATENÇÃO: Código demonstrativo para aulas do SENAI no Google Cloud Shell.
NÃO UTILIZAR EM AMBIENTE DE PRODUÇÃO!
"""

from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def init_db():
    """Inicializa banco SQLite de teste em memória/arquivo."""
    conn = sqlite3.connect('vulneravel.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            senha TEXT,
            saldo REAL
        )
    ''')
    cursor.execute('DELETE FROM usuarios')
    cursor.execute("INSERT INTO usuarios (usuario, senha, saldo) VALUES ('admin', 'senha_super_secreta_123', 50000.0)")
    cursor.execute("INSERT INTO usuarios (usuario, senha, saldo) VALUES ('aluno_senai', '123456', 250.0)")
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'Servidor Vulnerável Ativo (Porta 5001)',
        'alerta': 'Este endpoint possui vulnerabilidades propositais de SQL Injection!'
    }), 200

# ==============================================================================
# VULNERABILIDADE 1: LOGIN VULNERÁVEL (Bypass de Autenticação)
# ==============================================================================
@app.route('/api/login-vulneravel', methods=['POST'])
def login_vulneravel():
    dados = request.get_json() or {}
    usuario = dados.get('usuario', '')
    senha = dados.get('senha', '')

    conn = sqlite3.connect('vulneravel.db')
    cursor = conn.cursor()

    # VULNERABILIDADE CRÍTICA: Concatenação direta de strings (f-string)
    # Permite que comandos SQL enviados pelo usuário sejam interpretados pelo banco!
    sql_query = f"SELECT id, usuario, saldo FROM usuarios WHERE usuario = '{usuario}' AND senha = '{senha}'"
    
    print(f"\n[LOG TERMINAL - QUERY SQL EXECUTADA]:\n{sql_query}\n")

    try:
        cursor.execute(sql_query)
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            return jsonify({
                'status': 'ALERTA: LOGIN EFETUADO COM SUCESSO!',
                'vulnerabilidade_explorada': True,
                'usuario_logado': resultado[1],
                'saldo_exposto': resultado[2]
            }), 200
        else:
            return jsonify({'status': 'Falha', 'mensagem': 'Credenciais inválidas'}), 401

    except sqlite3.Error as err:
        conn.close()
        return jsonify({'erro_sql': str(err), 'query_executada': sql_query}), 500

# ==============================================================================
# VULNERABILIDADE 2: BUSCA VULNERÁVEL VIA QUERY PARAM (Injeção via GET)
# ==============================================================================
@app.route('/api/buscar-vulneravel', methods=['GET'])
def buscar_vulneravel():
    termo = request.args.get('q', '')

    conn = sqlite3.connect('vulneravel.db')
    cursor = conn.cursor()

    # VULNERABILIDADE: Concatena o parâmetro 'q' da URL diretamente na instrução SQL
    sql_query = f"SELECT id, usuario, saldo FROM usuarios WHERE usuario LIKE '%{termo}%'"
    print(f"\n[LOG TERMINAL - QUERY BUSCA]:\n{sql_query}\n")

    try:
        cursor.execute(sql_query)
        registros = cursor.fetchall()
        conn.close()
        return jsonify([{'id': r[0], 'usuario': r[1], 'saldo': r[2]} for r in registros]), 200
    except sqlite3.Error as err:
        conn.close()
        return jsonify({'erro_sql': str(err), 'query_executada': sql_query}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
