# App_Barbearia/routs.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from App_Barbearia import database, bcrypt, mail, create_app
from App_Barbearia.forms import FormLogin, FormCriarConta, Form_Agendar, Form_EditarPerfil, Form_Botao, FormRecuperarSenha, FormRedefinirSenha
from App_Barbearia.decorators import admin_required
from App_Barbearia.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image
from sqlalchemy import and_, func
from datetime import date, datetime, timedelta
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
import pywhatkit as kit
from .ml_model import preparar_dados_para_ml, treinar_modelo_ml, prever_proxima_visita, segmentar_clientes_kmeans

# Instância global do modelo de ML para ser acessível nas rotas
modelo_ml_global = None

# 🔹 Agora é um Blueprint (não mais app direto)
main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("home.html", ano=datetime.now().year)

@main.route("/login", methods=["GET", "POST"])
def login():
    form_login = FormLogin()
    form_criarconta = FormCriarConta()

    if form_login.validate_on_submit() and "botao_submit_login" in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f"Login Feito com Sucesso no E-Mail: {form_login.email.data}", "alert alert-success")
            par_next = request.args.get("next")
            return redirect(par_next) if par_next else redirect(url_for("main.home"))
        else:
            flash("Falha no Login, Verifique Senha ou E-Mail", "alert-danger")

    if form_criarconta.validate_on_submit() and "botao_submit_criarconta" in request.form:
        senha_crypt = bcrypt.generate_password_hash(form_criarconta.senha.data)
        usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email.data, senha=senha_crypt)
        database.session.add(usuario)
        database.session.commit()
        flash(f"Conta Criada com Sucesso para o E-Mail: {form_criarconta.email.data}", "alert success")
        return redirect(url_for("main.home"))
    return render_template("login.html", form_login=form_login, form_criarconta=form_criarconta)

@main.route("/sair")
@login_required
def sair():
    logout_user()
    flash("Logout Feito com sucesso", "alert-success")
    return render_template("home.html", ano=datetime.now().year)

@main.route("/perfil")
@login_required
def perfil():
    foto_perfil = url_for("static", filename=f"fotos_perfil/{current_user.foto_perfil}")
    return render_template("perfil.html", foto_perfil=foto_perfil)

def enviar_email_confirmacao(email_destino, agendamento):
    msg = Message(
        subject="Confirmação de Agendamento - Barbearia CorteFácil",
        recipients=[email_destino],
        body=f"""Olá, {agendamento.username}!
        
Seu agendamento foi confirmado com sucesso.

Detalhes do Agendamento:
Serviço: {agendamento.servico}
Data: {agendamento.data.strftime('%d/%m/%Y')}
Hora: {agendamento.hora}

Se precisar reagendar, entre em contato conosco.

Atenciosamente,
Equipe CorteFácil
"""
    )
    try:
        mail.send(msg)
        print(f"Email de confirmação enviado com sucesso para {email_destino}")
    except Exception as e:
        print(f"Falha ao enviar e-mail de confirmação: {e}")

