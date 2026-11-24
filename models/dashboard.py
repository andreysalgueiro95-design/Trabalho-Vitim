"""Consultas agregadas utilizadas pelo painel inicial."""

from database.db_manager import db


class Dashboard:
    """Fornece indicadores e séries resumidas sem alterar os registros."""

    @staticmethod
    def obter_indicadores() -> dict:
        doadores = db.fetch_one("SELECT COUNT(*) AS total FROM doadores")
        doacoes = db.fetch_one("SELECT COUNT(*) AS total FROM doacoes")
        estoque = db.fetch_one(
            """
            SELECT COALESCE(SUM(quantidade), 0) AS total
            FROM doacoes
            WHERE status = 'Disponível'
              AND (validade IS NULL OR validade >= date('now', 'localtime'))
            """
        )
        distribuicoes = db.fetch_one(
            "SELECT COUNT(*) AS total FROM distribuicoes"
        )
        itens_distribuidos = db.fetch_one(
            "SELECT COALESCE(SUM(quantidade), 0) AS total FROM distribuicoes"
        )
        return {
            "doadores": int(doadores["total"]),
            "doacoes": int(doacoes["total"]),
            "estoque": int(estoque["total"]),
            "distribuicoes": int(distribuicoes["total"]),
            "itens_distribuidos": int(itens_distribuidos["total"]),
        }

    @staticmethod
    def distribuicoes_por_categoria() -> list:
        return db.fetch_all(
            """
            SELECT d.categoria, COALESCE(SUM(di.quantidade), 0) AS total
            FROM distribuicoes di
            INNER JOIN doacoes d ON d.id = di.doacao_id
            GROUP BY d.categoria
            HAVING SUM(di.quantidade) > 0
            ORDER BY total DESC, d.categoria
            """
        )

    @staticmethod
    def distribuicoes_por_mes() -> list:
        return db.fetch_all(
            """
            SELECT strftime('%Y-%m', data_entrega) AS mes,
                   SUM(quantidade) AS total
            FROM distribuicoes
            WHERE date(data_entrega) >= date('now', 'localtime', '-5 months', 'start of month')
            GROUP BY strftime('%Y-%m', data_entrega)
            ORDER BY mes
            """
        )

    @staticmethod
    def ultimas_distribuicoes(limite: int = 5) -> list:
        return db.fetch_all(
            """
            SELECT di.instituicao_destino, di.quantidade, di.data_entrega,
                   di.responsavel, d.item
            FROM distribuicoes di
            INNER JOIN doacoes d ON d.id = di.doacao_id
            ORDER BY date(di.data_entrega) DESC, di.id DESC
            LIMIT ?
            """,
            (limite,)
        )
