from flask import render_template, redirect, url_for, flash, request, abort
from site_verbo_amar import app, database, bcrypt
from site_verbo_amar.forms import FormCriarConta,FormLogin, FormCadAtividade, FormTurma, FormChamada
from site_verbo_amar.models import Usuario, Aluno, Atividade, Turma, ListaAulas, Professor
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from datetime import datetime
import sys


@app.route("/home", methods=['POST','GET'])
@login_required
def home():
    nome_usuario = current_user
    lista_alunos,lista_professores, lista_adms = carregar_aniversarios()

    data_atual = datetime.now()
    data_atual = data_atual.strftime("%d/%m/%Y")

    lista_aniversario_prof = []
    lista_aniversario_alun = []
    lista_aniversario_adm = []

    for a in lista_professores:
        if a[1][:4] == data_atual[:4]:
            lista_aniversario_prof.append(a[0])
    
    for a in lista_alunos:
        if a[1][:4] == data_atual[:4]:
            lista_aniversario_alun.append(a[0])
    
    for a in lista_adms:
        if a[1][:4] == data_atual[:4]:
            if a not in lista_professores:
                lista_aniversario_adm.append(a[0])

    if len(lista_aniversario_prof) > 0 or len(lista_aniversario_alun) > 0 or len(lista_aniversario_adm)>0:
        resposta=True
    else:
        resposta=False


    return render_template("home.html",
                           nome_usuario=nome_usuario,
                           lista_aniversario_prof=lista_aniversario_prof,
                           lista_aniversario_alun=lista_aniversario_alun,
                           lista_aniversario_adm=lista_aniversario_adm,
                           aniversariantes=resposta)


@app.route("/")
def pag_inicial():
    return render_template("pag_inicial.html")


@app.route("/area-academica", methods=['POST','GET'])
@login_required
def area_academica():
    atividades = carregar_nome_atividades()
    atividades = carregar_turmas(atividades)
    adm = current_user.adm

    if adm=="1":
        privilegio=True
    else:
        privilegio=False
    
    return render_template("area_academica.html", atividades=atividades,privilegio=privilegio)


@app.route('/login', methods=['GET','POST'])
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
            form_login.senha.errors.append("E-mail ou senha incorretos.")
            form_login.email.errors.append("E-mail ou senha incorretos.")
            flash(f'Falha no login. E-mail ou senha incorretos.', 'alert-danger')


    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        data_nascimento = datetime.strptime(form_criarconta.data_nascimento.data, '%d/%m/%Y')
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data)

        usuario = Usuario(username=form_criarconta.username.data,
                          email=form_criarconta.email.data,
                          senha=senha_cript,
                          sexo=form_criarconta.sexo.data,
                          adm=form_criarconta.adm.data,
                          professor=form_criarconta.professor.data,
                          data_nascimento=data_nascimento)
        
        database.session.add(usuario)
        database.session.commit()

        if form_criarconta.professor.data == 1:
            id_prof = carregar_id_professor(nome=form_criarconta.username.data, data_nascimento=data_nascimento)
            if id_prof == None:
                cad_professor = Professor(
                    nome_completo=form_criarconta.username.data,
                    data_nascimento=data_nascimento,
                    sexo=form_criarconta.sexo.data
                )
                database.session.add(cad_professor)
                database.session.commit()
        
        flash(f'Conta criada para o e-mail: {form_criarconta.email.data}', 'alert-success')
        return redirect(url_for('home'))
    
    return render_template('login.html', form_login=form_login, form_criarconta=form_criarconta)


@app.route("/sair")
def sair():
    logout_user()
    flash(f'Logout Feito com Sucesso', 'alert-success')
    return redirect(url_for('pag_inicial'))


@app.route('/cadastro')
@login_required
def cadastro():
    return render_template('cadastro.html')


