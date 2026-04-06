# Dashboard Comercial Externo — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar um sistema completo Excel → Python → HTML que permite acompanhar o funil de vendas de um agente comercial externo, com alertas de SLA e dashboard interativo.

**Architecture:** O usuário preenche `dados_comercial.xlsx` (3 abas: EMPRESAS, VISITAS, CONFIG). Ao dar duplo clique em `atualizar.bat`, o script `gerar_dashboard.py` lê o Excel com pandas/openpyxl, calcula métricas conforme as regras de negócio da spec, e renderiza `dashboard.html` via Jinja2. O navegador abre automaticamente com os dados atualizados.

**Tech Stack:** Python 3.8+, pandas, openpyxl, jinja2 · Excel .xlsx · HTML/CSS/JS estático · Windows batch scripts

**Spec:** `docs/superpowers/specs/2026-04-06-dashboard-comercial-externo-design.md`

**Output dir:** `dashboard-comercial/` (dentro do diretório do projeto)

---

## File Structure

```
dashboard-comercial/
├── dados_comercial.xlsx       # Fonte de dados — usuário preenche aqui
├── criar_excel.py             # Gera/regenera dados_comercial.xlsx
├── gerar_dashboard.py         # Script principal (entry point)
├── metricas.py                # Regras de negócio puras (testável)
├── loader.py                  # Leitura e validação do Excel
├── template.html              # Template Jinja2 do dashboard
├── dashboard.html             # Gerado pelo script — não editar
├── atualizar.bat              # Duplo clique → atualiza + abre dashboard
├── setup.bat                  # Setup inicial (instala Python + deps)
├── requirements.txt           # pandas, openpyxl, jinja2
├── INSTRUCOES.md              # Guia de uso em português
└── tests/
    ├── test_metricas.py       # Testes das regras de negócio
    ├── test_loader.py         # Testes de leitura do Excel
    └── fixtures.py            # Dados de teste reutilizáveis
```

**Responsabilidades:**
- `loader.py` — lê o Excel, normaliza tipos, retorna DataFrames limpos. Não sabe nada de métricas.
- `metricas.py` — recebe DataFrames limpos, aplica todas as regras de negócio da spec, retorna dicionário `context` pronto para o template. Não sabe nada de Excel ou HTML.
- `template.html` — template Jinja2 puro. Recebe `context`, produz HTML. Não contém lógica Python.
- `gerar_dashboard.py` — orquestra: chama loader → metricas → renderiza template → salva dashboard.html → abre no navegador.

---

## Task 1: Scaffold — estrutura de diretórios e dependências

**Files:**
- Create: `dashboard-comercial/requirements.txt`
- Create: `dashboard-comercial/setup.bat`

- [ ] **Step 1: Criar o diretório do projeto**

```bash
mkdir dashboard-comercial
cd dashboard-comercial
```

- [ ] **Step 2: Criar requirements.txt**

```
pandas>=2.0.0
openpyxl>=3.1.0
jinja2>=3.1.0
```

- [ ] **Step 3: Criar setup.bat**

```bat
@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ============================================
echo  Setup — Dashboard Comercial Externo
echo ============================================
echo.

:: Verificar Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python nao encontrado. Tentando instalar via winget...
    winget install Python.Python.3.12 --silent
    if %errorlevel% neq 0 (
        echo.
        echo ATENCAO: Instalacao automatica falhou.
        echo Instale manualmente em: https://www.python.org/downloads/
        echo Marque a opcao "Add Python to PATH" durante a instalacao.
        echo Depois execute este arquivo novamente.
        pause
        exit /b 1
    )
    echo Python instalado com sucesso!
) else (
    echo Python encontrado:
    python --version
)

echo.
echo Instalando dependencias...
python -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Setup concluido! Use atualizar.bat para
echo  gerar o dashboard.
echo ============================================
pause
```

- [ ] **Step 4: Verificar estrutura**

```bash
ls dashboard-comercial/
```
Esperado: `requirements.txt`, `setup.bat`

- [ ] **Step 5: Commit**

```bash
git add dashboard-comercial/
git commit -m "feat: scaffold dashboard-comercial — requirements e setup.bat"
```

---

## Task 2: loader.py — leitura e normalização do Excel

**Files:**
- Create: `dashboard-comercial/loader.py`
- Create: `dashboard-comercial/tests/fixtures.py`
- Create: `dashboard-comercial/tests/test_loader.py`

- [ ] **Step 1: Criar fixtures.py com DataFrames de teste**

```python
# dashboard-comercial/tests/fixtures.py
import pandas as pd
from datetime import date

EMPRESAS = pd.DataFrame({
    "ID": ["EMP001", "EMP002", "EMP003"],
    "Nome da Empresa": ["Metalúrgica Souza", "Distribuidora Norte", "Alpha Contabilidade"],
    "CNPJ": ["12.345.678/0001-99", None, "55.123.456/0001-77"],
    "Segmento": ["Indústria", "Comércio", "Contabilidade"],
    "Cidade": ["São Paulo", "Campinas", "São Paulo"],
    "Estado": ["SP", "SP", "SP"],
    "Nome Contato": ["Carlos Souza", "Ana Lima", "Roberto Alves"],
    "Cargo": ["Diretor", "Gerente Financeiro", "Sócio"],
    "Telefone": ["(11) 99999-0001", "(19) 98888-0002", "(11) 97777-0003"],
    "E-mail": ["carlos@souza.com", "ana@dnorte.com.br", "roberto@alpha.cnt"],
    "Temperatura": ["Quente", "Normal", "Quente"],
    "Porte": ["Médio", "Grande", "Pequeno"],
    "Origem Lead": ["Indicação", "Prospecção ativa", "LinkedIn"],
    "Observações Gerais": ["Interesse REFIS", "Aguarda diretoria", "Reunião marcada"],
    "Ativo?": ["SIM", "SIM", "SIM"],
})

VISITAS = pd.DataFrame({
    "Data": [
        date(2026, 1, 2), date(2026, 1, 15), date(2026, 2, 10),
        date(2026, 3, 20),
    ],
    "ID Empresa": ["EMP001", "EMP002", "EMP002", "EMP003"],
    "Etapa": ["1ª Visita", "1ª Visita", "2ª Visita", "Reunião de Fechamento"],
    "Visita Realizada?": ["SIM", "SIM", "SIM", "SIM"],
    "Procuração Assinada?": ["NÃO", "NÃO", "NÃO", "SIM"],
    "Proposta Enviada?": ["NÃO", "NÃO", "SIM", "SIM"],
    "Contrato Fechado?": ["NÃO", "NÃO", "NÃO", "NÃO"],
    "Duração (min)": [45, 30, 60, 90],
    "Resultado": ["Positivo", "Neutro", "Positivo", "Positivo"],
    "Interesse (1-5)": [5, 3, 4, 5],
    "Próxima Ação": ["Agendar 2ª visita", "Aguardar retorno", "Aguardar procuração", "Reunião assinatura"],
    "Data Próx. Ação": [date(2026, 2, 15), date(2026, 2, 1), date(2026, 2, 25), date(2026, 4, 15)],
    "Obstáculo": [None, "Decisão em comitê", "Aguarda jurídico", None],
    "Relatório Resumido": ["Diretor receptivo", "Gerente receptiva", "Apresentou simulação", "Sócio aprovou"],
    "Registrado por": ["João Silva"] * 4,
})

CONFIG = {
    "nome_agente": "João Silva",
    "sla_quente_dias": 30,
    "sla_normal_dias": 90,
    "ano_filtro": 2026,
    "empresa_nome": "Inteligência Tributária Ltda",
    "cor_primaria": "#001b47",
    "cor_acento": "#af946c",
    "alerta_amarelo_pct": 75,
    "mostrar_cnpj": "SIM",
    "mostrar_telefone": "NÃO",
}
```

