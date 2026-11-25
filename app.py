"""
Aplicação Flask RESTful com SQLAlchemy - Projeto Prático para o Google Cloud Shell
Disciplina: Desenvolvimento Back-end (SENAI)
"""

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Instancia a aplicação Flask
app = Flask(__name__)

# Configura o banco de dados SQLite local
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tarefas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o ORM SQLAlchemy
db = SQLAlchemy(app)

# ==========================================
# MODELO DE DADOS (ORM)
# ==========================================
class Tarefa(db.Model):
    __tablename__ = 'tarefas'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    concluida = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Converte a entidade do banco de dados para um dicionário Python (serializável em JSON)."""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'concluida': self.concluida,
            'data_criacao': self.data_criacao.strftime('%Y-%m-%d %H:%M:%S')
        }

# Cria as tabelas do banco de dados no momento da inicialização
with app.app_context():
    db.create_all()

# ==========================================
# ROTAS DA API RESTful
# ==========================================

# MÓDULO 1: Rota Base (Teste de Conectividade)
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'mensagem': 'Bem-vindo à API RESTful de Tarefas (SENAI Back-end)',
        'status': 'operacional',
        'versao': '1.0'
    }), 200

# MÓDULO 2 & 3: Listar todas as tarefas (READ ALL)
@app.route('/api/tarefas', methods=['GET'])
def listar_tarefas():
    tarefas = Tarefa.query.all()
    # Converte a lista de objetos Tarefa para uma lista de dicionários
    return jsonify([t.to_dict() for t in tarefas]), 200

# MÓDULO 2 & 3: Buscar uma tarefa específica por ID (READ ONE)
@app.route('/api/tarefas/<int:id>', methods=['GET'])
def buscar_tarefa(id):
    tarefa = db.session.get(Tarefa, id)
    if not tarefa:
        return jsonify({'erro': 'Tarefa não encontrada'}), 404
    return jsonify(tarefa.to_dict()), 200

# MÓDULO 2 & 3: Criar uma nova tarefa (CREATE)
@app.route('/api/tarefas', methods=['POST'])
def criar_tarefa():
    dados = request.get_json()
    
    # Validação simples do payload JSON recebido
    if not dados or 'titulo' not in dados or not dados['titulo'].strip():
        return jsonify({'erro': 'O campo "titulo" é obrigatório'}), 400

    nova_tarefa = Tarefa(
        titulo=dados['titulo'].strip(),
        concluida=dados.get('concluida', False)
    )
    
    db.session.add(nova_tarefa)
    db.session.commit()
    
    return jsonify(nova_tarefa.to_dict()), 201

# MÓDULO 2 & 3: Atualizar uma tarefa existente (UPDATE)
@app.route('/api/tarefas/<int:id>', methods=['PUT'])
def atualizar_tarefa(id):
    tarefa = db.session.get(Tarefa, id)
    if not tarefa:
        return jsonify({'erro': 'Tarefa não encontrada'}), 404

    dados = request.get_json()
    if not dados:
        return jsonify({'erro': 'Corpo da requisição JSON inválido ou vazio'}), 400

    if 'titulo' in dados and dados['titulo'].strip():
        tarefa.titulo = dados['titulo'].strip()
    
    if 'concluida' in dados:
        tarefa.concluida = bool(dados['concluida'])

    db.session.commit()
    return jsonify(tarefa.to_dict()), 200

# MÓDULO 2 & 3: Deletar uma tarefa (DELETE)
@app.route('/api/tarefas/<int:id>', methods=['DELETE'])
def deletar_tarefa(id):
    tarefa = db.session.get(Tarefa, id)
    if not tarefa:
        return jsonify({'erro': 'Tarefa não encontrada'}), 404

    db.session.delete(tarefa)
    db.session.commit()
    return jsonify({'mensagem': f'Tarefa {id} removida com sucesso'}), 200

# Execução do servidor no Cloud Shell (porta 5000)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
