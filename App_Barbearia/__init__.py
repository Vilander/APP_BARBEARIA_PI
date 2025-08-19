# App_Barbearia/__init__.py
import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail # Importar a classe Mail

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