- [ ] **Step 2: Escrever testes para loader**

```python
# dashboard-comercial/tests/test_loader.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import tempfile
import openpyxl
from loader import carregar_excel, carregar_config

def criar_excel_minimo(path):
    """Cria um Excel mínimo válido para testes."""
    wb = openpyxl.Workbook()
    # Aba EMPRESAS
    ws_emp = wb.active
    ws_emp.title = "EMPRESAS"
    ws_emp.append(["ID", "Nome da Empresa", "CNPJ", "Segmento", "Cidade",
                   "Estado", "Nome Contato", "Cargo", "Telefone", "E-mail",
                   "Temperatura", "Porte", "Origem Lead", "Observações Gerais", "Ativo?"])
    ws_emp.append(["EMP001", "Empresa Teste", None, "Serviços", "SP", "SP",
                   "João", "Diretor", None, None, "Quente", "Médio", None, None, "SIM"])
    # Aba VISITAS
    ws_vis = wb.create_sheet("VISITAS")
    ws_vis.append(["Data", "ID Empresa", "Etapa", "Visita Realizada?",
                   "Procuração Assinada?", "Proposta Enviada?", "Contrato Fechado?",
                   "Duração (min)", "Resultado", "Interesse (1-5)", "Próxima Ação",
                   "Data Próx. Ação", "Obstáculo", "Relatório Resumido", "Registrado por"])
    from datetime import date
    ws_vis.append([date(2026, 3, 1), "EMP001", "1ª Visita", "SIM",
                   "NÃO", "NÃO", "NÃO", 30, "Positivo", 4, None, None, None, None, None])
    # Aba CONFIG
    ws_cfg = wb.create_sheet("CONFIG")
    ws_cfg.append(["Parâmetro", "Valor", "Descrição"])
    for row in [
        ["nome_agente", "Agente Teste", ""],
        ["sla_quente_dias", 30, ""],
        ["sla_normal_dias", 90, ""],
        ["ano_filtro", 2026, ""],
        ["empresa_nome", "Empresa X", ""],
        ["cor_primaria", "#001b47", ""],
        ["cor_acento", "#af946c", ""],
        ["alerta_amarelo_pct", 75, ""],
        ["mostrar_cnpj", "SIM", ""],
        ["mostrar_telefone", "NÃO", ""],
    ]:
        ws_cfg.append(row)
    wb.save(path)


def test_carregar_excel_retorna_tres_dataframes():
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        path = f.name
    criar_excel_minimo(path)
    empresas, visitas, config = carregar_excel(path)
    assert len(empresas) == 1
    assert len(visitas) == 1
    assert config["nome_agente"] == "Agente Teste"


def test_carregar_excel_arquivo_inexistente():
    with pytest.raises(FileNotFoundError):
        carregar_excel("nao_existe.xlsx")


def test_carregar_config_valores_numericos():
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        path = f.name
    criar_excel_minimo(path)
    _, _, config = carregar_excel(path)
    assert isinstance(config["sla_quente_dias"], int)
    assert isinstance(config["sla_normal_dias"], int)
    assert isinstance(config["alerta_amarelo_pct"], int)
    assert config["sla_quente_dias"] == 30


def test_carregar_config_fallback_campos_vazios():
    wb = openpyxl.Workbook()
    ws_emp = wb.active
    ws_emp.title = "EMPRESAS"
    ws_emp.append(["ID", "Nome da Empresa", "CNPJ", "Segmento", "Cidade",
                   "Estado", "Nome Contato", "Cargo", "Telefone", "E-mail",
                   "Temperatura", "Porte", "Origem Lead", "Observações Gerais", "Ativo?"])
    ws_vis = wb.create_sheet("VISITAS")
    ws_vis.append(["Data", "ID Empresa", "Etapa", "Visita Realizada?",
                   "Procuração Assinada?", "Proposta Enviada?", "Contrato Fechado?",
                   "Duração (min)", "Resultado", "Interesse (1-5)", "Próxima Ação",
                   "Data Próx. Ação", "Obstáculo", "Relatório Resumido", "Registrado por"])
    ws_cfg = wb.create_sheet("CONFIG")
    ws_cfg.append(["Parâmetro", "Valor", "Descrição"])
    ws_cfg.append(["nome_agente", None, ""])   # vazio
    ws_cfg.append(["empresa_nome", None, ""])  # vazio
    ws_cfg.append(["sla_quente_dias", 30, ""])
    ws_cfg.append(["sla_normal_dias", 90, ""])
    ws_cfg.append(["ano_filtro", 2026, ""])
    ws_cfg.append(["cor_primaria", "#001b47", ""])
    ws_cfg.append(["cor_acento", "#af946c", ""])
    ws_cfg.append(["alerta_amarelo_pct", 75, ""])
    ws_cfg.append(["mostrar_cnpj", "SIM", ""])
    ws_cfg.append(["mostrar_telefone", "NÃO", ""])
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        path = f.name
    wb.save(path)
    _, _, config = carregar_excel(path)
    assert config["nome_agente"] == "Agente"
    assert config["empresa_nome"] == "Minha Empresa"
```

- [ ] **Step 3: Rodar testes — confirmar que FALHAM**

```bash
cd dashboard-comercial
python -m pytest tests/test_loader.py -v
```
Esperado: `ModuleNotFoundError: No module named 'loader'`

- [ ] **Step 4: Implementar loader.py**

```python
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

    config = _carregar_config(xls)
    return df_empresas, df_visitas, config


def _carregar_config(xls: pd.ExcelFile) -> dict:
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
```

- [ ] **Step 5: Rodar testes — confirmar que PASSAM**

```bash
python -m pytest tests/test_loader.py -v
```
Esperado: 4 testes `PASSED`

- [ ] **Step 6: Commit**

```bash
git add dashboard-comercial/loader.py dashboard-comercial/tests/
git commit -m "feat: loader.py — leitura e normalização do Excel"
```

---

## Task 3: metricas.py — regras de negócio

**Files:**
- Create: `dashboard-comercial/metricas.py`
- Create: `dashboard-comercial/tests/test_metricas.py`

- [ ] **Step 1: Escrever testes para metricas**

