from __future__ import annotations

import os
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from postgrest.types import ReturnMethod
from streamlit.errors import StreamlitSecretNotFoundError
from supabase import Client, create_client


SUPABASE_URL_NAMES = (
    "SUPABASE_URL",
    "SUPABASE_PROJECT_URL",
    "NEXT_PUBLIC_SUPABASE_URL",
    "VITE_SUPABASE_URL",
    "supabase_url",
    "url",
)
SUPABASE_KEY_NAMES = (
    "SUPABASE_KEY",
    "SUPABASE_PUBLISHABLE_KEY",
    "SUPABASE_ANON_KEY",
    "SUPABASE_API_KEY",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY",
    "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY",
    "VITE_SUPABASE_ANON_KEY",
    "VITE_SUPABASE_PUBLISHABLE_KEY",
    "supabase_key",
    "supabase_publishable_key",
    "supabase_anon_key",
    "api_key",
    "key",
    "anon_key",
    "publishable_key",
)
SUPABASE_SECRET_SECTIONS = ((), ("supabase",), ("SUPABASE",), ("connections", "supabase"))


def _clean_setting(value: Any) -> str | None:
    value = str(value).strip() if value is not None else ""
    return value or None


def _secret_setting(path: tuple[str, ...]) -> str | None:
    try:
        current: Any = st.secrets
        for key in path:
            if key not in current:
                return None
            current = current[key]
    except (KeyError, TypeError, StreamlitSecretNotFoundError):
        return None
    return _clean_setting(current)


def _setting(names: tuple[str, ...]) -> str | None:
    for section in SUPABASE_SECRET_SECTIONS:
        for name in names:
            value = _secret_setting((*section, name))
            if value:
                return value

    for name in names:
        value = _clean_setting(os.getenv(name))
        if value:
            return value

    return None


def _supabase_settings() -> tuple[str | None, str | None]:
    load_dotenv()
    return _setting(SUPABASE_URL_NAMES), _setting(SUPABASE_KEY_NAMES)


@st.cache_resource(show_spinner=False)
def _create_supabase_client(url: str, key: str) -> Client:
    return create_client(url, key)


def get_supabase_client() -> Client | None:
    url, key = _supabase_settings()
    if not url or not key:
        return None
    return _create_supabase_client(url, key)


def save_bet(payload: dict[str, Any]) -> tuple[bool, str]:
    client = get_supabase_client()
    if client is None:
        url, key = _supabase_settings()
        missing = []
        if not url:
            missing.append("SUPABASE_URL")
        if not key:
            missing.append("SUPABASE_KEY")

        return False, (
            "Configuracao do Supabase incompleta nos Secrets do Streamlit Cloud: "
            f"faltando {', '.join(missing)}. "
            "Abra Manage app > Settings > Secrets, cole SUPABASE_URL e SUPABASE_KEY, "
            "salve e reinicie o app."
        )

    try:
        client.table("palpites").insert(payload, returning=ReturnMethod.minimal).execute()
    except Exception as exc:  # pragma: no cover - depends on external Supabase.
        return False, f"Nao foi possivel salvar no Supabase: {exc}"

    return True, "Palpite salvo com sucesso."
