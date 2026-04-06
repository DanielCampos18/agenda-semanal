# dashboard-comercial/loader.py
"""Leitura e normalização do arquivo Excel dados_comercial.xlsx."""

import pandas as pd
from pathlib import Path


COLUNAS_EMPRESAS = [
    "ID", "Nome da Empresa", "CNPJ", "Segmento", "Cidade", "Estado",
    "Nome Contato", "Cargo", "Telefone", "E-mail", "Temperatura", "Porte",
    "Origem Lead", "Observações Gerais", "Ativo?",
]

COLUNAS_VISITAS = [
    "Data", "ID Empresa", "Etapa", "Visita Realizada?", "Procuração Assinada?",
    "Proposta Enviada?", "Contrato Fechado?", "Duração (min)", "Resultado",
    "Interesse (1-5)", "Próxima Ação", "Data Próx. Ação", "Obstáculo",
    "Relatório Resumido", "Registrado por",
]

CONFIG_DEFAULTS = {
    "nome_agente": "Agente",
    "sla_quente_dias": 30,
    "sla_normal_dias": 90,
    "ano_filtro": 2026,
    "empresa_nome": "Minha Empresa",
    "cor_primaria": "#001b47",
    "cor_acento": "#af946c",
    "alerta_amarelo_pct": 75,
    "mostrar_cnpj": "SIM",
    "mostrar_telefone": "NÃO",
}

CONFIG_INT_FIELDS = {"sla_quente_dias", "sla_normal_dias", "ano_filtro", "alerta_amarelo_pct"}


def carregar_excel(path: str) -> tuple:
    """Lê o Excel e retorna (df_empresas, df_visitas, config_dict).

    Raises:
        FileNotFoundError: se o arquivo não existir.
        ValueError: se alguma aba obrigatória estiver ausente.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    xls = pd.ExcelFile(path, engine="openpyxl")

    for aba in ("EMPRESAS", "VISITAS", "CONFIG"):
        if aba not in xls.sheet_names:
            raise ValueError(f"Aba obrigatória '{aba}' não encontrada no Excel.")

    df_empresas = pd.read_excel(xls, sheet_name="EMPRESAS", dtype=str)
    df_empresas = df_empresas.reindex(columns=COLUNAS_EMPRESAS)
    df_empresas = df_empresas.where(df_empresas.notna(), other=None)

    df_visitas = pd.read_excel(xls, sheet_name="VISITAS", dtype=str,
                               parse_dates=["Data", "Data Próx. Ação"])
    df_visitas = df_visitas.reindex(columns=COLUNAS_VISITAS)
    df_visitas["Data"] = pd.to_datetime(df_visitas["Data"], errors="coerce")
    df_visitas = df_visitas.where(df_visitas.notna(), other=None)
    for col in ("Duração (min)", "Interesse (1-5)"):
        if col in df_visitas.columns:
            df_visitas[col] = pd.to_numeric(df_visitas[col], errors="coerce")

    config = _carregar_config(xls)
    return df_empresas, df_visitas, config


def _carregar_config(xls: pd.ExcelFile) -> dict:
    """Carrega configurações da aba CONFIG do Excel.

    Valores ausentes ou vazios mantêm o default de CONFIG_DEFAULTS.
    Campos numéricos (CONFIG_INT_FIELDS) são convertidos para int.

    Returns:
        dict: Configuração com tipos corretos.
    """
    df = pd.read_excel(xls, sheet_name="CONFIG", header=0, dtype=str)
    cfg = dict(CONFIG_DEFAULTS)  # começa com defaults

    if "Parâmetro" not in df.columns or "Valor" not in df.columns:
        return cfg

    for _, row in df.iterrows():
        key = str(row.get("Parâmetro", "")).strip()
        val = row.get("Valor")

        if key not in cfg and key not in CONFIG_INT_FIELDS:
            continue  # ignora chaves desconhecidas

        if val is None or str(val).strip() in ("", "nan", "None"):
            continue  # mantém default

        val_str = str(val).strip()

        if key in CONFIG_INT_FIELDS:
            try:
                cfg[key] = int(float(val_str))
            except (ValueError, TypeError):
                pass  # mantém default
        else:
            cfg[key] = val_str

    return cfg


# Alias público para uso externo
carregar_config = _carregar_config
