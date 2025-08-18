def test_login_page(client):
    """Testa se a página de login carrega corretamente."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data # Verifica se a palavra 'Login' está no HTML

def test_register_page(client):
    """Testa se a página de login/cadastro carrega corretamente."""
    response = client.get('/login')  # <--- Mude a URL aqui
    assert response.status_code == 200

def test_protected_route_redirects(client):
    """Testa se uma rota protegida redireciona para o login."""
    response = client.get('/perfil', follow_redirects=True)
    assert response.status_code == 200
    assert b"Fazer Login" in response.data