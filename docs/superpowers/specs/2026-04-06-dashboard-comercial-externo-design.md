# Dashboard Comercial Externo — Especificação de Design
**Data:** 2026-04-06
**Status:** Aprovado
**Fase:** A (Excel + Python + HTML) — Fase B (Agendor API) planejada para depois

---

## 1. Contexto e Objetivo

Empresa de inteligência tributária precisa monitorar a efetividade de um agente comercial externo que até então não era acompanhado por nenhum sistema interno. O objetivo é medir produtividade, rastrear o funil de vendas por empresa e identificar oportunidades em risco de perda por falta de follow-up dentro do SLA.

**Problema central:** Os dados existem no Agendor CRM, mas o relatório nativo é fraco, não-interativo e não permite a visão personalizada necessária para medir custo × retorno do agente.

---

## 2. Solução — Fase A

### Arquitetura

```
dados_comercial.xlsx
    ├── Aba EMPRESAS   → cadastro de cada prospect
    ├── Aba VISITAS    → registro de cada ação/etapa
    └── Aba CONFIG     → parâmetros configuráveis

          ↓  (duplo clique em atualizar.bat)

gerar_dashboard.py
    ├── Lê as 3 abas com openpyxl / pandas
    ├── Calcula métricas (etapa atual, dias sem retorno, alertas)
    └── Renderiza dashboard.html via Jinja2

          ↓

dashboard.html  →  abre automaticamente no navegador padrão
```

### Fluxo do Usuário
1. Agente realiza visita → relata por WhatsApp ou Agendor
2. Usuário registra 1 linha na aba **VISITAS** do Excel
3. Duplo clique em **`atualizar.bat`** (~2 segundos)
4. Navegador abre com dashboard completamente atualizado

---

## 3. Estrutura do Excel

### Aba EMPRESAS (cadastro único por prospect)

| Coluna | Tipo | Obrigatoriedade | Descrição |
|--------|------|-----------------|-----------|
| ID | Texto | AUTO | Gerado automaticamente (EMP001, EMP002…) |
| Nome da Empresa | Texto | OBRIGATÓRIO | Razão social ou nome fantasia |
| CNPJ | Texto | Opcional | Formatado com máscara |
| Segmento | Texto | OBRIGATÓRIO | Ex: Indústria, Comércio, Serviços, Contabilidade |
| Cidade | Texto | Opcional | |
| Estado | Texto (UF) | Opcional | |
| Nome Contato | Texto | Opcional | |
| Cargo | Texto | Opcional | |
| Telefone | Texto | Opcional | |
| E-mail | Texto | Opcional | |
| Temperatura | Lista | OBRIGATÓRIO | `Quente` (SLA 30d) ou `Normal` (SLA 90d) |
| Porte | Lista | Opcional | Pequeno / Médio / Grande |
| Origem Lead | Texto | Opcional | Ex: Indicação, Prospecção ativa, LinkedIn |
| Observações Gerais | Texto | Opcional | Campo livre |
| Ativo? | Lista | OBRIGATÓRIO | `SIM` ou `NÃO` (para arquivar sem deletar) |
| Etapa Atual | Texto | AUTO | Calculado pelo script com base na aba VISITAS |
| Dias Sem Retorno | Número | AUTO | Calculado pelo script |

### Aba VISITAS (1 linha por ação realizada)

| Coluna | Tipo | Obrigatoriedade | Descrição |
|--------|------|-----------------|-----------|
| Data | Data | OBRIGATÓRIO | Data da ação |
| ID Empresa | Texto | OBRIGATÓRIO | Referência ao ID da aba EMPRESAS |
| Etapa | Lista | OBRIGATÓRIO | 1ª Visita / 2ª Visita / Procuração Eletrônica / Reunião de Fechamento |
| Visita Realizada? | Lista | OBRIGATÓRIO | `SIM` ou `NÃO` |
| Procuração Assinada? | Lista | Opcional | `SIM` ou `NÃO` |
| Proposta Enviada? | Lista | Opcional | `SIM` ou `NÃO` |
| Contrato Fechado? | Lista | Opcional | `SIM` ou `NÃO` |
| Duração (min) | Número | Opcional | Duração da reunião em minutos |
| Resultado | Lista | OBRIGATÓRIO | Positivo / Neutro / Negativo / Sem Contato |
| Interesse (1–5) | Número | Opcional | 1 = frio, 5 = muito quente |
| Próxima Ação | Texto | Opcional | O que deve ser feito em seguida |
| Data Próx. Ação | Data | Opcional | Prazo para próxima ação |
| Obstáculo | Texto | Opcional | O que está impedindo o avanço |
| Relatório Resumido | Texto | Opcional | Texto livre do agente |
| Registrado por | Texto | Opcional | Nome de quem registrou |

