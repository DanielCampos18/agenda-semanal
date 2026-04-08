# Dashboard Indicadores - Comercial Interno & Parceiros

**Data:** 2026-04-08
**Autor:** Dashboard Dev
**Status:** Aprovado para implementação

## Objetivo

Criar um dashboard HTML interativo para visualização dos indicadores do comercial interno (Inbound Marketing), setor de parcerias e comercial externo. O dashboard será apresentado aos sócios da empresa e deve ser referência visual na organização.

O sistema segue o mesmo padrão do `dashboard-comercial` existente: o usuário atualiza a planilha Excel, salva, fecha, e executa um `.bat` que gera automaticamente o HTML atualizado.

## Fonte de Dados

**Arquivo:** `C:\Users\admin\Desktop\Indicadores\Dashboard Indicadores.xlsx`

### Abas e Estrutura

#### 1. Inbound Dados (dados diários)
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| Dia | datetime | Data do registro |
| Mês | string | Nome do mês em português |
| Nº Leads | int | Quantidade de leads no dia |
| Leads com Interesse | int | Leads qualificados |
| Contratos Fechados | int | Contratos assinados |

- ~92 linhas (Jan-Abr 2026), crescendo diariamente
- Linha final: "TOTAL GERAL" (deve ser ignorada no processamento)

#### 2. Resumo Mensal (calculado automaticamente no Excel)
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| Mês | string | Nome do mês |
| Total Leads | int | Soma mensal |
| Com Interesse | int | Soma mensal |
| Contratos Fechados | int | Soma mensal |
| % Interesse | float | Com Interesse / Total Leads |
| % Fechamento (total) | float | Contratos / Total Leads |
| % Conv. Interesse→Fecha | float | Contratos / Com Interesse |
| Média Leads/Dia | float | Total / Dias com dados |
| Dias com Dados | int | Dias úteis registrados |

- 12 linhas (meses) + 1 linha TOTAL
- Dados calculados automaticamente pelo Excel

#### 3. Parceiros (KPIs consolidados)
| Campo | Valor Atual | Tipo |
|-------|-------------|------|
| Parceiros Totais | 110 | int (input) |
| Parceiros que Indicaram Empresas | 54 | int (input) |
| Parceiros que Fecharam Negócio | 13 | int (input) |
| % que Indicou Empresa | 49.1% | float (calculado) |
| Eficiência de Conversão | 24.1% | float (calculado) |
| Win Rate da Base | 11.8% | float (calculado) |
| Parceiros sem Indicação | 56 | int (calculado) |
| Indicaram mas não Fecharam | 41 | int (calculado) |

- Estrutura key-value (coluna A = label, coluna B = valor)
- Seção "Para Gráficos" com dados pré-formatados para visualização

#### 4. Clientes de Parceiros (pipeline individual)
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| Data | datetime | Data do registro |
| Parceiro | string | Nome do parceiro |
| Empresa | string | Empresa indicada |
| Reunião | string/bool | Status da etapa |
| Análise Inicial | string/bool | Status da etapa |
| Apresentação de Resultados | string/bool | Status da etapa |
| Fechamento de contrato | string/bool | Status da etapa |

- Atualmente vazia (só cabeçalhos) — o dashboard deve exibir estado vazio amigável
- Quando preenchida, mostrar pipeline visual

#### 5. Comercial Externo (resumo mensal)
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| Mês | string | Nome do mês |
| 1ª Visita | int | Qtd no mês |
| 2ª Visita | int | Qtd no mês |
| Procuração Eletrônica | int | Qtd no mês |
| Reunião de Fechamento | int | Qtd no mês |
| Total Ações | int | Soma (calculado) |

- 12 linhas (meses) + 1 TOTAL

## Arquitetura