```python
# dashboard-comercial/tests/test_metricas.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from datetime import date, timedelta
import pandas as pd
from tests.fixtures import EMPRESAS, VISITAS, CONFIG
from metricas import (
    calcular_etapa_atual,
    calcular_dias_sem_retorno,
    calcular_alertas,
    calcular_funil,
    calcular_kpis,
    calcular_resumo_mensal,
    calcular_contexto,
)


# ── calcular_etapa_atual ───────────────────────────────────────────

def test_etapa_atual_retorna_etapa_mais_recente():
    resultado = calcular_etapa_atual("EMP002", VISITAS)
    assert resultado == "2ª Visita"  # última visita realizada de EMP002

def test_etapa_atual_sem_visitas_retorna_tracejado():
    resultado = calcular_etapa_atual("EMP999", VISITAS)
    assert resultado == "—"

def test_etapa_atual_visita_nao_realizada_ignorada():
    visitas = pd.DataFrame({
        "Data": [date(2026, 1, 1), date(2026, 2, 1)],
        "ID Empresa": ["EMP001", "EMP001"],
        "Etapa": ["1ª Visita", "2ª Visita"],
        "Visita Realizada?": ["SIM", "NÃO"],  # 2ª não realizada
    })
    resultado = calcular_etapa_atual("EMP001", visitas)
    assert resultado == "1ª Visita"

def test_etapa_atual_ordenacao_por_data_descendente():
    visitas = pd.DataFrame({
        "Data": [date(2026, 3, 1), date(2026, 1, 1)],
        "ID Empresa": ["EMP001", "EMP001"],
        "Etapa": ["2ª Visita", "1ª Visita"],
        "Visita Realizada?": ["SIM", "SIM"],
    })
    # linha 0 tem data mais recente apesar de ser linha 0
    resultado = calcular_etapa_atual("EMP001", visitas)
    assert resultado == "2ª Visita"

def test_etapa_atual_empate_de_data_usa_ultima_linha():
    """Spec: em empate de data, usar a última linha (maior número de linha)."""
    visitas = pd.DataFrame({
        "Data": [date(2026, 3, 1), date(2026, 3, 1)],  # mesma data
        "ID Empresa": ["EMP001", "EMP001"],
        "Etapa": ["1ª Visita", "2ª Visita"],  # linha 1 é a "última"
        "Visita Realizada?": ["SIM", "SIM"],
    })
    resultado = calcular_etapa_atual("EMP001", visitas)
    assert resultado == "2ª Visita"  # última linha ganha em empate


# ── calcular_dias_sem_retorno ─────────────────────────────────────

def test_dias_sem_retorno_sem_visitas_retorna_none():
    resultado = calcular_dias_sem_retorno("EMP999", VISITAS, hoje=date(2026, 4, 6))
    assert resultado is None

def test_dias_sem_retorno_calcula_diferenca_corretamente():
    visitas = pd.DataFrame({
        "Data": [date(2026, 3, 1)],
        "ID Empresa": ["EMP001"],
        "Visita Realizada?": ["SIM"],
        "Etapa": ["1ª Visita"],
    })
    resultado = calcular_dias_sem_retorno("EMP001", visitas, hoje=date(2026, 4, 6))
    assert resultado == 36  # 06/04 - 01/03 = 36 dias


# ── calcular_alertas ─────────────────────────────────────────────

def test_alerta_vermelho_quando_dias_maior_igual_sla():
    # Quente: SLA 30d. 30 dias = vermelho
    alerta = _make_empresa_alerta(dias=30, temperatura="Quente", config=CONFIG)
    assert alerta["cor"] == "red"

def test_alerta_amarelo_quando_dias_entre_75pct_e_sla():
    # Quente: SLA 30d. 75% = 22.5d → ≥23 dias = amarelo, <30 = amarelo
    alerta = _make_empresa_alerta(dias=25, temperatura="Quente", config=CONFIG)
    assert alerta["cor"] == "yellow"

def test_sem_alerta_quando_dentro_do_prazo():
    alerta = _make_empresa_alerta(dias=10, temperatura="Quente", config=CONFIG)
    assert alerta is None

def test_empresa_com_visita_atrasada_gera_alerta():
    alertas = calcular_alertas(EMPRESAS, VISITAS, CONFIG, hoje=date(2026, 4, 6))
    ids = [a["id"] for a in alertas]
    # EMP001 tem 1 visita em 02/01/2026 → 94 dias → vermelho (quente, sla=30)
    assert "EMP001" in ids

def test_empresa_sem_visita_nao_gera_alerta():
    """Spec: empresas sem visitas realizadas não geram alertas."""
    empresas = pd.DataFrame({
        "ID": ["EMPX"], "Nome da Empresa": ["Sem Visita"], "Temperatura": ["Quente"],
        "Ativo?": ["SIM"], "Segmento": ["Serviços"],
        "Cidade": [None], "Estado": [None], "Observações Gerais": [None],
    })
    visitas_vazias = pd.DataFrame(columns=["Data", "ID Empresa", "Etapa", "Visita Realizada?"])
    alertas = calcular_alertas(empresas, visitas_vazias, CONFIG, hoje=date(2026, 4, 6))
    assert len(alertas) == 0

def _make_empresa_alerta(dias, temperatura, config):
    """Helper: cria empresa+visita sintética e retorna alerta se houver."""
    hoje = date(2026, 4, 6)
    data_visita = hoje - timedelta(days=dias)
    empresas = pd.DataFrame({
        "ID": ["EMPX"], "Nome da Empresa": ["Teste"], "Temperatura": [temperatura],
        "Ativo?": ["SIM"], "Segmento": ["Serviços"],
        "Cidade": [None], "Estado": [None], "Observações Gerais": [None],
    })
    visitas = pd.DataFrame({
        "Data": [data_visita], "ID Empresa": ["EMPX"],
        "Etapa": ["1ª Visita"], "Visita Realizada?": ["SIM"],
    })
    alertas = calcular_alertas(empresas, visitas, config, hoje=hoje)
    return alertas[0] if alertas else None


# ── calcular_funil ────────────────────────────────────────────────

def test_funil_conta_empresas_distintas_por_etapa():
    funil = calcular_funil(EMPRESAS, VISITAS)
    # Spec: conta empresas com ao menos 1 visita realizada EM CADA ETAPA (não cumulativo)
    # EMP001: tem "1ª Visita" → conta na barra 1ª Visita
    # EMP002: tem "1ª Visita" e "2ª Visita" → conta em ambas
    # EMP003: tem "Reunião de Fechamento" apenas → conta só no Fechamento, NÃO na 1ª Visita
    assert funil["1ª Visita"]["count"] == 2    # EMP001, EMP002
    assert funil["2ª Visita"]["count"] == 1    # EMP002

def test_funil_percentual_calculado_sobre_primeira_visita():
    funil = calcular_funil(EMPRESAS, VISITAS)
    total_1v = funil["1ª Visita"]["count"]
    pct_2v = funil["2ª Visita"]["pct"]
    assert pct_2v == round(funil["2ª Visita"]["count"] / total_1v * 100, 1)

def test_funil_maior_queda_formato_portugues():
    funil = calcular_funil(EMPRESAS, VISITAS)
    maior_queda = funil["maior_queda"]
    assert "→" in maior_queda
    assert "%" in maior_queda

def test_funil_sem_dados_retorna_strings_vazias():
    """Spec: dataset vazio não deve gerar divisão por zero ou texto inválido."""
    visitas_vazias = pd.DataFrame(columns=["Data", "ID Empresa", "Etapa", "Visita Realizada?"])
    funil = calcular_funil(EMPRESAS, visitas_vazias)
    assert funil["1ª Visita"]["count"] == 0
    assert funil["1ª Visita"]["pct"] == 0.0
    assert funil["maior_queda"] == ""  # sem dados → sem texto de queda


# ── calcular_kpis ─────────────────────────────────────────────────

def test_kpi_total_primeira_visita():
    kpis = calcular_kpis(EMPRESAS, VISITAS, CONFIG, hoje=date(2026, 4, 6))
    assert kpis["total_1v"] == 2  # EMP001, EMP002

def test_kpi_procuracoes_conta_etapa_nao_booleano():
    # EMP003 tem Reunião de Fechamento mas não Procuração Eletrônica no fixture
    kpis = calcular_kpis(EMPRESAS, VISITAS, CONFIG, hoje=date(2026, 4, 6))
    assert kpis["total_procuracoes"] == 0  # nenhuma Procuração Eletrônica no fixture


# ── calcular_resumo_mensal ────────────────────────────────────────

def test_resumo_mensal_conta_por_mes_e_etapa():
    resumo = calcular_resumo_mensal(VISITAS, ano=2026)
    # Janeiro: 1 visita de EMP001 (1ª Visita) + 1 de EMP002 (1ª Visita)
    jan = resumo[1]  # mês 1
    assert jan["1ª Visita"] == 2

def test_resumo_mensal_nao_conta_nao_realizada():
    visitas = pd.DataFrame({
        "Data": [date(2026, 1, 5)],
        "ID Empresa": ["EMP001"],
        "Etapa": ["1ª Visita"],
        "Visita Realizada?": ["NÃO"],
    })
    resumo = calcular_resumo_mensal(visitas, ano=2026)
    assert resumo[1]["1ª Visita"] == 0
```