### Aba CONFIG (parâmetros sem código)

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| nome_agente | Agente | Nome exibido no dashboard (fallback: "Agente" se vazio) |
| sla_quente_dias | 30 | SLA em dias para prospects Quentes |
| sla_normal_dias | 90 | SLA em dias para prospects Normais |
| ano_filtro | 2026 | Ano padrão do dashboard |
| empresa_nome | Minha Empresa | Nome da empresa (rodapé; fallback: "Minha Empresa" se vazio) |
| cor_primaria | #001b47 | Navy da marca |
| cor_acento | #af946c | Ouro da marca |
| alerta_amarelo_pct | 75 | % do SLA para exibir amarelo |
| mostrar_cnpj | SIM | Exibir CNPJ na tabela |
| mostrar_telefone | NÃO | Exibir telefone na tabela |

---

## 4. Dashboard HTML

### Sistema de Design (UI/UX Pro Max)
- **Estilo:** Data-Dense Dashboard (máx. informação, grid compacto)
- **Fonte:** Montserrat (400/500/600/700/800) via Google Fonts
- **Cores:**
  - Navy: `#001b47` (topbar, cabeçalhos, funil)
  - Gold: `#af946c` (destaques, mês atual, fechamento)
  - Background: `#F0F4F9`
  - Cards: `#ffffff`
  - Danger: `#DC2626` | Warn: `#D97706` | OK: `#16A34A`
- **Contraste:** WCAG AA em todos os pares de cores
- **Interações:** hover 150ms ease, cursor-pointer, foco via teclado

### Componentes

#### KPIs (5 cards no topo)
1. Total de 1ªs Visitas — subtítulo com total do mês
2. Total de 2ªs Visitas — subtítulo com % de conversão
3. Procurações Assinadas — borda verde
4. Reuniões de Fechamento — borda dourada
5. Alertas de Retorno — borda vermelha com contagem críticos/atenção

#### Funil de Conversão (card esquerdo)
- Barras horizontais proporcionais para cada etapa
- Percentual de conversão por etapa à direita
- Destaque textual da maior queda de conversão

#### Gráfico Mensal de 1ªs Visitas (card direito)
- Barras verticais por mês (Jan–Dez)
- Mês atual destacado em dourado
- Meses futuros esmaecidos
- Botão de alternância de ano (2026 / 2025)

#### Painel de Alertas de Follow-up
- Lista de empresas com SLA vencido ou próximo do prazo
- Vermelho: SLA ultrapassado
- Amarelo: SLA ≥ 75% consumido
- Exibe: nome, etapa, temperatura, dias decorridos

#### Tabela de Empresas
- Filtros rápidos: Todas / Quentes / Atrasadas / Em Fechamento
- Colunas: Empresa, Segmento, Temperatura, Etapa, Última Ação, Dias s/ retorno, SLA, Observação
- Pills coloridos por etapa
- Dias sem retorno com cor semântica (verde/amarelo/vermelho)
- Linhas clicáveis com hover state

#### Resumo Mensal (mini tabela lateral)
- Colunas: Mês, 1ª Visita, 2ª Visita, Fechamento
- Formato similar à planilha original do usuário

---

## 5. Arquivos Entregues

| Arquivo | Descrição |
|---------|-----------|
| `dados_comercial.xlsx` | Excel pré-formatado com validações de lista |
| `gerar_dashboard.py` | Script Python principal |
| `dashboard.html` | Dashboard gerado (não editar manualmente) |
| `atualizar.bat` | Atalho Windows: atualiza + abre dashboard |
| `setup.bat` | Instalação do Python e dependências (1ª execução) |
| `requirements.txt` | openpyxl, pandas, jinja2 |
| `INSTRUCOES.md` | Guia de uso em português |

---

## 6. Regras de Negócio

