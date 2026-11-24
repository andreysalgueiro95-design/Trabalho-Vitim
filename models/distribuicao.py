"""Regras de negócio e persistência das distribuições."""

import sqlite3
from datetime import date

from database.db_manager import db


class Distribuicao:
    """Registra entregas e mantém o saldo das doações consistente."""

    @staticmethod
    def listar(termo: str = "") -> list[sqlite3.Row]:
        filtro = f"%{termo.strip()}%"
        return db.fetch_all(
            """
            SELECT
                di.id, di.doacao_id, di.instituicao_destino,
                di.quantidade, di.data_entrega, di.responsavel,
                d.item, d.categoria, do.nome AS nome_doador
            FROM distribuicoes di
            INNER JOIN doacoes d ON d.id = di.doacao_id
            INNER JOIN doadores do ON do.id = d.doador_id
            WHERE di.instituicao_destino LIKE ?
               OR di.responsavel LIKE ?
               OR d.item LIKE ?
               OR do.nome LIKE ?
            ORDER BY di.data_entrega DESC, di.id DESC
            """,
            (filtro, filtro, filtro, filtro)
        )

    @staticmethod
    def buscar(distribuicao_id: int):
        return db.fetch_one(
            "SELECT * FROM distribuicoes WHERE id = ?", (distribuicao_id,)
        )

    @staticmethod
    def listar_doacoes_disponiveis(doacao_atual_id: int | None = None):
        """Lista doações com saldo; inclui a doação atual durante a edição."""
        return db.fetch_all(
            """
            SELECT d.id, d.item, d.categoria, d.quantidade,
                   d.validade, do.nome AS nome_doador
            FROM doacoes d
            INNER JOIN doadores do ON do.id = d.doador_id
            WHERE (
                d.quantidade > 0
                AND d.status = 'Disponível'
                AND (d.validade IS NULL OR d.validade >= date('now', 'localtime'))
            ) OR d.id = ?
            ORDER BY d.item COLLATE NOCASE
            """,
            (doacao_atual_id,)
        )

    @staticmethod
    def _validar_saldo(doacao, quantidade: int) -> None:
        if doacao is None:
            raise ValueError("A doação selecionada não existe.")
        if doacao["validade"] and doacao["validade"] < date.today().isoformat():
            raise ValueError("Não é permitido distribuir um item vencido.")
        if doacao["status"] == "Vencido":
            raise ValueError("Esta doação está vencida.")
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        if quantidade > doacao["quantidade"]:
            raise ValueError(
                f"Estoque insuficiente. Saldo disponível: {doacao['quantidade']}."
            )

    @staticmethod
    def cadastrar(
        doacao_id: int, instituicao_destino: str, quantidade: int,
        data_entrega: str, responsavel: str
    ) -> int:
        with db.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            doacao = connection.execute(
                "SELECT id, quantidade, validade, status FROM doacoes WHERE id = ?",
                (doacao_id,)
            ).fetchone()
            Distribuicao._validar_saldo(doacao, quantidade)

            cursor = connection.execute(
                """
                INSERT INTO distribuicoes
                    (doacao_id, instituicao_destino, quantidade, data_entrega, responsavel)
                VALUES (?, ?, ?, ?, ?)
                """,
                (doacao_id, instituicao_destino, quantidade, data_entrega, responsavel)
            )
            novo_saldo = doacao["quantidade"] - quantidade
            novo_status = "Esgotado" if novo_saldo == 0 else "Disponível"
            connection.execute(
                """
                UPDATE doacoes
                SET quantidade = ?, status = ?,
                    atualizado_em = datetime('now', 'localtime')
                WHERE id = ?
                """,
                (novo_saldo, novo_status, doacao_id)
            )
            return int(cursor.lastrowid)

    @staticmethod
    def atualizar(
        distribuicao_id: int, doacao_id: int, instituicao_destino: str,
        quantidade: int, data_entrega: str, responsavel: str
    ) -> None:
        with db.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            anterior = connection.execute(
                "SELECT * FROM distribuicoes WHERE id = ?", (distribuicao_id,)
            ).fetchone()
            if anterior is None:
                raise ValueError("A distribuição não foi encontrada.")

            # Devolve o saldo da entrega anterior antes de validar a nova operação.
            antiga = connection.execute(
                "SELECT id, quantidade, validade FROM doacoes WHERE id = ?",
                (anterior["doacao_id"],)
            ).fetchone()
            if antiga is None:
                raise ValueError("A doação vinculada não foi encontrada.")
            saldo_restaurado = antiga["quantidade"] + anterior["quantidade"]
            status_restaurado = (
                "Vencido" if antiga["validade"] and
                antiga["validade"] < date.today().isoformat()
                else "Disponível"
            )
            connection.execute(
                """
                UPDATE doacoes
                SET quantidade = ?, status = ?,
                    atualizado_em = datetime('now', 'localtime')
                WHERE id = ?
                """,
                (saldo_restaurado, status_restaurado, anterior["doacao_id"])
            )

            nova = connection.execute(
                "SELECT id, quantidade, validade, status FROM doacoes WHERE id = ?",
                (doacao_id,)
            ).fetchone()
            Distribuicao._validar_saldo(nova, quantidade)

            connection.execute(
                """
                UPDATE distribuicoes
                SET doacao_id = ?, instituicao_destino = ?, quantidade = ?,
                    data_entrega = ?, responsavel = ?,
                    atualizado_em = datetime('now', 'localtime')
                WHERE id = ?
                """,
                (
                    doacao_id, instituicao_destino, quantidade,
                    data_entrega, responsavel, distribuicao_id
                )
            )
            novo_saldo = nova["quantidade"] - quantidade
            novo_status = "Esgotado" if novo_saldo == 0 else "Disponível"
            connection.execute(
                """
                UPDATE doacoes
                SET quantidade = ?, status = ?,
                    atualizado_em = datetime('now', 'localtime')
                WHERE id = ?
                """,
                (novo_saldo, novo_status, doacao_id)
            )

    @staticmethod
    def excluir(distribuicao_id: int) -> None:
        with db.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            registro = connection.execute(
                "SELECT * FROM distribuicoes WHERE id = ?", (distribuicao_id,)
            ).fetchone()
            if registro is None:
                raise ValueError("A distribuição não foi encontrada.")

            doacao = connection.execute(
                "SELECT id, quantidade, validade FROM doacoes WHERE id = ?",
                (registro["doacao_id"],)
            ).fetchone()
            if doacao is None:
                raise ValueError("A doação vinculada não foi encontrada.")

            saldo = doacao["quantidade"] + registro["quantidade"]
            status = (
                "Vencido" if doacao["validade"] and
                doacao["validade"] < date.today().isoformat()
                else "Disponível"
            )
            connection.execute(
                """
                UPDATE doacoes
                SET quantidade = ?, status = ?,
                    atualizado_em = datetime('now', 'localtime')
                WHERE id = ?
                """,
                (saldo, status, registro["doacao_id"])
            )
            connection.execute(
                "DELETE FROM distribuicoes WHERE id = ?", (distribuicao_id,)
            )
