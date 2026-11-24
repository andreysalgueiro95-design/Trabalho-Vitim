"""Gerenciamento do banco SQLite do Solidário Tech.

O banco é criado automaticamente em data/ e não exige servidor externo.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Optional, Sequence

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "solidario_tech.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS doadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf TEXT NOT NULL UNIQUE,
    telefone TEXT,
    email TEXT,
    endereco TEXT,
    criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    atualizado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS doacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doador_id INTEGER NOT NULL,
    item TEXT NOT NULL,
    categoria TEXT NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    data_doacao TEXT NOT NULL DEFAULT (date('now', 'localtime')),
    validade TEXT,
    status TEXT NOT NULL DEFAULT 'Disponível'
        CHECK (status IN ('Disponível', 'Esgotado', 'Vencido')),
    criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    atualizado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (doador_id) REFERENCES doadores(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS distribuicoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doacao_id INTEGER NOT NULL,
    instituicao_destino TEXT NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    data_entrega TEXT NOT NULL DEFAULT (date('now', 'localtime')),
    responsavel TEXT NOT NULL,
    criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    atualizado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (doacao_id) REFERENCES doacoes(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_doacoes_doador ON doacoes(doador_id);
CREATE INDEX IF NOT EXISTS idx_doacoes_categoria ON doacoes(categoria);
CREATE INDEX IF NOT EXISTS idx_doacoes_data ON doacoes(data_doacao);
CREATE INDEX IF NOT EXISTS idx_doacoes_status ON doacoes(status);
CREATE INDEX IF NOT EXISTS idx_distribuicoes_doacao ON distribuicoes(doacao_id);
CREATE INDEX IF NOT EXISTS idx_distribuicoes_data ON distribuicoes(data_entrega);
"""


class DatabaseManager:
    """Centraliza conexões, transações e operações básicas do SQLite."""

    def __init__(self, db_path: Optional[Path | str] = None) -> None:
        self.db_path = Path(db_path) if db_path else DATABASE_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Abre conexão com chaves estrangeiras e timeout habilitados."""
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        """Garante commit, rollback e fechamento da conexão."""
        connection = self.get_connection()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        """Cria tabelas, índices e o usuário administrador inicial."""
        try:
            with self.connection() as connection:
                connection.executescript(SCHEMA)
                self._create_default_admin(connection)
        except sqlite3.Error as exc:
            raise RuntimeError(f"Falha ao inicializar o SQLite: {exc}") from exc

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> str:
        """Gera hash PBKDF2 com salt aleatório, sem armazenar senha em texto puro."""
        salt_value = salt or secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"),
            salt_value.encode("utf-8"), 200_000
        ).hex()
        return "pbkdf2_sha256$" + salt_value + "$" + digest

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """Valida uma senha usando comparação segura do hash."""
        try:
            algorithm, salt, expected = stored_hash.split("$", maxsplit=2)
            if algorithm != "pbkdf2_sha256":
                return False
            candidate = DatabaseManager.hash_password(password, salt).split("$")[-1]
            return hmac.compare_digest(candidate, expected)
        except (ValueError, AttributeError):
            return False

        def _create_default_admin(self, connection: sqlite3.Connection) -> None:
        """Garante a conta inicial andrey/123 para a apresentação."""
        andrey = connection.execute(
            "SELECT id FROM usuarios WHERE usuario = ?", ("andrey",)
        ).fetchone()

        if andrey is not None:
            return

        admin_anterior = connection.execute(
            "SELECT id FROM usuarios WHERE usuario = ?", ("admin",)
        ).fetchone()

        senha_hash = self.hash_password("123")

        if admin_anterior is not None:
            connection.execute(
                "UPDATE usuarios SET usuario = ?, senha_hash = ? WHERE id = ?",
                ("andrey", senha_hash, admin_anterior["id"])
            )
        else:
            connection.execute(
                "INSERT INTO usuarios (usuario, senha_hash) VALUES (?, ?)",
                ("andrey", senha_hash)
            )

    def execute(self, query: str, parameters: Sequence[Any] = ()) -> int:
        """Executa INSERT/UPDATE/DELETE e retorna o ID ou linhas afetadas."""
        with self.connection() as connection:
            cursor = connection.execute(query, parameters)
            return cursor.lastrowid or cursor.rowcount

    def fetch_one(
        self, query: str, parameters: Sequence[Any] = ()
    ) -> Optional[sqlite3.Row]:
        """Retorna um registro ou None."""
        with self.connection() as connection:
            return connection.execute(query, parameters).fetchone()

    def fetch_all(
        self, query: str, parameters: Sequence[Any] = ()
    ) -> list[sqlite3.Row]:
        """Retorna todos os registros encontrados."""
        with self.connection() as connection:
            return connection.execute(query, parameters).fetchall()


db = DatabaseManager()

if __name__ == "__main__":
    db.initialize()
    print(f"Banco inicializado: {db.db_path}")
