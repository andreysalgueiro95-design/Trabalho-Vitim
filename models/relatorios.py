"""Consultas e montagem dos dados para os relatórios do sistema."""

from database.db_manager import db


class Relatorios:
    """Centraliza consultas de relatórios, sem modificar dados do sistema."""

    @staticmethod
    def gerar(tipo: str, data_inicial: str = "", data_final: str = "") -> dict:
        inicio = data_inicial.strip()
        fim = data_final.strip()
        if inicio and fim and inicio > fim:
            raise ValueError("A data inicial não pode ser posterior à data final.")

        if tipo == "Doações recebidas":
            where, params = Relatorios._periodo("d.data_doacao", inicio, fim)
            registros = db.fetch_all(
                f"""
                SELECT d.data_doacao, d.item, d.categoria, d.quantidade,
                       do.nome AS doador, COALESCE(d.validade, 'Não informada') AS validade
                FROM doacoes d
                INNER JOIN doadores do ON do.id = d.doador_id
                {where}
                ORDER BY date(d.data_doacao) DESC, d.id DESC
                """,
                params
            )
            return Relatorios._resultado(
                "Relatório de doações recebidas",
                ["Data", "Item", "Categoria", "Quantidade", "Doador", "Validade"],
                [[r["data_doacao"], r["item"], r["categoria"], r["quantidade"],
                  r["doador"], r["validade"]] for r in registros],
                "Registros encontrados",
            )

        if tipo == "Distribuições realizadas":
            where, params = Relatorios._periodo("di.data_entrega", inicio, fim)
            registros = db.fetch_all(
                f"""
                SELECT di.data_entrega, d.item, di.quantidade,
                       di.instituicao_destino, di.responsavel, do.nome AS doador
                FROM distribuicoes di
                INNER JOIN doacoes d ON d.id = di.doacao_id
                INNER JOIN doadores do ON do.id = d.doador_id
                {where}
                ORDER BY date(di.data_entrega) DESC, di.id DESC
                """,
                params
            )
            return Relatorios._resultado(
                "Relatório de distribuições realizadas",
                ["Data", "Item", "Quantidade", "Instituição", "Responsável", "Doador"],
                [[r["data_entrega"], r["item"], r["quantidade"],
                  r["instituicao_destino"], r["responsavel"], r["doador"]]
                 for r in registros],
                "Entregas encontradas",
            )

        if tipo == "Estoque atual":
            registros = db.fetch_all(
                """
                SELECT d.item, d.categoria, d.quantidade, do.nome AS doador,
                       COALESCE(d.validade, 'Não informada') AS validade,
                       CASE
                         WHEN d.validade IS NOT NULL
                              AND d.validade < date('now', 'localtime') THEN 'Vencido'
                         WHEN d.quantidade <= 0 OR d.status = 'Esgotado' THEN 'Esgotado'
                         ELSE 'Disponível'
                       END AS situacao
                FROM doacoes d
                INNER JOIN doadores do ON do.id = d.doador_id
                ORDER BY d.item COLLATE NOCASE
                """
            )
            return Relatorios._resultado(
                "Relatório de estoque atual",
                ["Item", "Categoria", "Quantidade", "Doador", "Validade", "Situação"],
                [[r["item"], r["categoria"], r["quantidade"], r["doador"],
                  r["validade"], r["situacao"]] for r in registros],
                "Itens cadastrados",
            )

        if tipo == "Resumo por instituição":
            where, params = Relatorios._periodo("di.data_entrega", inicio, fim)
            registros = db.fetch_all(
                f"""
                SELECT di.instituicao_destino,
                       COUNT(*) AS entregas,
                       SUM(di.quantidade) AS itens,
                       MAX(date(di.data_entrega)) AS ultima_entrega
                FROM distribuicoes di
                {where}
                GROUP BY di.instituicao_destino
                ORDER BY itens DESC, di.instituicao_destino COLLATE NOCASE
                """,
                params
            )
            return Relatorios._resultado(
                "Resumo de entregas por instituição",
                ["Instituição", "Entregas", "Itens recebidos", "Última entrega"],
                [[r["instituicao_destino"], r["entregas"], r["itens"],
                  r["ultima_entrega"]] for r in registros],
                "Instituições atendidas",
            )

        raise ValueError("Tipo de relatório inválido.")

    @staticmethod
    def _periodo(coluna: str, inicio: str, fim: str) -> tuple[str, tuple]:
        condicoes = []
        parametros = []
        if inicio:
            condicoes.append(f"date({coluna}) >= date(?)")
            parametros.append(inicio)
        if fim:
            condicoes.append(f"date({coluna}) <= date(?)")
            parametros.append(fim)
        where = "WHERE " + " AND ".join(condicoes) if condicoes else ""
        return where, tuple(parametros)

    @staticmethod
    def _resultado(titulo: str, colunas: list, linhas: list, rotulo: str) -> dict:
        return {
            "titulo": titulo,
            "colunas": colunas,
            "linhas": linhas,
            "total_registros": len(linhas),
            "total_quantidade": sum(
                int(linha[2]) for linha in linhas
                if len(linha) > 2 and isinstance(linha[2], (int, float))
            ),
            "rotulo_total": rotulo,
        }
