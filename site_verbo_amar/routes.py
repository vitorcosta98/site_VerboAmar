from flask import render_template, redirect, url_for, flash, request, abort
from site_verbo_amar import app, database, bcrypt
from site_verbo_amar.forms import FormCriarConta, FormCadAluno,FormLogin, FormCadAtividade, FormTurma
from site_verbo_amar.models import Usuario, Aluno, Atividade, Turma
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from datetime import datetime

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/area-academica")
def area_academica():
    return render_template("area_academica.html")

@app.route('/login')
def login():
    form_login = FormLogin()
    form_criarconta = FormCriarConta()
    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f'Login feito com sucesso no e-mail: {form_login.email.data}', 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash(f'Falha no login. E-mail ou senha incorretos.', 'alert-danger')
    if form_criarconta.validate_on_submit() and 'botao_submit_criarcontar' in request.form:
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data)
        usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email.data,senha=senha_cript, professor=form_criarconta.professor.data,adm=form_criarconta.adm.data, cursos=form_criarconta.cursos.data)
        database.session.add(usuario)
        database.session.commit()
        flash(f'Conta criada para o e-mail: {form_criarconta.email.data}', 'alert-success')
        return redirect(url_for('home'))
    
    return render_template('login.html', form_login=form_login, form_criarconta=form_criarconta)

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')


@app.route('/cadastro/cad_professor', methods=['GET','POST'])
def cad_professor():
    form_criarconta = FormCriarConta()
    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        data_aniversario = datetime.strptime(form_criarconta.data_aniversario.data, '%d/%m/%Y')
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data)
        usuario = Usuario(username=form_criarconta.username.data,
                          email=form_criarconta.email.data,
                          senha=senha_cript, sexo=form_criarconta.sexo.data,
                          adm=form_criarconta.adm.data, professor=form_criarconta.professor.data,
                          data_aniversario=data_aniversario)
        
        database.session.add(usuario)
        database.session.commit()
        flash(f'Conta criada para o e-mail: {form_criarconta.email.data}', 'alert-success')
        return redirect(url_for('home'))
    return render_template('cad_professor.html', form_criarconta=form_criarconta, info_sexo=['M', 'F'])


@app.route('/cadastro/cad_aluno', methods=['GET','POST'])
def cad_aluno():
    form_cad_aluno = FormCadAluno()
    if form_cad_aluno.validate_on_submit() and 'botao_submit_cad' in request.form:
        data_aniversario = datetime.strptime(form_cad_aluno.data_aniversario.data, '%d/%m/%Y')
        aluno = Aluno(nome_completo=form_cad_aluno.nome_completo.data,
                        cpf = form_cad_aluno.cpf.data,
                        sexo = form_cad_aluno.sexo.data,
                        nome_mae= form_cad_aluno.nome_mae.data,
                        nome_pai = form_cad_aluno.nome_pai.data,
                        data_aniversario = data_aniversario
                        )
        
        database.session.add(aluno)
        database.session.commit()
        flash(f'Cadastro do aluno: {form_cad_aluno.nome_completo.data} concluído com sucesso!', 'alert-success')
        return redirect(url_for('home'))
    return render_template('cad_aluno.html', form_cad_aluno=form_cad_aluno, info_sexo=['M', 'F'])


def dias_cursos(form):
    lista_dias = []
    for campo in form:
        if "_feira" in campo.name or campo.name in ('sabado','doming'):
            if campo.data:
                lista_dias.append(campo.label.text)
    return ";".join(lista_dias)


@app.route('/cadastro/cad_atividade', methods=['GET','POST'])
def cad_atividade():
    form_cad_ativ = FormCadAtividade()
    if form_cad_ativ.validate_on_submit() and 'botao_submit_ativ' in request.form:
        dias_atividade = dias_cursos(form_cad_ativ)
        ativ = Atividade(atividade=form_cad_ativ.atividade.data,
                        dias_aula = dias_atividade)
        
        database.session.add(ativ)
        database.session.commit()
        flash(f'Cadastro da atividade: {form_cad_ativ.atividade.data} concluído com sucesso!', 'alert-success')
        return redirect(url_for('home'))
    return render_template('cad_atividade.html', form_cad_ativ=form_cad_ativ)


def carregar_atividades():
    atividades = Atividade.query.order_by(Atividade.id.asc())
    return atividades


def carregar_professores():
    professores = Usuario.query.order_by(Usuario.username.asc())
    return professores


def carregar_alunos():
    alunos = Aluno.query.order_by(Aluno.nome_completo.asc())
    return alunos


def id_atividade(nome_atividade):
    atividade = Atividade.query.filter_by(atividade=nome_atividade).first()
    id = atividade.id
    return id


def id_professor(nome_professor):
    professor = Usuario.query.filter_by(username=nome_professor).first()
    id_professor = professor.id
    return id_professor  


def id_aluno(lista_aluno):
    lista_id = []
    for aluno in lista_aluno:
        mat_aluno = Aluno.query.filter_by(nome_completo=aluno).first()
        id_aluno = str(mat_aluno.id)
        lista_id.append(id_aluno)

    return ";".join(lista_id)


@app.route("/cadastro/cad_turma", methods=['GET','POST'])
def cad_turma():
    form_cad_turma = FormTurma()
    atividades = carregar_atividades()
    professores = carregar_professores()
    alunos = carregar_alunos()

    if form_cad_turma.validate_on_submit() and 'botao_submit_turma' in request.form:
        form_ativ = request.form.get('atividade')
        form_prof = request.form.get('professor')
        form_alunos = request.form.getlist("aluno")
        
        id_ativ = id_atividade(form_ativ)
        id_prof = id_professor(form_prof)
        id_alu = id_aluno(form_alunos)
        print(id_alu) 
        
        turma = Turma(nome_turma=form_cad_turma.nome_turma.data,
                      id_atividade=id_ativ,
                      id_professor=id_prof,
                      id_aluno=id_alu,)
        

        database.session.add(turma)
        database.session.commit()

        flash(f"Cadastro da turma {form_cad_turma.nome_turma.data} concluído!", "alert-success")
        return redirect(url_for('home'))

    return render_template('cad_turma.html',
                           form_cad_turma=form_cad_turma,
                           atividades=atividades,
                           professores=professores,
                           alunos=alunos)
