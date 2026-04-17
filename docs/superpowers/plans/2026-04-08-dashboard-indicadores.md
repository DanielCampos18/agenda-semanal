# Dashboard Indicadores - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an interactive HTML dashboard for Inbound Marketing, Partners, and External Commercial indicators — auto-generated from an Excel spreadsheet via Python + BAT, following the same architecture as the existing `dashboard-comercial` project.

**Architecture:** Python pipeline reads Excel → calculates KPIs → renders Jinja2 template → outputs static HTML with Chart.js graphs and vanilla JS interactivity. Single-page layout with sticky nav, scroll spy, and section drill-downs. R-Torn visual identity (Montserrat, Navy #001b47, Gold #af946c).

**Tech Stack:** Python 3.12, pandas, openpyxl, Jinja2, Chart.js (CDN), vanilla CSS/JS.

**Spec:** `docs/superpowers/specs/2026-04-08-dashboard-indicadores-design.md`

**Reference project:** `dashboard-comercial/` (same repo, same patterns)

**Excel source:** `C:\Users\admin\Desktop\Indicadores\Dashboard Indicadores.xlsx`

---

## File Structure

```
dashboard-indicadores/
├── loader.py              # Reads all 5 Excel tabs, normalizes data
├── metricas.py            # Pure calculations: KPIs, funnels, trends, comparisons
├── gerar_dashboard.py     # Orchestrator: loader → metricas → Jinja2 → HTML
├── template.html          # Jinja2 template with embedded CSS + JS + Chart.js
├── dashboard.html          # Generated output (not versioned)
├── atualizar.bat           # Double-click trigger for Windows
├── setup.bat               # First-time dependency installer
├── requirements.txt        # pandas, openpyxl, jinja2
└── INSTRUCOES.md           # User guide
```

Each file has one clear responsibility:
- **loader.py**: I/O boundary — reads Excel, returns normalized Python dicts/DataFrames
- **metricas.py**: Pure business logic — no I/O, no side effects, receives data and returns computed context
- **gerar_dashboard.py**: Orchestration glue — connects loader→metricas→template→output
- **template.html**: Presentation — all HTML/CSS/JS in one self-contained file

---

## Task 1: Project Scaffold

**Files:**
- Create: `dashboard-indicadores/requirements.txt`
- Create: `dashboard-indicadores/setup.bat`
- Create: `dashboard-indicadores/atualizar.bat`
- Create: `dashboard-indicadores/INSTRUCOES.md`

- [ ] **Step 1: Create the project directory**

```bash
mkdir -p dashboard-indicadores
```

- [ ] **Step 2: Create requirements.txt**

```
pandas>=2.0.0
openpyxl>=3.1.0
jinja2>=3.1.0
```

- [ ] **Step 3: Create setup.bat**

Same pattern as `dashboard-comercial/setup.bat`. Detects Python, installs dependencies via pip.

```bat
@echo off
chcp 65001 >nul
echo ============================================
echo   Setup - Dashboard Indicadores
echo ============================================
echo.
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python nao encontrado. Tentando instalar via winget...
    winget install -e --id Python.Python.3.12
    if %ERRORLEVEL% NEQ 0 (
        echo ERRO: Nao foi possivel instalar Python.
        echo Instale manualmente: https://python.org/downloads
        pause
        exit /b 1
    )
)
echo Instalando dependencias...
pip install -r requirements.txt
echo.
echo Setup concluido!
pause
```

- [ ] **Step 4: Create atualizar.bat**

```bat
@echo off
chcp 65001 >nul
echo Atualizando Dashboard Indicadores...
python gerar_dashboard.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERRO ao gerar dashboard!
    pause
    exit /b 1
)
echo Dashboard atualizado com sucesso!
timeout /t 2 >nul
```

- [ ] **Step 5: Create INSTRUCOES.md**

Brief user guide in Portuguese: how to update Excel, save, close, double-click BAT. Same format as `dashboard-comercial/INSTRUCOES.md`.

- [ ] **Step 6: Commit**

```bash
git add dashboard-indicadores/
git commit -m "feat: scaffold dashboard-indicadores — requirements, setup, BAT, docs"
```

---

## Task 2: loader.py — Excel Data Ingestion

**Files:**
- Create: `dashboard-indicadores/loader.py`

**Reference:** `dashboard-comercial/loader.py` for pattern (but this one reads different tabs).

The Excel path is hardcoded: `C:\Users\admin\Desktop\Indicadores\Dashboard Indicadores.xlsx`

- [ ] **Step 1: Write loader.py with carregar_indicadores()**

```python
def carregar_indicadores(path: str) -> dict:
    """
    Reads all tabs from the indicators Excel and returns normalized data.
    
    Returns dict with keys:
        - inbound_diario: pd.DataFrame (columns: dia, mes, leads, interesse, contratos)
        - inbound_mensal: pd.DataFrame (columns: mes, total_leads, com_interesse, 
          contratos, pct_interesse, pct_fechamento, pct_conv, media_dia, dias_dados)
        - parceiros: dict with keys totais, indicaram, fecharam, pct_indicou,
          eficiencia, win_rate, sem_indicacao, indicaram_sem_fechar
        - clientes_parceiros: pd.DataFrame (columns: data, parceiro, empresa,
          reuniao, analise, apresentacao, fechamento)
        - comercial_externo: pd.DataFrame (columns: mes, visita_1, visita_2,
          procuracao, fechamento, total)
    """
```

Key implementation details:

**Inbound Dados tab:**
- Skip rows 0-1 (title + instruction), header at row 2 (0-indexed)
- Read with `header=2` or skip first 2 rows
- Column mapping: "Dia"→dia, "Mês"→mes, "Nº Leads"→leads, "Leads com Interesse"→interesse, "Contratos Fechados"→contratos
- Filter out row where col A = "TOTAL GERAL"
- Convert "Dia" to datetime, numeric cols to int (fillna 0)

**Resumo Mensal tab:**
- Skip rows 0-1 (title + instruction), header at row 2
- Column mapping: "Mês"→mes, "Total Leads"→total_leads, "Com Interesse"→com_interesse, "Contratos Fechados"→contratos, "% Interesse"→pct_interesse, "% Fechamento (total)"→pct_fechamento, "% Conv. Interesse→Fecha"→pct_conv, "Média Leads/Dia"→media_dia, "Dias com Dados"→dias_dados
- Filter out row where mes = "TOTAL"
- Numeric cols: fillna(0), floats stay as float

**Parceiros tab:**
- Key-value structure (col A = label, col B = value)
- Read specific cells by label matching:
  - "Parceiros Totais" → totais (int)
  - "Parceiros que Indicaram Empresas" → indicaram (int)
  - "Parceiros que Fecharam Negócio" → fecharam (int)
  - "% que Indicou Empresa" → pct_indicou (float)
  - "Eficiência de Conversão" → eficiencia (float)
  - "Win Rate da Base" → win_rate (float)
  - "Parceiros sem Indicação" → sem_indicacao (int)
  - "Indicaram mas não Fecharam" → indicaram_sem_fechar (int)

**Clientes de Parceiros tab:**
- Standard table with header at row 0
- Column mapping: "Data"→data, "Parceiro"→parceiro, "Empresa"→empresa, "Reunião"→reuniao, "Análise Inicial"→analise, "Apresentação de Resultados"→apresentacao, "Fechamento de contrato"→fechamento
- May be empty (only headers) — return empty DataFrame with correct columns

**Comercial Externo tab:**
- Skip rows 0-1, header at row 2
- Column mapping: "Mês"→mes, "1ª Visita"→visita_1, "2ª Visita"→visita_2, "Procuração Eletrônica"→procuracao, "Reunião de Fechamento"→fechamento, "Total Ações"→total
- Filter out "TOTAL" row
- Numeric cols: fillna(0), convert to int

- [ ] **Step 2: Test loader against real Excel**

```bash
cd dashboard-indicadores
python -c "
from loader import carregar_indicadores
dados = carregar_indicadores(r'C:\Users\admin\Desktop\Indicadores\Dashboard Indicadores.xlsx')
print('Inbound diário:', len(dados['inbound_diario']), 'rows')
print('Inbound mensal:', len(dados['inbound_mensal']), 'rows')
print('Parceiros:', dados['parceiros'])
print('Clientes parceiros:', len(dados['clientes_parceiros']), 'rows')
print('Comercial externo:', len(dados['comercial_externo']), 'rows')
"
```

Expected: Inbound diário ~89 rows (92 - header rows - TOTAL), mensal 12 rows, parceiros dict with all 8 keys, clientes 0 rows, externo 12 rows.

- [ ] **Step 3: Validate KPI values match Excel Dashboard tab**

```bash
python -c "
from loader import carregar_indicadores
d = carregar_indicadores(r'C:\Users\admin\Desktop\Indicadores\Dashboard Indicadores.xlsx')
m = d['inbound_mensal']
total = m['total_leads'].sum()
interesse = m['com_interesse'].sum()
contratos = m['contratos'].sum()
print(f'Total leads: {total} (expected 297)')
print(f'Com interesse: {interesse} (expected 95)')
print(f'Contratos: {contratos} (expected 13)')
p = d['parceiros']
print(f'Parceiros totais: {p[\"totais\"]} (expected 110)')
print(f'Indicaram: {p[\"indicaram\"]} (expected 54)')
print(f'Fecharam: {p[\"fecharam\"]} (expected 13)')
"
```

Expected: All values match the Excel Dashboard tab.

- [ ] **Step 4: Commit**

```bash
git add dashboard-indicadores/loader.py
git commit -m "feat(indicadores): loader.py — leitura e normalização do Excel"
```

---

## Task 3: metricas.py — Business Logic

**Files:**
- Create: `dashboard-indicadores/metricas.py`

**No I/O** — pure functions that take data and return computed dicts.

- [ ] **Step 1: Write metricas.py with all calculation functions**

```python
MESES_PT = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
             "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

MESES_FULL = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
              "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

def calcular_contexto(dados: dict, hoje: date) -> dict:
    """Main entry point: returns complete Jinja2 context."""
    # Calls all sub-functions and assembles the context dict
    
def calcular_kpis_inbound(inbound_mensal: pd.DataFrame) -> dict:
    """Returns: total_leads, com_interesse, contratos, taxa_conversao,
    taxa_interesse, taxa_conv_interesse"""
    # Sum all months, compute rates
    
def calcular_tendencia_diaria(inbound_diario: pd.DataFrame) -> list[dict]:
    """Returns list of {data: "DD/MM", leads: int, interesse: int, contratos: int}
    for Chart.js line chart."""
    # Convert DataFrame rows to list of dicts with formatted dates

def calcular_media_movel(inbound_diario: pd.DataFrame, janela: int = 7) -> list:
    """Returns 7-day moving average of leads for trend line overlay."""
    
def calcular_funil_inbound(inbound_mensal: pd.DataFrame) -> dict:
    """Returns {etapas: [{nome, count, pct}], maior_queda: str}
    Stages: Total Leads → Com Interesse → Contratos"""
    
def calcular_kpis_parceiros(parceiros: dict) -> dict:
    """Returns enriched parceiros dict with donut_data for Chart.js."""
    # Add: donut segments (fecharam, indicaram_sem_fechar, sem_indicacao)
    # Add: barras data for horizontal bar chart
    
def calcular_pipeline_parceiros(clientes: pd.DataFrame) -> list[dict]:
    """Returns list of client pipeline rows with stage badges."""
    # Each row: {data, parceiro, empresa, etapas: [{nome, status: bool}]}
    
def calcular_kpis_externo(externo: pd.DataFrame) -> dict:
    """Returns KPIs and monthly chart data for external commercial."""
    # total per stage, monthly stacked bar data
    
def calcular_comparativo(inbound_mensal, parceiros, externo) -> dict:
    """Cross-channel comparison data."""
    # Monthly: contratos_inbound per month (from inbound_mensal)
    # parceiros doesn't have monthly data — show as single total
    # externo: fechamento per month
    # Donut: total by channel
```

Key context dict structure returned by `calcular_contexto`:
```python
{
    "data_atualizacao": "08/04/2026 14:30",
    "kpis_inbound": {...},
    "tendencia_diaria": [...],
    "media_movel": [...],
    "funil_inbound": {...},
    "inbound_mensal": [...],  # table data
    "kpis_parceiros": {...},
    "pipeline_parceiros": [...],
    "kpis_externo": {...},
    "externo_mensal": [...],  # chart data
    "comparativo": {...},
    "meses_pt": MESES_PT,
}
```

- [ ] **Step 2: Test metricas against real data**

```bash
cd dashboard-indicadores
python -c "
from loader import carregar_indicadores
from metricas import calcular_contexto
from datetime import date
dados = carregar_indicadores(r'C:\Users\admin\Desktop\Indicadores\Dashboard Indicadores.xlsx')
ctx = calcular_contexto(dados, date.today())
print('KPIs Inbound:', ctx['kpis_inbound'])
print('KPIs Parceiros:', ctx['kpis_parceiros'])
print('KPIs Externo:', ctx['kpis_externo'])
print('Tendencia diaria entries:', len(ctx['tendencia_diaria']))
print('Comparativo:', ctx['comparativo'])
"
```

Expected: KPI values match Excel Dashboard tab values (297 leads, 95 interesse, 13 contratos, 110 parceiros, etc.)

- [ ] **Step 3: Commit**

```bash
git add dashboard-indicadores/metricas.py
git commit -m "feat(indicadores): metricas.py — cálculos de KPIs, funis e comparativos"
```

---

## Task 4: gerar_dashboard.py — Orchestrator

**Files:**
- Create: `dashboard-indicadores/gerar_dashboard.py`

**Reference:** `dashboard-comercial/gerar_dashboard.py` (same pattern, simpler — no Agendor API).

- [ ] **Step 1: Write gerar_dashboard.py**

```python
"""Ponto de entrada: lê o Excel, calcula métricas e gera dashboard.html."""

import json
import sys
import webbrowser
from pathlib import Path
from datetime import date, datetime

from jinja2 import Environment, FileSystemLoader

from loader import carregar_indicadores
from metricas import calcular_contexto

BASE_DIR = Path(__file__).parent
EXCEL_PATH = Path(r"C:\Users\admin\Desktop\Indicadores\Dashboard Indicadores.xlsx")
OUTPUT_PATH = BASE_DIR / "dashboard.html"


def main():
    print("Dashboard Indicadores — gerando...")

    if not EXCEL_PATH.exists():
        print(f"ERRO: Arquivo não encontrado: {EXCEL_PATH}")
        sys.exit(1)

    try:
        dados = carregar_indicadores(str(EXCEL_PATH))
    except Exception as e:
        print(f"ERRO ao ler Excel: {e}")
        sys.exit(1)

    contexto = calcular_contexto(dados, date.today())

    env = Environment(
        loader=FileSystemLoader(str(BASE_DIR)),
        autoescape=False,
    )
    env.filters["tojson"] = lambda v: json.dumps(v, ensure_ascii=False)

    template = env.get_template("template.html")
    html = template.render(**contexto)

    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Dashboard gerado: {OUTPUT_PATH}")

    webbrowser.open(OUTPUT_PATH.as_uri())
    print("Abrindo no navegador...")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add dashboard-indicadores/gerar_dashboard.py
git commit -m "feat(indicadores): gerar_dashboard.py — orquestrador Excel→HTML"
```

---

## Task 5: template.html — Complete Dashboard Template

**Files:**
- Create: `dashboard-indicadores/template.html`

This is the largest task. The template contains all CSS, HTML structure, and JavaScript.

**Reference:** `dashboard-comercial/template.html` for CSS patterns, but this template has different content.

- [ ] **Step 1: Write the HTML structure with embedded CSS**

Create `template.html` with:

**CSS (in `<style>`):**
- CSS variables matching R-Torn identity:
  ```css
  :root {
    --navy: #001b47;
    --gold: #af946c;
    --white: #ffffff;
    --bg: #F0F4F9;
    --card: #ffffff;
    --text: #0F172A;
    --muted: #64748B;
    --border: #CBD5E1;
    --green: #16A34A;
    --amber: #D97706;
    --red: #DC2626;
    --shadow: 0 1px 3px rgba(0,0,0,0.08);
    --shadow-md: 0 4px 6px rgba(0,0,0,0.08);
    --radius: 12px;
    --radius-sm: 8px;
  }
  ```
- Montserrat from Google Fonts (preconnect + link)
- Topbar: sticky, navy bg, 60px height
- Section containers: max-width 1400px, centered
- KPI cards: grid, hover elevation effect
- Chart containers: proper aspect ratio
- Table styles: navy header, alternating rows, hover highlight
- Funnel bars: CSS gradient navy→gold
- Scroll spy active state
- Print media queries
- Smooth scroll behavior

**HTML Structure:**
```html
<!-- Topbar -->
<header class="topbar">
  <div class="topbar-inner">
    <div class="topbar-brand">Dashboard Indicadores</div>
    <nav class="topbar-nav">
      <a href="#visao-geral" class="nav-link active">Visão Geral</a>
      <a href="#inbound" class="nav-link">Inbound</a>
      <a href="#parceiros" class="nav-link">Parceiros</a>
      <a href="#externo" class="nav-link">Externo</a>
      <a href="#comparativo" class="nav-link">Comparativo</a>
    </nav>
    <div class="topbar-meta">Atualizado: {{ data_atualizacao }}</div>
  </div>
</header>

<!-- Section 1: Visão Executiva -->
<section id="visao-geral" class="section">
  <!-- 3-column hero grid with KPIs per sector -->
  <!-- Each column clickable → smooth scroll to detail section -->
</section>

<!-- Section 2: Inbound Marketing -->
<section id="inbound" class="section">
  <!-- 4 KPI cards -->
  <!-- 2-col grid: bar chart (monthly) + line chart (daily trend) -->
  <!-- 2-col grid: funnel (CSS) + monthly summary table -->
</section>

<!-- Section 3: Parceiros -->
<section id="parceiros" class="section">
  <!-- 4 KPI cards -->
  <!-- 2-col grid: donut chart + horizontal bar chart -->
  <!-- Pipeline table (or empty state) -->
</section>

<!-- Section 4: Comercial Externo -->
<section id="externo" class="section">
  <!-- 4 KPI cards -->
  <!-- Stacked bar chart -->
  <!-- Monthly table -->
</section>

<!-- Section 5: Comparativo -->
<section id="comparativo" class="section">
  <!-- Grouped bar chart -->
  <!-- Donut distribution chart -->
</section>
```

- [ ] **Step 2: Write the JavaScript section**

In `<script>` at bottom of template:

```javascript
// Data from Jinja2
const TENDENCIA = {{ tendencia_diaria | tojson }};
const MEDIA_MOVEL = {{ media_movel | tojson }};
const INBOUND_MENSAL = {{ inbound_mensal | tojson }};
const PARCEIROS = {{ kpis_parceiros | tojson }};
const PIPELINE = {{ pipeline_parceiros | tojson }};
const EXTERNO_MENSAL = {{ externo_mensal | tojson }};
const COMPARATIVO = {{ comparativo | tojson }};
const MESES = {{ meses_pt | tojson }};
```

**Chart.js charts to create (each in its own function):**

1. `renderInboundMensal()` — Grouped bar chart (12 months × 3 series)
2. `renderTendenciaDiaria()` — Line chart with fill gradient + moving average overlay
3. `renderDonutParceiros()` — Donut with center label "110 Parceiros"
4. `renderTaxasParceiros()` — Horizontal bar chart (3 bars: % Indicou, Eficiência, Win Rate)
5. `renderExternoMensal()` — Stacked bar chart (12 months × 4 stages)
6. `renderComparativoMensal()` — Grouped bar chart (3 channels)
7. `renderComparativoDonut()` — Donut distribution by channel

**Interactivity functions:**
- `initScrollSpy()` — IntersectionObserver on sections, updates nav active state
- `initAnimations()` — IntersectionObserver on chart containers, triggers Chart.js animation
- `filterPipeline(parceiro)` — Filter pipeline table rows by partner name
- `scrollToSection(id)` — Smooth scroll on hero card click
- `_esc(str)` — HTML escape helper (same as dashboard-comercial)

**Chart.js configuration:**
- Load via CDN: `<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>`
- Common config: Montserrat font, responsive true, animation duration 800ms
- Tooltip: backgroundColor #0F172A, padding 12, cornerRadius 8
- Legend: position bottom, labels with boxWidth 12

- [ ] **Step 3: Run end-to-end test**

```bash
cd dashboard-indicadores
python gerar_dashboard.py
```

Expected: `dashboard.html` generated and opens in browser with all sections visible and charts rendering.

- [ ] **Step 4: Validate visual output**

Open `dashboard.html` in browser and verify:
- Topbar renders with nav links
- Visão Geral shows 3 columns with correct KPI values
- Inbound section: 4 KPIs, bar chart, line chart, funnel, table
- Parceiros section: 4 KPIs, donut, horizontal bars, empty pipeline state
- Externo section: 4 KPIs, stacked bars, table
- Comparativo section: grouped bars, donut
- Scroll spy works
- Chart tooltips work on hover

- [ ] **Step 5: Commit**

```bash
git add dashboard-indicadores/template.html
git commit -m "feat(indicadores): template.html — dashboard completo com Chart.js"
```

---

## Task 6: End-to-End Validation

**Files:**
- All files in `dashboard-indicadores/`

- [ ] **Step 1: Run full pipeline and verify KPI values**

```bash
cd dashboard-indicadores
python -c "
from loader import carregar_indicadores
from metricas import calcular_contexto
from datetime import date
dados = carregar_indicadores(r'C:\Users\admin\Desktop\Indicadores\Dashboard Indicadores.xlsx')
ctx = calcular_contexto(dados, date.today())

# Validate against Excel Dashboard tab
kpi = ctx['kpis_inbound']
assert kpi['total_leads'] == 297, f'Expected 297, got {kpi[\"total_leads\"]}'
assert kpi['com_interesse'] == 95, f'Expected 95, got {kpi[\"com_interesse\"]}'
assert kpi['contratos'] == 13, f'Expected 13, got {kpi[\"contratos\"]}'

p = ctx['kpis_parceiros']
assert p['totais'] == 110, f'Expected 110, got {p[\"totais\"]}'
assert p['indicaram'] == 54, f'Expected 54, got {p[\"indicaram\"]}'
assert p['fecharam'] == 13, f'Expected 13, got {p[\"fecharam\"]}'

print('All KPI validations passed!')
"
```

- [ ] **Step 2: Test atualizar.bat**

Double-click `atualizar.bat` or run:
```bash
cd dashboard-indicadores && cmd //c atualizar.bat
```

Expected: Dashboard generates and opens in browser.

- [ ] **Step 3: Verify all Chart.js charts render**

Use preview tools to check:
- All 7 canvas elements have rendered content
- No JavaScript console errors
- Tooltips appear on hover

- [ ] **Step 4: Commit any fixes**

```bash
git add dashboard-indicadores/
git commit -m "fix(indicadores): correções de validação end-to-end"
```

---

## Task 7: UI/UX Pro Max Polish

**Files:**
- Modify: `dashboard-indicadores/template.html`

This is the final refinement pass using the `ui-ux-pro-max` skill.

- [ ] **Step 1: Invoke ui-ux-pro-max skill**

Apply the UI/UX Pro Max skill to review and enhance the dashboard's visual design:
- Typography hierarchy and spacing
- Color consistency and contrast
- Card shadows and border-radius refinement
- Animation smoothness and timing
- Chart color palettes and readability
- Responsive behavior (projector 1920x1080 + laptop 1366x768)
- Print stylesheet
- Micro-interactions (hover, focus, active states)
- Visual rhythm and whitespace balance

- [ ] **Step 2: Apply UI/UX improvements to template.html**

Implement all recommendations from the UI/UX review.

- [ ] **Step 3: Verify visual improvements**

Generate dashboard and take screenshots for comparison.

- [ ] **Step 4: Final commit**

```bash
git add dashboard-indicadores/template.html
git commit -m "feat(indicadores): UI/UX Pro Max — polish visual final"
```

---

## Summary

| Task | Description | Key Output |
|------|-------------|------------|
| 1 | Project Scaffold | requirements.txt, setup.bat, atualizar.bat, INSTRUCOES.md |
| 2 | loader.py | Excel reader for all 5 tabs |
| 3 | metricas.py | KPI calculations, funnels, trends |
| 4 | gerar_dashboard.py | Orchestrator (loader→metricas→Jinja2→HTML) |
| 5 | template.html | Full dashboard with CSS + JS + Chart.js |
| 6 | End-to-End Validation | All KPIs verified, BAT tested, charts working |
| 7 | UI/UX Pro Max | Final visual polish |
