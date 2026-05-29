from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from site_verbo_amar.models import Usuario
from flask_login import current_user

class FormCriarConta(FlaskForm):
    username = StringField("Nome do Usuário", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha:", validators=[DataRequired(), Length(6, 20)])
    confirmacao_senha = PasswordField("Confirmação da Senha:", validators=[DataRequired(), EqualTo('senha')])

    botao_submit_criarconta = SubmitField('Criar Conta')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('E-mail já cadastrado. Cadastre-se com outro e-mail ou faça login para continuar.')

class FormLogin(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6,20)])
    lembrar_dados = BooleanField('Lembrar Dados')
    botao_submit_login = SubmitField('Fazer Login')