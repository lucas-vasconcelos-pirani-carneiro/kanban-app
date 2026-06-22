# KanbanApp
Aplicação desktop de gerenciamento de projetos via método Kanban, desenvolvida como trabalho prático da disciplina de Engenharia de Software do Professor Fernando Chacon.

Integrantes:
- EDUARDO PEREIRA DE SOUSA  - 231018937
- LUCAS VASCONCELOS PIRANI CARNEIRO - 251031785 
- MARCELO MARQUES RODRIGUES - 221018960


## Tecnologias
- **Linguagem:** Python
- **Interface gráfica:** PyQt6
- **Banco de dados:** SQLite 3, via módulo sqlite3 nativo do Python.
- Tranformar em **Executável:** PyInstaller

## Arquitetura

O projeto adota uma arquitetura em camadas inspirada no padrão MVC:

- **View:** Telas e componentes da interface gráfica (PyQt6)
- **Controller:** Recebe eventos da View, valida entradas e aciona os Services
- **Service:** Contém as regras de negócio (ex: cálculo de métricas Kanban, validação de WIP limit)
- **Repository:** Responsável pelo acesso ao banco de dados (queries SQL via sqlite3)
- **Models:** Classes de domínio que representam as entidades (Usuário, Projeto, Quadro, Cartão etc.)

## Estrutura de Diretórios

```plaintext
📂 kanban
├── 📂 database
│   ├── SQLite-2.sql          # Script de criação das tabelas
│   ├── init_db.py            # Script de inicialização do banco
│   └── kanban.db             # Arquivo do banco de dados SQLite (Gerado automaticamente)
├── 📂 src
│   ├── 📂 models             # Classes de domínio (entidades)
│   ├── 📂 repositories
│   │   ├── 📂 interfaces     # Contratos dos repositórios (ABCs)
│   │   └── ...               # Implementações concretas
│   ├── 📂 services
│   │   ├── 📂 interfaces     # Contratos dos services (ABCs)
│   │   └── ...               # Implementações concretas
│   ├── 📂 controllers        # Intermediação entre View e Service
│   ├── 📂 views              # Telas e componentes CustomTkinter 
│   └── path_config.py        # Gerenciamento de caminhos dinâmicos (PyInstaller vs Script)
├── 📂 tests
│   ├── 📂 mocks              # Repositórios falsos para testes
│   ├── 📂 services           # Testes das regras de negócio
│   ├── 📂 repositories       # Testes de acesso ao banco
│   └── 📂 controllers        # Testes dos controllers
├── 📂 docs                   # Artefatos do trabalho (PDFs)
├── main.py                   # Ponto de entrada da aplicação
├── requirements.txt
└── README.md
```

## Autenticação

Cadastro e Login por e-mail e senha. 
  - As senhas são armazenadas com hash (bcrypt ou hashlib), nunca em texto puro.

## Configuração do Ambiente

1. Crie o ambiente virtual: `python3 -m venv .venv`
2. Ative o ambiente: `source .venv/bin/activate` (Linux/Mac) ou `.venv\Scripts\activate` (Windows)
3. Instale as dependências: `pip install -r requirements.txt`

## Como Executar

1. Instale as dependências:

```python
pip install -r requirements.txt
```

2. Execute:
```python
python main.py`
```

## Como gerar o executável
```python
pyinstaller --onefile --add-data "database/SQLite-2.sql;database" main.py
```
Se for gerar o executável no Linux ou Mac, troque o ponto e vírgula ; por dois pontos : no comando acima.
