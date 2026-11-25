"""
DEMO DE SEGURANÇA: Aplicação Protegida contra SQL Injection
Padrões Utilizados: Consultas Parametrizadas (Prepared Statements) e ORM (Flask-SQLAlchemy)
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///seguro.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==============================================================================
# 1. MODELO ORM (Abstração Segura pelo SQLAlchemy)
# ==============================================================================
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    saldo = db.Column(db.Float, default=0.0)

    def to_dict(self):
        return {'id': self.id, 'usuario': self.usuario, 'saldo': self.saldo}

with app.app_context():
    db.create_all()
    # Reset de dados
    Usuario.query.delete()
    db.session.add(Usuario(usuario='admin', senha='senha_super_secreta_123', saldo=50000.0))
    db.session.add(Usuario(usuario='aluno_senai', senha='123456', saldo=250.0))
    db.session.commit()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'Servidor SEGURO Ativo (Porta 5002)',
        'protecao': 'Consultas parametrizadas e Mapeamento Objeto-Relacional (ORM) ativos.'
    }), 200

# ==============================================================================
# PREVENÇÃO 1: LOGIN SEGURO USANDO ORM (FLASK-SQLALCHEMY)
# ==============================================================================
@app.route('/api/login-seguro', methods=['POST'])
def login_seguro():
    dados = request.get_json() or {}
    usuario_input = dados.get('usuario', '')
    senha_input = dados.get('senha', '')

    # PROTEÇÃO: O ORM trata as entradas como VALORES PUROS (literais), desarmando as aspas simples e operadores SQL
    usuario_encontrado = Usuario.query.filter_by(
        usuario=usuario_input, 
        senha=senha_input
    ).first()

    if usuario_encontrado:
        return jsonify({
            'status': 'Login efetuado com SUCESSO',
            'seguranca': 'Consulta tratada com segurança pelo ORM',
            'usuario': usuario_encontrado.usuario,
            'saldo': usuario_encontrado.saldo
        }), 200
    
    return jsonify({'status': 'Falha', 'mensagem': 'Credenciais inválidas'}), 401

# ==============================================================================
# PREVENÇÃO 2: BUSCA SEGURA COM CONSULTAS PARAMETRIZADAS (PREPARED STATEMENTS)
# ==============================================================================
@app.route('/api/buscar-seguro', methods=['GET'])
def buscar_seguro():
    termo = request.args.get('q', '')

    conn = sqlite3.connect('seguro.db')
    cursor = conn.cursor()

    # PROTEÇÃO: Uso de marcadores de posição '?' (Prepared Statements)
    # A estrutura do comando SQL é pré-compilada pelo banco antes da entrada dos dados
    sql_instrucao = "SELECT id, usuario, saldo FROM usuarios WHERE usuario LIKE ?"
    print(f"\n[LOG TERMINAL - QUERY PARAMETRIZADA]: {sql_instrucao}")
    print(f"[LOG TERMINAL - PARÂMETRO TRATADO SEPARADAMENTE]: ('%{termo}%',)\n")

    # Passagem de parâmetros como tupla
    cursor.execute(sql_instrucao, (f"%{termo}%",))
    registros = cursor.fetchall()
    conn.close()

    return jsonify([{'id': r[0], 'usuario': r[1], 'saldo': r[2]} for r in registros]), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
