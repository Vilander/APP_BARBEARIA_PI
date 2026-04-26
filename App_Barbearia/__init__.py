# App_Barbearia/__init__.py
import os
import threading
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail # Importar a classe Mail
import pywhatkit as kit

# Carrega variáveis de ambiente
load_dotenv()

# Instâncias das extensões
database = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'alert-info'
migrate = Migrate()
mail = Mail() # Inicializar a instância da extensão

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Configuração do app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'chave-secreta-teste'

    # Configurações do Flask-Mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = ('Barbearia CorteFácil', os.environ.get('MAIL_USERNAME'))

    # Garante que a pasta instance exista
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    # Caminho absoluto do banco de dados
    db_path = os.path.join(app.instance_path, 'barbearia.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar extensões
    database.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, database)
    mail.init_app(app) # Inicializar a extensão 'mail'

    # Registrar rotas
    from .routs import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Cria tabelas automaticamente se ainda não existirem (não recomendado com Flask-Migrate,
    # use `flask db upgrade` para migrações)
    # with app.app_context():
    #     database.create_all()

    return app


def formatar_numero_whatsapp(cell):
    if not cell:
        return None
    numeros = ''.join(filter(str.isdigit, cell))
    if numeros.startswith('55') and len(numeros) == 13:
        return f'+{numeros}'
    if len(numeros) == 11:
        return f'+55{numeros}'
    if len(numeros) >= 11:
        return f'+{numeros}'
    return None


def enviar_whatsapp_lembrete(agendamento, tempo_antes):
    """Envia lembrete de agendamento via WhatsApp com informação do tempo.
    tempo_antes: string com a quantidade de tempo (ex: '24 horas', '2 horas', '1 hora', '30 minutos')
    """
    numero = formatar_numero_whatsapp(agendamento.cell)
    if not numero:
        print(f"Número inválido para lembrete de agendamento {agendamento.id}: {agendamento.cell}")
        return False

    mensagem = (
        f"Olá {agendamento.username}!\n"
        f"Lembrando que você tem um atendimento na Barbearia CorteFácil em {tempo_antes}:\n"
        f"Serviço: {agendamento.servico}\n"
        f"Data: {agendamento.data.strftime('%d/%m/%Y')}\n"
        f"Hora: {agendamento.hora}\n"
        f"Estamos te aguardando!"
    )

    try:
        kit.sendwhatmsg_instantly(numero, mensagem, wait_time=20, tab_close=True, close_time=5)
        print(f"Lembrete ({tempo_antes}) enviado para {numero} referente ao agendamento {agendamento.id}")
        return True
    except Exception as e:
        print(f"Falha ao enviar lembrete para {numero}: {e}")
        return False


def verificar_lembretes():
    from App_Barbearia.models import Post

    agora = datetime.now()
    
    # Define os 4 horários de lembrete
    lembretes = [
        (timedelta(days=1), 'lembrete_24h_enviado', '24 horas'),
        (timedelta(hours=2), 'lembrete_2h_enviado', '2 horas'),
        (timedelta(hours=1), 'lembrete_1h_enviado', '1 hora'),
        (timedelta(minutes=30), 'lembrete_30min_enviado', '30 minutos'),
    ]
    
    # Busca agendamentos de hoje e amanhã
    agora_data = agora.date()
    amanha_data = agora_data + timedelta(days=1)
    
    agendamentos = Post.query.filter(
        (Post.data == agora_data) | (Post.data == amanha_data)
    ).all()
    
    for agendamento in agendamentos:
        try:
            horario_agendamento = datetime.strptime(agendamento.hora, '%H:%M').time()
        except ValueError:
            continue
        
        data_horario = datetime.combine(agendamento.data, horario_agendamento)
        tempo_falta = data_horario - agora
        
        # Verifica cada lembrete
        for intervalo, campo_enviado, texto_tempo in lembretes:
            # Se o campo já foi enviado, pula
            if getattr(agendamento, campo_enviado):
                continue
            
            # Verifica se está no horário correto (5 minutos de margem)
            margem = timedelta(minutes=5)
            if -margem <= (tempo_falta - intervalo) <= margem:
                if enviar_whatsapp_lembrete(agendamento, texto_tempo):
                    setattr(agendamento, campo_enviado, True)
    
    database.session.commit()


def iniciar_servico_lembretes(app):
    def worker():
        with app.app_context():
            while True:
                try:
                    verificar_lembretes()
                except Exception as e:
                    print(f"Erro no serviço de lembretes: {e}")
                time.sleep(60)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
