# Agenda Semanal Pro — Notion Template Design

**Date:** 2026-04-14
**Status:** Revised (v2 — post spec review)
**Approach:** Board Semanal Turbinado (Opção A)

---

## Goal

Create a Notion weekly agenda template that replaces the user's existing basic board. The new template must:

1. Display tasks organized by day of the week (Mon–Fri)
2. Allow marking tasks as complete
3. Show task completion counts and progress metrics on a dashboard
4. Visually alert when tasks are near their deadline or overdue
5. Be visually appealing and more elaborate than the current basic board

Notion does not support push notifications, so "alerts" are implemented as visual formula-driven indicators (emoji + color) that update automatically as time passes.

---

## Architecture

### One Database Per Week + Linked Views Pattern

Each weekly page contains its own `Tarefas` database (created by duplicating the template). Within a given week, all views — the weekly board, calendar, metrics, and alert panel — are **Linked Views** of that week's database with different filters and groupings. This keeps each week isolated and self-contained, with prior weeks acting as a historical log.

```
📅 Agenda Semanal Pro   ← Main page (open daily)
  ├── [Callout] Métricas da Semana        (manual summary callout — see note)
  ├── [Linked View] ⚠️ Alertas           (tasks where Urgência contains 🔴/🟠/🚨)
  ├── [Linked View] Board Semanal         (grouped by Dia, all non-cancelled tasks)
  ├── [Linked View] Calendário            (by Prazo, rolling 4-week filter)
  └── 🗄️ Tarefas                         (hidden database, child page)
```

---

## Database Design — `Tarefas`

### Properties

| Property | Type | Values / Notes |
|---|---|---|
| `Nome` | Title | Task name |
| `Status` | Select | `A Fazer` · `Em Andamento` · `Concluída` · `Cancelada` |
| `Dia` | Select | `Segunda` · `Terça` · `Quarta` · `Quinta` · `Sexta` · `Fim de Semana` |
| `Prazo` | Date | Deadline (date + optional time) |
| `Prioridade` | Select | `🔴 Alta` · `🟡 Média` · `🟢 Baixa` |
| `Categoria` | Multi-Select | `Reunião` · `Entrega` · `Admin` · `Pessoal` · (customizable) |
| `Urgência` | Formula | Auto-computed urgency label (see formula below) |

**Removed:** `Semana` formula (fragile — see note) and `Concluída?` checkbox (redundant with Status).

> **Note on weekly scope:** The template uses one Notion page per week. Each page contains a fresh linked view that shows **all non-cancelled tasks** — there is no week-number filter. Completed tasks from prior weeks are naturally absent because the prior week's page holds them. This is simpler and more reliable than formula-based week filtering.

### Formula: `Urgência`

```
if(
  prop("Status") == "Concluída", "✅ Concluída",
  if(
    prop("Status") == "Cancelada", "🚫 Cancelada",
    if(
      empty(prop("Prazo")), "— Sem prazo",
      if(
        dateBetween(prop("Prazo"), now(), "days") < 0, "🚨 ATRASADA",
        if(
          dateBetween(prop("Prazo"), now(), "days") == 0, "🔴 HOJE",
          if(
            dateBetween(prop("Prazo"), now(), "days") == 1, "🟠 Amanhã",
            if(
              dateBetween(prop("Prazo"), now(), "days") <= 3,
              "🟡 " + format(dateBetween(prop("Prazo"), now(), "days")) + " dias",
              "🟢 " + format(dateBetween(prop("Prazo"), now(), "days")) + " dias"
            )
          )
        )
      )
    )
  )
)
```

**Implementation note:** `dateBetween(prop("Prazo"), now(), "days")` returns a positive number when the deadline is in the future and a negative number when it is past. The argument order — `Prazo` first, `now()` second — is intentional and must not be swapped.

This formula recalculates every time the page is opened and gives instant visual feedback on deadline proximity without any external automation.

---

## Dashboard Page Layout

The main page (`Agenda Semanal Pro`) is structured top-to-bottom:

### Block 1 — Week Header

A styled callout block showing the current week range and a brief instruction reminder:

```
📅  Semana 16  ·  14–18 Abril 2026
    "Foco nas entregas críticas. Verifique os alertas no topo."
```

This is a static text block — updated manually when duplicating for a new week (~10 seconds).

### Block 2 — Metrics Callout

> **Limitation:** Notion does not support count-only inline views — linked database views always render as full tables/boards/lists and cannot show a single aggregate number as a clean tile. The workaround is a manually updated callout block.

A **Callout block** at the top of the page displays the week's progress summary:

```
📊  Semana 16  —  ✅ 3 concluídas  ·  ⏳ 5 pendentes  ·  🚨 1 urgente
```

The user updates this manually (takes ~10 seconds) or uses the Table View footer — see below.

