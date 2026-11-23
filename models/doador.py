"""Operações de domínio relacionadas aos doadores."""

import sqlite3
from typing import Optional

from database.db_manager import db


class Doador:
    """Representa e persiste um doador no banco SQLite."""

    @staticmethod
    def listar(termo: str = "") -> list[sqlite3.Row]:
        """Lista doadores; pesquisa por nome, CPF, telefone ou e-mail."""
        termo = f"%{termo.strip()}%"
        return db.fetch_all(
            """
            SELECT id, nome, cpf, telefone, email, endereco, criado_em
            FROM doadores
            WHERE nome LIKE ? OR cpf LIKE ? OR telefone LIKE ? OR email LIKE ?
            ORDER BY nome COLLATE NOCASE
            """,
            (termo, termo, termo, termo)
        )

    @staticmethod
    def buscar(doador_id: int) -> Optional[sqlite3.Row]:
        return db.fetch_one(
            "SELECT * FROM doadores WHERE id = ?", (doador_id,)
        )

    @staticmethod
    def cadastrar(
        nome: str, cpf: str, telefone: str, email: str, endereco: str
    ) -> int:
        return db.execute(
            """
            INSERT INTO doadores (nome, cpf, telefone, email, endereco)
            VALUES (?, ?, ?, ?, ?)
            """,
            (nome, cpf, telefone, email, endereco)
        )

    @staticmethod
    def atualizar(
        doador_id: int, nome: str, cpf: str, telefone: str,
        email: str, endereco: str
    ) -> None:
        db.execute(
            """
            UPDATE doadores
            SET nome = ?, cpf = ?, telefone = ?, email = ?, endereco = ?,
                atualizado_em = datetime('now', 'localtime')
            WHERE id = ?
            """,
            (nome, cpf, telefone, email, endereco, doador_id)
        )

    @staticmethod
    def excluir(doador_id: int) -> None:
        """Impede exclusão se houver doações relacionadas."""
        vinculadas = db.fetch_one(
            "SELECT COUNT(*) AS total FROM doacoes WHERE doador_id = ?",
            (doador_id,)
        )
        if vinculadas and vinculadas["total"] > 0:
            raise ValueError(
                "Este doador possui doações vinculadas e não pode ser excluído."
            )
        db.execute("DELETE FROM doadores WHERE id = ?", (doador_id,))
