# forms.py

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from App_Barbearia.models import Usuario, Post
from flask_login import current_user
from datetime import date, datetime
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired

# 🟢 Novo formulário para gerenciar serviços
class Form_GerenciarServicos(FlaskForm):
    nome_servico = StringField('Nome do Serviço', validators=[DataRequired()])
    valor_servico = IntegerField('Valor do Serviço (R$)', validators=[DataRequired()])
    botao_adicionar = SubmitField('Adicionar/Atualizar')

# 🟢 Novo formulário para o relatório de lucro (consistente com o filtro de datas)
class Form_RelatorioLucro(FlaskForm):
    data_inicio = DateField('Data de Início', format='%Y-%m-%d', validators=[DataRequired()])
    data_fim = DateField('Data de Fim', format='%Y-%m-%d', validators=[DataRequired()])
    botao_submit = SubmitField('Filtrar')

class FormCriarConta(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    confirmacao_senha = PasswordField('Confirmação da Senha', validators=[DataRequired(), EqualTo('senha')])
    botao_submit_criarconta = SubmitField('Criar Conta')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('Email já cadastrado. Faça login para continuar.')

class FormLogin(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    lembrar_dados = BooleanField('Lembrar Dados de Acesso')
    botao_submit_login = SubmitField('Fazer Login')

# 🟢 Mantido o seu validador personalizado 'DataFutura'
class DataFutura(object):
    def __init__(self, message=None):
        if not message:
            message = 'A data não pode ser anterior à data atual.'
        self.message = message

    def __call__(self, form, field):
        hoje = datetime.today().date()
        if field.data < hoje:
            raise ValidationError(self.message)

class Form_Agendar(FlaskForm):
    # 🟢 As opções de serviço serão preenchidas dinamicamente na rota
    username = StringField('Nome', validators=[DataRequired()])
    cell = StringField("DD + Celular", validators=[DataRequired(), Length(11, 11)])
    servico = SelectField('Serviço', validators=[DataRequired()])
    datar = DateField('Data', validators=[DataRequired(), DataFutura()])
    hora = SelectField('Hora', validators=[DataRequired()])
    botao_submit_agendar = SubmitField('Agendar')

    # Você pode manter a lista de horas aqui ou preencher dinamicamente na rota
    # Se quiser manter aqui, adicione a lógica para preencher o campo 'hora'
    # Ex: self.hora.choices = [('8:00', '8:00'), ('9:00', '9:00'), ...]

class Form_EditarPerfil(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    foto_perfil = FileField('Atualizar Foto', validators=[FileAllowed(['jpg', 'png'])])
    botao_submit_editarperfil = SubmitField('Confirmar Edição')

    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError('Já existe um usuário com esse e-mail. Cadastre outro e-mail ou faça Login')

class Form_Botao(FlaskForm):
    data_pesquisa = DateField('Data de Pesquisa')
    botao_submit_agenda_data = SubmitField('Pesquisar Agendamentos')

class FormRecuperarSenha(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar')

class FormRedefinirSenha(FlaskForm):
    senha = PasswordField('Nova Senha', validators=[DataRequired()])
    confirmacao_senha = PasswordField('Confirmar Nova Senha', validators=[DataRequired(), EqualTo('senha', message='As senhas devem ser iguais')])
    submit = SubmitField('Redefinir Senha')

class Form_GerenciarServicos(FlaskForm):
    nome_servico = StringField('Nome do Serviço', validators=[DataRequired()])
    valor_servico = FloatField('Valor do Serviço', validators=[DataRequired()])
    # 🟢 NOVO: Adicionando o campo de envio
    submit = SubmitField('Adicionar/Atualizar Serviço')