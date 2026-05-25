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
    foto_perfil = database.Column(database.String, default='default.png')
    professor = database.Column(database.String, nullable=False, default='Não')
    adm = database.Column(database.String, nullable=False, default='Não')
    cursos = database.Column(database.String, nullable=False, default='Sem Turmas')

class Curso(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    nome_curso = database.Column(database.String, nullable=False, unique=True)
    dias_de_aula = database.Column(database.String, nullable=False)
    horario_inicio = database.Column(database.String, nullable=False)
    horario_fim = database.Column(database.String, nullable=False)

class Aluno(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    nome_completo = database.Column(database.String, nullable=False)
    nome_mãe = database.Column(database.String, nullable=False)
    nome_pai = database.Column(database.String, nullable=False)
    data_aniversario = database.Column(database.Datetime, nullable=False)

class Turma(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    id_professor = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    id_aluno = database.Column(database.Integer, database.ForeignKey('aluno.id'))
    id_curso = database.Column(database.Integer, database.ForeignKey('curso.id'))


