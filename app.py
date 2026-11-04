import streamlit as st
import streamlit.components.v1 as components
import json
import base64
import urllib.request
import urllib.error
from urllib.parse import quote
from io import BytesIO
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import copy
import uuid
import time
import hmac
import hashlib
import re
import secrets
from datetime import date, timedelta, time as horario_time
from contextlib import contextmanager

try:
    from streamlit_local_storage import LocalStorage
except Exception:
    LocalStorage = None

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
)
from reportlab.graphics.shapes import Drawing, Path as RLPath, Rect, Circle, Line

# =========================================================
# PÁGINA
# =========================================================

st.set_page_config(
    page_title="F Climatização",
    page_icon="F",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =========================================================
# CONSTANTES
# =========================================================

OWNER = "guilhermesdemedeiros-dotcom"
CONFIG_REPO = "f-climatizacao"
DATA_REPO = st.secrets.get("DATA_GITHUB_REPO", "f-climatizacao-dados")
BRANCH = "main"

CONFIG_FILE = "config.json"
BUDGETS_FILE = "orcamentos.json"
FINANCE_FILE = "financeiro.json"
BUDGET_META_FILE = "orcamentos_meta.json"
AGENDA_FILE = "agenda_disponibilidade.json"

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
ADMIN_KEY = st.secrets.get("ADMIN_KEY", "")

CAPACIDADES = ["9.000 BTUs", "12.000 BTUs", "18.000 BTUs", "24.000 BTUs"]
TIPOS_AR = ["Inverter", "Convencional"]
UNIDADES_ITEM = ["unidade", "metro", "serviço", "equipamento"]
FUSO_BRASILIA = ZoneInfo("America/Sao_Paulo")

REFERENCIA_AREA = {
    "9.000 BTUs": "até 12 m²",
    "12.000 BTUs": "13 a 19 m²",
    "18.000 BTUs": "20 a 27 m²",
    "24.000 BTUs": "28 a 37 m²",
}

BTU_NUM = {
    "9.000 BTUs": 9000,
    "12.000 BTUs": 12000,
    "18.000 BTUs": 18000,
    "24.000 BTUs": 24000,
}

AREA_MIN_BTU = {
    "Até 12 m²": 9000,
    "13 a 19 m²": 12000,
    "20 a 27 m²": 18000,
    "28 a 37 m²": 24000,
}

OPCOES_AREA = [
    "Não sei",
    "Até 12 m²",
    "13 a 19 m²",
    "20 a 27 m²",
