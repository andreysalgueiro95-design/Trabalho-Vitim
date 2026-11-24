"""Janela principal com menu lateral e área de conteúdo."""

import customtkinter as ctk

from views.tela_doadores import TelaDoadores
from views.tela_doacoes import TelaDoacoes
from views.tela_distribuicoes import TelaDistribuicoes
from views.tela_dashboard import TelaDashboard

from utils.estilos import (
    COR_FUNDO, COR_PRIMARIA, COR_VERDE, COR_TEXTO,
    COR_TEXTO_SECUNDARIO, COR_SUPERFICIE, FONTE
)


class TelaPrincipal(ctk.CTkFrame):
    """Estrutura principal da aplicação após o login."""

    def __init__(self, master, usuario: str, on_logout) -> None:
        super().__init__(master, fg_color=COR_FUNDO)
        self.usuario = usuario
        self.on_logout = on_logout
        self.pack(fill="both", expand=True)
        self._montar_interface()
        self.mostrar_inicio()

    def _montar_interface(self) -> None:
        self.sidebar = ctk.CTkFrame(
            self, width=235, corner_radius=0, fg_color=COR_PRIMARIA
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar, text="Solidário Tech",
            text_color="#FFFFFF", font=(FONTE, 21, "bold")
        ).pack(anchor="w", padx=22, pady=(30, 4))

        ctk.CTkLabel(
            self.sidebar, text="GESTÃO SOLIDÁRIA",
            text_color="#B9D0E2", font=(FONTE, 10, "bold")
        ).pack(anchor="w", padx=23, pady=(0, 28))

        menu = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        menu.pack(fill="x", padx=12)

        opcoes = [
            ("⌂", "Início", self.mostrar_inicio),
            ("♙", "Doadores", self.mostrar_doadores),
            ("＋", "Doações", self.mostrar_doacoes),
            ("⇢", "Distribuições", self.mostrar_distribuicoes),
            ("▦", "Relatórios", self._modulo_em_breve),
        ]
        for simbolo, nome, comando in opcoes:
            ctk.CTkButton(
                menu, text=f"  {simbolo}   {nome}", anchor="w",
                height=43, corner_radius=8, fg_color="transparent",
                hover_color="#24577F", text_color="#FFFFFF",
                font=(FONTE, 13), command=comando
            ).pack(fill="x", pady=3)

        ctk.CTkButton(
            self.sidebar, text="Sair da conta", height=40,
            fg_color="#FFFFFF", hover_color="#E8EEF3",
            text_color=COR_PRIMARIA, corner_radius=8,
            command=self.on_logout
        ).pack(side="bottom", fill="x", padx=15, pady=20)

        self.conteudo = ctk.CTkFrame(self, fg_color=COR_FUNDO)
        self.conteudo.pack(side="left", fill="both", expand=True)

        topo = ctk.CTkFrame(
            self.conteudo, fg_color=COR_SUPERFICIE, height=66
        )
        topo.pack(fill="x")
        topo.pack_propagate(False)

        ctk.CTkLabel(
            topo, text="Painel de gerenciamento",
            text_color=COR_TEXTO, font=(FONTE, 16, "bold")
        ).pack(side="left", padx=26)

        ctk.CTkLabel(
            topo, text=f"Conectado: {self.usuario}",
            text_color=COR_TEXTO_SECUNDARIO, font=(FONTE, 12)
        ).pack(side="right", padx=26)

        self.pagina = ctk.CTkFrame(self.conteudo, fg_color="transparent")
        self.pagina.pack(fill="both", expand=True, padx=28, pady=26)

    def _limpar_pagina(self) -> None:
        for widget in self.pagina.winfo_children():
            widget.destroy()

    def mostrar_inicio(self) -> None:
        """Abre o painel de indicadores e gráficos."""
        self._limpar_pagina()
        TelaDashboard(self.pagina)

    def mostrar_doadores(self) -> None:
        """Abre o módulo de gerenciamento de doadores."""
        self._limpar_pagina()
        TelaDoadores(self.pagina)

    def mostrar_doacoes(self) -> None:
        """Abre o módulo de gerenciamento de doações."""
        self._limpar_pagina()
        TelaDoacoes(self.pagina)

    def mostrar_distribuicoes(self) -> None:
        """Abre o módulo de gerenciamento de distribuições."""
        self._limpar_pagina()
        TelaDistribuicoes(self.pagina)

    def _modulo_em_breve(self) -> None:
        self._limpar_pagina()
        ctk.CTkLabel(
            self.pagina, text="Módulo em desenvolvimento",
            text_color=COR_TEXTO, font=(FONTE, 24, "bold")
        ).pack(anchor="w", pady=10)
        ctk.CTkLabel(
            self.pagina,
            text="Esta área será implementada nas próximas etapas.",
            text_color=COR_TEXTO_SECUNDARIO, font=(FONTE, 14)
        ).pack(anchor="w")
