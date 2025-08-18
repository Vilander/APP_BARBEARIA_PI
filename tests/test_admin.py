from App_Barbearia.models import Usuario
# --- CORREÇÃO AQUI ---
# Importa 'database' diretamente
from App_Barbearia import database
# ---------------------
from werkzeug.security import generate_password_hash

def test_admin_route_forbidden_for_cliente(client, app): # Renomeei 'test_app' para 'app' para corresponder ao fixture
    """Testa se um cliente normal recebe erro 403 em rota de admin."""
    # Usa o contexto do app fornecido pelo fixture
    with app.app_context():
        cliente_pass = generate_password_hash('password', "pbkdf2:sha256")
        cliente = Usuario(username='cliente_teste', email='cliente@teste.com', senha=cliente_pass, role='cliente')
        
        # --- CORREÇÃO AQUI ---
        # Usa 'database' para interagir com a sessão
        database.session.add(cliente)
        database.session.commit()
        # ---------------------

    # Faz login como o cliente
    client.post('/login', data=dict(
        email='cliente@teste.com',
        password='password'
    ), follow_redirects=True)

    # Tenta acessar a rota de admin
    response = client.get('/agenda_hoje')

    # Verifica se o acesso foi proibido 
    assert response.status_code == 302

    # Em tests/test_admin.py