### Stack Técnico
- **Python 3.12+** — processamento de dados
- **pandas + openpyxl** — leitura do Excel
- **Jinja2** — renderização do template HTML
- **Chart.js** (CDN ou inline) — gráficos interativos
- **CSS vanilla** — estilização (identidade R-Torn)
- **JavaScript vanilla** — interatividade e animações
- **atualizar.bat** — trigger de atualização

### Fluxo de Dados
```
Dashboard Indicadores.xlsx
        ↓
    loader.py (lê todas as abas, normaliza dados)
        ↓
    metricas.py (calcula KPIs, tendências, funis)
        ↓
    gerar_dashboard.py (orquestra: loader → metricas → Jinja2 → HTML)
        ↓
    template.html (Jinja2 com CSS + JS embutidos)
        ↓
    dashboard.html (arquivo final, abre no navegador)
        ↓
    atualizar.bat (trigger: python gerar_dashboard.py)
```

### Estrutura de Arquivos
```
dashboard-indicadores/
├── loader.py              # Leitura e normalização do Excel
├── metricas.py            # Cálculos de KPIs e métricas
├── gerar_dashboard.py     # Orquestrador principal
├── template.html          # Template Jinja2 do dashboard
├── dashboard.html         # Output gerado (não versionado)
├── atualizar.bat          # Trigger de atualização
├── setup.bat              # Instalação de dependências
├── requirements.txt       # pandas, openpyxl, jinja2
└── INSTRUCOES.md          # Guia de uso para o usuário
```

## Design do Dashboard

### Identidade Visual (R-Torn)
- **Fonte:** Montserrat (Google Fonts, weights: 400, 500, 600, 700, 800)
- **Cores primárias:** Navy #001b47, Gold #af946c, White #ffffff
- **Cores de status:** Green #16A34A, Amber #D97706, Red #DC2626
- **Background:** #F0F4F9 (cinza azulado claro)
- **Cards:** #ffffff com sombra suave
- **Border-radius:** 12px (cards), 8px (botões)

### Layout — Página Única com Scroll e Navegação

#### Topbar (sticky, 60px)
- Background navy #001b47
- Logo R-Torn à esquerda
- Título: "Dashboard Indicadores" com destaque gold
- Navegação: links "Visão Geral" | "Inbound" | "Parceiros" | "Externo"
- Badge: "Atualizado: DD/MM/YYYY HH:MM"
- Scroll spy: destaca a seção visível no nav

#### Seção 1: Visão Executiva (hero)
3 colunas representando cada setor:

**Coluna Inbound Marketing:**
- Ícone + título "Inbound Marketing"
- KPI grande: Total de Leads (297)
- KPI secundário: Contratos Fechados (13)
- KPI secundário: Taxa de Conversão (4%)
- Mini sparkline dos últimos 3 meses

**Coluna Parceiros:**
- Ícone + título "Parceiros"
- KPI grande: Parceiros Totais (110)
- KPI secundário: Fecharam Negócio (13)
- KPI secundário: Eficiência (24%)
- Mini donut chart (Fecharam / Indicaram / Não indicaram)

**Coluna Comercial Externo:**
- Ícone + título "Comercial Externo"
- KPI grande: Total Ações (6)
- KPI secundário: 1ªs Visitas (6)
- Mini bar chart dos meses

Cada coluna é clicável → scroll suave para a seção detalhada.

#### Seção 2: Inbound Marketing (detalhes)

**Linha 1 — 4 KPI Cards:**
| Total Leads | Com Interesse | Contratos Fechados | Taxa Conversão |
|-------------|---------------|--------------------|-----------------| 
| 297         | 95            | 13                 | 4.4%            |

**Linha 2 — 2 gráficos lado a lado:**
- **Esquerda:** Gráfico de barras agrupadas (Chart.js) — 12 meses
  - Barras: Leads (navy), Interesse (gold), Contratos (green)
  - Tooltip com valores exatos
  - Animação de entrada

