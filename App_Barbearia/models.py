# App_Barbearia/models.py

from App_Barbearia import database, login_manager
from datetime import datetime, date
from flask_login import UserMixin
# IMPORTAÇÃO NOVA NECESSÁRIA
from sqlalchemy import UniqueConstraint

@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))

class Usuario(database.Model, UserMixin):
    __tablename__ = 'usuario' # É uma boa prática definir o nome da tabela explicitamente

    id = database.Column(database.Integer, primary_key=True)
    # REMOVEMOS O unique=True DAQUI
    username = database.Column(database.String(30), nullable=False)
    # E DAQUI TAMBÉM
    email = database.Column(database.String(120), nullable=False)
    foto_perfil = database.Column(database.String(20), nullable=False, server_default='default.jpg')
    senha = database.Column(database.String(60), nullable=False)
    role = database.Column(database.String(20), nullable=False, default='cliente')
    
    posts = database.relationship('Post', backref='autor', lazy=True)

    # ADICIONAMOS AS RESTRIÇÕES NOMEADAS AQUI
    __table_args__ = (
        UniqueConstraint('username', name='uq_usuario_username'),
        UniqueConstraint('email', name='uq_usuario_email'),
    )

    def __repr__(self):
        return f"Usuario('{self.username}', '{self.email}')"

# A classe Post continua igual
class Post(database.Model):
    __tablename__ = 'post'

    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False)
    cell = database.Column(database.String, nullable=False)
    servico = database.Column(database.String, nullable=False)
    hora = database.Column(database.String, nullable=False)
    data = database.Column(database.Date, nullable=False)
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)