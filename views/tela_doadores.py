"""Tela de cadastro, consulta, edição e exclusão de doadores."""

import sqlite3
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from models.doador import Doador
from utils.validacoes import validar_cpf, validar_email, formatar_cpf
from utils.estilos import (
    COR_FUNDO, COR_PRIMARIA, COR_VERDE, COR_TEXTO,
    COR_TEXTO_SECUNDARIO, COR_SUPERFICIE, COR_BORDA, FONTE
)


class TelaDoadores(ctk.CTkFrame):
    """Gerencia os doadores e atualiza a listagem após cada operação."""

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
            topo, text="Gerenciamento de doadores",
            text_color=COR_TEXTO, font=(FONTE, 25, "bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            topo, text="Cadastre, consulte, edite e mantenha os dados dos doadores.",
            text_color=COR_TEXTO_SECUNDARIO, font=(FONTE, 13)
        ).pack(anchor="w", pady=(4, 0))

        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", pady=(0, 14))

        self.busca = ctk.CTkEntry(
            barra, textvariable=self.termo_busca, height=40,
            placeholder_text="Pesquisar por nome, CPF, telefone ou e-mail..."
        )
        self.busca.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.busca.bind("<KeyRelease>", lambda _event: self.atualizar_lista())

        ctk.CTkButton(
            barra, text="+ Novo doador", width=145, height=40,
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
        colunas = [("Nome", 2), ("CPF", 1), ("Telefone", 1), ("E-mail", 2), ("Ações", 1)]
        for texto, peso in colunas:
            cabecalho.grid_columnconfigure(len(cabecalho.grid_slaves()), weight=peso)
            ctk.CTkLabel(
                cabecalho, text=texto, text_color="#FFFFFF",
                font=(FONTE, 12, "bold"), anchor="w"
            ).pack_forget()
        for indice, (texto, peso) in enumerate(colunas):
            cabecalho.grid_columnconfigure(indice, weight=peso)
            ctk.CTkLabel(
                cabecalho, text=texto, text_color="#FFFFFF",
                font=(FONTE, 12, "bold"), anchor="w"
            ).grid(row=0, column=indice, sticky="ew", padx=10, pady=12)

        self.lista = ctk.CTkScrollableFrame(
            self, fg_color=COR_SUPERFICIE, corner_radius=10,
            border_width=1, border_color=COR_BORDA
        )
        self.lista.pack(fill="both", expand=True)

    def atualizar_lista(self) -> None:
        """Recarrega a tabela de doadores com o filtro atual."""
        for widget in self.lista.winfo_children():
            widget.destroy()

        try:
            doadores = Doador.listar(self.termo_busca.get())
            self.contagem.configure(text=f"{len(doadores)} doador(es) encontrado(s)")
            if not doadores:
                ctk.CTkLabel(
                    self.lista, text="Nenhum doador encontrado.",
                    text_color=COR_TEXTO_SECUNDARIO, font=(FONTE, 13)
                ).pack(pady=28)
                return

            for doador in doadores:
                linha = ctk.CTkFrame(self.lista, fg_color="transparent")
                linha.pack(fill="x", padx=5, pady=3)
                pesos = [2, 1, 1, 2, 1]
                valores = [
                    doador["nome"], doador["cpf"],
                    doador["telefone"] or "—", doador["email"] or "—"
                ]
                for indice, peso in enumerate(pesos):
                    linha.grid_columnconfigure(indice, weight=peso)
                for indice, valor in enumerate(valores):
                    ctk.CTkLabel(
                        linha, text=str(valor), text_color=COR_TEXTO,
                        font=(FONTE, 11), anchor="w"
                    ).grid(row=0, column=indice, sticky="ew", padx=8, pady=10)

                acoes = ctk.CTkFrame(linha, fg_color="transparent")
                acoes.grid(row=0, column=4, sticky="e", padx=5)
                ctk.CTkButton(
                    acoes, text="Editar", width=55, height=29,
                    fg_color=COR_PRIMARIA, hover_color="#24577F",
                    command=lambda item_id=doador["id"]: self.abrir_formulario(item_id)
                ).pack(side="left", padx=2)
                ctk.CTkButton(
                    acoes, text="Excluir", width=58, height=29,
                    fg_color="#B42318", hover_color="#8F1D14",
                    command=lambda item_id=doador["id"]: self.excluir(item_id)
                ).pack(side="left", padx=2)

                ctk.CTkFrame(
                    self.lista, height=1, fg_color=COR_BORDA
                ).pack(fill="x", padx=8)

        except sqlite3.Error as exc:
            messagebox.showerror("Erro no banco de dados", str(exc))

    def abrir_formulario(self, doador_id=None) -> None:
        """Abre formulário modal para cadastrar ou editar um doador."""
        registro = Doador.buscar(doador_id) if doador_id else None
        janela = ctk.CTkToplevel(self)
        janela.title("Editar doador" if registro else "Novo doador")
        janela.geometry("480x590")
        janela.resizable(False, False)
        janela.transient(self.winfo_toplevel())
        janela.grab_set()

        ctk.CTkLabel(
            janela, text="Editar doador" if registro else "Cadastrar doador",
            text_color=COR_PRIMARIA, font=(FONTE, 22, "bold")
        ).pack(anchor="w", padx=28, pady=(24, 4))
        ctk.CTkLabel(
            janela, text="Os campos marcados com * são obrigatórios.",
            text_color=COR_TEXTO_SECUNDARIO, font=(FONTE, 12)
        ).pack(anchor="w", padx=28, pady=(0, 16))

        campos = {}
        definicoes = [
            ("Nome completo *", "nome"),
            ("CPF *", "cpf"),
            ("Telefone", "telefone"),
            ("E-mail", "email"),
            ("Endereço", "endereco")
        ]
        for rotulo, chave in definicoes:
            ctk.CTkLabel(
                janela, text=rotulo, text_color=COR_TEXTO,
                font=(FONTE, 12, "bold")
            ).pack(anchor="w", padx=28, pady=(5, 3))
            campo = ctk.CTkEntry(janela, height=38)
            campo.pack(fill="x", padx=28)
            campos[chave] = campo
            if registro and registro[chave]:
                campo.insert(0, registro[chave])

        def salvar() -> None:
            dados = {chave: campo.get().strip() for chave, campo in campos.items()}
            if not dados["nome"] or not dados["cpf"]:
                messagebox.showwarning(
                    "Campos obrigatórios", "Informe o nome e o CPF.", parent=janela
                )
                return
            if not validar_cpf(dados["cpf"]):
                messagebox.showwarning(
                    "CPF inválido", "Informe um CPF válido com 11 dígitos.", parent=janela
                )
                return
            if not validar_email(dados["email"]):
                messagebox.showwarning(
                    "E-mail inválido", "Confira o formato do e-mail.", parent=janela
                )
                return

            try:
                cpf = formatar_cpf(dados["cpf"])
                if registro:
                    Doador.atualizar(
                        doador_id, dados["nome"], cpf, dados["telefone"],
                        dados["email"], dados["endereco"]
                    )
                    mensagem = "Doador atualizado com sucesso."
                else:
                    Doador.cadastrar(
                        dados["nome"], cpf, dados["telefone"],
                        dados["email"], dados["endereco"]
                    )
                    mensagem = "Doador cadastrado com sucesso."
                janela.destroy()
                self.atualizar_lista()
                messagebox.showinfo("Sucesso", mensagem)
            except sqlite3.IntegrityError:
                messagebox.showerror(
                    "CPF já cadastrado",
                    "Já existe um doador registrado com este CPF.",
                    parent=janela
                )
            except (sqlite3.Error, ValueError) as exc:
                messagebox.showerror("Erro ao salvar", str(exc), parent=janela)

        botoes = ctk.CTkFrame(janela, fg_color="transparent")
        botoes.pack(fill="x", padx=28, pady=22)
        ctk.CTkButton(
            botoes, text="Cancelar", fg_color="#E7ECF1",
            text_color=COR_TEXTO, hover_color="#D7DEE6",
            command=janela.destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(
            botoes, text="Salvar", fg_color=COR_VERDE,
            hover_color="#1B6E49", command=salvar
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def excluir(self, doador_id: int) -> None:
        """Solicita confirmação e respeita vínculos com doações."""
        if not messagebox.askyesno(
            "Confirmar exclusão",
            "Deseja realmente excluir este doador?",
            parent=self.winfo_toplevel()
        ):
            return
        try:
            Doador.excluir(doador_id)
            self.atualizar_lista()
            messagebox.showinfo("Sucesso", "Doador excluído com sucesso.")
        except ValueError as exc:
            messagebox.showwarning("Exclusão não permitida", str(exc))
        except sqlite3.Error as exc:
            messagebox.showerror("Erro ao excluir", str(exc))
