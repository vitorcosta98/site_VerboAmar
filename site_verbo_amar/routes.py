from flask import render_template, redirect, url_for, flash, request, abort
from site_verbo_amar import app, database, bcrypt
from site_verbo_amar.forms import FormCriarConta, FormCadAluno,FormLogin, FormCadAtividade
from site_verbo_amar.models import Usuario, Aluno, Atividade
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
        print(dias_atividade)
        print(type(dias_atividade))
        ativ = Atividade(atividade=form_cad_ativ.atividade.data,
                        dias_aula = dias_atividade)
        
        database.session.add(ativ)
        database.session.commit()
        flash(f'Cadastro da atividade: {form_cad_ativ.atividade.data} concluído com sucesso!', 'alert-success')
        return redirect(url_for('home'))
    return render_template('cad_atividade.html', form_cad_ativ=form_cad_ativ)