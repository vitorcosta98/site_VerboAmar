from site_verbo_amar import database, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(id_usuario):
    return Usuario.query.get(int(id_usuario))

class Usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    senha = database.Column(database.String, nullable=False)
    sexo = database.Column(database.String, nullable=False)
    adm = database.Column(database.String, nullable=False)
    professor = database.Column(database.String, nullable=False)
    data_aniversario = database.Column(database.DateTime, nullable=False)


class Atividade(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    atividade = database.Column(database.String, nullable=False, unique=True)
    dias_aula = database.Column(database.String, nullable=False)


class Aluno(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    nome_completo = database.Column(database.String, nullable=False)
    cpf = database.Column(database.Integer, nullable=False)
    sexo = database.Column(database.String, nullable=False)
    nome_mae = database.Column(database.String, nullable=False)
    nome_pai = database.Column(database.String, nullable=False)
    data_aniversario = database.Column(database.DateTime, nullable=False)

class Turma(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    id_professor = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    id_aluno = database.Column(database.Integer, database.ForeignKey('aluno.id'))
    id_curso = database.Column(database.Integer, database.ForeignKey('atividade.id'))
    horario_inicio = database.Column(database.Integer, nullable=False)
    horario_fim = database.Column(database.Integer, nullable=False)