@app.route('/cadastro/cad_atividade', methods=['GET','POST'])
@login_required
def cad_atividade():
    form_cad_ativ = FormCadAtividade()
    if form_cad_ativ.validate_on_submit() and 'botao_submit_ativ' in request.form:
        dias_atividade = dias_cursos(form_cad_ativ)
        ativ = Atividade(atividade=form_cad_ativ.atividade.data,
                        dias_aula = dias_atividade)
        
        database.session.add(ativ)
        database.session.commit()
        flash(f'Cadastro da atividade: {form_cad_ativ.atividade.data} concluído com sucesso!', 'alert-success')
        return redirect(url_for('cadastro'))
    return render_template('cad_atividade.html', form_cad_ativ=form_cad_ativ)


def carregar_id_professor(nome, data_nascimento):
    id_professor = Professor.query.filter_by(nome_completo=nome, data_nascimento=data_nascimento).first()
    if id_professor:
        id = id_professor.id
    else:
        id = None
    return id


def carregar_id_aluno(nome, data_nascimento):
    id_aluno = Aluno.query.filter_by(nome_completo=nome, data_nascimento=data_nascimento).first()
    if id_aluno:
        id = id_aluno.id
    else:
        id = None
    return id


@app.route("/cadastro/cad_turma", methods=['GET','POST'])
@login_required
def cad_turma():
    form_cad_turma = FormTurma()
    atividades = carregar_atividades()

    if form_cad_turma.validate_on_submit() and 'botao_submit_turma' in request.form:
        nome_turma = form_cad_turma.nome_turma.data
        id_ativ = id_atividade(request.form.get('atividade'))
        
        nome_professor = request.form.get('nomeProfessor')
        data_ani_prof = request.form.get('dataProfessor')
        genero_prof = request.form.get('generoProfessor')

        try:
            data_prof = datetime.strptime(data_ani_prof, "%d/%m/%Y")
            id_prof = carregar_id_professor(nome=nome_professor, data_nascimento=data_prof)
            if id_prof == None:
                cad_professor = Professor(
                    nome_completo=nome_professor,
                    data_nascimento=data_prof,
                    sexo=genero_prof
                )
                database.session.add(cad_professor)
                database.session.commit()
                id_prof = carregar_id_professor(nome=nome_professor, data_nascimento=data_prof)   

        except:
            flash("Falha ao cadastrar professor. Por favor, revise os campos digitados", "alert-danger")
            return redirect(url_for("cad_turma"))
        
        l_nomesAlunos = request.form.getlist("nomeAluno[]")
        l_datasAlunos = request.form.getlist("dataAluno[]")
        l_generoAlunos= request.form.getlist("generoAluno[]")

        l_regAlunos = tuple(zip(l_nomesAlunos,l_datasAlunos,l_generoAlunos))

        l_idAlunos = []

        for a in l_regAlunos:
            try:
                data_nasc_aluno = datetime.strptime(a[1], "%d/%m/%Y")
                nome_aluno = a[0]
                genero_aluno = a[2]
                id_aluno = carregar_id_aluno(nome=nome_aluno, data_nascimento=data_nasc_aluno)
                if id_aluno == None:
                    cad_aluno = Aluno(
                        nome_completo = nome_aluno,
                        sexo=genero_aluno,
                        data_nascimento=data_nasc_aluno
                    )
                    database.session.add(cad_aluno)
                    database.session.commit()

                    id_aluno = carregar_id_aluno(nome=nome_aluno, data_nascimento=data_nasc_aluno)
                
                l_idAlunos.append(str(id_aluno))
            except Exception as e:
                print(f"Erro {e}")
                flash("Falha ao cadastrar alunos. Por favor, revise os campos digitados.", "alert-danger")
                return redirect(url_for('cad_turma'))


        ids_alunos = ";".join(l_idAlunos)

        cad_turma = Turma(
            nome_turma = nome_turma,
            id_professor = id_prof,
            id_atividade = id_ativ,
            id_aluno= ids_alunos,
        )

        database.session.add(cad_turma)
        database.session.commit()

        flash(f"Cadastro da turma {form_cad_turma.nome_turma.data} concluído!", "alert-success")

    return render_template('cad_turma.html',
                           form_cad_turma=form_cad_turma,
                           atividades=atividades)


