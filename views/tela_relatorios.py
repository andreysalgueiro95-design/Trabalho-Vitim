"""Interface de consulta e exportação de relatórios em PDF."""

from datetime import datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)

from models.relatorios import Relatorios
from utils.estilos import (
    COR_BORDA, COR_FUNDO, COR_PRIMARIA, COR_SUPERFICIE,
    COR_TEXTO, COR_TEXTO_SECUNDARIO, COR_VERDE, FONTE
)


class TelaRelatorios(ctk.CTkFrame):
    """Permite filtrar, visualizar e exportar relatórios em PDF."""

    TIPOS = [
        "Doações recebidas",
        "Distribuições realizadas",
        "Estoque atual",
        "Resumo por instituição",
    ]

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.resultado_atual = None
        self._montar_interface()

    def _montar_interface(self):
        ctk.CTkLabel(
            self, text="Relatórios",
            text_color=COR_TEXTO, font=(FONTE, 27, "bold")
        ).pack(anchor="w")
        ctk.CTkLabel(
            self, text="Consulte os registros e exporte documentos em PDF.",
            text_color=COR_TEXTO_SECUNDARIO, font=(FONTE, 13)
        ).pack(anchor="w", pady=(3, 18))

        filtros = ctk.CTkFrame(
            self, fg_color=COR_SUPERFICIE, corner_radius=12,
            border_width=1, border_color=COR_BORDA
        )
        filtros.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            filtros, text="Tipo de relatório", text_color=COR_TEXTO,
            font=(FONTE, 12, "bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(14, 4))

        self.tipo = ctk.CTkOptionMenu(
            filtros, values=self.TIPOS, width=230,
            fg_color=COR_PRIMARIA, button_color=COR_PRIMARIA,
            button_hover_color="#24577F"
        )
        self.tipo.set(self.TIPOS[0])
        self.tipo.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 14))

        ctk.CTkLabel(
            filtros, text="Data inicial (AAAA-MM-DD)",
            text_color=COR_TEXTO, font=(FONTE, 12, "bold")
        ).grid(row=0, column=1, sticky="w", padx=10, pady=(14, 4))
        self.data_inicial = ctk.CTkEntry(
            filtros, width=165, placeholder_text="Ex.: 2026-01-01"
        )
        self.data_inicial.grid(row=1, column=1, sticky="w", padx=10, pady=(0, 14))

        ctk.CTkLabel(
            filtros, text="Data final (AAAA-MM-DD)",
            text_color=COR_TEXTO, font=(FONTE, 12, "bold")
        ).grid(row=0, column=2, sticky="w", padx=10, pady=(14, 4))
        self.data_final = ctk.CTkEntry(
            filtros, width=165, placeholder_text="Ex.: 2026-12-31"
        )
        self.data_final.grid(row=1, column=2, sticky="w", padx=10, pady=(0, 14))

        botoes = ctk.CTkFrame(filtros, fg_color="transparent")
        botoes.grid(row=1, column=3, padx=15, pady=(0, 14), sticky="e")
        ctk.CTkButton(
            botoes, text="Consultar", width=110,
            fg_color=COR_PRIMARIA, hover_color="#24577F",
            command=self.consultar
        ).pack(side="left", padx=(0, 7))
        self.exportar_btn = ctk.CTkButton(
            botoes, text="Exportar PDF", width=120,
            fg_color=COR_VERDE, hover_color="#1B6E49",
            command=self.exportar_pdf, state="disabled"
        )
        self.exportar_btn.pack(side="left")

        for coluna in range(4):
            filtros.grid_columnconfigure(coluna, weight=1 if coluna == 3 else 0)

        self.resumo = ctk.CTkLabel(
            self, text="Selecione um relatório e clique em Consultar.",
            text_color=COR_TEXTO_SECUNDARIO, font=(FONTE, 12)
        )
        self.resumo.pack(anchor="w", pady=(0, 8))

        self.tabela = ctk.CTkTextbox(
            self, fg_color=COR_SUPERFICIE, text_color=COR_TEXTO,
            border_width=1, border_color=COR_BORDA,
            corner_radius=10, font=("Consolas", 11), wrap="none"
        )
        self.tabela.pack(fill="both", expand=True)
        self.tabela.configure(state="disabled")

    @staticmethod
    def _validar_data(valor: str, nome: str):
        if not valor:
            return
        try:
            datetime.strptime(valor, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError(f"{nome} deve estar no formato AAAA-MM-DD.") from exc

    def consultar(self):
        try:
            inicio = self.data_inicial.get().strip()
            fim = self.data_final.get().strip()
            self._validar_data(inicio, "A data inicial")
            self._validar_data(fim, "A data final")
            self.resultado_atual = Relatorios.gerar(self.tipo.get(), inicio, fim)
            self._mostrar_resultado()
            self.exportar_btn.configure(state="normal")
        except Exception as exc:
            messagebox.showerror("Erro ao gerar relatório", str(exc), parent=self)

    def _mostrar_resultado(self):
        resultado = self.resultado_atual
        self.resumo.configure(
            text=f"{resultado['rotulo_total']}: {resultado['total_registros']}  |  "
                 f"Quantidade total (quando aplicável): {resultado['total_quantidade']}"
        )
        linhas = [resultado["titulo"], "=" * 110]
        linhas.append(" | ".join(str(c) for c in resultado["colunas"]))
        linhas.append("-" * 110)
        if resultado["linhas"]:
            for linha in resultado["linhas"]:
                linhas.append(" | ".join(str(valor) for valor in linha))
        else:
            linhas.append("Nenhum registro encontrado para os filtros informados.")
        texto = "\n".join(linhas)

        self.tabela.configure(state="normal")
        self.tabela.delete("1.0", "end")
        self.tabela.insert("1.0", texto)
        self.tabela.configure(state="disabled")

    def exportar_pdf(self):
        if not self.resultado_atual:
            return
        caminho = filedialog.asksaveasfilename(
            parent=self,
            title="Salvar relatório em PDF",
            defaultextension=".pdf",
            filetypes=[("Documento PDF", "*.pdf")],
            initialfile="relatorio_solidario_tech.pdf"
        )
        if not caminho:
            return
        try:
            self._criar_pdf(caminho, self.resultado_atual)
            messagebox.showinfo(
                "PDF gerado",
                f"Relatório exportado com sucesso para:\n{caminho}",
                parent=self
            )
        except Exception as exc:
            messagebox.showerror("Erro ao exportar PDF", str(exc), parent=self)

    @staticmethod
    def _criar_pdf(caminho: str, resultado: dict):
        documento = SimpleDocTemplate(
            caminho, pagesize=landscape(A4),
            rightMargin=14 * mm, leftMargin=14 * mm,
            topMargin=14 * mm, bottomMargin=14 * mm
        )
        estilos = getSampleStyleSheet()
        titulo = ParagraphStyle(
            "TituloSolidario", parent=estilos["Title"],
            textColor=colors.HexColor(COR_PRIMARIA),
            alignment=TA_CENTER, fontName="Helvetica-Bold",
            fontSize=17, spaceAfter=6
        )
        normal = ParagraphStyle(
            "NormalSolidario", parent=estilos["BodyText"],
            fontName="Helvetica", fontSize=8, leading=10
        )
        elementos = [
            Paragraph("Solidário Tech", titulo),
            Paragraph(resultado["titulo"], estilos["Heading2"]),
            Paragraph(
                f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
                normal
            ),
            Spacer(1, 8),
        ]

        dados = [resultado["colunas"]]
        for linha in resultado["linhas"]:
            dados.append([str(valor) for valor in linha])
        if len(dados) == 1:
            dados.append(["Nenhum registro encontrado"] +
                         [""] * (len(resultado["colunas"]) - 1))

        tabela = Table(dados, repeatRows=1, hAlign="LEFT")
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(COR_PRIMARIA)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor(COR_BORDA)),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#F2F5F8")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elementos.append(tabela)
        elementos.append(Spacer(1, 10))
        elementos.append(Paragraph(
            f"{resultado['rotulo_total']}: {resultado['total_registros']}",
            normal
        ))
        documento.build(elementos)