**Table view footer (best native alternative):**
Keep a small linked Table view with `Status` as a group header and the **footer Count row enabled**. This shows "N tasks" per status group automatically and updates live. Place it in a toggle block to keep it hidden by default:

```
▶ Ver contagens detalhadas
  [Linked Table View — grouped by Status, footer: Count]
```

### Block 3 — Alert Panel

A linked view titled **⚠️ Atenção — Prazo Próximo**:
- **Filter:** `Urgência contains "🔴"` OR `Urgência contains "🟠"` OR `Urgência contains "🚨"`
- **Layout:** List view
- **Visible properties:** `Nome`, `Urgência`, `Prioridade`, `Dia`
- **Sorted by:** `Prazo` ascending (most urgent first)
- **Block color:** Red callout background for visual prominence

This filter catches both **overdue** tasks (🚨) and tasks **due today** (🔴) or **tomorrow** (🟠), which is the full set of tasks needing immediate attention. Tasks with no deadline or with deadline ≥ 2 days away are excluded.

### Block 4 — Weekly Board

The main working area:
- Linked view of `Tarefas`
- **Layout:** Board
- **Group by:** `Dia` (Segunda → Sexta columns, plus Fim de Semana)
- **Filter:** `Status ≠ Cancelada` (shows all active tasks for this week's page)
- **Sort:** `Prioridade` descending (🔴 Alta first)
- **Card properties visible:** `Status`, `Urgência`, `Categoria`, `Prioridade`
- **Marking complete:** Click `Status` on the card → select `Concluída`. The card immediately updates `Urgência` to "✅ Concluída" and drops from the Alert Panel.
- **New task button** visible at bottom of each column

### Block 5 — Calendar View (in toggle)

A linked view showing tasks plotted on a calendar by `Prazo`:
- **Layout:** Calendar (monthly)
- **Filter:** `Prazo is within the next 28 days` (rolling 4-week window to prevent clutter)
- Wrapped in a **toggle block** (▶ Calendário) to keep the page clean by default

---

## Visual Design Principles

The template uses Notion's native styling capabilities:

- **Icons:** Each section has a distinct emoji for quick scanning
- **Dividers:** Horizontal rules between sections for visual breathing room
- **Block colors:** Alert panel uses red callout background; metrics callout uses blue
- **Column headers:** Day columns use emoji prefix (📅 Segunda, 📅 Terça, etc.)
- **Card density:** Max 3 properties visible on board cards to avoid clutter
- **Toggle blocks:** Calendar and detailed count table hidden by default to keep the page uncluttered on daily use
- **Dark mode:** Fully compatible with Notion's native dark mode

For a more polished look: apply a cover image and custom icon to the page, enable **Small text** mode, and set the font to **Default** or **Mono**.

---

## Weekly Reset Workflow

At the start of each week (Monday morning, ~2 minutes):

1. Open `Agenda Semanal Pro` (the template page)
2. Click `···` → **Duplicate**
3. Rename the duplicate: e.g., "📅 Semana 17 · 21–25 Abril"
4. Update the header callout text with the new week dates
5. Reset the metrics callout to "✅ 0 concluídas · ⏳ N pendentes · 🚨 0 urgentes"
6. Use the **Template Button** (see below) to add recurring tasks — or add tasks manually

> **What happens to old tasks:** Previous tasks remain inside the *prior week's page* (since `Tarefas` is a child database of each weekly page). Each week gets its own isolated database. This is clean and simple: old weeks serve as a personal history log.

---

## Template Button

A **Template Button block** inside the page lets the user add recurring weekly tasks with one click:

- **Button label:** `+ Iniciar Semana`
- **Action:** Creates a pre-configured set of recurring tasks (e.g., "Atualizar indicadores — Segunda", "Relatório semanal — Sexta") with `Status = A Fazer`, `Prioridade = Média`, and `Dia` pre-filled
- The user customizes these recurring tasks once when setting up the template

---

## Out of Scope

- Push/email notifications (not supported by Notion natively)
- Automatic week rollover (requires Zapier/Make — out of scope for pure Notion)
- Time tracking per task
- Team collaboration / task assignment
- Automatic metrics counts as visual tiles (Notion limitation — see Block 2 note)

---

## Success Criteria

- [ ] User can add a task to any day of the week in under 5 seconds
- [ ] Changing Status to "Concluída" immediately removes the task from the Alert Panel
- [ ] Any task with `Urgência` = 🔴/🟠/🚨 appears in the Alert Panel automatically
- [ ] The table footer count view updates live as tasks change status
- [ ] The template can be duplicated and set up for a new week in under 2 minutes
- [ ] The design looks visually richer than the original basic board
- [ ] The `Urgência` formula correctly shows overdue, today, tomorrow, and future tasks
