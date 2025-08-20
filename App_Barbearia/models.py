# App_Barbearia/models.py

from App_Barbearia import database, login_manager
from datetime import datetime, date
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from datetime import datetime

@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))

class Usuario(database.Model, UserMixin):
    __tablename__ = 'usuario'

    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(30), nullable=False)
    email = database.Column(database.String(120), nullable=False)
    foto_perfil = database.Column(database.String(20), nullable=False, server_default='default.jpg')
    senha = database.Column(database.String(60), nullable=False)
    role = database.Column(database.String(20), nullable=False, default='cliente')

    posts = database.relationship('Post', backref='autor', lazy=True)

    __table_args__ = (
        UniqueConstraint('username', name='uq_usuario_username'),
        UniqueConstraint('email', name='uq_usuario_email'),
    )

    def __repr__(self):
        return f"Usuario('{self.username}', '{self.email}')"

    def get_reset_token(self, expires_sec=1800):
        """Gera um token de redefinição de senha."""
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        """Verifica se o token de redefinição é válido."""
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            # O token contém o user_id e a data de expiração
            user_id = s.loads(token, max_age=1800)['user_id']
        except:
            return None
        return Usuario.query.get(user_id)

# 🟢 Novo modelo para armazenar os serviços e seus valores.
class Servico(database.Model):
    __tablename__ = 'servico'
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String(100), nullable=False, unique=True)
    valor = database.Column(database.Float, nullable=False)
    
    def __repr__(self):
        return f"Servico('{self.nome}', R${self.valor}')"

class Post(database.Model):
    __tablename__ = 'post'

    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False)
    cell = database.Column(database.String, nullable=False)
    servico = database.Column(database.String, nullable=False)
    # 🟢 Adicionado o campo 'valor' para registrar o preço no momento do agendamento
    valor = database.Column(database.Float, nullable=False, default=0.0)
    hora = database.Column(database.String, nullable=False)
    data = database.Column(database.Date, nullable=False)
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.username}', '{self.servico}', '{self.data}')"