- [ ] **Step 2: Rodar testes — confirmar que FALHAM**

```bash
python -m pytest tests/test_metricas.py -v
```
Esperado: `ModuleNotFoundError: No module named 'metricas'`

- [ ] **Step 3: Implementar metricas.py**

```python
# dashboard-comercial/metricas.py
"""Regras de negócio do dashboard — sem dependências de I/O."""

from datetime import date
import math
import pandas as pd

ETAPAS_ORDEM = [
    "1ª Visita",
    "2ª Visita",
    "Procuração Eletrônica",
    "Reunião de Fechamento",
]

MESES_PT = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
             "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def _visitas_realizadas(df_visitas: pd.DataFrame) -> pd.DataFrame:
    """Retorna apenas linhas com Visita Realizada? == SIM."""
    mask = df_visitas["Visita Realizada?"].str.upper().str.strip() == "SIM"
    return df_visitas[mask].copy()


def _empresas_ativas(df_empresas: pd.DataFrame) -> pd.DataFrame:
    mask = df_empresas["Ativo?"].str.upper().str.strip() == "SIM"
    return df_empresas[mask].copy()


def calcular_etapa_atual(id_empresa: str, df_visitas: pd.DataFrame) -> str:
    """Etapa da última visita realizada da empresa. Retorna '—' se nenhuma."""
    df = _visitas_realizadas(df_visitas)
    df = df[df["ID Empresa"] == id_empresa].copy()
    if df.empty:
        return "—"
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.sort_values("Data", ascending=False, kind="stable")
    return str(df.iloc[0]["Etapa"])


def calcular_dias_sem_retorno(id_empresa: str, df_visitas: pd.DataFrame,
                               hoje: date = None) -> int | None:
    """Dias desde a última visita realizada. Retorna None se sem visitas."""
    if hoje is None:
        hoje = date.today()
    df = _visitas_realizadas(df_visitas)
    df = df[df["ID Empresa"] == id_empresa].copy()
    if df.empty:
        return None
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    ultima = df["Data"].max()
    if pd.isna(ultima):
        return None
    return (pd.Timestamp(hoje) - ultima).days


def calcular_alertas(df_empresas: pd.DataFrame, df_visitas: pd.DataFrame,
                      config: dict, hoje: date = None) -> list:
    """Retorna lista de alertas ordenados por dias desc."""
    if hoje is None:
        hoje = date.today()

    ativas = _empresas_ativas(df_empresas)
    sla_map = {
        "quente": config["sla_quente_dias"],
        "normal": config["sla_normal_dias"],
    }
    pct = config["alerta_amarelo_pct"] / 100
    alertas = []

    for _, emp in ativas.iterrows():
        id_emp = emp["ID"]
        dias = calcular_dias_sem_retorno(id_emp, df_visitas, hoje)
        if dias is None:
            continue

        temp = str(emp.get("Temperatura", "Normal")).strip().lower()
        sla = sla_map.get(temp, sla_map["normal"])
        limiar_amarelo = math.ceil(sla * pct)

        if dias >= sla:
            cor = "red"
        elif dias >= limiar_amarelo:
            cor = "yellow"
        else:
            continue

        etapa = calcular_etapa_atual(id_emp, df_visitas)
        alertas.append({
            "id": id_emp,
            "empresa": emp["Nome da Empresa"],
            "etapa": etapa,
            "temperatura": emp.get("Temperatura", "Normal"),
            "dias": dias,
            "sla": sla,
            "cor": cor,
        })

    return sorted(alertas, key=lambda x: x["dias"], reverse=True)


def calcular_funil(df_empresas: pd.DataFrame, df_visitas: pd.DataFrame) -> dict:
    """Calcula contagem e % por etapa + texto da maior queda."""
    ativas = _empresas_ativas(df_empresas)
    ids_ativas = set(ativas["ID"].tolist())
    realizadas = _visitas_realizadas(df_visitas)
    realizadas = realizadas[realizadas["ID Empresa"].isin(ids_ativas)]

    funil = {}
    for etapa in ETAPAS_ORDEM:
        empresas_na_etapa = set(
            realizadas[realizadas["Etapa"] == etapa]["ID Empresa"].unique()
        )
        funil[etapa] = {"count": len(empresas_na_etapa)}

    total_1v = funil["1ª Visita"]["count"]
    for etapa in ETAPAS_ORDEM:
        count = funil[etapa]["count"]
        funil[etapa]["pct"] = round(count / total_1v * 100, 1) if total_1v > 0 else 0.0

    # Maior queda entre etapas consecutivas
    # Somente calculado quando há ao menos 1 empresa na 1ª Visita
    maior_queda_txt = ""
    if total_1v > 0:
        maior_queda_diff = -1
        for i in range(len(ETAPAS_ORDEM) - 1):
            e_a, e_b = ETAPAS_ORDEM[i], ETAPAS_ORDEM[i + 1]
            diff = funil[e_a]["pct"] - funil[e_b]["pct"]
            if diff > maior_queda_diff:
                maior_queda_diff = diff
                n = round(diff, 1)
                maior_queda_txt = f"Maior queda: {e_a} → {e_b} ({n}%)"

    funil["maior_queda"] = maior_queda_txt
    return funil


def calcular_kpis(df_empresas: pd.DataFrame, df_visitas: pd.DataFrame,
                   config: dict, hoje: date = None) -> dict:
    """Retorna dicionário com os 5 valores dos KPI cards."""
    if hoje is None:
        hoje = date.today()

    ativas = _empresas_ativas(df_empresas)
    ids_ativas = set(ativas["ID"].tolist())
    realizadas = _visitas_realizadas(df_visitas)
    realizadas = realizadas[realizadas["ID Empresa"].isin(ids_ativas)]

    def _count_etapa(etapa):
        return len(set(realizadas[realizadas["Etapa"] == etapa]["ID Empresa"].unique()))

    total_1v = _count_etapa("1ª Visita")
    total_2v = _count_etapa("2ª Visita")
    total_proc = _count_etapa("Procuração Eletrônica")
    total_fech = _count_etapa("Reunião de Fechamento")

    alertas = calcular_alertas(df_empresas, df_visitas, config, hoje)
    total_alertas = len(alertas)
    alertas_criticos = sum(1 for a in alertas if a["cor"] == "red")
    alertas_atencao = sum(1 for a in alertas if a["cor"] == "yellow")

    pct_conv_2v = round(total_2v / total_1v * 100, 1) if total_1v > 0 else 0.0

    return {
        "total_1v": total_1v,
        "total_2v": total_2v,
        "total_procuracoes": total_proc,
        "total_fechamentos": total_fech,
        "total_alertas": total_alertas,
        "alertas_criticos": alertas_criticos,
        "alertas_atencao": alertas_atencao,
        "pct_conv_2v": pct_conv_2v,
    }


def calcular_resumo_mensal(df_visitas: pd.DataFrame, ano: int) -> dict:
    """Retorna dict {mes_num: {etapa: count}} apenas para visitas realizadas no ano.

    Nota: conta LINHAS (visitas), não empresas distintas — por spec Section 6.
    Isso é diferente do funil e dos KPIs, que contam empresas distintas.
    """
    realizadas = _visitas_realizadas(df_visitas).copy()
    realizadas["Data"] = pd.to_datetime(realizadas["Data"], errors="coerce")
    realizadas = realizadas[realizadas["Data"].dt.year == ano]

    resumo = {m: {e: 0 for e in ETAPAS_ORDEM} for m in range(1, 13)}
    for _, row in realizadas.iterrows():
        mes = row["Data"].month
        etapa = str(row["Etapa"]).strip()
        if etapa in resumo[mes]:
            resumo[mes][etapa] += 1

    return resumo


def calcular_tabela_empresas(df_empresas: pd.DataFrame, df_visitas: pd.DataFrame,
                               config: dict, hoje: date = None) -> list:
    """Retorna lista de dicts com dados completos por empresa para a tabela."""
    if hoje is None:
        hoje = date.today()

    sla_map = {
        "quente": config["sla_quente_dias"],
        "normal": config["sla_normal_dias"],
    }
    pct = config["alerta_amarelo_pct"] / 100

    rows = []
    for _, emp in df_empresas.iterrows():
        ativo = str(emp.get("Ativo?", "SIM")).strip().upper()
        id_emp = emp["ID"]
        etapa = calcular_etapa_atual(id_emp, df_visitas)
        dias = calcular_dias_sem_retorno(id_emp, df_visitas, hoje)

        temp = str(emp.get("Temperatura", "Normal")).strip().lower()
        sla = sla_map.get(temp, sla_map["normal"])
        limiar_amarelo = math.ceil(sla * pct)

        if dias is None:
            cor_dias = "none"
        elif dias >= sla:
            cor_dias = "red"
        elif dias >= limiar_amarelo:
            cor_dias = "yellow"
        else:
            cor_dias = "green"

        # Última ação
        realizadas = _visitas_realizadas(df_visitas)
        emp_vis = realizadas[realizadas["ID Empresa"] == id_emp].copy()
        emp_vis["Data"] = pd.to_datetime(emp_vis["Data"], errors="coerce")
        ultima_data = ""
        if not emp_vis.empty:
            ultima_data = emp_vis["Data"].max().strftime("%d/%m/%Y")

        rows.append({
            "id": id_emp,
            "nome": emp.get("Nome da Empresa", ""),
            "segmento": emp.get("Segmento", ""),
            "temperatura": emp.get("Temperatura", "Normal"),
            "etapa": etapa,
            "ultima_data": ultima_data,
            "dias": dias if dias is not None else "—",
            "cor_dias": cor_dias,
            "sla": sla,
            "observacao": emp.get("Observações Gerais", "") or "",
            "ativo": ativo,
            "cnpj": emp.get("CNPJ", "") or "",
            "telefone": emp.get("Telefone", "") or "",
        })

    return rows


def calcular_contexto(df_empresas: pd.DataFrame, df_visitas: pd.DataFrame,
                       config: dict, hoje: date = None) -> dict:
    """Ponto de entrada único: retorna contexto completo para o template."""
    if hoje is None:
        hoje = date.today()

    ano = config["ano_filtro"]
    return {
        "config": config,
        "data_atualizacao": hoje.strftime("%d/%m/%Y"),
        "kpis": calcular_kpis(df_empresas, df_visitas, config, hoje),
        "funil": calcular_funil(df_empresas, df_visitas),
        "alertas": calcular_alertas(df_empresas, df_visitas, config, hoje),
        "tabela": calcular_tabela_empresas(df_empresas, df_visitas, config, hoje),
        # resumo_por_ano: chave = ano (int), valor = dict mensal
        # O template embute ambos como JSON; o JS troca via botão de ano
        "resumo_por_ano": {
            ano: calcular_resumo_mensal(df_visitas, ano),
            ano - 1: calcular_resumo_mensal(df_visitas, ano - 1),
        },
        "meses_pt": MESES_PT,
        "etapas_ordem": ETAPAS_ORDEM,
        "hoje_ano": hoje.year,
        "ano_filtro": ano,
    }
```

