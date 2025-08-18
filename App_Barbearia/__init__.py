# App_Barbearia/__init__.py
import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

# Carrega variáveis de ambiente
load_dotenv()

# Extensões
database = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'alert-info'
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Configuração do app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'chave-secreta-teste'

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

    # Registrar rotas
    from .routs import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # **Cria tabelas automaticamente se ainda não existirem**
    with app.app_context():
        database.create_all()

    return app