- **Direita:** Gráfico de linha (Chart.js) — tendência diária
  - Linha de leads diários com fill gradient
  - Média móvel (7 dias) sobreposta
  - Zoom/pan habilitado via plugin

**Linha 3 — Funil de Conversão + Tabela:**
- **Esquerda:** Funil visual horizontal
  - Total Leads (100%) → Com Interesse (32%) → Contratos (4.4%)
  - Taxas de queda entre etapas
  - Barras degradê navy→gold

- **Direita:** Tabela resumo mensal completa
  - Todas as colunas do "Resumo Mensal"
  - Header navy, linhas alternadas
  - Coluna do mês atual destacada
  - Hover com highlight

#### Seção 3: Parceiros (detalhes)

**Linha 1 — 4 KPI Cards:**
| Parceiros Totais | Indicaram Empresa | Fecharam Negócio | Eficiência Conversão |
|------------------|-------------------|------------------|----------------------|
| 110              | 54 (49%)          | 13               | 24.1%                |

**Linha 2 — 2 gráficos lado a lado:**
- **Esquerda:** Gráfico Donut (Chart.js)
  - 3 segmentos: Fecharam (green), Indicaram sem fechar (gold), Não indicaram (gray)
  - Label central: "110 Parceiros"
  - Tooltip com valores e percentuais

- **Direita:** Barras horizontais de taxas
  - % Indicou Empresa (49.1%)
  - Eficiência Conversão (24.1%)
  - Win Rate (11.8%)
  - Barras com gradiente navy, labels à direita

**Linha 3 — Pipeline de Clientes de Parceiros:**
- Tabela interativa com status visual por etapa
- Cada etapa (Reunião → Análise → Apresentação → Fechamento) como ícone/badge
- Se checado: badge verde ✓ / Se não: badge cinza ○
- Estado vazio amigável quando sem dados: "Nenhum cliente de parceiro registrado ainda"
- Filtro por parceiro (dropdown)

#### Seção 4: Comercial Externo (detalhes)

**Linha 1 — 4 KPI Cards:**
| 1ª Visita | 2ª Visita | Procuração | Fechamento |
|-----------|-----------|------------|------------|
| 6         | 0         | 0          | 0          |

**Linha 2 — Gráfico de barras empilhadas:**
- 12 meses, 4 cores (uma por etapa)
- Mesma paleta do dashboard externo existente
- Total no topo de cada barra

**Linha 3 — Tabela mensal:**
- Mês × Etapa com totais
- Nota/link: "Para detalhes por empresa, consulte o Dashboard Comercial Externo"

#### Seção 5: Comparativo Geral

**Gráfico de barras agrupadas:**
- Eixo X: meses
- 3 séries: Contratos Inbound, Fechamentos Parceiros, Fechamentos Externo
- Compara performance dos 3 canais lado a lado

**Card de contribuição:**
- Donut mostrando % de cada canal no total de negócios fechados
- Label: "Distribuição de Resultados por Canal"

### Interatividade

1. **Navegação scroll spy** — nav no topo destaca seção visível
2. **Click nos KPIs da visão geral** → scroll suave para seção
3. **Tooltips** em todos os gráficos (Chart.js nativo)
4. **Animações de entrada** — gráficos animam ao entrar na viewport (IntersectionObserver)
5. **Hover effects** — cards elevam com sombra, tabelas destacam linha
6. **Filtro por parceiro** na tabela de pipeline
7. **Responsivo** — funciona em projetor (1920x1080) e monitores menores
8. **Tecla Escape** fecha modais/overlays
9. **Print-friendly** — CSS @media print para impressão limpa

## Módulo: loader.py

