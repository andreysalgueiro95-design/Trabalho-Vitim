"""Ponto de entrada do Solidário Tech."""

from database.db_manager import db
from controllers.app_controller import AppController


def main() -> None:
    """Inicializa o banco e abre a interface desktop."""
    try:
        db.initialize()
        aplicacao = AppController()
        aplicacao.executar()
    except (RuntimeError, OSError) as exc:
        print(f"Erro ao iniciar o Solidário Tech: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
