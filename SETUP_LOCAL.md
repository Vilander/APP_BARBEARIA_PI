# 🚀 Guia Passo a Passo - Executar APP_BARBEARIA Localmente

## 📋 Pré-requisitos
- **Python 3.8+** instalado
- **Git** (opcional)
- Acesso a uma conta **Gmail** (para notificações por e-mail)
- Navegador web moderno

---

## 🔧 Passo 1: Clonar ou Acessar o Repositório

```powershell
# Se você ainda não tem o projeto
git clone <url-do-seu-repositorio>
cd APP_BARBEARIA_PI
```

---

## 🔐 Passo 2: Criar e Ativar Ambiente Virtual

### No Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Se receber erro de permissão, execute primeiro:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### No macOS/Linux (Terminal):
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 📦 Passo 3: Instalar Dependências

Com o ambiente virtual **ativado**, execute:

```powershell
pip install -r requirements.txt
```

As dependências são:
- **Flask** - Framework web
- **Flask-SQLAlchemy** - ORM para banco de dados
- **Flask-Login** - Autenticação de usuários
- **Flask-Bcrypt** - Criptografia de senhas
- **Flask-Mail** - Envio de e-mails
- **PyWhatKit** - Envio de mensagens WhatsApp (para lembretes)
- **WTForms** - Validação de formulários
- **Pillow** - Processamento de imagens

---

## 🔑 Passo 4: Configurar Variáveis de Ambiente

Crie um arquivo `.env` na **raiz do projeto** (ao lado de `app.py`):

```ini
SECRET_KEY=sua-chave-secreta-super-segura-aqui
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app-do-gmail
```

### 📧 Como gerar `MAIL_PASSWORD`:
1. Acesse https://myaccount.google.com/
2. Segurança → Senhas de app
3. Selecione "Mail" e "Windows Computer"
4. Copie a senha gerada (16 caracteres)
5. Cole no `.env` como `MAIL_PASSWORD`

---

## 🗄️ Passo 5: Configurar o Banco de Dados

Execute as migrações para criar as tabelas:

```powershell
$env:FLASK_APP='app.py'
flask db upgrade
```

---

## 👨‍💼 Passo 6: Criar Usuário Administrador

### Opção A: Via Script (Recomendado)
```powershell
python set_admin.py
```
- Digite o e-mail do usuário para promover a admin
- O usuário já deve estar cadastrado

### Opção B: Acesso Direto ao Banco
Se o script não funcionar, use o arquivo `instance/reset_usuario.py` ou `instance/reset_banco.py`

---

## ▶️ Passo 7: Executar a Aplicação

### Opção A: Com Lembretes Automáticos (Recomendado)
```powershell
python app.py
```
- Inicia o servidor com serviço de lembretes automáticos de WhatsApp
- A app estará em: http://localhost:5000

### Opção B: Modo Debug (Sem Lembretes)
```powershell
$env:FLASK_APP='app.py'
flask run --debug
```
- Recarrega automaticamente ao alterar arquivos
- Ideal para desenvolvimento

### Opção C: Produção
```powershell
python main.py
```
- Roda em http://0.0.0.0:5000

---

## ✅ Verificar se Está Funcionando

1. Abra: **http://localhost:5000**
2. Você verá a página inicial
3. Clique em "Cadastrar" para criar uma conta
4. Use um e-mail para teste
5. Após cadastro, faça login
6. Teste "Agendar" para criar um agendamento

---

## 🎯 Funcionalidades Principais

### Para Clientes:
- ✅ Agendar serviços
- ✅ Visualizar "Meus Agendamentos"
- ✅ **Avaliar atendimento (0-5)** ⭐ NOVO
- ✅ Receber e-mail de confirmação
- ✅ Receber lembrete via WhatsApp 1h antes ⭐ NOVO
- ✅ Editar perfil

### Para Administradores:
- ✅ Visualizar agenda do dia
- ✅ Consultar agendamentos por data
- ✅ Gerenciar serviços (CRUD)
- ✅ Ver avaliações dos clientes ⭐ NOVO
- ✅ Ver status de lembretes ⭐ NOVO
- ✅ Relatórios e gráficos
- ✅ Segmentação de clientes (RFM)

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'flask'"
**Solução:** Verifique se o ambiente virtual está ativado
```powershell
# Checar se está ativado (deve ter (venv) no prompt)
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Erro: "Cannot add a NOT NULL column"
**Solução:** A migração já foi aplicada. Limpe o banco:
```powershell
# Backup do banco primeiro!
# Depois delete instance/barbearia.db e rode:
flask db upgrade
```

### Lembretes não estão sendo enviados
**Solução:** 
- Execute com `python app.py` (não `flask run`)
- Verifique se o PyWhatKit está instalado: `pip install pywhatkit`
- Certifique-se de que o número tem 11 dígitos (DDD + 9 dígitos)

### E-mail de confirmação não chega
**Solução:**
- Verifique as credenciais no `.env`
- Confirme que é senha de app (não senha da conta)
- Verifique a pasta de spam

---

## 📁 Estrutura do Projeto

```
APP_BARBEARIA_PI/
├── App_Barbearia/          # Código principal
│   ├── __init__.py         # Inicialização + lembretes
│   ├── models.py           # Modelos de dados (Usuario, Post, Servico)
│   ├── forms.py            # Formulários (Agendar, Avaliar, etc.)
│   ├── routs.py            # Rotas principais
│   ├── decorators.py       # Decoradores (admin_required)
│   ├── templates/          # HTML
│   └── static/             # CSS, JS, imagens
├── migrations/             # Histórico de migrações
├── instance/               # Banco de dados (barbearia.db)
├── app.py                  # Ponto de entrada principal
├── main.py                 # Alternativa de execução
├── requirements.txt        # Dependências
├── .env                    # Variáveis de ambiente (CRIAR)
└── README.md               # Documentação completa
```

---

## 🆘 Precisa de Ajuda?

Se houver problemas:
1. Verifique que o ambiente virtual está ativado
2. Confirme que todas as dependências foram instaladas
3. Verifique o arquivo `.env` (não compartilhe suas credenciais!)
4. Confira se o Python é 3.8+

Bom uso! 🎉