### Etapa Atual
- = a `Etapa` da linha mais recente (maior `Data`) na aba VISITAS onde `ID Empresa` = empresa e `Visita Realizada = SIM`
- Ordenação: sempre por coluna `Data` descendente; em caso de empate de data, usar a última linha (maior número de linha)
- Se a mesma etapa aparecer em múltiplas linhas, retornar aquela etapa normalmente sem deduplicação
- Se a empresa não tiver **nenhuma** linha em VISITAS com `Visita Realizada = SIM`: exibir `—` na coluna Etapa Atual

### Dias Sem Retorno
- = `data de hoje − Data` da linha mais recente com `Visita Realizada = SIM` para aquela empresa
- Se a empresa não tiver visitas realizadas: exibir `—` e **não incluir** no painel de alertas nem no funil

### Regras de Alerta
- **Alerta vermelho** = dias sem retorno **≥ SLA** (30d quente / 90d normal)
- **Alerta amarelo** = dias sem retorno ≥ `SLA × alerta_amarelo_pct / 100` **e** < SLA
- Empresas sem visitas realizadas não geram alertas

### Funil de Conversão
- Conta o número de **empresas distintas** (ativas) que possuem ao menos 1 visita realizada em cada etapa
- Percentual exibido = empresas na etapa ÷ empresas na **1ª Visita** (taxa acumulada desde o topo)
- Texto de maior queda: formato português — `"Maior queda: [Etapa A] → [Etapa B] ([N]%)"` onde N é a maior diferença percentual entre etapas consecutivas; em caso de empate, exibir a primeira ocorrência

### KPI Card 3 — Procurações Assinadas
- Conta empresas distintas (ativas) com ao menos 1 linha em VISITAS onde `Etapa = Procuração Eletrônica` **e** `Visita Realizada = SIM`
- (O campo `Procuração Assinada?` é informativo para o histórico, não para o KPI)

### Resumo Mensal — coluna "Fechamento"
- Conta visitas com `Etapa = Reunião de Fechamento` e `Visita Realizada = SIM` no mês/ano correspondente
- (Não é o campo `Contrato Fechado?`, que é um boolean separado)

### Filtro de Ano (gráfico mensal)
- O botão de ano filtra **apenas** o gráfico de barras mensais
- KPI cards, funil, alertas e tabela de empresas sempre exibem dados **acumulados de todos os anos**

### Empresas Inativas (`Ativo = NÃO`)
- Excluídas do funil, KPI cards e painel de alertas
- Na tabela de empresas: **ocultas por padrão** no filtro "Todas"; visíveis apenas se existir filtro "Inativas" (implementar como filtro adicional)
- Histórico de visitas é preservado no Excel e no cálculo interno, mas não exibido

### Conversão de Etapa
- Empresa avança no funil quando há ao menos 1 linha em VISITAS para aquela empresa com `Visita Realizada = SIM` na etapa em questão

---

## 7. Pré-requisitos Técnicos

- **Windows 10/11**
- **Python 3.8+** — `setup.bat` tenta instalar via `winget`; se falhar (ex.: UAC bloqueado ou `winget` indisponível), `INSTRUCOES.md` incluirá link para download manual em python.org e passos passo a passo
- **Microsoft Excel** (para editar o arquivo .xlsx)
- **Navegador moderno** (Chrome, Edge ou Firefox)
- **Encoding:** o arquivo `.xlsx` é lido via `openpyxl` em UTF-8 nativo; comparações de etapa no Python usarão strings Unicode literais (ex.: `"Procuração Eletrônica"`) para garantir correspondência correta com acentos

---

## 8. Fase B — Agendor API (planejada)

Após a Fase A estar em uso e validada, será construída a Fase B:
- Script consulta a API REST do Agendor com chave de API
- Dados são puxados automaticamente sem necessidade do Excel
- Dashboard mantém o mesmo visual — apenas a fonte de dados muda
- Aba CONFIG ganha parâmetro `agendor_api_key`
- Script `atualizar.bat` passará a chamar `sincronizar_agendor.py` antes de `gerar_dashboard.py`

---

## 9. Fora do Escopo (Fase A)

- Métricas financeiras (custo × retorno) — fase futura
- Multi-agente (apenas 1 agente por arquivo)
- Autenticação / login
- Hospedagem web
- Notificações automáticas por e-mail/WhatsApp
