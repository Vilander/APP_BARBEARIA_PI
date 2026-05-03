# APP_BARBEARIA

# APP_BARBEARIA

Uma aplicação web completa para gerenciamento de barbearias, desenvolvida com Flask e integrada com inteligência artificial para otimizar agendamentos e estratégias de negócio.

---

## 📋 Visão Geral

**APP_BARBEARIA** é uma plataforma web moderna e intuitiva, construída com o framework Flask em Python, destinada a revolucionar a gestão de barbearias. O sistema oferece uma experiência completa tanto para clientes quanto para administradores, combinando funcionalidades tradicionais de agendamento com recursos avançados de análise de dados e automação.

### 🎯 Objetivos Principais
- **Para Clientes:** Facilitar o agendamento de serviços de forma rápida e personalizada, com lembretes automáticos e sugestões inteligentes baseadas no histórico de uso.
- **Para Administradores:** Fornecer ferramentas poderosas de gestão, incluindo dashboards analíticos, controle de serviços e segmentação de clientes para estratégias de marketing direcionadas.
- **Diferencial Inovador:** Integração de Machine Learning para previsões de agendamento e análise RFM (Recência, Frequência, Valor Monetário) com clustering K-means, transformando dados em insights acionáveis.

O sistema inclui notificações automáticas via e-mail e WhatsApp, garantindo que nenhum agendamento seja esquecido, e utiliza um banco de dados SQLite robusto com migrações via Alembic para manter a integridade dos dados.

---

## 🚀 Funcionalidades Principais

### 👤 Para Clientes
- **Autenticação Segura:** Sistema completo de cadastro, login, logout e recuperação de senha com envio de e-mails seguros.
- **Perfil Personalizado:** Gerenciamento de informações pessoais, incluindo upload e edição de foto de perfil.
- **Agendamento Inteligente:**
  - Formulário dinâmico com validação em tempo real.
  - Prevenção de conflitos de horário.
  - Sugestão automática da próxima data ideal usando RandomForestRegressor, baseado no padrão histórico de agendamentos do cliente.
- **Notificações Automáticas:**
  - Confirmação imediata por e-mail após agendamento.
  - Lembretes via WhatsApp 24h, 2h, 1h e 30min antes do serviço, enviados automaticamente por um serviço em background.
- **Histórico Completo:** Visualização de todos os agendamentos passados e futuros.

### 👨‍💼 Para Administradores
- **Controle de Acesso:** Rotas protegidas com decorator personalizado para permissões de admin.
- **Gestão de Agenda:**
  - Visualização da agenda diária com opção de exclusão de agendamentos.
  - Consulta histórica por data específica.
- **CRUD de Serviços:** Interface completa para adicionar, editar, excluir e gerenciar preços de serviços oferecidos.
- **Dashboards Analíticos:**
  - Gráficos interativos com Chart.js mostrando agendamentos por dia, serviços mais populares e lucros acumulados.
  - Filtros de período para análise temporal.
- **Segmentação de Clientes com IA:**
  - Análise RFM automática para classificar clientes em "Alto Valor", "Intermediário" e "Novo Cliente".
  - Algoritmo K-means para agrupamento inteligente, auxiliando em campanhas de marketing personalizadas.
- **Ferramentas Administrativas:** Scripts para promoção de usuários a admin, reset de banco e verificação de senhas.

### 🤖 Inteligência Artificial Integrada
- **Modelo de Previsão:** RandomForestRegressor treinado com dados históricos para sugerir datas de agendamento otimizadas, reduzindo faltas e melhorando a satisfação do cliente.
- **Segmentação RFM/K-means:** Análise estatística para identificar padrões de comportamento, permitindo estratégias de fidelização direcionadas.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:**
  - **Python 3.8+** - Linguagem principal
  - **Flask** - Framework web leve e flexível
  - **Flask-SQLAlchemy** - ORM para interação com banco de dados
  - **Flask-Migrate & Alembic** - Sistema de migrações para versionamento do banco
  - **Flask-Login** - Gerenciamento de sessões de usuário
  - **Flask-Bcrypt** - Hashing seguro de senhas
  - **Flask-Mail** - Envio de e-mails via SMTP
  - **Flask-WTF** - Validação e geração de formulários

- **Banco de Dados:**
  - **SQLite** - Banco de dados relacional leve para desenvolvimento
  - **SQLAlchemy** - ORM para consultas e manipulação de dados

- **Frontend:**
  - **Jinja2** - Engine de templates para renderização dinâmica
  - **HTML5, CSS3, JavaScript** - Tecnologias web padrão
  - **Bootstrap 5** - Framework CSS responsivo para UI moderna
  - **Chart.js** - Biblioteca para gráficos interativos

- **Machine Learning:**
  - **Pandas** - Manipulação e análise de dados
  - **Scikit-learn** - Algoritmos de ML (RandomForestRegressor e KMeans)

- **Outras Bibliotecas:**
  - **python-dotenv** - Carregamento de variáveis de ambiente
  - **Pillow** - Processamento de imagens para uploads
  - **PyWhatKit** - Automação de WhatsApp para lembretes
  - **WTForms** - Validação avançada de formulários

---

## 📦 Instalação

Para instruções detalhadas de instalação e configuração do ambiente local, consulte o arquivo [SETUP_LOCAL.md](SETUP_LOCAL.md).

### Pré-requisitos Rápidos
- Python 3.8 ou superior
- Conta Gmail para notificações por e-mail
- WhatsApp Web logado para lembretes

---

## 🎮 Uso / Demonstração

### Executando a Aplicação
Após a instalação, execute:
```bash
python app.py
```
Acesse `http://localhost:5000` no navegador.

### Fluxo Básico
1. **Cadastro/Login:** Novos usuários se cadastram; admins são promovidos via script.
2. **Agendamento:** Cliente seleciona serviço, data e hora; recebe sugestão IA e confirmação por e-mail.
3. **Lembretes:** Sistema envia notificações automáticas via WhatsApp em intervalos pré-definidos.
4. **Administração:** Acesse `/admin` para visualizar agenda, gerenciar serviços e analisar relatórios.

### Funcionalidades em Destaque
- **Sugestão IA:** Após alguns agendamentos, o sistema sugere datas baseadas em padrões pessoais.
- **Segmentação:** Admins visualizam clusters de clientes para campanhas direcionadas.
- **Relatórios:** Dashboards com gráficos de lucros e popularidade de serviços.

---

## 📁 Estrutura do Projeto
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
├── requirements.txt            # Arquivo de dependências do projeto
├── SETUP_LOCAL.md              # Guia detalhado de instalação e execução
└── readme.md                   # Este arquivo
```

---

## 🗄️ Banco de Dados

O sistema utiliza SQLite com três tabelas principais:

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

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

### Diretrizes
- Siga os padrões de código Python (PEP 8)
- Adicione testes para novas funcionalidades
- Atualize a documentação conforme necessário

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

*Desenvolvido com ❤️ para barbearias modernas que querem crescer com tecnologia.*

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






