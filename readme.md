# APP_BARBEARIA

---

## 1. Visão Geral

**APP_BARBEARIA** é uma aplicação web desenvolvida com Flask, projetada para gerenciar as operações de uma barbearia moderna.  

A plataforma permite que clientes criem contas, agendem serviços e gerenciem seus perfis pessoais.  

Administradores têm acesso a um painel completo que inclui:  
- Visualização da agenda diária.  
- Consulta de agendamentos por data.  
- Gerenciamento dos serviços oferecidos (CRUD).  
- Acesso a relatórios analíticos sobre desempenho do negócio, incluindo lucros e serviços populares.  

Um diferencial importante do sistema é a incorporação de inteligência artificial, que sugere datas de agendamento para clientes com base no histórico, além de segmentar os clientes em grupos de valor (baseado em RFM — Recência, Frequência e Valor Monetário), auxiliando em estratégias de marketing e fidelização.

---

## 2. Funcionalidades Principais

### Para Clientes
- **Autenticação de Usuários:**  
  Cadastro, login, logout e recuperação de senha via e-mail de forma segura.  
- **Gerenciamento de Perfil:**  
  Visualização e edição do nome de usuário, e-mail e foto de perfil.  
- **Sistema de Agendamento:**  
  Formulário intuitivo para agendar serviços, com seleção dinâmica de data, hora e serviço, validação de dados e prevenção de agendamentos duplicados.  
- **Notificação por E-mail:**  
  Envio automático de confirmação de agendamento para o e-mail do cliente.  
- **Sugestão Inteligente:**  
  Sistema que usa modelo de machine learning para sugerir a melhor data para o próximo agendamento do cliente, com base na frequência histórica.

### Para Administradores
- **Controle de Acesso:**  
  Rotas administrativas protegidas por permissão `admin`.  
- **Visualização da Agenda:**  
  - Agenda do Dia: visualização dos agendamentos no dia atual, com possibilidade de exclusão.  
  - Consulta por Data: pesquisa de agendamentos por data específica.  
- **Gerenciamento de Serviços (CRUD):**  
  Interface para adicionar, editar e excluir serviços, atualizando nome e valor.  
- **Relatórios e Dashboards:**  
  Gráficos interativos que mostram:  
  - Número de agendamentos por dia.  
  - Tipos de serviço mais procurados (doughnut).  
  - Lucro diário acumulado, com filtro de período.  
- **Segmentação de Clientes (K-means):**  
  Agrupamento dos clientes em segmentos "Alto Valor", "Intermediário" e "Novo Cliente" baseado na análise RFM para ajudar no direcionamento de ações de marketing.

---

## 3. Tecnologias Utilizadas

- **Backend:**  
  - Python  
  - Flask  
  - Flask-SQLAlchemy  
  - Flask-Migrate & Alembic (migrações de banco)  
  - Flask-Login  
  - Flask-Bcrypt (hashing de senha)  
  - Flask-Mail (envio de emails)  
  - Flask-WTF (formularios e validação)  

- **Banco de Dados:**  
  - SQLite (desenvolvimento)  
  - SQLAlchemy (ORM)  

- **Frontend:**  
  - Jinja2 (templating Flask)  
  - HTML5, CSS3, JavaScript  
  - Bootstrap 5 (UI responsiva)  
  - Chart.js (visualização gráfica dos relatórios)  

- **Machine Learning:**  
  - Pandas (manipulação de dados)  
  - Scikit-learn (modelos RandomForestRegressor para previsão e KMeans para segmentação)  

- **Outras:**  
  - python-dotenv (variáveis de ambiente)  
  - Pillow (manipulação de imagens)  

---

## 4. Estrutura do Projeto
```
APP_BARBEARIA_PI/
├── App_Barbearia/               # Pacote principal da aplicação
│   ├── static/                  # Arquivos estáticos (CSS, imagens, JS)
│   ├── templates/               # Templates HTML (Jinja2)
│   ├── __init__.py              # Fábrica da aplicação e inicialização das extensões Flask
│   ├── decorators.py            # Decorators personalizados (ex: controle de acesso admin)
│   ├── forms.py                 # Definição dos formulários via Flask-WTF
│   ├── ml_model.py              # Modelos de Machine Learning (previsão e segmentação)
│   ├── models.py                # Modelos do banco de dados com SQLAlchemy
│   ├── routs.py                 # Rotas e controladores (lógica das views)
│   └── instance/                # Configurações da instância e scripts auxiliares
│       ├── reset_banco.py       # Reset de tabelas, exclusão e atualização no banco
│       ├── reset_usuario.py     # Reset da tabela usuário (ex: senha padrão)
│       └── verificar_senha.py   # Ferramenta para checar hash de senha
├── migrations/                  # Scripts de migração do banco via Alembic
│   └── versions/                # Versões das migrações
├── tests/                      # Testes unitários e funcionais da aplicação
│   ├── conftest.py             # Configuração para o ambiente de testes
│   ├── test_auth.py            # Testes para autenticação e registro
│   └── test_admin.py           # Testes para funcionalidades administrativas
├── app.py                      # Arquivo principal para iniciar a aplicação
├── ler_db.py                   # Script para consulta rápida ao banco SQLite (debug)
├── set_admin.py                # Script CLI para promover usuários a admins
└── requirements.txt            # Arquivo de dependências do projeto
```

---

## 5. Banco de Dados

O banco é composto pelas tabelas principais:

