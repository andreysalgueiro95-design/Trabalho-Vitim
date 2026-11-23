"""Operações de domínio relacionadas às doações."""

import sqlite3
from typing import Optional

from database.db_manager import db


class Doacao:
    """Representa e persiste uma doação no banco SQLite."""

    @staticmethod
    def listar(termo: str = "") -> list[sqlite3.Row]:
        """Lista doações e permite pesquisar item, categoria, doador ou status."""
        termo = f"%{termo.strip()}%"
        return db.fetch_all(
            """
            SELECT
                d.id, d.doador_id, d.item, d.categoria, d.quantidade,
                d.data_doacao, d.validade,
                CASE
                    WHEN d.status != 'Esgotado'
                         AND d.validade IS NOT NULL
                         AND d.validade < date('now', 'localtime')
                    THEN 'Vencido'
                    ELSE d.status
                END AS status,
                d.criado_em, do.nome AS nome_doador
            FROM doacoes d
            INNER JOIN doadores do ON do.id = d.doador_id
            WHERE d.item LIKE ?
               OR d.categoria LIKE ?
               OR do.nome LIKE ?
               OR d.status LIKE ?
            ORDER BY d.data_doacao DESC, d.id DESC
            """,
            (termo, termo, termo, termo)
        )

    @staticmethod
    def buscar(doacao_id: int) -> Optional[sqlite3.Row]:
        """Busca uma doação pelo identificador."""
        return db.fetch_one(
            "SELECT * FROM doacoes WHERE id = ?", (doacao_id,)
        )

    @staticmethod
    def listar_doadores() -> list[sqlite3.Row]:
        """Retorna os doadores disponíveis para vincular a uma doação."""
        return db.fetch_all(
            "SELECT id, nome FROM doadores ORDER BY nome COLLATE NOCASE"
        )

    @staticmethod
    def cadastrar(
        doador_id: int,
        item: str,
        categoria: str,
        quantidade: int,
        data_doacao: str,
        validade: str,
        status: str
    ) -> int:
        """Cadastra uma nova doação."""
        return db.execute(
            """
            INSERT INTO doacoes
                (doador_id, item, categoria, quantidade,
                 data_doacao, validade, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doador_id, item, categoria, quantidade,
                data_doacao, validade or None, status
            )
        )

    @staticmethod
    def atualizar(
        doacao_id: int,
        doador_id: int,
        item: str,
        categoria: str,
        quantidade: int,
        data_doacao: str,
        validade: str,
        status: str
    ) -> None:
        """Atualiza os dados de uma doação existente."""
        db.execute(
            """
            UPDATE doacoes
            SET doador_id = ?, item = ?, categoria = ?, quantidade = ?,
                data_doacao = ?, validade = ?, status = ?,
                atualizado_em = datetime('now', 'localtime')
            WHERE id = ?
            """,
            (
                doador_id, item, categoria, quantidade,
                data_doacao, validade or None, status, doacao_id
            )
        )

    @staticmethod
    def excluir(doacao_id: int) -> None:
        """Impede exclusão de doações que já possuam distribuições vinculadas."""
        vinculadas = db.fetch_one(
            "SELECT COUNT(*) AS total FROM distribuicoes WHERE doacao_id = ?",
            (doacao_id,)
        )
        if vinculadas and vinculadas["total"] > 0:
            raise ValueError(
                "Esta doação possui distribuições vinculadas e não pode ser excluída."
            )
        db.execute("DELETE FROM doacoes WHERE id = ?", (doacao_id,))