- [ ] **Step 4: Rodar testes — confirmar que PASSAM**

```bash
python -m pytest tests/test_metricas.py -v
```
Esperado: todos `PASSED`

- [ ] **Step 5: Commit**

```bash
git add dashboard-comercial/metricas.py dashboard-comercial/tests/test_metricas.py dashboard-comercial/tests/fixtures.py
git commit -m "feat: metricas.py — regras de negócio completas com testes"
```

---

## Task 4: template.html — template Jinja2 do dashboard

**Files:**
- Create: `dashboard-comercial/template.html`

> Nota: o mockup aprovado está em `.superpowers/brainstorm/262-1775504681/dashboard-v2.html` (gerado durante o brainstorming). O Step 1 abaixo copia esse arquivo como ponto de partida e instrui todas as substituições necessárias. Se o arquivo não existir, seguir as instruções do bloco abaixo.

- [ ] **Step 1: Copiar o mockup aprovado como base**

```bash
cp ".superpowers/brainstorm/262-1775504681/dashboard-v2.html" "dashboard-comercial/template.html"
```

**Se o arquivo não existir**, criar `dashboard-comercial/template.html` do zero com base na spec Section 4 (Design System + Componentes). O arquivo deve conter:
- Estrutura HTML5 completa com `<meta charset="UTF-8">` e viewport
- Google Fonts Montserrat (400/500/600/700/800)
- CSS inline com as variáveis CSS da spec: `--navy: {{ config.cor_primaria }}`, `--gold: {{ config.cor_acento }}`, `--bg: #F0F4F9`, danger/warn/ok tokens
- Topbar navy com nome do agente e data de atualização
- Grid de 5 KPI cards com borda colorida por tipo
- Card funil (barras horizontais) + card gráfico mensal (barras verticais)
- Card alertas + card resumo mensal em grid 2:1
- Tabela completa com filtros JavaScript
- Toda a lógica JavaScript descrita no Step 1a abaixo

