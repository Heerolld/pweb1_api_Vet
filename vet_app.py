from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///animais.db'
db = SQLAlchemy(app)

class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    tipo = db.Column(db.String(80), nullable=False)
    idade = db.Column(db.Integer)
    dono = db.Column(db.String(80))

@app.route('/animais', methods=['GET'])
def listagem_animais():
    animais = Animal.query.all()
    animal_list = [{'id': animal.id, 'nome': animal.nome, 'tipo': animal.tipo, 'idade': animal.idade, 'dono': animal.dono} for animal in animais]
    return jsonify(animal_list)

@app.route('/animais/<int:id>', methods=['GET'])
def obter_animal(id):
    animal = Animal.query.get(id)
    if animal:
        animal_data = {'id': animal.id, 'nome': animal.nome, 'tipo': animal.tipo, 'idade': animal.idade, 'dono': animal.dono}
        return jsonify(animal_data)
    return jsonify({'mensagem': 'Animal não encontrado'}), 404

@app.route('/animais/<int:id>', methods=['PUT'])
def atualizar_animal(id):
    animal = Animal.query.get(id)
    if not animal:
        return jsonify({'mensagem': 'Animal não encontrado'}), 404

    dados = request.get_json()
    animal.nome = dados.get('nome', animal.nome)
    animal.tipo = dados.get('tipo', animal.tipo)
    animal.idade = dados.get('idade', animal.idade)
    animal.dono = dados.get('dono', animal.dono)

    try:
        db.session.commit()
        return jsonify({'mensagem': 'Animal atualizado'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'mensagem': 'Erro ao atualizar', 'erro': str(e)}), 500

@app.route('/animais/<int:id>', methods=['DELETE'])
def excluir_animal(id):
    animal = Animal.query.get(id)
    if not animal:
        return jsonify({'mensagem': 'Animal não encontrado'}), 404

    try:
        db.session.delete(animal)
        db.session.commit()
        return jsonify({'mensagem': 'Animal excluído'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'mensagem': 'Erro ao excluir', 'erro': str(e)}), 500

@app.route('/animais', methods=['POST'])
def criar_animal():
    dados = request.get_json()

    if 'nome' not in dados or 'tipo' not in dados:
        return jsonify({'mensagem': 'Você deve preencher nome e tipo'}), 400

    # Validação
    if 'idade' in dados and not isinstance(dados['idade'], int):
        return jsonify({'mensagem': 'Preencha a idade om um número inteiro'}), 400

    nome = dados['nome']
    tipo = dados['tipo']
    idade = dados.get('idade')
    dono = dados.get('dono')

    novo_animal = Animal(nome=nome, tipo=tipo, idade=idade, dono=dono)

    try:
        db.session.add(novo_animal)
        db.session.commit()
        return jsonify({'mensagem': 'Animal registrado!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'mensagem': 'Erro, não foi possivel registrar animal', 'erro': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
