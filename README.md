# Solidário Tech

Sistema desktop de gerenciamento de doações para instituições de caridade, desenvolvido em Python.

## Tecnologias

- Python 3.10 ou superior
- CustomTkinter (interface gráfica)
- SQLite (banco de dados local)
- Matplotlib (gráficos)
- Pillow (imagens)

## Etapa atual: estrutura e banco de dados

A primeira versão da interface já inclui tela de login, autenticação pelo SQLite, janela principal e menu lateral. Os módulos de cadastro e relatórios serão conectados nas próximas etapas.

## Como executar

1. Instale o Python 3.10 ou superior.
2. Abra o terminal na pasta do projeto.
3. (Recomendado) Crie e ative um ambiente virtual:

   **Windows PowerShell**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

5. Inicialize:
   ```bash
   python main.py
   ```

O banco será criado automaticamente em `data/solidario_tech.db` e a janela de login será aberta.

## Acesso inicial

- Usuário: `admin`
- Senha: `admin`

A senha é armazenada com hash PBKDF2. A tela principal abre após autenticação válida. Altere a senha padrão quando o gerenciamento de usuários estiver disponível.

## Estrutura

- `database/`: conexão, esquema e operações SQLite.
- `models/`: entidades do sistema.
- `views/`: telas da interface.
- `controllers/`: regras de aplicação.
- `utils/`: validações e estilos.
- `assets/`: imagens e recursos visuais.

O SQLite e o módulo `sqlite3` já fazem parte do Python. Não é necessário instalar um servidor de banco de dados.
