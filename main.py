"""Ponto de entrada inicial do Solidário Tech.

A interface gráfica será conectada nas próximas etapas.
"""

from database.db_manager import db


def main() -> None:
    """Inicializa os recursos locais do sistema."""
    try:
        db.initialize()
        print("Solidário Tech: banco de dados inicializado com sucesso.")
        print(f"Arquivo do banco: {db.db_path}")
        print("Acesso inicial: usuário admin | senha admin")
        print("Próxima etapa: implementação da tela de login.")
    except (RuntimeError, OSError) as exc:
        print(f"Erro ao iniciar o Solidário Tech: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