@app.route("/area-academica/turmas/<nome>", methods=['GET', 'POST'])
@login_required
def exibir_turmas(nome):
    atividade = Atividade.query.filter_by(atividade=nome).first_or_404()
    turmas = Turma.query.filter_by(id_atividade=atividade.id).all()

    if current_user.adm == "1":
        privilegio=True
    else:
        privilegio=False

    return render_template('pag_turmas.html',
                           nome_atividade=atividade.atividade,
                           turmas=turmas,
                           privilegio=privilegio)


@app.route("/area-academica/turmas/chamada/<nome_turma>", methods=['GET','POST'])
@login_required
def carregar_chamada(nome_turma):
    turma = Turma.query.filter_by(nome_turma=nome_turma).first_or_404()
    if type(turma.id_aluno) == int:
        lista_id_alunos = [turma.id_aluno]
    else:
        lista_id_alunos = [id for id in turma.id_aluno.split(";") if id]
    

    lista_nomes_alunos = carregar_nomes_alunos(lista_id_alunos)
    form_chamada = FormChamada()

    if form_chamada.validate_on_submit() and "botao_submit_chamada" in request.form:
        data_aula = datetime.strptime(form_chamada.data_atual.data, '%d/%m/%Y')
        presenca = request.form.getlist("aluno")
        lista_presente=[]
        lista_faltou = []

        for p in presenca:
            i = p.index('|')
            if "presente" in p:
                presente= p[:i]
                lista_presente.append(presente)
            elif "faltou" in p:
                faltou = p[:i]
                lista_faltou.append(faltou)
        
        presenca = ListaAulas(id_professor=current_user.id,
                              data_aula=data_aula,
                              presente=";".join(lista_presente),
                              faltou=";".join(lista_faltou))
        
        database.session.add(presenca)
        database.session.commit()

        flash('Chamada registrada com sucesso!', "alert-success")

    return render_template('pag_chamada.html',
                           nome_turma=nome_turma,
                           form_chamada=form_chamada,
                           lista_nomes_alunos=lista_nomes_alunos)


def carregar_aniversarios():
    professores = Professor.query.all()
    alunos = Aluno.query.all()
    adms = Usuario.query.all()

    lista_professores = [[a.nome_completo, datetime.strftime(a.data_nascimento, "%d/%m/%Y")] for a in professores]
    lista_alunos = [[a.nome_completo, datetime.strftime(a.data_nascimento, "%d/%m/%Y")] for a in alunos]
    lista_usuarios = [[a.username, datetime.strftime(a.data_nascimento, "%d/%m/%Y")] for a in adms]
    return lista_alunos, lista_professores, lista_usuarios


def carregar_nomes_alunos(lista_id_alunos):
    lista_nomes_alunos = []

    for id in lista_id_alunos:
        aluno = Aluno.query.filter_by(id=id).first_or_404()
        if aluno:
            lista_nomes_alunos.append([aluno.nome_completo,aluno.id])
    
    return lista_nomes_alunos


def carregar_nome_atividades():
    dict_ativ = {}
    atividades = Atividade.query.order_by(Atividade.atividade.asc()).all()
    for ativ in atividades:
        dict_ativ[ativ.id] = {"nome_atividade":ativ.atividade,
                              "dias_aula":ativ.dias_aula.replace(";",' - '),
                              "turmas":0,
                              "professores":[],
                              "alunos":0,
                              "n_professores":0}

    return dict_ativ


def carregar_turmas(dict_ativ):
    turmas = Turma.query.order_by(Turma.id_atividade.asc()).all()
    
    for ativ in dict_ativ:
        for id in turmas:
            if ativ == id.id_atividade:
                dict_ativ[ativ]['turmas'] += 1
                if type(id.id_aluno) == int and id.id_aluno !=0:
                    total_alunos =1
                else:
                    total_alunos = len(id.id_aluno) - id.id_aluno.count(';')
                dict_ativ[ativ]['alunos'] += total_alunos
                if not id.id_professor in dict_ativ[ativ]['professores']:
                    dict_ativ[ativ]['professores'].append(id.id_professor)
                    dict_ativ[ativ]['n_professores'] +=1
                

    return dict_ativ


