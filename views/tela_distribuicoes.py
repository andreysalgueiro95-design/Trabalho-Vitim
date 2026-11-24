"""Tela de cadastro, consulta, edição e exclusão de distribuições."""

import sqlite3
import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox

import customtkinter as ctk

from models.distribuicao import Distribuicao
from utils.estilos import (
    COR_PRIMARIA, COR_VERDE, COR_TEXTO, COR_TEXTO_SECUNDARIO,
    COR_SUPERFICIE, COR_BORDA, FONTE
)


class TelaDistribuicoes(ctk.CTkFrame):
    """Gerencia as entregas realizadas pela instituição."""

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
            topo, text="Gerenciamento de distribuições",
            text_color=COR_TEXTO, font=(FONTE, 25, "bold")
        ).pack(anchor="w")
        ctk.CTkLabel(
            topo, text="Registre as entregas e acompanhe a saída dos itens do estoque.",
            text_color=COR_TEXTO_SECUNDARIO, font=(FONTE, 13)
        ).pack(anchor="w", pady=(4, 0))

        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", pady=(0, 14))
        self.busca = ctk.CTkEntry(
            barra, textvariable=self.termo_busca, height=40,
            placeholder_text="Pesquisar por instituição, item, doador ou responsável..."
        )
        self.busca.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.busca.bind("<KeyRelease>", lambda _event: self.atualizar_lista())
        ctk.CTkButton(
            barra, text="+ Nova distribuição", width=165, height=40,
            fg_color=COR_VERDE, hover_color="#1B6E49",
            command=self.abrir_formulario
        ).pack(side="right")

        self.contagem = ctk.CTkLabel(
            self, text="", text_color=COR_TEXTO_SECUNDARIO, font=(FONTE, 12)
        )
        self.contagem.pack(anchor="w", pady=(0, 8))

        cabecalho = ctk.CTkFrame(self, fg_color=COR_PRIMARIA, corner_radius=8)
        cabecalho.pack(fill="x", pady=(0, 5))
        colunas = [
            ("Instituição", 2), ("Item", 2), ("Quantidade", 1),
            ("Data", 1), ("Responsável", 2), ("Ações", 1)
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
        for widget in self.lista.winfo_children():
            widget.destroy()
        try:
            registros = Distribuicao.listar(self.termo_busca.get())
            self.contagem.configure(
                text=f"{len(registros)} distribuição(ões) encontrada(s)"
            )
            if not registros:
                ctk.CTkLabel(
                    self.lista, text="Nenhuma distribuição encontrada.",
                    text_color=COR_TEXTO_SECUNDARIO, font=(FONTE, 13)
                ).pack(pady=28)
                return

            for registro in registros:
                linha = ctk.CTkFrame(self.lista, fg_color="transparent")
                linha.pack(fill="x", padx=5, pady=3)
                pesos = [2, 2, 1, 1, 2, 1]
                for indice, peso in enumerate(pesos):
                    linha.grid_columnconfigure(indice, weight=peso)
                valores = [
                    registro["instituicao_destino"], registro["item"],
                    str(registro["quantidade"]), registro["data_entrega"],
                    registro["responsavel"]
                ]
                for indice, valor in enumerate(valores):
                    ctk.CTkLabel(
                        linha, text=str(valor), text_color=COR_TEXTO,
                        font=(FONTE, 10), anchor="w"
                    ).grid(row=0, column=indice, sticky="ew", padx=7, pady=10)

                acoes = ctk.CTkFrame(linha, fg_color="transparent")
                acoes.grid(row=0, column=5, sticky="e", padx=3)
                ctk.CTkButton(
                    acoes, text="Editar", width=52, height=28,
                    fg_color=COR_PRIMARIA, hover_color="#24577F",
                    command=lambda rid=registro["id"]: self.abrir_formulario(rid)
                ).pack(side="left", padx=2)
                ctk.CTkButton(
                    acoes, text="Excluir", width=55, height=28,
                    fg_color="#B42318", hover_color="#8F1D14",
                    command=lambda rid=registro["id"]: self.excluir(rid)
                ).pack(side="left", padx=2)
                ctk.CTkFrame(self.lista, height=1, fg_color=COR_BORDA).pack(
                    fill="x", padx=8
                )
        except sqlite3.Error as exc:
            messagebox.showerror("Erro no banco de dados", str(exc))

    def abrir_formulario(self, distribuicao_id=None) -> None:
        registro = (
            Distribuicao.buscar(distribuicao_id) if distribuicao_id else None
        )
        opcoes = Distribuicao.listar_doacoes_disponiveis(
            registro["doacao_id"] if registro else None
        )
        if not opcoes:
            messagebox.showwarning(
                "Estoque indisponível",
                "Não há doações disponíveis para distribuir.",
                parent=self.winfo_toplevel()
            )
            return

        janela = ctk.CTkToplevel(self)
        janela.title("Editar distribuição" if registro else "Nova distribuição")
        janela.geometry("540x570")
        janela.resizable(False, False)
        janela.transient(self.winfo_toplevel())
        janela.grab_set()

        ctk.CTkLabel(
            janela, text="Editar distribuição" if registro else "Registrar distribuição",
            text_color=COR_PRIMARIA, font=(FONTE, 22, "bold")
        ).pack(anchor="w", padx=28, pady=(22, 4))
        ctk.CTkLabel(
            janela, text="A quantidade informada será descontada do estoque.",
            text_color=COR_TEXTO_SECUNDARIO, font=(FONTE, 12)
        ).pack(anchor="w", padx=28, pady=(0, 12))

        def rotulo(texto):
            ctk.CTkLabel(
                janela, text=texto, text_color=COR_TEXTO,
                font=(FONTE, 12, "bold")
            ).pack(anchor="w", padx=28, pady=(10, 3))

        rotulo("Doação / item *")
        mapa = {}
        valores_combo = []
        for item in opcoes:
            texto = (
                f'#{item["id"]} | {item["item"]} | saldo: {item["quantidade"]} '
                f'| doador: {item["nome_doador"]}'
            )
            mapa[texto] = item["id"]
            valores_combo.append(texto)
        combo = ctk.CTkComboBox(
            janela, values=valores_combo, height=36, state="readonly"
        )
        combo.pack(fill="x", padx=28)
        selecionada = next(
            (texto for texto, did in mapa.items()
             if registro and did == registro["doacao_id"]),
            valores_combo[0]
        )
        combo.set(selecionada)

        campos = {}
        def campo(rotulo_texto, chave, valor):
            rotulo(rotulo_texto)
            entrada = ctk.CTkEntry(janela, height=36)
            entrada.pack(fill="x", padx=28)
            entrada.insert(0, str(valor))
            campos[chave] = entrada

        campo("Instituição de destino *", "instituicao",
              registro["instituicao_destino"] if registro else "")
        campo("Quantidade *", "quantidade",
              registro["quantidade"] if registro else "1")
        campo("Data da entrega * (AAAA-MM-DD)", "data",
              registro["data_entrega"] if registro else date.today().isoformat())
        campo("Responsável pela entrega *", "responsavel",
              registro["responsavel"] if registro else "")

        def salvar():
            instituicao = campos["instituicao"].get().strip()
            responsavel = campos["responsavel"].get().strip()
            quantidade_txt = campos["quantidade"].get().strip()
            data_txt = campos["data"].get().strip()
            if not instituicao or not responsavel or not quantidade_txt or not data_txt:
                messagebox.showwarning(
                    "Campos obrigatórios", "Preencha todos os campos.",
                    parent=janela
                )
                return
            try:
                quantidade = int(quantidade_txt)
                if quantidade <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning(
                    "Quantidade inválida",
                    "Informe um número inteiro maior que zero.", parent=janela
                )
                return
            try:
                data_entrega = datetime.strptime(data_txt, "%Y-%m-%d").date()
                if data_entrega > date.today():
                    messagebox.showwarning(
                        "Data inválida", "A data da entrega não pode estar no futuro.",
                        parent=janela
                    )
                    return
            except ValueError:
                messagebox.showwarning(
                    "Data inválida", "Use o formato AAAA-MM-DD.",
                    parent=janela
                )
                return
            try:
                doacao_id = mapa[combo.get()]
                argumentos = (
                    doacao_id, instituicao, quantidade,
                    data_entrega.isoformat(), responsavel
                )
                if registro:
                    Distribuicao.atualizar(distribuicao_id, *argumentos)
                    mensagem = "Distribuição atualizada com sucesso."
                else:
                    Distribuicao.cadastrar(*argumentos)
                    mensagem = "Distribuição registrada com sucesso."
                janela.destroy()
                self.atualizar_lista()
                messagebox.showinfo("Sucesso", mensagem)
            except (sqlite3.Error, ValueError, KeyError) as exc:
                messagebox.showerror("Não foi possível salvar", str(exc), parent=janela)

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

    def excluir(self, distribuicao_id: int) -> None:
        if not messagebox.askyesno(
            "Confirmar exclusão",
            "Deseja realmente excluir esta distribuição? O saldo será devolvido ao estoque.",
            parent=self.winfo_toplevel()
        ):
            return
        try:
            Distribuicao.excluir(distribuicao_id)
            self.atualizar_lista()
            messagebox.showinfo(
                "Sucesso", "Distribuição excluída e saldo restaurado ao estoque."
            )
        except (sqlite3.Error, ValueError) as exc:
            messagebox.showerror("Erro ao excluir", str(exc))