### Tabela: `usuario`
| Coluna      | Tipo       | Restrições                      | Descrição                        |
|-------------|------------|--------------------------------|---------------------------------|
| id          | Integer    | PK                             | Identificador único             |
| username    | String(30) | Único, não nulo                 | Nome do usuário                |
| email       | String(120)| Único, não nulo                 | E-mail                        |
| foto_perfil | String(20) | Não nulo, padrão 'default.jpg' | Nome arquivo foto perfil       |
| senha       | String(60) | Não nulo                       | Senha (hash bcrypt)            |
| role        | String(20) | Não nulo, default 'cliente'     | Papel do usuário (`admin`/`cliente`) |

### Tabela: `servico`
| Coluna | Tipo       | Restrições            | Descrição                       |
|--------|------------|----------------------|--------------------------------|
| id     | Integer    | PK                   | Identificador único             |
| nome   | String(100)| Único, não nulo      | Nome do serviço (ex: Corte)    |
| valor  | Float      | Não nulo             | Preço do serviço                |

### Tabela: `post` (agendamentos)
| Coluna      | Tipo       | Restrições               | Descrição                             |
|-------------|------------|-------------------------|-------------------------------------|
| id          | Integer    | PK                      | Identificador único                  |
| username    | String     | Não nulo                | Nome do cliente para o agendamento  |
| cell        | String     | Não nulo                | Número de celular do cliente         |
| servico     | String     | Não nulo                | Nome do serviço agendado             |
| valor       | Float      | Não nulo, default 0.0   | Valor do serviço no momento do agendamento |
| hora        | String     | Não nulo                | Hora agendada                       |
| data        | Date       | Não nulo                | Data do agendamento                 |
| id_usuario  | Integer    | FK para usuario.id      | Referência ao usuário que agendou  |

---

## 6. Configuração e Execução Local

### Pré-requisitos
- Python 3.8 ou superior
- Git (opcional para clonar o repositório)

### Passo a Passo

1. Clone o repositório  

```
git clone <url-do-seu-repositorio>
cd APP_BARBEARIA_PI
```


2. Crie e ative um ambiente virtual  
**Windows**  

```
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux**  

```
python3 -m venv venv
source venv/bin/activate
```


3. Instale as dependências  
Crie um arquivo chamado `requirements.txt` (exemplo abaixo) e execute:  

```
pip install -r requirements.txt
```


Exemplo `requirements.txt`:  
```
flask>=2.0
flask_sqlalchemy>=2.5
flask_wtf>=1.0
flask_login>=0.6
flask_bcrypt>=1.0
pywhatkit>=5.4
flask_mail>=0.9
wtforms>=3.0
pillow>=10.0
email_validator>=2.0

```

4. Configure variáveis de ambiente  
Crie o arquivo `.env` na raiz e preencha:  

```
SECRET_KEY='sua-chave-secreta-aqui'
MAIL_USERNAME='seu-email-do-gmail@gmail.com'
MAIL_PASSWORD='sua-senha-de-app-do-gmail'
```
**Nota:** Para o `MAIL_PASSWORD`, gere uma senha de app na conta Google para o envio via SMTP.

5. Configure o banco de dados  
Com o ambiente virtual ativo, rode as migrações para criar as tabelas:  
```
flask db upgrade
```

6. Crie um usuário administrador  
Primeiro, faça o registro de um novo usuário via interface web.  
Depois rode o script CLI:  
```
python set_admin.py
```
Informe o e-mail do usuário para promover para administrador.

7. Inicie a aplicação  
```
flask run --debug
```
A aplicação estará disponível em: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## 7. Scripts Auxiliares

- **set_admin.py**  
Transforma um usuário existente em administrador pelo e-mail.

- **ler_db.py**  
Script para conexão SQLite e listagem do conteúdo para debug.

- **instance/reset_banco.py**  
Interface simples para resetar tabelas, remover registros ou atualizar campos específicos no banco.

- **instance/reset_usuario.py**  
Script para resetar a tabela `usuario` e inserir usuários padrão com senha definida.

- **instance/verificar_senha.py**  
Verifica se uma senha em texto plano confere com o hash bcrypt armazenado no banco para um usuário específico.

---

## 8. Modelos de Machine Learning

- **Previsão de Próxima Visita:**  
Modelo baseado em `RandomForestRegressor` que usa dados históricos de agendamento para sugerir a próxima data para um cliente, considerando a média de dias entre visitas e o dia da semana.

- **Segmentação de Clientes (K-means):**  
Análise dos clientes usando as métricas RFM para agrupá-los em três segmentos: "Alto Valor", "Intermediário" e "Novo Cliente".

Os modelos são treinados a partir dos dados da base e integrados à aplicação para fornecer sugestões no fluxo de agendamento e análise administrativa.

---

## 9. Referências

- Framework e extensões Flask: flask.palletsprojects.com  
- SQLAlchemy ORM: docs.sqlalchemy.org  
- Flask-Migrate & Alembic: flask-migrate.readthedocs.io  
- Uso do Flask-Login: flask-login.readthedocs.io  
- Flask-Mail para envio de e-mails: flask-mail.readthedocs.io  
- Machine Learning com scikit-learn: scikit-learn.org  
- Pandas para manipulação de dados: pandas.pydata.org  
- Chart.js para gráficos: chartjs.org  
- Bootstrap 5 para UI responsiva: getbootstrap.com  

---

## 10. Contato e Suporte

Para dúvidas, sugestões ou contribuições, entre em contato com o desenvolvedor responsável pelo projeto.

---

**APP_BARBEARIA - Gerencie sua barbearia com estilo e inteligência!**