- [ ] **Step 1a: Substituir todos os valores estáticos por variáveis Jinja2**

Abrir `dashboard-comercial/template.html` e aplicar as seguintes substituições:

| Valor estático | Variável Jinja2 |
|---|---|
| `"João Silva"` (agente) | `{{ config.nome_agente }}` |
| `"06/04/2026 · 14:32"` | `Atualizado: {{ data_atualizacao }}` |
| Número `24` (1ª visita KPI) | `{{ kpis.total_1v }}` |
| Número `14` (2ª visita KPI) | `{{ kpis.total_2v }}` |
| Número `6` (procurações KPI) | `{{ kpis.total_procuracoes }}` |
| Número `3` (fechamentos KPI) | `{{ kpis.total_fechamentos }}` |
| Número `5` (alertas KPI) | `{{ kpis.total_alertas }}` |
| `"2 críticos · 3 em atenção"` | `{{ kpis.alertas_criticos }} críticos · {{ kpis.alertas_atencao }} em atenção` |
| `"58% de conversão"` | `{{ kpis.pct_conv_2v }}% de conversão` |
| Barras do funil (width%) | `{{ funil['1ª Visita'].pct }}` etc. |
| Texto maior queda | `{{ funil.maior_queda }}` |
| Barras mensais (height) | `{% for mes in range(1,13) %}` loop |
| Lista de alertas | `{% for alerta in alertas %}` loop |
| Linhas da tabela | `{% for emp in tabela %}` loop |
| Pills de etapa | `{% if emp.etapa == '1ª Visita' %}pill-1{% endif %}` |
| Cor dos dias | `class="dias-{{ emp.cor_dias }}"` |
| `#001b47` | `{{ config.cor_primaria }}` |
| `#af946c` | `{{ config.cor_acento }}` |
| Filtro CNPJ visível | `{% if config.mostrar_cnpj == 'SIM' %}` |
| Filtro Telefone visível | `{% if config.mostrar_telefone == 'SIM' %}` |
| Botão de anos | `{{ ano_filtro }}` e `{{ ano_filtro - 1 }}` |
| Resumo mensal linhas | `{% for m in range(1,13) %}` loop |
| Dados mensais (JS) | `const RESUMO_POR_ANO = {{ resumo_por_ano \| tojson }};` |

O template deve incluir o JavaScript para:
- Filtros da tabela (Todas / Quentes / Atrasadas / Em Fechamento / Inativas)
- Troca de ano no gráfico mensal: `RESUMO_POR_ANO[anoSelecionado]` — os dados de ambos os anos já estão embutidos como JSON; o JS apenas troca qual objeto renderiza as barras
- Botões filter-btn com toggle de classe `active`

- [ ] **Step 2: Verificar que o template é sintaxe Jinja2 válida**

```python
from jinja2 import Environment
env = Environment()
with open("template.html") as f:
    src = f.read()
env.parse(src)
print("Template válido")
```

- [ ] **Step 3: Commit**

```bash
git add dashboard-comercial/template.html
git commit -m "feat: template.html — template Jinja2 do dashboard"
```

---

## Task 5: gerar_dashboard.py — orquestrador principal

**Files:**
- Create: `dashboard-comercial/gerar_dashboard.py`

- [ ] **Step 1: Implementar gerar_dashboard.py**

```python
# dashboard-comercial/gerar_dashboard.py
"""Ponto de entrada: lê o Excel, calcula métricas e gera dashboard.html."""

import sys
import webbrowser
from pathlib import Path
from datetime import date

from jinja2 import Environment, FileSystemLoader

from loader import carregar_excel
from metricas import calcular_contexto

BASE_DIR = Path(__file__).parent
EXCEL_PATH = BASE_DIR / "dados_comercial.xlsx"
TEMPLATE_PATH = BASE_DIR / "template.html"
OUTPUT_PATH = BASE_DIR / "dashboard.html"


def main():
    print("Dashboard Comercial Externo — gerando...")

    # 1. Carregar dados
    if not EXCEL_PATH.exists():
        print(f"ERRO: Arquivo não encontrado: {EXCEL_PATH}")
        print("Certifique-se que 'dados_comercial.xlsx' está na mesma pasta.")
        sys.exit(1)

    try:
        df_empresas, df_visitas, config = carregar_excel(str(EXCEL_PATH))
    except Exception as e:
        print(f"ERRO ao ler o Excel: {e}")
        sys.exit(1)

    # 2. Calcular contexto
    contexto = calcular_contexto(df_empresas, df_visitas, config, hoje=date.today())

    # 3. Renderizar template
    env = Environment(
        loader=FileSystemLoader(str(BASE_DIR)),
        autoescape=False,
    )
    # Adiciona filtro tojson para uso no template
    import json
    env.filters["tojson"] = lambda v: json.dumps(v, ensure_ascii=False)

    template = env.get_template("template.html")
    html = template.render(**contexto)

    # 4. Salvar dashboard.html
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Dashboard gerado: {OUTPUT_PATH}")

    # 5. Abrir no navegador
    webbrowser.open(OUTPUT_PATH.as_uri())
    print("Abrindo no navegador...")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Criar atualizar.bat**

```bat
@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo Atualizando dashboard...
python gerar_dashboard.py
if %errorlevel% neq 0 (
    echo.
    echo ERRO ao gerar o dashboard.
    echo Verifique se o Python esta instalado (execute setup.bat).
    pause
) else (
    echo.
    echo Dashboard atualizado com sucesso!
    timeout /t 3 > nul
)
```

- [ ] **Step 3: Testar geração end-to-end com dados do fixture**

```python
# Rodar manualmente para verificar
# 1. Copiar temporariamente um Excel de teste
# 2. python gerar_dashboard.py
# 3. Verificar que dashboard.html foi criado e abre no navegador
```

```bash
cd dashboard-comercial
python gerar_dashboard.py
```
Esperado: mensagem `Dashboard gerado: ...dashboard.html` + navegador abre

- [ ] **Step 4: Commit**

```bash
git add dashboard-comercial/gerar_dashboard.py dashboard-comercial/atualizar.bat
git commit -m "feat: gerar_dashboard.py + atualizar.bat — orquestrador e atalho Windows"
```

---

## Task 6: dados_comercial.xlsx — Excel pré-formatado

**Files:**
- Create: `dashboard-comercial/criar_excel.py` (mantido no repo — permite regenerar o Excel se necessário)
- Create: `dashboard-comercial/dados_comercial.xlsx`

- [ ] **Step 1: Criar script para gerar o Excel com formatação e validações**

```python
# dashboard-comercial/criar_excel.py
"""Gera o dados_comercial.xlsx pré-formatado com validações e dados de exemplo."""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter
from datetime import date

