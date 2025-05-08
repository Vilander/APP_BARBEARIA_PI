from flask import render_template, redirect, url_for, flash, request, abort
from App_Barbearia import app, database, bcrypt
from App_Barbearia.forms import FormLogin, FormCriarConta, Form_EditarPerfil, Form_Agendar, Form_Botao
from App_Barbearia.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image
from sqlalchemy import and_
from datetime import date, datetime, timedelta
import pywhatkit as kit

@app.route('/')
def home():
    return render_template('home.html', ano=datetime.now().year)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    form_criarconta = FormCriarConta()

    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f'Login Feito com Sucesso no E-Mail: {form_login.email.data}', "alert alert-success")
            par_next = request.args.get('next')
            return redirect(par_next) if par_next else redirect(url_for('home'))
        else:
            flash(f'Falha no Login, Verifique Senha ou E-Mail', 'alert-danger')

    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        senha_crypt = bcrypt.generate_password_hash(form_criarconta.senha.data)
        usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email.data, senha=senha_crypt)
        database.session.add(usuario)
        database.session.commit()
        flash(f'Conta Criada com Sucesso para o E-Mail: {form_criarconta.email.data}', 'alert success')
        return redirect(url_for('home'))
    return render_template('login.html', form_login=form_login, form_criarconta=form_criarconta)

@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash(f'Logout Feito com sucesso', "alert-success")
    return render_template('home.html', ano=datetime.now().year)

@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('perfil.html', foto_perfil=foto_perfil)

def enviar_mensagem_whatsapp(numero_destino):
    numero_destino = "+55" + numero_destino
    agora = datetime.now()
    hora = agora.hour
    minutos = agora.minute + 1
    kit.sendwhatmsg_instantly(numero_destino, "Seu agendamento foi confirmado!", wait_time=10)

@app.route('/agendar', methods=["GET", "POST"])
@login_required
def agendar():
    form_agendar = Form_Agendar()

    if form_agendar.validate_on_submit():
        agendamento_existente = Post.query.filter(and_(Post.data == form_agendar.datar.data, Post.hora == form_agendar.hora.data)).first()
        if agendamento_existente:
            flash('Já existe um agendamento para essa data e hora.', 'alert-danger')
        else:
            post = Post(username=form_agendar.username.data, cell=form_agendar.cell.data,
                        servico=form_agendar.servico.data,
                        data=form_agendar.datar.data, hora=form_agendar.hora.data, id_usuario=current_user.id)
            database.session.add(post)
            database.session.commit()
            flash('Agendado com Sucesso', 'alert-success')
            enviar_mensagem_whatsapp("55" + form_agendar.cell.data)
            return render_template('agendar.html', form_agendar=form_agendar)
    else:
        print(form_agendar.errors)

    return render_template('agendar.html', form_agendar=form_agendar)

@app.route('/usuarios')
@login_required
def usuarios():
    return render_template('usuarios.html')

def salvar_img(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)
    tamanho = (400, 400)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo

@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form_editar = Form_EditarPerfil()
    if form_editar.validate_on_submit():
        current_user.email = form_editar.email.data
        current_user.username = form_editar.username.data
        if form_editar.foto_perfil.data:
            nome_imagem = salvar_img(form_editar.foto_perfil.data)
            current_user.foto_perfil = nome_imagem
        database.session.commit()
        flash(f'Atualizado com Sucesso para o E-Mail: {form_editar.email.data}', 'alert success')
        return redirect(url_for('perfil'))
    elif request.method == "GET":
        form_editar.email.data = current_user.email
        form_editar.username.data = current_user.username
    
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('editar_perfil.html', foto_perfil=foto_perfil, form_editar=form_editar)

@app.route('/agenda_data', methods=["GET", "POST"])
@login_required
def agenda_data():
    form_botao = Form_Botao()
    lista_agendamentos_data = None

    if form_botao.validate_on_submit():
        data_pesquisa = form_botao.data_pesquisa.data
        agendamentos_data = Post.query.filter(Post.data == data_pesquisa).all()
        lista_agendamentos_data = [agendamento for agendamento in agendamentos_data]

    return render_template('agenda_data.html', lista_agendamentos_data=lista_agendamentos_data, form_botao=form_botao)

@app.route('/relatorio', methods=['GET'])
@login_required
def relatorio():
    from collections import Counter

    hoje = date.today()
    sete_dias_atras = hoje - timedelta(days=6)

    inicio_str = request.args.get('inicio') or sete_dias_atras.strftime('%Y-%m-%d')
    fim_str = request.args.get('fim') or hoje.strftime('%Y-%m-%d')

    try:
        data_inicio = datetime.strptime(inicio_str, '%Y-%m-%d').date()
        data_fim = datetime.strptime(fim_str, '%Y-%m-%d').date()
    except:
        flash('Erro no formato da data.', 'alert-danger')
        data_inicio = sete_dias_atras
        data_fim = hoje

    agendamentos = Post.query.filter(Post.data.between(data_inicio, data_fim)).all()
    contagem_por_dia = Counter([ag.data.strftime('%d/%m/%Y') for ag in agendamentos])

    datas_ordenadas = sorted(contagem_por_dia.items(), key=lambda x: datetime.strptime(x[0], '%d/%m/%Y'))
    labels = [item[0] for item in datas_ordenadas]
    valores = [item[1] for item in datas_ordenadas]

    return render_template('relatorio.html', labels=labels, valores=valores, inicio=inicio_str, fim=fim_str)

@app.route('/agenda_hoje')
@login_required
def agenda_hoje():
    agendamentos_dia = Post.query.filter_by(data=date.today()).order_by(Post.hora).all()
    return render_template('agenda_hoje.html', agendamentos_dia=agendamentos_dia)

@app.route('/excluir_agendamento/<int:id>', methods=['POST'])
@login_required
def excluir_agendamento(id):
    agendamento = Post.query.get_or_404(id)
    database.session.delete(agendamento)
    database.session.commit()
    flash("Agendamento excluído com sucesso!", "alert-success")
    return redirect(url_for('agenda_hoje'))

