"""Tela de autenticação do Solidário Tech."""

import customtkinter as ctk
from tkinter import messagebox

from utils.estilos import (
    COR_FUNDO, COR_PRIMARIA, COR_VERDE, COR_TEXTO,
    COR_TEXTO_SECUNDARIO, COR_ERRO, FONTE
)


class TelaLogin(ctk.CTkFrame):
    """Formulário de login com validação no banco SQLite."""

    def __init__(self, master, on_success) -> None:
        super().__init__(master, fg_color=COR_FUNDO)
        self.on_success = on_success
        self.pack(fill="both", expand=True)
        self._montar_interface()

    def _montar_interface(self) -> None:
        area = ctk.CTkFrame(self, fg_color="transparent")
        area.pack(expand=True)

        cartao = ctk.CTkFrame(
            area, width=420, height=500, corner_radius=18,
            fg_color="#FFFFFF", border_width=1, border_color="#DCE3EA"
        )
        cartao.pack(padx=24, pady=24)
        cartao.pack_propagate(False)

        ctk.CTkLabel(
            cartao, text="ST", width=54, height=54, corner_radius=14,
            fg_color=COR_VERDE, text_color="#FFFFFF",
            font=(FONTE, 22, "bold")
        ).pack(pady=(34, 12))

        ctk.CTkLabel(
            cartao, text="Solidário Tech", text_color=COR_PRIMARIA,
            font=(FONTE, 25, "bold")
        ).pack()

        ctk.CTkLabel(
            cartao, text="Gestão de doações com propósito",
            text_color=COR_TEXTO_SECUNDARIO, font=(FONTE, 13)
        ).pack(pady=(4, 22))

        formulario = ctk.CTkFrame(cartao, fg_color="transparent")
        formulario.pack(fill="x", padx=42)

        ctk.CTkLabel(
            formulario, text="Usuário", anchor="w",
            text_color=COR_TEXTO, font=(FONTE, 13, "bold")
        ).pack(fill="x", pady=(0, 6))

        self.campo_usuario = ctk.CTkEntry(
            formulario, height=42, placeholder_text="Digite seu usuário"
        )
        self.campo_usuario.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            formulario, text="Senha", anchor="w",
            text_color=COR_TEXTO, font=(FONTE, 13, "bold")
        ).pack(fill="x", pady=(0, 6))

        self.campo_senha = ctk.CTkEntry(
            formulario, height=42, placeholder_text="Digite sua senha", show="*"
        )
        self.campo_senha.pack(fill="x")
        self.campo_senha.bind("<Return>", lambda _event: self._entrar())

        self.mensagem = ctk.CTkLabel(
            formulario, text="", text_color=COR_ERRO,
            font=(FONTE, 12), wraplength=320
        )
        self.mensagem.pack(fill="x", pady=(8, 0))

        ctk.CTkButton(
            formulario, text="Entrar no sistema", height=44,
            fg_color=COR_VERDE, hover_color="#1B6E49",
            font=(FONTE, 14, "bold"), command=self._entrar
        ).pack(fill="x", pady=(10, 0))

        ctk.CTkLabel(
            cartao, text="Acesso administrativo",
            text_color=COR_TEXTO_SECUNDARIO, font=(FONTE, 11)
        ).pack(side="bottom", pady=18)

        self.campo_usuario.focus_set()

    def _entrar(self) -> None:
        usuario = self.campo_usuario.get().strip()
        senha = self.campo_senha.get()

        if not usuario or not senha:
            self.mensagem.configure(text="Preencha o usuário e a senha.")
            return

        try:
            # Importação local evita dependência circular entre tela e controlador.
            from controllers.app_controller import AppController

            if AppController.autenticar(usuario, senha):
                self.on_success(usuario)
            else:
                self.mensagem.configure(
                    text="Usuário ou senha incorretos. Tente novamente."
                )
                self.campo_senha.delete(0, "end")
                self.campo_senha.focus_set()
        except Exception as exc:
            messagebox.showerror(
                "Erro de autenticação",
                f"Não foi possível validar o acesso.\n{exc}"
            )
