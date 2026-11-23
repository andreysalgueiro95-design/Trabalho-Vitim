"""Tela de cadastro, consulta, edição e exclusão de doações."""

import sqlite3
import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox

import customtkinter as ctk

from models.doacao import Doacao
from utils.estilos import (
    COR_PRIMARIA, COR_VERDE, COR_TEXTO, COR_TEXTO_SECUNDARIO,
    COR_SUPERFICIE, COR_BORDA, FONTE
)


class TelaDoacoes(ctk.CTkFrame):
    """Gerencia as doações registradas no sistema."""

    CATEGORIAS = [
        "Alimentos", "Higiene", "Limpeza", "Roupas",
        "Material escolar", "Móveis", "Outros"
    ]
    STATUS = ["Disponível", "Esgotado"]

    def __init__(self, master) -> None:
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self.termo_busca = tk.StringVar()
        self._montar_interface()
        self.atualizar_lista()

    def _montar_interface(self) -> None:
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", pady=(0, 18))

        ctk.CTkLabel(
            topo, text="Gerenciamento de doações",
            text_color=COR_TEXTO, font=(FONTE, 25, "bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            topo,
            text="Registre e acompanhe os itens recebidos pela instituição.",
            text_color=COR_TEXTO_SECUNDARIO, font=(FONTE, 13)
        ).pack(anchor="w", pady=(4, 0))

        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", pady=(0, 14))

        self.busca = ctk.CTkEntry(
            barra, textvariable=self.termo_busca, height=40,
            placeholder_text="Pesquisar por item, categoria, doador ou status..."
        )
        self.busca.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.busca.bind("<KeyRelease>", lambda _event: self.atualizar_lista())

        ctk.CTkButton(
            barra, text="+ Nova doação", width=145, height=40,
            fg_color=COR_VERDE, hover_color="#1B6E49",
            command=lambda: self.abrir_formulario()
        ).pack(side="right")

        self.contagem = ctk.CTkLabel(
            self, text="", text_color=COR_TEXTO_SECUNDARIO,
            font=(FONTE, 12)
        )
        self.contagem.pack(anchor="w", pady=(0, 8))

        cabecalho = ctk.CTkFrame(self, fg_color=COR_PRIMARIA, corner_radius=8)
        cabecalho.pack(fill="x", pady=(0, 5))
        colunas = [
            ("Item", 2), ("Categoria", 1), ("Quantidade", 1),
            ("Doador", 2), ("Validade", 1), ("Status", 1), ("Ações", 1)
        ]
        for indice, (texto, peso) in enumerate(colunas):
            cabecalho.grid_columnconfigure(indice, weight=peso)
            ctk.CTkLabel(
                cabecalho, text=texto, text_color="#FFFFFF",
                font=(FONTE, 11, "bold"), anchor="w"
            ).grid(row=0, column=indice, sticky="ew", padx=7, pady=12)

        self.lista = ctk.CTkScrollableFrame(
            self, fg_color=COR_SUPERFICIE, corner_radius=10,
            border_width=1, border_color=COR_BORDA
        )
        self.lista.pack(fill="both", expand=True)

    def atualizar_lista(self) -> None:
        """Recarrega as doações usando o filtro informado."""
        for widget in self.lista.winfo_children():
            widget.destroy()

        try:
            doacoes = Doacao.listar(self.termo_busca.get())
            self.contagem.configure(
                text=f"{len(doacoes)} doação(ões) encontrada(s)"
            )
            if not doacoes:
                ctk.CTkLabel(
                    self.lista, text="Nenhuma doação encontrada.",
                    text_color=COR_TEXTO_SECUNDARIO, font=(FONTE, 13)
                ).pack(pady=28)
                return

            for doacao in doacoes:
                linha = ctk.CTkFrame(self.lista, fg_color="transparent")
                linha.pack(fill="x", padx=5, pady=3)
                pesos = [2, 1, 1, 2, 1, 1, 1]
                for indice, peso in enumerate(pesos):
                    linha.grid_columnconfigure(indice, weight=peso)

                validade = doacao["validade"] or "—"
                valores = [
                    doacao["item"], doacao["categoria"],
                    str(doacao["quantidade"]), doacao["nome_doador"],
                    validade, doacao["status"]
                ]
                for indice, valor in enumerate(valores):
                    ctk.CTkLabel(
                        linha, text=str(valor), text_color=COR_TEXTO,
                        font=(FONTE, 10), anchor="w"
                    ).grid(row=0, column=indice, sticky="ew", padx=7, pady=10)

                acoes = ctk.CTkFrame(linha, fg_color="transparent")
                acoes.grid(row=0, column=6, sticky="e", padx=3)
                ctk.CTkButton(
                    acoes, text="Editar", width=52, height=28,
                    fg_color=COR_PRIMARIA, hover_color="#24577F",
                    command=lambda item_id=doacao["id"]:
                        self.abrir_formulario(item_id)
                ).pack(side="left", padx=2)
                ctk.CTkButton(
                    acoes, text="Excluir", width=55, height=28,
                    fg_color="#B42318", hover_color="#8F1D14",
                    command=lambda item_id=doacao["id"]: self.excluir(item_id)
                ).pack(side="left", padx=2)

                ctk.CTkFrame(
                    self.lista, height=1, fg_color=COR_BORDA
                ).pack(fill="x", padx=8)

        except sqlite3.Error as exc:
            messagebox.showerror("Erro no banco de dados", str(exc))

    def abrir_formulario(self, doacao_id=None) -> None:
        """Abre formulário modal para cadastrar ou editar uma doação."""
        doadores = Doacao.listar_doadores()
        if not doadores:
            messagebox.showwarning(
                "Nenhum doador cadastrado",
                "Cadastre pelo menos um doador antes de registrar uma doação.",
                parent=self.winfo_toplevel()
            )
            return

        registro = Doacao.buscar(doacao_id) if doacao_id else None
        janela = ctk.CTkToplevel(self)
        janela.title("Editar doação" if registro else "Nova doação")
        janela.geometry("520x700")
        janela.resizable(False, False)
        janela.transient(self.winfo_toplevel())
        janela.grab_set()

        ctk.CTkLabel(
            janela, text="Editar doação" if registro else "Cadastrar doação",
            text_color=COR_PRIMARIA, font=(FONTE, 22, "bold")
        ).pack(anchor="w", padx=28, pady=(22, 4))
        ctk.CTkLabel(
            janela, text="Preencha os dados da doação recebida.",
            text_color=COR_TEXTO_SECUNDARIO, font=(FONTE, 12)
        ).pack(anchor="w", padx=28, pady=(0, 12))

        campos = {}

        def adicionar_campo(rotulo, chave, valor=""):
            ctk.CTkLabel(
                janela, text=rotulo, text_color=COR_TEXTO,
                font=(FONTE, 12, "bold")
            ).pack(anchor="w", padx=28, pady=(7, 3))
            campo = ctk.CTkEntry(janela, height=36)
            campo.pack(fill="x", padx=28)
            if valor is not None:
                campo.insert(0, str(valor))
            campos[chave] = campo
            return campo

        doador_por_nome = {item["nome"]: item["id"] for item in doadores}
        nome_selecionado = next(
            (item["nome"] for item in doadores
             if registro and item["id"] == registro["doador_id"]),
            doadores[0]["nome"]
        )

        ctk.CTkLabel(
            janela, text="Doador *", text_color=COR_TEXTO,
            font=(FONTE, 12, "bold")
        ).pack(anchor="w", padx=28, pady=(7, 3))
        campo_doador = ctk.CTkComboBox(
            janela, values=list(doador_por_nome.keys()), height=36,
            state="readonly"
        )
        campo_doador.pack(fill="x", padx=28)
        campo_doador.set(nome_selecionado)

        adicionar_campo("Nome do item *", "item", registro["item"] if registro else "")
        
        ctk.CTkLabel(
            janela, text="Categoria *", text_color=COR_TEXTO,
            font=(FONTE, 12, "bold")
        ).pack(anchor="w", padx=28, pady=(7, 3))
        campo_categoria = ctk.CTkComboBox(
            janela, values=self.CATEGORIAS, height=36, state="readonly"
        )
        campo_categoria.pack(fill="x", padx=28)
        campo_categoria.set(
            registro["categoria"] if registro else self.CATEGORIAS[0]
        )

        adicionar_campo(
            "Quantidade *", "quantidade",
            registro["quantidade"] if registro else "1"
        )
        adicionar_campo(
            "Data da doação * (AAAA-MM-DD)", "data_doacao",
            registro["data_doacao"] if registro else date.today().isoformat()
        )
        adicionar_campo(
            "Data de validade (AAAA-MM-DD, se houver)", "validade",
            registro["validade"] if registro and registro["validade"] else ""
        )

        ctk.CTkLabel(
            janela, text="Status *", text_color=COR_TEXTO,
            font=(FONTE, 12, "bold")
        ).pack(anchor="w", padx=28, pady=(7, 3))
        campo_status = ctk.CTkComboBox(
            janela, values=self.STATUS, height=36, state="readonly"
        )
        campo_status.pack(fill="x", padx=28)
        campo_status.set(
            registro["status"] if registro and registro["status"] in self.STATUS
            else "Disponível"
        )

        def salvar() -> None:
            dados = {chave: campo.get().strip() for chave, campo in campos.items()}
            if not dados["item"] or not dados["quantidade"] or not dados["data_doacao"]:
                messagebox.showwarning(
                    "Campos obrigatórios",
                    "Preencha o item, a quantidade e a data da doação.",
                    parent=janela
                )
                return

            try:
                quantidade = int(dados["quantidade"])
                if quantidade <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning(
                    "Quantidade inválida",
                    "A quantidade deve ser um número inteiro maior que zero.",
                    parent=janela
                )
                return

            try:
                data_registro = datetime.strptime(
                    dados["data_doacao"], "%Y-%m-%d"
                ).date()
                validade = None
                if dados["validade"]:
                    validade = datetime.strptime(
                        dados["validade"], "%Y-%m-%d"
                    ).date()
                    if validade < data_registro:
                        messagebox.showwarning(
                            "Validade inválida",
                            "A validade não pode ser anterior à data da doação.",
                            parent=janela
                        )
                        return
            except ValueError:
                messagebox.showwarning(
                    "Data inválida",
                    "Use o formato AAAA-MM-DD para as datas.",
                    parent=janela
                )
                return

            try:
                argumentos = (
                    doador_por_nome[campo_doador.get()],
                    dados["item"], campo_categoria.get(), quantidade,
                    data_registro.isoformat(),
                    validade.isoformat() if validade else "",
                    campo_status.get()
                )
                if registro:
                    Doacao.atualizar(doacao_id, *argumentos)
                    mensagem = "Doação atualizada com sucesso."
                else:
                    Doacao.cadastrar(*argumentos)
                    mensagem = "Doação cadastrada com sucesso."

                janela.destroy()
                self.atualizar_lista()
                messagebox.showinfo("Sucesso", mensagem)
            except (sqlite3.Error, KeyError, ValueError) as exc:
                messagebox.showerror("Erro ao salvar", str(exc), parent=janela)

        botoes = ctk.CTkFrame(janela, fg_color="transparent")
        botoes.pack(fill="x", padx=28, pady=18)
        ctk.CTkButton(
            botoes, text="Cancelar", fg_color="#E7ECF1",
            text_color=COR_TEXTO, hover_color="#D7DEE6",
            command=janela.destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(
            botoes, text="Salvar", fg_color=COR_VERDE,
            hover_color="#1B6E49", command=salvar
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def excluir(self, doacao_id: int) -> None:
        """Confirma a exclusão e preserva doações ligadas a distribuições."""
        if not messagebox.askyesno(
            "Confirmar exclusão",
            "Deseja realmente excluir esta doação?",
            parent=self.winfo_toplevel()
        ):
            return
        try:
            Doacao.excluir(doacao_id)
            self.atualizar_lista()
            messagebox.showinfo("Sucesso", "Doação excluída com sucesso.")
        except ValueError as exc:
            messagebox.showwarning("Exclusão não permitida", str(exc))
        except sqlite3.Error as exc:
            messagebox.showerror("Erro ao excluir", str(exc))