NAVY = "001b47"
GOLD = "af946c"
HEADER_FONT = Font(name="Calibri", bold=True, color="FFFFFF", size=10)
HEADER_FILL = PatternFill("solid", fgColor=NAVY)
AUTO_FILL = PatternFill("solid", fgColor="DBEAFE")  # azul claro = auto
CENTER = Alignment(horizontal="center", vertical="center")
WRAP = Alignment(wrap_text=True, vertical="top")

def estilizar_cabecalho(ws, colunas):
    for i, col in enumerate(colunas, 1):
        cell = ws.cell(row=1, column=i, value=col)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = CENTER
    ws.row_dimensions[1].height = 30

def adicionar_validacao_lista(ws, col_letra, valores, start_row=2, end_row=1000):
    dv = DataValidation(type="list", formula1=f'"{",".join(valores)}"', allow_blank=True)
    dv.sqref = f"{col_letra}{start_row}:{col_letra}{end_row}"
    ws.add_data_validation(dv)

wb = openpyxl.Workbook()

# ── ABA EMPRESAS ──────────────────────────────────────────────────
ws_emp = wb.active
ws_emp.title = "EMPRESAS"

cols_emp = [
    "ID", "Nome da Empresa", "CNPJ", "Segmento", "Cidade", "Estado",
    "Nome Contato", "Cargo", "Telefone", "E-mail", "Temperatura",
    "Porte", "Origem Lead", "Observações Gerais", "Ativo?",
    "Etapa Atual", "Dias Sem Retorno",
]
estilizar_cabecalho(ws_emp, cols_emp)

# Colunas AUTO com fill azul
for col_auto in ["A", "P", "Q"]:
    ws_emp.column_dimensions[col_auto].width = 10
    cell = ws_emp[f"{col_auto}1"]
    cell.fill = PatternFill("solid", fgColor="1E40AF")

# Larguras
larguras_emp = [10, 30, 20, 18, 15, 6, 20, 20, 16, 28, 10, 10, 18, 35, 8, 20, 16]
for i, w in enumerate(larguras_emp, 1):
    ws_emp.column_dimensions[get_column_letter(i)].width = w

# Validações
adicionar_validacao_lista(ws_emp, "K", ["Quente", "Normal"])
adicionar_validacao_lista(ws_emp, "L", ["Pequeno", "Médio", "Grande"])
adicionar_validacao_lista(ws_emp, "O", ["SIM", "NÃO"])

# Dados de exemplo
exemplos_emp = [
    ["EMP001", "Metalúrgica Souza Ltda", "12.345.678/0001-99", "Indústria",
     "São Paulo", "SP", "Carlos Souza", "Diretor", "(11) 99999-0001",
     "carlos@souza.com", "Quente", "Médio", "Indicação", "Interesse em REFIS", "SIM", "", ""],
    ["EMP002", "Distribuidora Norte S/A", "98.765.432/0001-11", "Comércio",
     "Campinas", "SP", "Ana Lima", "Gerente Financeiro", "(19) 98888-0002",
     "ana@dnorte.com.br", "Normal", "Grande", "Prospecção ativa", "Aguarda diretoria", "SIM", "", ""],
]
for row in exemplos_emp:
    ws_emp.append(row)

# Congelar linha de cabeçalho
ws_emp.freeze_panes = "A2"

# ── ABA VISITAS ───────────────────────────────────────────────────
ws_vis = wb.create_sheet("VISITAS")
cols_vis = [
    "Data", "ID Empresa", "Etapa", "Visita Realizada?", "Procuração Assinada?",
    "Proposta Enviada?", "Contrato Fechado?", "Duração (min)", "Resultado",
    "Interesse (1-5)", "Próxima Ação", "Data Próx. Ação", "Obstáculo",
    "Relatório Resumido", "Registrado por",
]
estilizar_cabecalho(ws_vis, cols_vis)

larguras_vis = [12, 10, 25, 16, 20, 16, 16, 12, 20, 14, 25, 14, 25, 40, 18]
for i, w in enumerate(larguras_vis, 1):
    ws_vis.column_dimensions[get_column_letter(i)].width = w

adicionar_validacao_lista(ws_vis, "C", ["1ª Visita", "2ª Visita", "Procuração Eletrônica", "Reunião de Fechamento"])
adicionar_validacao_lista(ws_vis, "D", ["SIM", "NÃO"])
adicionar_validacao_lista(ws_vis, "E", ["SIM", "NÃO"])
adicionar_validacao_lista(ws_vis, "F", ["SIM", "NÃO"])
adicionar_validacao_lista(ws_vis, "G", ["SIM", "NÃO"])
adicionar_validacao_lista(ws_vis, "I", ["Positivo", "Neutro", "Negativo", "Sem Contato"])

ws_vis.append([date(2026, 1, 2), "EMP001", "1ª Visita", "SIM", "NÃO", "NÃO", "NÃO",
               45, "Positivo", 5, "Agendar 2ª visita", date(2026, 2, 15),
               None, "Diretor muito receptivo ao REFIS", "João Silva"])
ws_vis.freeze_panes = "A2"

# ── ABA CONFIG ────────────────────────────────────────────────────
ws_cfg = wb.create_sheet("CONFIG")
ws_cfg.column_dimensions["A"].width = 22
ws_cfg.column_dimensions["B"].width = 30
ws_cfg.column_dimensions["C"].width = 50

header_cfg = ["Parâmetro", "Valor", "Descrição"]
estilizar_cabecalho(ws_cfg, header_cfg)

params = [
    ["nome_agente", "João Silva", "Nome do agente exibido no dashboard"],
    ["sla_quente_dias", 30, "Prazo máximo de retorno para prospects Quentes (dias)"],
    ["sla_normal_dias", 90, "Prazo máximo de retorno para prospects Normais (dias)"],
    ["ano_filtro", 2026, "Ano padrão do gráfico mensal"],
    ["empresa_nome", "Inteligência Tributária Ltda", "Nome da sua empresa (rodapé)"],
    ["cor_primaria", "#001b47", "Cor principal do dashboard (Navy)"],
    ["cor_acento", "#af946c", "Cor de destaque (Ouro)"],
    ["alerta_amarelo_pct", 75, "% do SLA para exibir alerta amarelo"],
    ["mostrar_cnpj", "SIM", "Exibir CNPJ na tabela (SIM ou NÃO)"],
    ["mostrar_telefone", "NÃO", "Exibir telefone na tabela (SIM ou NÃO)"],
]
for row in params:
    ws_cfg.append(row)
    ws_cfg.cell(ws_cfg.max_row, 3).alignment = WRAP

