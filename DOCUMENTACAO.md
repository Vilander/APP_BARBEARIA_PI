# 📋 Documentação - App Barbearia PI

## Índice
1. [Visão Geral](#visão-geral)
2. [Funcionalidades Principais](#funcionalidades-principais)
3. [Funcionalidades Prioritárias](#-funcionalidades-prioritárias)
4. [Rotas da Aplicação](#rotas-da-aplicação)
5. [Estrutura de Modelos](#estrutura-de-modelos)
6. [Folhas de Estilo](#folhas-de-estilo)
7. [Estrutura de Arquivos](#estrutura-de-arquivos)

---

## Visão Geral

O **App Barbearia** é uma aplicação Flask para gerenciar agendamentos de barbearia com funcionalidades de:
- ✅ Autenticação de usuários
- ✅ Sistema de agendamentos
- ✅ **Avaliações de serviços** ⭐ (PRIORITÁRIO)
- ✅ **Notificações via WhatsApp** 📱 (PRIORITÁRIO)
- ✅ Relatórios de lucro e desempenho
- ✅ Segmentação de clientes com ML
- ✅ Gerenciamento de serviços

---

## 🎯 Funcionalidades Prioritárias

### 1️⃣ **AVALIAÇÕES DE SERVIÇOS** ⭐⭐⭐

#### O que é?
Sistema que permite aos clientes avaliar os serviços recebidos em uma escala de 0 a 5 estrelas após o agendamento ser realizado.

#### Arquivos Relacionados:

| Aspecto | Localização | Descrição |
|--------|-----------|-----------|
| **Modelo de Dados** | [App_Barbearia/models.py](App_Barbearia/models.py#L63-L70) | Campo `avaliacao` na tabela `Post` (INTEGER, nullable) |
| **Formulário** | [App_Barbearia/forms.py](App_Barbearia/forms.py#L49-L55) | `Form_Avaliar` - SelectField com opções de 0 a 5 |
| **Rota Principal** | [App_Barbearia/routs.py](App_Barbearia/routs.py#L184-L200) | `avaliar_agendamento()` - Salva avaliação no DB |
| **Template** | [App_Barbearia/templates/avaliar.html](App_Barbearia/templates/avaliar.html) | Interface de avaliação |
| **Relatório** | [App_Barbearia/routs.py](App_Barbearia/routs.py#L314-L344) | Rota `relatorio_avaliacoes()` |
| **Template Relatório** | [App_Barbearia/templates/relatorio_avaliacoes.html](App_Barbearia/templates/relatorio_avaliacoes.html) | Dashboard de médias por serviço |

#### Funcionalidades:
- ✅ Avaliação pós-agendamento (escala 0-5)
- ✅ Média de avaliações por serviço
- ✅ Relatório visual com gráficos
- ✅ Estatística geral de satisfação

#### Código Principal:
```python
# Rota para avaliar agendamento
@main.route("/avaliar_agendamento/<int:id>", methods=["GET", "POST"])
@login_required
def avaliar_agendamento(id):
    agendamento = Post.query.get_or_404(id)
    form_avaliar = Form_Avaliar()
    if form_avaliar.validate_on_submit():
        agendamento.avaliacao = form_avaliar.nota.data
        database.session.commit()
        flash('Avaliação salva com sucesso!', 'alert-success')
```

#### Acessos:
- 👤 Cliente avalia seu agendamento: `meus_agendamentos.html` → botão avaliar
- 👨‍💼 Admin vê relatório: `/relatorio_avaliacoes`

---

### 2️⃣ **NOTIFICAÇÕES VIA WHATSAPP** 📱⭐⭐⭐

#### O que é?
Sistema automático de lembretes que envia mensagens via WhatsApp em 4 momentos diferentes:
- 📅 24 horas antes
- ⏰ 2 horas antes
- ⏰ 1 hora antes
- ⏰ 30 minutos antes

#### Arquivos Relacionados:

| Aspecto | Localização | Descrição |
|--------|-----------|-----------|
| **Serviço de Lembretes** | [App_Barbearia/__init__.py](App_Barbearia/__init__.py#L61-L140) | Funções de verificação e envio |
| **Função Principal** | [App_Barbearia/__init__.py](App_Barbearia/__init__.py#L75-L95) | `enviar_whatsapp_lembrete()` |
| **Verificação** | [App_Barbearia/__init__.py](App_Barbearia/__init__.py#L98-L140) | `verificar_lembretes()` |
| **Inicialização** | [app.py](app.py#L1-L15) | `iniciar_servico_lembretes(app)` |
| **Modelo de Dados** | [App_Barbearia/models.py](App_Barbearia/models.py#L63-L70) | Campos de controle: `lembrete_24h_enviado`, `lembrete_2h_enviado`, etc |
| **Confirmação Email** | [App_Barbearia/routs.py](App_Barbearia/routs.py#L70-L88) | `enviar_email_confirmacao()` |

#### Funcionalidades:
- ✅ Envio automático via WhatsApp
- ✅ 4 lembretes em momentos estratégicos
- ✅ Controle de envio (não duplica)
- ✅ Formatação automática de números
- ✅ Confirmação por email
- ✅ Thread de execução em background

#### Código Principal:
```python
# Função que envia lembrete via WhatsApp
def enviar_whatsapp_lembrete(agendamento, tempo_antes):
    numero = formatar_numero_whatsapp(agendamento.cell)
    mensagem = f"Olá {agendamento.username}!..."
    kit.sendwhatmsg_instantly(numero, mensagem, wait_time=20)

# Verificação periódica (a cada 60 segundos)
def verificar_lembretes():
    lembretes = [
        (timedelta(days=1), 'lembrete_24h_enviado', '24 horas'),
        (timedelta(hours=2), 'lembrete_2h_enviado', '2 horas'),
        (timedelta(hours=1), 'lembrete_1h_enviado', '1 hora'),
        (timedelta(minutes=30), 'lembrete_30min_enviado', '30 minutos'),
    ]
```

#### Campos no Banco de Dados:
```python
lembrete_24h_enviado = database.Column(database.Boolean, default=False)
lembrete_2h_enviado = database.Column(database.Boolean, default=False)
lembrete_1h_enviado = database.Column(database.Boolean, default=False)
lembrete_30min_enviado = database.Column(database.Boolean, default=False)
```

#### Como Funciona:
1. Usuário cria agendamento
2. Email de confirmação é enviado
3. Thread inicia verificação a cada 60 segundos
4. Nos horários programados, WhatsApp é enviado
5. Campo booleano marca como enviado (evita duplicação)

---

## Rotas da Aplicação

### 🏠 Rotas Públicas

| Rota | Método | Função | Arquivo |
|------|--------|--------|---------|
| `/` | GET | Home page | [routs.py](App_Barbearia/routs.py#L28-L29) |
| `/login` | GET, POST | Login/Criar conta | [routs.py](App_Barbearia/routs.py#L31-L51) |
| `/recuperar_senha` | GET, POST | Recuperar senha | [routs.py](App_Barbearia/routs.py#L447-L460) |
| `/redefinir_senha/<token>` | GET, POST | Redefinir com token | [routs.py](App_Barbearia/routs.py#L462-L493) |
| `/servicos` | GET | Lista de serviços | [routs.py](App_Barbearia/routs.py#L500-L502) |

### 👤 Rotas de Usuário (Requer Login)

| Rota | Método | Função | Arquivo |
|------|--------|--------|---------|
| `/sair` | GET | Logout | [routs.py](App_Barbearia/routs.py#L53-L57) |
| `/perfil` | GET | Ver perfil | [routs.py](App_Barbearia/routs.py#L59-L62) |
| `/perfil/editar` | GET, POST | Editar perfil | [routs.py](App_Barbearia/routs.py#L104-L122) |
| `/agendar` | GET, POST | Criar agendamento | [routs.py](App_Barbearia/routs.py#L125-L174) |
| `/meus_agendamentos` | GET | Ver agendamentos | [routs.py](App_Barbearia/routs.py#L381-L383) |
| **`/avaliar_agendamento/<id>`** | GET, POST | **Avaliar serviço** ⭐ | [routs.py](App_Barbearia/routs.py#L184-L200) |

### 👨‍💼 Rotas de Admin (Requer admin_required)

| Rota | Método | Função | Arquivo |
|------|--------|--------|---------|
| `/agenda_data` | GET, POST | Buscar agendamentos por data | [routs.py](App_Barbearia/routs.py#L177-L183) |
| `/agenda_hoje` | GET | Ver agendamentos de hoje | [routs.py](App_Barbearia/routs.py#L374-L376) |
| `/gerenciar_servicos` | GET, POST | CRUD de serviços | [routs.py](App_Barbearia/routs.py#L203-L225) |
| `/excluir_servico/<id>` | POST | Deletar serviço | [routs.py](App_Barbearia/routs.py#L228-L233) |
| `/relatorio` | GET, POST | Gráficos de lucro/agendamentos | [routs.py](App_Barbearia/routs.py#L237-L313) |
| **`/relatorio_avaliacoes`** | GET | **Relatório de avaliações** ⭐ | [routs.py](App_Barbearia/routs.py#L316-L344) |
| `/segmentacao` | GET | Segmentação ML de clientes | [routs.py](App_Barbearia/routs.py#L347-L356) |
| `/excluir_agendamento/<id>` | POST | Deletar agendamento | [routs.py](App_Barbearia/routs.py#L385-L390) |

---

## Estrutura de Modelos

### 📊 Modelo: `Usuario`

**Arquivo:** [App_Barbearia/models.py](App_Barbearia/models.py#L16-L47)

```python
class Usuario:
    id (PK)
    username (String, unique)
    email (String, unique)
    foto_perfil (String)
    senha (String, hashed)
    role (String: 'cliente' ou 'admin')
    posts (Relationship)
```

### 📅 Modelo: `Post` (Agendamento)

**Arquivo:** [App_Barbearia/models.py](App_Barbearia/models.py#L50-L70)

```python
class Post:
    id (PK)
    username (String)
    cell (String)
    servico (String)
    valor (Float)
    hora (String: 'HH:MM')
    data (Date)
    id_usuario (FK)
    avaliacao (Integer, 0-5) ⭐ NOVO
    lembrete_24h_enviado (Boolean) 📱 NOVO
    lembrete_2h_enviado (Boolean) 📱 NOVO
    lembrete_1h_enviado (Boolean) 📱 NOVO
    lembrete_30min_enviado (Boolean) 📱 NOVO
```

### 💇 Modelo: `Servico`

**Arquivo:** [App_Barbearia/models.py](App_Barbearia/models.py#L37-L43)

```python
class Servico:
    id (PK)
    nome (String, unique)
    valor (Float)
```

---

## 🎨 Folhas de Estilo

### Arquivo Principal: CSS

| Arquivo | Localização | Descrição |
|---------|-----------|-----------|
| **styles.css** | [App_Barbearia/static/css/styles.css](App_Barbearia/static/css/styles.css) | Estilos principais (variáveis CSS, cards, forms) |
| **main.css** | [App_Barbearia/static/main.css](App_Barbearia/static/main.css) | Estilos secundários (complementares) |

### Variáveis CSS Principais:

```css
:root {
    /* Cores */
    --color-bg-dark: #1f1f1f;           /* Fundo escuro */
    --color-bg-card: #212529;           /* Cards */
    --color-bg-primary: #007bff;        /* Botões primários (azul) */
    --color-bg-success: #28a745;        /* Sucesso (verde) */
    --color-bg-danger: #dc3545;         /* Perigo/Deletar (vermelho) */
    --color-bg-warning: #ffb700;        /* Atenção (amarelo) */
    --color-font-main: white;           /* Texto principal */
    
    /* Dimensões */
    --radius-card: 1rem;                /* Bordas arredondadas */
    --padding-card: 2rem;               /* Espaçamento interno */
    --shadow-card: 0 0 15px rgba(...);  /* Sombra de cards */
}
```

### Classes CSS Utilizadas:

```css
.card-relatorio         /* Cards de relatórios */
.card-agenda-data       /* Cards de agenda por data */
.card-agenda-hoje       /* Cards de agenda de hoje */
.card-agendar           /* Cards de agendamento */
.card-editar-perfil     /* Cards de edição */
.card-login             /* Cards de login */
.card-grafico           /* Container para gráficos (40vh altura) */

.form-control           /* Campos de formulário */
.form-label             /* Labels de formulário */
.form-group             /* Grupos de formulário */
```

### Design:
- 🌙 **Tema escuro** com fundo gradiente
- 🎨 **Cores Bootstrap**: Primary (azul), Success (verde), Danger (vermelho), Warning (amarelo)
- 📱 **Responsivo** com Flexbox/Grid
- ✨ **Animações**: Fade-in ao carregar cards

---

## Estrutura de Arquivos

```
APP_BARBEARIA_PI/
│
├── 📄 app.py                          # Ponto de entrada principal
├── 📄 main.py                         # Alternativa de execução
├── 📄 requirements.txt                # Dependências do projeto
├── 📄 SETUP_LOCAL.md                  # Guia de setup
├── 📄 readme.md                       # README original
├── 📄 DOCUMENTACAO.md                 # ESTA DOCUMENTAÇÃO ✅
│
├── 📁 App_Barbearia/                  # Pacote principal
│   ├── 📄 __init__.py                 # Inicialização e config (ML, lembretes)
│   ├── 📄 models.py                   # Modelos SQLAlchemy
│   ├── 📄 routs.py                    # Todas as rotas Flask
│   ├── 📄 forms.py                    # Formulários WTForms
│   ├── 📄 decorators.py               # Decoradores (admin_required)
│   ├── 📄 ml_model.py                 # Modelos de ML (previsão, segmentação)
│   ├── 📄 redefinir_senha.py          # Funções de redefinição
│   ├── 📄 reconfg.py                  # Reconfiguração
│   │
│   ├── 📁 static/                     # Arquivos estáticos
│   │   ├── 📄 main.css                # CSS complementar
│   │   ├── 📁 css/
│   │   │   └── 📄 styles.css          # CSS principal ⭐
│   │   ├── 📁 fotos_perfil/           # Fotos de usuários
│   │   └── 📁 img/                    # Imagens
│   │
│   ├── 📁 templates/                  # Templates HTML Jinja2
│   │   ├── 📄 base.html               # Template base
│   │   ├── 📄 navbar.html             # Navegação
│   │   ├── 📄 home.html               # Página inicial
│   │   ├── 📄 login.html              # Login/Criar conta
│   │   ├── 📄 perfil.html             # Perfil do usuário
│   │   ├── 📄 editar_perfil.html      # Edição de perfil
│   │   ├── 📄 agendar.html            # Agendamento
│   │   ├── 📄 meus_agendamentos.html  # Lista de agendamentos
│   │   ├── 📄 avaliar.html            # Avaliação ⭐
│   │   ├── 📄 agenda_data.html        # Agenda por data (admin)
│   │   ├── 📄 agenda_hoje.html        # Agenda de hoje (admin)
│   │   ├── 📄 gerenciar_servicos.html # CRUD serviços (admin)
│   │   ├── 📄 relatorio.html          # Gráficos lucro (admin)
│   │   ├── 📄 relatorio_avaliacoes.html # Gráficos avaliações (admin) ⭐
│   │   ├── 📄 segmentacao.html        # Segmentação ML (admin)
│   │   ├── 📄 recuperar_senha.html    # Recuperação de senha
│   │   ├── 📄 redefinir_senha.html    # Redefinição de senha
│   │   ├── 📄 usuarios.html           # Página de usuários
│   │   ├── 📄 servicos.html           # Página de serviços
│   │   └── 📄 404.html                # Página de erro
│   │
│   └── 📁 instance/                   # Banco de dados
│       ├── 📄 barbearia.db            # SQLite DB
│       └── 📄 reset_*.py              # Scripts de reset
│
└── 📁 migrations/                     # Migrações SQLAlchemy
    └── versions/                      # Histórico de migrações
```

---

## 🔧 Dependências Principais

**Arquivo:** [requirements.txt](requirements.txt)

```
flask>=2.0                    # Framework web
flask_sqlalchemy>=2.5         # ORM - Banco de dados
flask_login>=0.6              # Autenticação
flask_bcrypt>=1.0             # Hash de senhas
flask_mail>=0.9               # Envio de emails
pywhatkit>=5.4                # Integração WhatsApp ⭐
wtforms>=3.0                  # Formulários
pillow>=10.0                  # Processamento de imagens
scikit-learn                  # ML - Clustering, Regressão
pandas                        # ML - Manipulação de dados
```

---

## 📱 Como Funciona o Fluxo de Avaliação

```
1. Cliente faz agendamento
   ↓
2. Recebe email de confirmação
   ↓
3. WhatsApp lembretes nos horários programados
   ↓
4. Agendamento passa
   ↓
5. Cliente acessa "Meus Agendamentos"
   ↓
6. Clica em "Avaliar"
   ↓
7. Seleciona nota (0-5 estrelas)
   ↓
8. Avaliação é salva no banco
   ↓
9. Admin acessa "/relatorio_avaliacoes"
   ↓
10. Vê média por serviço e estatísticas
```

---

## 📲 Como Funciona o Fluxo de Notificações

```
AGENDAMENTO CRIADO (Data: 20/05/2026 às 14:00)
↓
THREAD INICIADA (verifica a cada 60 segundos)
↓
├─ 19/05/2026 14:00 → Envia WhatsApp "24 horas antes" ✓
├─ 20/05/2026 12:00 → Envia WhatsApp "2 horas antes" ✓
├─ 20/05/2026 13:00 → Envia WhatsApp "1 hora antes" ✓
└─ 20/05/2026 13:30 → Envia WhatsApp "30 minutos antes" ✓

(Campo booleano marca cada envio para evitar duplicatas)
```

---

## 🚀 Como Iniciar a Aplicação

```bash
# 1. Ativar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente (.env)
SECRET_KEY=sua_chave_secreta
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_app

# 4. Executar migrações (opcional)
flask db upgrade

# 5. Iniciar aplicação
python app.py
```

---

## ✅ Checklist de Funcionalidades

- ✅ **Autenticação**: Login, Criar conta, Recuperar/Redefinir senha
- ✅ **Agendamentos**: CRUD de agendamentos
- ✅ **⭐ Avaliações**: Sistema de avaliação 0-5 com relatório
- ✅ **📱 Notificações**: 4 lembretes via WhatsApp
- ✅ **Serviços**: CRUD de serviços com preços
- ✅ **Relatórios**: Lucro, agendamentos, avaliações
- ✅ **ML**: Previsão de próxima visita, segmentação de clientes
- ✅ **Email**: Confirmação e recuperação de senha
- ✅ **Perfil**: Edição e foto de perfil

---

## 📞 Suporte e Contato

Para dúvidas sobre funcionalidades específicas, consulte:
- 📄 [SETUP_LOCAL.md](SETUP_LOCAL.md) - Configuração local
- 📄 [readme.md](readme.md) - Informações gerais
- 🔗 Código-fonte em [App_Barbearia/](App_Barbearia/)

---

**Última atualização:** 30 de abril de 2026
**Versão:** 1.0 com Avaliações e Notificações
