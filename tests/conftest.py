# tests/conftest.py
import pytest
import sys
import os

# Garante que a raiz do projeto está no path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from App_Barbearia import create_app, database

@pytest.fixture(scope="module")
def app():
    """Cria uma instância do app para testes"""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # banco em memória para os testes
        "WTF_CSRF_ENABLED": False  # desabilita CSRF para facilitar POST nos testes
    })

    with app.app_context():
        database.create_all()  # cria as tabelas no banco de testes
        yield app
        database.drop_all()  # limpa o banco após os testes

@pytest.fixture()
def client(app):
    """Fornece um cliente de teste para requisições HTTP"""
    return app.test_client()

@pytest.fixture()
def runner(app):
    """Permite rodar comandos CLI do Flask nos testes"""
    return app.test_cli_runner()
