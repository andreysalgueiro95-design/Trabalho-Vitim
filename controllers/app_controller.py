"""Controlador central: autenticação e transição entre telas."""

import customtkinter as ctk

from database.db_manager import db
from views.tela_login import TelaLogin
from views.tela_principal import TelaPrincipal
from utils.estilos import COR_FUNDO


class AppController:
    """Coordena a janela principal e as telas da aplicação."""

    def __init__(self) -> None:
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Solidário Tech")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        self.root.configure(fg_color=COR_FUNDO)
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self._mostrar_login()

    def _limpar_tela(self) -> None:
        for widget in self.root.winfo_children():
            widget.destroy()

    def _mostrar_login(self) -> None:
        self._limpar_tela()
        TelaLogin(self.root, on_success=self._login_realizado)

    def _login_realizado(self, usuario: str) -> None:
        self._limpar_tela()
        TelaPrincipal(self.root, usuario=usuario, on_logout=self._mostrar_login)

    @staticmethod
    def autenticar(usuario: str, senha: str) -> bool:
        registro = db.fetch_one(
            "SELECT senha_hash FROM usuarios WHERE usuario = ?",
            (usuario.strip(),)
        )
        return bool(
            registro and db.verify_password(senha, registro["senha_hash"])
        )

    def executar(self) -> None:
        self.root.mainloop()
