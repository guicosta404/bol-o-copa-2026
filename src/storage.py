from __future__ import annotations

import os
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from postgrest.types import ReturnMethod
from streamlit.errors import StreamlitSecretNotFoundError
from supabase import Client, create_client


def _setting(name: str) -> str | None:
    try:
        if name in st.secrets:
            return str(st.secrets[name])
    except StreamlitSecretNotFoundError:
        pass
    return os.getenv(name)


@st.cache_resource(show_spinner=False)
def get_supabase_client() -> Client | None:
    load_dotenv()
    url = _setting("SUPABASE_URL")
    key = _setting("SUPABASE_KEY") or _setting("SUPABASE_PUBLISHABLE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


def save_bet(payload: dict[str, Any]) -> tuple[bool, str]:
    client = get_supabase_client()
    if client is None:
        return False, "Configure SUPABASE_URL e SUPABASE_KEY para salvar no banco."

    try:
        client.table("palpites").insert(payload, returning=ReturnMethod.minimal).execute()
    except Exception as exc:  # pragma: no cover - depends on external Supabase.
        return False, f"Nao foi possivel salvar no Supabase: {exc}"

    return True, "Palpite salvo com sucesso."
