from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField,SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from site_verbo_amar.models import Usuario, Aluno, Atividade
from flask_login import current_user
from wtforms.fields import DateField
from datetime import datetime

class FormCriarConta(FlaskForm):
    username = StringField("Nome do Usuário", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha:", validators=[DataRequired(), Length(6, 20)])
    confirmacao_senha = PasswordField("Confirmação da Senha:", validators=[DataRequired(), EqualTo('senha')])
    sexo = SelectField("Sexo", choices=[("",'Selecione...'), ('M',"M"),('F',"F")],validators=[DataRequired()])
    adm = BooleanField('Adm')
    professor = BooleanField('Professor')
    data_aniversario = StringField('Data Aniversário',
                                   validators=[
                                       DataRequired(),
                                       Regexp(r'^\d{2}/\d{2}/\d{4}',message="Use o formato DD/MM/AAAA")
                                   ],
                                   render_kw={'placeholder':'DD/MM/AAAA'})

    botao_submit_criarconta = SubmitField('Criar Conta')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('E-mail já cadastrado. Cadastre-se com outro e-mail ou faça login para continuar.')
        
    def validate_data_aniversario(self,field):
        try:
            datetime.strptime(field.data,"%d/%m/%Y")
        except ValueError:
            raise ValidationError('Data inválida. Use o formato DD/MM/AAAA')
        

class FormCadAtividade(FlaskForm):
    atividade = StringField("Nome da Atividade:", validators=[DataRequired()])
    segunda_feira = BooleanField("Segunda-Feira")
    terca_feira = BooleanField("Terça-Feira")
    quarta_feira = BooleanField("Quarta-Feira")
    quinta_feira = BooleanField("Quinta-Feira")
    sexta_feira = BooleanField("Sexta-Feira")
    sabado = BooleanField("Sábado")
    domingo = BooleanField("Domingo")
    botao_submit_ativ = SubmitField('Cadastrar Atividade')

    def validate_atividade(self, atividade):
        ativ = Atividade.query.filter_by(atividade=atividade.data).first()
        if ativ:
            raise ValidationError('E-mail já cadastrado. Cadastre-se com outro e-mail ou faça login para continuar.')


class FormTurma(FlaskForm):
    nome_turma = StringField("Nome da Turma:", validators=[DataRequired()])
    atividade = StringField("Atividade:", validators=[DataRequired()])
    botao_submit_turma = SubmitField("Cadastrar Turma")


class FormLogin(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6,20)])
    lembrar_dados = BooleanField('Lembrar Dados')
    botao_submit_login = SubmitField('Fazer Login')


class FormChamada(FlaskForm):
    data_atual = StringField("Data da Aula: ", validators=[DataRequired(),
                                                           Regexp(r'^\d{2}/\d{2}/\d{4}',
                                                                  message="Use o formato DD/MM/AAAA")],
                                                                  render_kw={"placeholder":"DD/MM/AAAA"},
                                                            default=lambda: datetime.now().strftime("%d/%m/%Y"))
    alunos = BooleanField("Alunos:",)

    botao_submit_chamada = SubmitField("Confirmar Chamada")
    