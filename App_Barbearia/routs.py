# App_Barbearia/routs.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from App_Barbearia import database, bcrypt, mail, create_app
from App_Barbearia.forms import FormLogin, FormCriarConta, Form_Agendar, Form_EditarPerfil, Form_Botao, FormRecuperarSenha, FormRedefinirSenha, Form_GerenciarServicos, Form_RelatorioLucro
from App_Barbearia.decorators import admin_required
from App_Barbearia.models import Usuario, Post, Servico
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
from flask import render_template


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
    
    from App_Barbearia.models import Servico
    # Popula dinamicamente as opções de serviço do banco de dados
    servicos = Servico.query.all()
    
    # 🟢 CORREÇÃO AQUI: O primeiro elemento da tupla deve ser o ID (s.id) e não o nome.
    form_agendar.servico.choices = [(s.id, f"{s.nome} - R$ {s.valor}") for s in servicos]

    # Popula dinamicamente os horários (opcional, mas recomendado)
    lista_horas = [8, 9, 10, 11, 12, 14, 15, 16]
    form_agendar.hora.choices = [(f"{h}:00", f"{h}:00") for h in lista_horas]

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
            # 🟢 CORREÇÃO AQUI: Use o ID para buscar o serviço
            servico_escolhido = Servico.query.get(form_agendar.servico.data)
            valor_servico = servico_escolhido.valor if servico_escolhido else 0.0

            # 🟢 CORREÇÃO AQUI: Atribua o nome do serviço para o campo 'servico' do post
            nome_servico = servico_escolhido.nome if servico_escolhido else ""

            post = Post(
                username=form_agendar.username.data,
                cell=form_agendar.cell.data,
                servico=nome_servico, # Atribui o nome do serviço ao post
                valor=valor_servico, # Atribui o valor do serviço ao post
                data=form_agendar.datar.data,
                hora=form_agendar.hora.data,
                id_usuario=current_user.id,
            )
            database.session.add(post)
            database.session.commit()
            flash("Agendado com Sucesso", "alert-success")
            
            # 🟢 Chamada para a função de envio de e-mail.
            enviar_email_confirmacao(current_user.email, post)
            
            return redirect(url_for("main.agendar"))
    else:
        print(form_agendar.errors)

    return render_template("agendar.html", 
                           form_agendar=form_agendar, 
                           data_sugerida=data_sugerida, 
                           servicos=servicos)


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

#  Rota para gerenciar os serviços (CRUD)
@main.route("/gerenciar_servicos", methods=["GET", "POST"])
@login_required
@admin_required
def gerenciar_servicos():
    form_servico = Form_GerenciarServicos()
    servicos = Servico.query.order_by(Servico.id).all()
    
    if form_servico.validate_on_submit():
        nome = form_servico.nome_servico.data
        valor = form_servico.valor_servico.data
        
        servico_existente = Servico.query.filter_by(nome=nome).first()
        if servico_existente:
            # Atualiza o serviço existente
            servico_existente.valor = valor
            flash(f"Serviço '{nome}' atualizado com sucesso!", "alert-success")
        else:
            # Adiciona um novo serviço
            novo_servico = Servico(nome=nome, valor=valor)
            database.session.add(novo_servico)
            flash(f"Serviço '{nome}' adicionado com sucesso!", "alert-success")
        
        database.session.commit()
        return redirect(url_for("main.gerenciar_servicos"))
        
    return render_template("gerenciar_servicos.html", form_servico=form_servico, servicos=servicos)

# 🟢 Rota para excluir um serviço
@main.route("/excluir_servico/<int:id>", methods=["POST"])
@login_required
@admin_required
def excluir_servico(id):
    servico = Servico.query.get_or_404(id)
    database.session.delete(servico)
    database.session.commit()
    flash("Serviço excluído com sucesso!", "alert-success")
    return redirect(url_for("main.gerenciar_servicos"))

#novo relatório

@main.route("/relatorio", methods=["GET", "POST"])
@login_required
@admin_required
def relatorio():
    from collections import Counter
    # 🔹 Obter as datas do filtro
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    # 🔹 Define um período padrão se as datas não foram fornecidas
    if not data_inicio or not data_fim:
        hoje = date.today()
        # Define a data de início como 30 dias atrás
        data_inicio = (hoje - timedelta(days=30)).strftime('%Y-%m-%d')
        # Define a data de fim como hoje
        data_fim = hoje.strftime('%Y-%m-%d')

    # Converte as strings de data para objetos date
    data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
    data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()

    # 🔹 Consulta para todos os agendamentos no período
    agendamentos = Post.query.filter(Post.data.between(data_inicio_obj, data_fim_obj)).all()

    # Lógica para o primeiro gráfico (Agendamentos por Dia)
    contagem_por_dia = Counter([ag.data.strftime("%Y-%m-%d") for ag in agendamentos])
    # Cria uma lista de todas as datas no período para garantir a ordem e preencher dias sem agendamentos
    all_dates = [data_inicio_obj + timedelta(days=x) for x in range((data_fim_obj - data_inicio_obj).days + 1)]
    dados_agendamentos = {d.strftime("%d/%m/%Y"): contagem_por_dia.get(d.strftime("%Y-%m-%d"), 0) for d in all_dates}


    # Lógica para o segundo gráfico (Análise por Serviço)
    contagem_servicos = database.session.query(Post.servico, func.count(Post.id)).filter(
        Post.data.between(data_inicio_obj, data_fim_obj)
    ).group_by(Post.servico).all()
    dados_servicos = dict(contagem_servicos)

    # Lógica para o terceiro gráfico (Lucro Diário)
    # 🆕 Consulta o banco de dados para obter a soma do valor por dia
    lucro_por_dia = database.session.query(Post.data, func.sum(Post.valor)).filter(
        Post.data.between(data_inicio_obj, data_fim_obj)
    ).group_by(Post.data).order_by(Post.data).all()
    
    # 🆕 Prepara os dados para o gráfico de linha, preenchendo os dias sem lucro com zero
    dados_lucro_diario = {d.strftime("%d/%m/%Y"): 0.0 for d in all_dates}
    for data, valor in lucro_por_dia:
        dados_lucro_diario[data.strftime("%d/%m/%Y")] = float(valor)

    # Calcula o lucro total para o período filtrado
    lucro_total = sum(dados_lucro_diario.values())
    total_valor_formatado = f"{lucro_total:,.2f}".replace('.', ',')

    return render_template(
        "relatorio.html",
        dados_agendamentos=dados_agendamentos,
        dados_servicos=dados_servicos,
        dados_lucro_diario=dados_lucro_diario,
        total_valor_formatado=total_valor_formatado,
        data_inicio=data_inicio,
        data_fim=data_fim
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

# E adicione este código ao final do seu arquivo routs.py
@main.app_errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template('404.html'), 404