### Função principal
```python
def carregar_indicadores(path: str) -> dict:
    """
    Retorna dicionário com todos os dados normalizados:
    {
        "inbound_diario": pd.DataFrame,    # Inbound Dados
        "inbound_mensal": pd.DataFrame,     # Resumo Mensal
        "parceiros": dict,                  # KPIs de parceiros
        "clientes_parceiros": pd.DataFrame, # Pipeline clientes
        "comercial_externo": pd.DataFrame,  # Dados mensais externo
        "atualizado_em": str,               # Timestamp de geração
    }
    """
```

### Regras de normalização
- Ignorar linhas "TOTAL GERAL" e "TOTAL"
- Converter datas para datetime
- Tratar valores None como 0 para numéricos
- Ignorar linhas de cabeçalho/instrução (rows 1-2 em cada aba)
- Parceiros: ler como key-value da estrutura específica
- Validar que colunas esperadas existem (erro amigável se não)

## Módulo: metricas.py

### Funções principais
```python
def calcular_contexto(dados: dict, hoje: date) -> dict:
    """Retorna contexto completo para o template Jinja2."""

def calcular_kpis_inbound(inbound_mensal: pd.DataFrame) -> dict:
    """KPIs acumulados: total_leads, com_interesse, contratos, taxa_conversao."""

def calcular_tendencia_diaria(inbound_diario: pd.DataFrame) -> list[dict]:
    """Lista de {data, leads, interesse, contratos} para gráfico de linha."""

def calcular_funil_inbound(inbound_mensal: pd.DataFrame) -> dict:
    """Funil: leads → interesse → contratos com percentuais de queda."""

def calcular_kpis_parceiros(parceiros: dict) -> dict:
    """KPIs: totais, indicaram, fecharam, taxas, segmentação para donut."""

def calcular_pipeline_parceiros(clientes: pd.DataFrame) -> list[dict]:
    """Pipeline individual de cada cliente de parceiro."""

def calcular_kpis_externo(externo: pd.DataFrame) -> dict:
    """KPIs e dados mensais do comercial externo."""

def calcular_comparativo(inbound_mensal, parceiros, externo) -> dict:
    """Dados para gráfico comparativo entre canais."""
```

## Módulo: gerar_dashboard.py

### Fluxo
1. Localizar o Excel (caminho fixo ou argumento)
2. `loader.carregar_indicadores(path)` → dados
3. `metricas.calcular_contexto(dados, date.today())` → contexto
4. Jinja2: renderizar `template.html` com contexto
5. Escrever `dashboard.html`
6. Abrir no navegador padrão

## atualizar.bat

```bat
@echo off
chcp 65001 >nul
echo Atualizando dashboard...
python gerar_dashboard.py
if %ERRORLEVEL% NEQ 0 (
    echo ERRO ao gerar dashboard!
    pause
    exit /b 1
)
echo Dashboard atualizado com sucesso!
timeout /t 2 >nul
```

## Chart.js

Usar Chart.js via CDN inline (copiar o JS minificado no template para funcionar offline) ou via tag `<script src="cdn">` se internet disponível.

### Gráficos necessários:
1. **Bar chart agrupado** — Inbound mensal (leads/interesse/contratos)
2. **Line chart** — Tendência diária de leads
3. **Horizontal funnel** — Conversão Inbound (CSS puro, não Chart.js)
4. **Donut chart** — Segmentação de parceiros
5. **Horizontal bar chart** — Taxas de parceiros
6. **Stacked bar chart** — Comercial externo por etapa
7. **Grouped bar chart** — Comparativo entre canais
8. **Donut chart** — Distribuição de resultados por canal

## Critérios de Sucesso

1. Dashboard gera corretamente a partir do Excel atual
2. Todos os KPIs calculados batem com os valores da aba Dashboard do Excel
3. Gráficos renderizam com dados corretos e são interativos
4. Navegação scroll spy funciona suavemente
5. Visual segue identidade R-Torn (Montserrat, Navy, Gold)
6. atualizar.bat funciona no Windows com duplo-clique
7. UI/UX Pro Max aplicado como etapa final
8. Dashboard apresentável para sócios em projetor
