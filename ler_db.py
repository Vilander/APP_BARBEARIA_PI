import sqlite3

# Caminho do banco de dados
db_path = r'instance/barbearia.db'

# Conecta ao banco
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Lista as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tabelas = cursor.fetchall()
print("Tabelas:", tabelas)

# Exemplo: listar usuários
print("\nUsuários:")
for row in cursor.execute("SELECT * FROM usuario"):
    print(row)

# Exemplo: listar agendamentos
print("\nAgendamentos:")
for row in cursor.execute("SELECT * FROM post"):
    print(row)

conn.close()