ws_cfg.freeze_panes = "A2"

wb.save("dados_comercial.xlsx")
print("dados_comercial.xlsx gerado com sucesso.")
```

- [ ] **Step 2: Executar o script**

```bash
cd dashboard-comercial
python criar_excel.py
```
Esperado: `dados_comercial.xlsx gerado com sucesso.`

- [ ] **Step 3: Verificar o Excel no Excel/LibreOffice**

Abrir `dados_comercial.xlsx` e confirmar:
- 3 abas presentes (EMPRESAS, VISITAS, CONFIG)
- Cabeçalhos navy com texto branco
- Dropdowns funcionando nas colunas de lista
- 2 linhas de exemplo na aba EMPRESAS
- 1 linha de exemplo na aba VISITAS
- 10 parâmetros na aba CONFIG

- [ ] **Step 4: Commit**

```bash
git add dashboard-comercial/dados_comercial.xlsx dashboard-comercial/criar_excel.py
git commit -m "feat: dados_comercial.xlsx — Excel pré-formatado com validações e exemplos"
```

> `criar_excel.py` é mantido no repositório para permitir regenerar o Excel caso o arquivo seja corrompido ou precise de atualização de colunas.

---

## Task 7: INSTRUCOES.md — guia do usuário

**Files:**
- Create: `dashboard-comercial/INSTRUCOES.md`

- [ ] **Step 1: Criar INSTRUCOES.md em português**

```markdown
# Dashboard Comercial Externo — Instruções de Uso

## Primeiro uso (apenas 1 vez)

1. Dê duplo clique em **`setup.bat`**
2. Aguarde a instalação automática do Python e das dependências
3. Se aparecer erro de Python não encontrado:
   - Acesse: https://www.python.org/downloads/
   - Baixe a versão mais recente (botão amarelo)
   - Durante a instalação, marque **"Add Python to PATH"**
   - Execute `setup.bat` novamente

---

## Uso diário

### 1. Registrar uma nova empresa
1. Abra `dados_comercial.xlsx`
2. Vá para a aba **EMPRESAS**
3. Adicione uma linha com os dados da empresa
   - Preencha: Nome, Segmento, Temperatura e Ativo? (obrigatórios)
   - Deixe as colunas **Etapa Atual** e **Dias Sem Retorno** em branco — elas são automáticas

### 2. Registrar uma visita ou ação
1. Vá para a aba **VISITAS**
2. Adicione uma linha nova com:
   - **Data**: data da visita
   - **ID Empresa**: ID da aba EMPRESAS (ex: EMP001)
   - **Etapa**: escolha da lista
   - **Visita Realizada?**: SIM ou NÃO
   - Preencha os demais campos conforme disponível
3. Salve o arquivo (Ctrl+S)

### 3. Atualizar o dashboard
- Dê duplo clique em **`atualizar.bat`**
- O dashboard abrirá automaticamente no navegador
- O processo leva cerca de 2 segundos

---

## Entendendo o dashboard

### KPIs (cards do topo)
- **1ªs Visitas**: empresas que receberam a primeira visita
- **2ªs Visitas**: empresas que receberam o retorno
- **Procurações**: empresas que chegaram à etapa de Procuração Eletrônica
- **Fechamentos**: empresas em Reunião de Fechamento
- **Alertas**: empresas com SLA de retorno vencido ou próximo

### Alertas de Follow-up
- 🔴 **Vermelho**: prazo de retorno ultrapassado (ação urgente)
- 🟡 **Amarelo**: prazo ≥ 75% consumido (atenção)

### Prazos (SLA)
- Prospect **Quente**: retorno esperado em até **30 dias**
- Prospect **Normal**: retorno esperado em até **90 dias**

### Tabela de Empresas — Filtros
- **Todas**: todas as empresas ativas
- **Quentes**: apenas temperatura Quente
- **Atrasadas**: empresas com alerta vermelho ou amarelo
- **Em Fechamento**: empresas na etapa Reunião de Fechamento
- **Inativas**: empresas marcadas como Ativo? = NÃO

---

## Configurações (aba CONFIG)

Para ajustar parâmetros sem precisar de programação, edite a coluna **Valor** na aba CONFIG:

| Parâmetro | O que faz |
|---|---|
| `nome_agente` | Nome exibido no topo do dashboard |
| `sla_quente_dias` | Prazo de retorno para prospects Quentes |
| `sla_normal_dias` | Prazo de retorno para prospects Normais |
| `empresa_nome` | Nome da sua empresa no rodapé |
| `alerta_amarelo_pct` | % do SLA que ativa alerta amarelo (padrão: 75%) |
| `mostrar_cnpj` | SIM ou NÃO — exibe CNPJ na tabela |

Após editar o CONFIG, salve o Excel e rode `atualizar.bat`.

---

## Problemas comuns

**"Python não encontrado"**
→ Execute `setup.bat` ou instale em python.org (marque "Add Python to PATH")

**"Arquivo não encontrado: dados_comercial.xlsx"**
→ Certifique-se que `atualizar.bat` está na mesma pasta que `dados_comercial.xlsx`

**Dashboard abre mas sem dados**
→ Verifique se a coluna "Visita Realizada?" está preenchida com "SIM" (não "sim" ou "s")

**Aba ausente no Excel**
→ O arquivo precisa ter as 3 abas: EMPRESAS, VISITAS, CONFIG (com estes nomes exatos)
```

- [ ] **Step 2: Commit**

```bash
git add dashboard-comercial/INSTRUCOES.md
git commit -m "docs: INSTRUCOES.md — guia de uso em português"
```

---

## Task 8: Teste end-to-end e validação final

- [ ] **Step 1: Rodar toda a suite de testes**

```bash
cd dashboard-comercial
python -m pytest tests/ -v
```
Esperado: todos os testes `PASSED`, zero `FAILED`

- [ ] **Step 2: Teste de geração completa**

```bash
python gerar_dashboard.py
```
Verificar no navegador:
- [ ] KPIs exibem valores corretos baseados nos dados de exemplo
- [ ] Funil mostra barras proporcionais
- [ ] Painel de alertas exibe EMP001 (visita de jan/2026, >30 dias)
- [ ] Tabela lista as 2 empresas de exemplo com pills corretos
- [ ] Gráfico mensal mostra barra em Janeiro
- [ ] Filtros da tabela funcionam ao clicar
- [ ] Troca de ano no gráfico funciona

- [ ] **Step 3: Verificar template Jinja2 não deixou placeholders**

```bash
grep -n "{{" dashboard-comercial/dashboard.html | head -5
```
Esperado: nenhuma ocorrência (todo `{{ }}` foi substituído)

- [ ] **Step 4: Commit final**

```bash
git add -A
git commit -m "feat: dashboard comercial externo fase A — entrega completa

- loader.py: leitura e normalização do Excel
- metricas.py: regras de negócio com testes
- template.html: dashboard HTML/CSS/JS interativo
- gerar_dashboard.py: orquestrador
- dados_comercial.xlsx: Excel pré-formatado
- atualizar.bat + setup.bat: automação Windows
- INSTRUCOES.md: guia do usuário em português"
```
