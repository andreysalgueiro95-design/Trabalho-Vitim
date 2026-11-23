"""Validações reutilizáveis dos formulários."""

import re


def somente_digitos(valor: str) -> str:
    """Remove caracteres que não sejam números."""
    return re.sub(r"\D", "", valor)


def validar_cpf(cpf: str) -> bool:
    """Valida CPF com 11 dígitos e seus dois dígitos verificadores."""
    numero = somente_digitos(cpf)
    if len(numero) != 11 or numero == numero[0] * 11:
        return False

    soma = sum(int(numero[i]) * (10 - i) for i in range(9))
    primeiro = (soma * 10 % 11) % 10
    if primeiro != int(numero[9]):
        return False

    soma = sum(int(numero[i]) * (11 - i) for i in range(10))
    segundo = (soma * 10 % 11) % 10
    return segundo == int(numero[10])


def validar_email(email: str) -> bool:
    """Verifica formato básico de e-mail quando o campo for preenchido."""
    if not email.strip():
        return True
    return bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email.strip()))


def formatar_cpf(cpf: str) -> str:
    """Normaliza CPF para armazenamento apenas com números."""
    return somente_digitos(cpf)