def dias_cursos(form):
    lista_dias = []
    for campo in form:
        if "_feira" in campo.name or campo.name in ('sabado','domingo'):
            if campo.data:
                lista_dias.append(campo.label.text)
    return ";".join(lista_dias)


def carregar_atividades():
    atividades = Atividade.query.order_by(Atividade.id.asc())
    return atividades


def id_atividade(nome_atividade):
    atividade = Atividade.query.filter_by(atividade=nome_atividade).first()
    id = atividade.id
    return id


def carregar_id_professor(nome, data_nascimento):
    id_professor = Professor.query.filter_by(nome_completo=nome, data_nascimento=data_nascimento).first()
    if id_professor:
        id = id_professor.id
    else:
        id = None
    return id


def carregar_id_aluno(nome, data_nascimento):
    id_aluno = Aluno.query.filter_by(nome_completo=nome, data_nascimento=data_nascimento).first()
    if id_aluno:
        id = id_aluno.id
    else:
        id = None
    return id


def carregar_id_turma(nome):
    id_turma = Turma.query.filter_by(nome_turma=nome).first()

    if id_turma:
        id = id_turma.id
    else:
        id=None
    
    return id


@app.route('/area-academica/<nome_atividade>', methods=['GET','POST'])
def excluir_atividade(nome_atividade):
    id_ativ = id_atividade(nome_atividade=nome_atividade)

    try:
        excluir_atividade = Atividade.query.filter_by(id=id_ativ).first()
        excluir_turma = Turma.__table__.delete().where(Turma.id_atividade==id_ativ)
        
        database.session.delete(excluir_atividade)
        database.session.execute(excluir_turma)
        database.session.commit()
    except Exception as e:
        flash("Ocorreu um erro ao excluir a Atividade, recarregue a página")
        return redirect(url_for("area_academica"))

    flash(f'{nome_atividade} excluída!', "alert-success")
    return redirect(url_for("area_academica"))


@app.route('/area-academica/turmas/<atividade>/<nome_turma>', methods=['GET','POST'])
def excluir_turma(nome_turma,atividade):
    id_turma = carregar_id_turma(nome=nome_turma)
    atividade=atividade
    try:
        excluir_turma = Turma.__table__.delete().where(Turma.id==id_turma)
        database.session.execute(excluir_turma)
        database.session.commit()
    except Exception as e:
        flash("Ocorreu um erro ao excluir a Atividade, recarregue a página.")
        return redirect(url_for("exibir_turmas", nome=atividade))

    flash(f'{nome_turma} excluída com sucesso!', 'alert-success')

    return redirect(url_for("exibir_turmas", nome=atividade))


@app.route('/area-academica/turmas/chamada/excluir/<turma>/<nome_aluno>/<id_aluno>', methods=['GET','POST'])
def excluir_aluno(turma, nome_aluno,id_aluno):
    turma=turma
    try:
        excluir_aluno = Aluno.query.filter_by(id=id_aluno).first()
        database.session.delete(excluir_aluno)
    
        turma_aluno = Turma.query.filter_by(nome_turma=turma).first()
        ids = turma_aluno.id_aluno.split(";")
        excluir_id_aluno = [id for id in ids if id != str(id_aluno)]
        turma_aluno.id_aluno = ";".join(excluir_id_aluno)
        database.session.commit()

    except Exception as e:
        flash("Ocorreu um erro ao excluir Aluno, recarregue a página", 'alert-danger')
        return redirect(url_for("carregar_chamada", nome_turma=turma))

    flash(f"Aluno {nome_aluno} excluído com sucesso.", 'alert-success')
    return redirect(url_for("carregar_chamada", nome_turma=turma))
