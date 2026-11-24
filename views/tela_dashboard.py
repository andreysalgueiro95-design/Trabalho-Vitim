"""Painel inicial com indicadores e gráficos do Solidário Tech."""

import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from models.dashboard import Dashboard
from utils.estilos import (
    COR_BORDA, COR_FUNDO, COR_PRIMARIA, COR_SUPERFICIE,
    COR_TEXTO, COR_TEXTO_SECUNDARIO, COR_VERDE, FONTE
)


class TelaDashboard(ctk.CTkFrame):
    """Exibe um resumo atualizado dos dados cadastrados no sistema."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self._montar_interface()

    def _montar_interface(self):
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", pady=(0, 18))

        textos = ctk.CTkFrame(topo, fg_color="transparent")
        textos.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            textos, text="Visão geral",
            text_color=COR_TEXTO, font=(FONTE, 27, "bold")
        ).pack(anchor="w")
        ctk.CTkLabel(
            textos,
            text="Acompanhe os principais números das operações solidárias.",
            text_color=COR_TEXTO_SECUNDARIO, font=(FONTE, 13)
        ).pack(anchor="w", pady=(3, 0))

        ctk.CTkButton(
            topo, text="Atualizar painel", width=145, height=36,
            fg_color=COR_PRIMARIA, hover_color="#24577F",
            command=self.atualizar
        ).pack(side="right", padx=(10, 0), pady=5)

        self.area = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0
        )
        self.area.pack(fill="both", expand=True)

        self.cartoes = ctk.CTkFrame(self.area, fg_color="transparent")
        self.cartoes.pack(fill="x", pady=(0, 16))

        self.graficos = ctk.CTkFrame(self.area, fg_color="transparent")
        self.graficos.pack(fill="both", expand=True)

        self.recentes = ctk.CTkFrame(
            self.area, fg_color=COR_SUPERFICIE,
            corner_radius=12, border_width=1, border_color=COR_BORDA
        )
        self.recentes.pack(fill="x", pady=(0, 18))

        self.atualizar()

    def _limpar(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def atualizar(self):
        indicadores = Dashboard.obter_indicadores()
        self._montar_cartoes(indicadores)
        self._montar_graficos()
        self._montar_recentes()

    def _montar_cartoes(self, dados):
        self._limpar(self.cartoes)
        cartoes = [
            ("Doadores cadastrados", dados["doadores"], COR_PRIMARIA),
            ("Doações registradas", dados["doacoes"], COR_VERDE),
            ("Itens disponíveis", dados["estoque"], COR_PRIMARIA),
            ("Distribuições realizadas", dados["distribuicoes"], COR_VERDE),
        ]

        for coluna in range(4):
            self.cartoes.grid_columnconfigure(coluna, weight=1, uniform="cards")

        for coluna, (titulo, valor, destaque) in enumerate(cartoes):
            card = ctk.CTkFrame(
                self.cartoes, fg_color=COR_SUPERFICIE,
                corner_radius=12, border_width=1, border_color=COR_BORDA
            )
            card.grid(row=0, column=coluna, sticky="nsew",
                      padx=(0 if coluna == 0 else 7, 7 if coluna < 3 else 0))
            ctk.CTkLabel(
                card, text=titulo, text_color=COR_TEXTO_SECUNDARIO,
                font=(FONTE, 12), wraplength=150
            ).pack(anchor="w", padx=15, pady=(15, 7))
            ctk.CTkLabel(
                card, text=f"{valor:,}".replace(",", "."),
                text_color=destaque, font=(FONTE, 27, "bold")
            ).pack(anchor="w", padx=15, pady=(0, 15))

        ctk.CTkLabel(
            self.cartoes,
            text=f"Total de itens já distribuídos: {dados['itens_distribuidos']:,}".replace(",", "."),
            text_color=COR_TEXTO_SECUNDARIO, font=(FONTE, 11)
        ).grid(row=1, column=0, columnspan=4, sticky="w", pady=(9, 0))

    def _montar_graficos(self):
        self._limpar(self.graficos)
        for coluna in range(2):
            self.graficos.grid_columnconfigure(coluna, weight=1, uniform="charts")

        categorias = Dashboard.distribuicoes_por_categoria()
        meses = Dashboard.distribuicoes_por_mes()

        card_categoria = ctk.CTkFrame(
            self.graficos, fg_color=COR_SUPERFICIE,
            corner_radius=12, border_width=1, border_color=COR_BORDA
        )
        card_categoria.grid(row=0, column=0, sticky="nsew", padx=(0, 7), pady=4)

        card_meses = ctk.CTkFrame(
            self.graficos, fg_color=COR_SUPERFICIE,
            corner_radius=12, border_width=1, border_color=COR_BORDA
        )
        card_meses.grid(row=0, column=1, sticky="nsew", padx=(7, 0), pady=4)

        self._titulo_card(card_categoria, "Itens distribuídos por categoria")
        self._titulo_card(card_meses, "Distribuições nos últimos 6 meses")

        fig1 = Figure(figsize=(4.2, 2.8), dpi=90, facecolor=COR_SUPERFICIE)
        ax1 = fig1.add_subplot(111)
        if categorias:
            nomes = [r["categoria"] for r in categorias]
            valores = [r["total"] for r in categorias]
            ax1.barh(nomes[::-1], valores[::-1], color=COR_VERDE)
            ax1.set_xlabel("Quantidade de itens")
            ax1.grid(axis="x", alpha=0.2)
            ax1.set_axisbelow(True)
        else:
            ax1.text(0.5, 0.5, "Ainda não há distribuições",
                     ha="center", va="center", color=COR_TEXTO_SECUNDARIO,
                     transform=ax1.transAxes)
            ax1.set_xticks([])
            ax1.set_yticks([])
        fig1.tight_layout()
        self._inserir_grafico(card_categoria, fig1)

        fig2 = Figure(figsize=(4.2, 2.8), dpi=90, facecolor=COR_SUPERFICIE)
        ax2 = fig2.add_subplot(111)
        if meses:
            rotulos = [r["mes"] for r in meses]
            valores = [r["total"] for r in meses]
            ax2.plot(rotulos, valores, marker="o", linewidth=2, color=COR_PRIMARIA)
            ax2.fill_between(range(len(valores)), valores, alpha=0.10,
                             color=COR_PRIMARIA)
            ax2.set_ylabel("Itens entregues")
            ax2.tick_params(axis="x", rotation=25)
            ax2.grid(axis="y", alpha=0.2)
            ax2.set_axisbelow(True)
        else:
            ax2.text(0.5, 0.5, "Ainda não há distribuições",
                     ha="center", va="center", color=COR_TEXTO_SECUNDARIO,
                     transform=ax2.transAxes)
            ax2.set_xticks([])
            ax2.set_yticks([])
        fig2.tight_layout()
        self._inserir_grafico(card_meses, fig2)

    @staticmethod
    def _titulo_card(card, titulo):
        ctk.CTkLabel(
            card, text=titulo, text_color=COR_TEXTO,
            font=(FONTE, 14, "bold")
        ).pack(anchor="w", padx=16, pady=(15, 0))

    @staticmethod
    def _inserir_grafico(card, figura):
        canvas = FigureCanvasTkAgg(figura, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    def _montar_recentes(self):
        self._limpar(self.recentes)
        ctk.CTkLabel(
            self.recentes, text="Últimas distribuições",
            text_color=COR_TEXTO, font=(FONTE, 15, "bold")
        ).pack(anchor="w", padx=17, pady=(15, 8))

        registros = Dashboard.ultimas_distribuicoes()
        if not registros:
            ctk.CTkLabel(
                self.recentes, text="Nenhuma distribuição registrada até o momento.",
                text_color=COR_TEXTO_SECUNDARIO, font=(FONTE, 12)
            ).pack(anchor="w", padx=17, pady=(0, 15))
            return

        cabecalho = ctk.CTkFrame(self.recentes, fg_color=COR_FUNDO, corner_radius=6)
        cabecalho.pack(fill="x", padx=12, pady=(0, 5))
        for texto, peso in [("Item / Instituição", 3), ("Quantidade", 1),
                            ("Data", 1), ("Responsável", 2)]:
            ctk.CTkLabel(
                cabecalho, text=texto, text_color=COR_TEXTO_SECUNDARIO,
                font=(FONTE, 11, "bold"), anchor="w"
            ).pack(side="left", fill="x", expand=True, padx=8, pady=8)

        for registro in registros:
            linha = ctk.CTkFrame(self.recentes, fg_color="transparent")
            linha.pack(fill="x", padx=12)
            valores = [
                f"{registro['item']} / {registro['instituicao_destino']}",
                str(registro["quantidade"]),
                registro["data_entrega"],
                registro["responsavel"],
            ]
            for valor in valores:
                ctk.CTkLabel(
                    linha, text=valor, text_color=COR_TEXTO,
                    font=(FONTE, 11), anchor="w"
                ).pack(side="left", fill="x", expand=True, padx=8, pady=7)
            ctk.CTkFrame(
                self.recentes, height=1, fg_color=COR_BORDA
            ).pack(fill="x", padx=12)