# Função para salvar a imagem
def salvar_img(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho_completo = os.path.join(os.getcwd(), "App_Barbearia", "static", "fotos_perfil", nome_arquivo)
    tamanho = (400, 400)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo

@main.route("/perfil/editar", methods=["GET", "POST"])
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
        flash(f"Atualizado com Sucesso para o E-Mail: {form_editar.email.data}", "alert success")
        return redirect(url_for("main.perfil"))
    elif request.method == "GET":
        form_editar.email.data = current_user.email
        form_editar.username.data = current_user.username

    foto_perfil = url_for("static", filename=f"fotos_perfil/{current_user.foto_perfil}")
    return render_template("editar_perfil.html", foto_perfil=foto_perfil, form_editar=form_editar)


@main.route("/agendar", methods=["GET", "POST"])
@login_required
def agendar():
    form_agendar = Form_Agendar()
    
    # Adiciona a previsão na página de agendamento se o modelo estiver disponível
    data_sugerida = None
    if modelo_ml_global:
        try:
            data_sugerida = prever_proxima_visita(modelo_ml_global, current_user.id)
        except Exception as e:
            print(f"Erro ao prever a data para o usuário {current_user.id}: {e}")
            data_sugerida = None
    
    if form_agendar.validate_on_submit():
        agendamento_existente = Post.query.filter(
            and_(Post.data == form_agendar.datar.data, Post.hora == form_agendar.hora.data)
        ).first()
        if agendamento_existente:
            flash("Já existe um agendamento para essa data e hora.", "alert-danger")
        else:
            post = Post(
                username=form_agendar.username.data,
                cell=form_agendar.cell.data,
                servico=form_agendar.servico.data,
                data=form_agendar.datar.data,
                hora=form_agendar.hora.data,
                id_usuario=current_user.id,
            )
            database.session.add(post)
            database.session.commit()
            flash("Agendado com Sucesso", "alert-success")
            
            # 🟢 Chamada para a função de envio de e-mail.
            enviar_email_confirmacao(current_user.email, post)
            
            # 🟢 Sugestão: Você pode redirecionar para uma página de sucesso
            # return redirect(url_for('main.alguma_pagina_de_sucesso'))

            return render_template("agendar.html", form_agendar=form_agendar)
    else:
        print(form_agendar.errors)

    return render_template("agendar.html", form_agendar=form_agendar, data_sugerida=data_sugerida)


@main.route("/agenda_data", methods=["GET", "POST"])
@login_required
@admin_required
def agenda_data():
    form_botao = Form_Botao()
    lista_agendamentos_data = None

    if form_botao.validate_on_submit():
        data_pesquisa = form_botao.data_pesquisa.data
        agendamentos_data = Post.query.filter(Post.data == data_pesquisa).all()
        lista_agendamentos_data = [agendamento for agendamento in agendamentos_data]

    return render_template("agenda_data.html", lista_agendamentos_data=lista_agendamentos_data, form_botao=form_botao)


#novo relatório

@main.route("/relatorio", methods=["GET"])
@login_required
@admin_required
def relatorio():
    hoje = date.today()
    sete_dias_atras = hoje - timedelta(days=7)
    
    # Obtém as datas do filtro ou usa o período padrão
    inicio_str = request.args.get("inicio") or sete_dias_atras.strftime("%Y-%m-%d")
    fim_str = request.args.get("fim") or hoje.strftime("%Y-%m-%d")

    try:
        data_inicio = datetime.strptime(inicio_str, "%Y-%m-%d").date()
        data_fim = datetime.strptime(fim_str, "%Y-%m-%d").date()
    except:
        flash("Erro no formato da data.", "alert-danger")
        data_inicio = sete_dias_atras
        data_fim = hoje

    # Lógica para o primeiro gráfico (Agendamentos por Dia)
    agendamentos_por_dia = Post.query.filter(Post.data.between(data_inicio, data_fim)).all()
    from collections import Counter
    contagem_por_dia = Counter([ag.data.strftime("%d/%m/%Y") for ag in agendamentos_por_dia])
    datas_ordenadas = sorted(contagem_por_dia.items(), key=lambda x: datetime.strptime(x[0], "%d/%m/%Y"))
    labels = [item[0] for item in datas_ordenadas]
    valores = [item[1] for item in datas_ordenadas]

    # 🆕 Lógica para o segundo gráfico (Análise por Serviço)
    # 🔹 Consulta o banco de dados para obter a contagem de agendamentos por tipo de serviço
    contagem_servicos = database.session.query(Post.servico, func.count(Post.id)).filter(
        Post.data.between(data_inicio, data_fim)
    ).group_by(Post.servico).all()

    # 🔹 Prepara os dados para o gráfico de donut
    service_labels = [item[0] for item in contagem_servicos]
    service_counts = [item[1] for item in contagem_servicos]

    return render_template(
        "relatorio.html",
        labels=labels,
        valores=valores,
        service_labels=service_labels, # Envia os rótulos de serviço para o template
        service_counts=service_counts, # Envia as contagens de serviço para o template
        inicio=inicio_str,
        fim=fim_str
    )

@main.route("/segmentacao", methods=["GET"])
@login_required
@admin_required
def segmentacao():
    """Rota para exibir a segmentação de clientes."""
    df_segmentos = segmentar_clientes_kmeans()
    
    if not df_segmentos.empty:
        # Converte o DataFrame para um formato de dicionário para o Jinja
        segmentos = df_segmentos.to_dict('records')
        return render_template("segmentacao.html", segmentos=segmentos)
    else:
        flash("Não há dados suficientes para segmentar os clientes.", "alert-info")
        return redirect(url_for("main.home"))

@main.route("/agenda_hoje")
@login_required
@admin_required
def agenda_hoje():
    agendamentos_dia = Post.query.filter_by(data=date.today()).order_by(Post.hora).all()
    return render_template("agenda_hoje.html", agendamentos_dia=agendamentos_dia)

@main.route("/excluir_agendamento/<int:id>", methods=["POST"])
@login_required
@admin_required
def excluir_agendamento(id):
    agendamento = Post.query.get_or_404(id)
    database.session.delete(agendamento)
    database.session.commit()
    flash("Agendamento excluído com sucesso!", "alert-success")
    return redirect(url_for("main.agenda_hoje"))

#redefinir senha

def enviar_email_recuperacao(usuario):
    token = usuario.get_reset_token()
    msg = Message('Recuperação de Senha',
                  sender='noreply@barbeariacortefacil.com',
                  recipients=[usuario.email])
    msg.body = f'''Para redefinir sua senha, visite o seguinte link:
{url_for('main.redefinir_senha', token=token, _external=True)}
Se você não solicitou esta redefinição, simplesmente ignore este e-mail e nenhuma alteração será feita na sua senha.
'''
    mail.send(msg)

@main.route("/recuperar_senha", methods=["GET", "POST"])
def recuperar_senha():
    form_recuperar = FormRecuperarSenha()
    if form_recuperar.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_recuperar.email.data).first()
        if usuario:
            enviar_email_recuperacao(usuario)
            flash("Um e-mail de recuperação de senha foi enviado.", "alert-success")
            return redirect(url_for("main.login"))
        else:
            flash("E-mail não encontrado.", "alert-danger")
    return render_template("recuperar_senha.html", form_recuperar=form_recuperar)

@main.route("/redefinir_senha/<token>", methods=["GET", "POST"])
def redefinir_senha(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

@main.route("/usuarios")
@login_required
def usuarios():
    return render_template("usuarios.html")

@main.route("/servicos")
def servicos():
    return render_template("servicos.html")
