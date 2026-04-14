# Agenda Semanal Pro — Notion Template Design

**Date:** 2026-04-14
**Status:** Draft
**Approach:** Board Semanal Turbinado (Opção A)

---

## Goal

Create a Notion weekly agenda template that replaces the user's existing basic board. The new template must:

1. Display tasks organized by day of the week (Mon–Fri)
2. Allow checking off tasks as they are completed
3. Show task completion counts and progress metrics on a dashboard
4. Visually alert when tasks are near their deadline or overdue
5. Be visually appealing and more elaborate than the current basic board

Notion does not support push notifications, so "alerts" are implemented as visual formula-driven indicators (emoji + color) that update automatically as time passes.

---

## Architecture

### Single Database + Linked Views Pattern

One Notion database (`Tarefas`) serves as the single source of truth. All views — the weekly board, calendar, metrics, and alert panel — are **Linked Views** of this same database with different filters and groupings. This avoids data duplication and keeps the template clean.

```
📅 Agenda Semanal Pro   ← Main page (open daily)
  ├── [Linked View] Métricas da Semana   (4 count views)
  ├── [Linked View] ⚠️ Alertas          (tasks due in ≤2 days, not done)
  ├── [Linked View] Board Semanal        (grouped by Dia)
  ├── [Linked View] Calendário           (by Prazo)
  └── 🗄️ Tarefas                        (hidden database, child page)
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
| `Semana` | Formula | ISO week number — used to filter current week across views |
| `Concluída?` | Checkbox | Quick-complete toggle visible directly on board cards |

### Formula: `Urgência`

```
if(
  prop("Status") == "Concluída", "✅ Concluída",
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
```

This formula recalculates every time the page is opened and gives instant visual feedback on deadline proximity without any external automation.

### Formula: `Semana`

```
formatDate(prop("Prazo"), "W")
```

Returns the ISO week number (e.g., "16"). Used as a filter in linked views to show only the current week.

---

## Dashboard Page Layout

The main page (`Agenda Semanal Pro`) is structured top-to-bottom:

### Block 1 — Week Header

A styled callout block showing the current week range and a brief instruction reminder:

```
📅  Semana 16  ·  14–18 Abril 2026
    "Foco nas entregas críticas. Filtre por urgência para priorizar."
```

This is a static text block — updated manually when duplicating for a new week (takes ~10 seconds).

### Block 2 — Metrics Row (4 Linked Views, inline)

Four side-by-side linked views, each showing a **Count** number. Each is filtered to the current week:

| View | Filter | Display |
|---|---|---|
| `📋 Total` | Semana = current week | Count of all tasks |
| `✅ Concluídas` | Status = Concluída + current week | Count completed |
| `⏳ Pendentes` | Status ≠ Concluída + current week | Count remaining |
| `🚨 Urgentes` | Urgência contains "🔴" or "🚨" + current week | Count critical |

These give an immediate progress snapshot at a glance.

### Block 3 — Alert Panel

A linked view titled **⚠️ Atenção — Prazo Próximo** showing:
- Filter: `Prazo ≤ today + 2 days` AND `Status ≠ Concluída`
- Layout: List view
- Visible properties: `Nome`, `Urgência`, `Prioridade`, `Dia`
- Sorted by `Prazo` ascending (most urgent first)
- Shown as a callout-colored block (red/orange tint via Notion block color)

This section is the "notification system" — anything needing immediate attention surfaces here automatically.

### Block 4 — Weekly Board

The main working area:
- Linked view of `Tarefas`
- **Group by:** `Dia` (Monday → Friday columns, plus Fim de Semana)
- **Filter:** Current week (Semana = current week number)
- **Sort:** `Prioridade` descending (Alta first)
- **Card properties visible:** `Concluída?` checkbox, `Urgência`, `Categoria`, `Prioridade`
- **New task button** visible at bottom of each column

### Block 5 — Calendar View

A linked view showing tasks plotted on a calendar by `Prazo`:
- **Layout:** Calendar (monthly)
- **Filter:** None (show all weeks for macro overview)
- Useful for planning ahead and spotting deadline clusters

---

## Visual Design Principles

The template uses Notion's native styling capabilities:

- **Icons:** Each section uses a distinct emoji icon for quick scanning
- **Dividers:** Horizontal rules between sections for visual breathing room
- **Block colors:** Alert panel uses red/orange callout background
- **Column headers:** Each day column has an emoji prefix (📅 Segunda, etc.)
- **Card density:** Only 3 properties shown on board cards to avoid clutter
- **Dark mode:** Fully compatible with Notion's native dark mode

For a more polished aesthetic beyond default Notion, the user can apply a **Notion AI-generated cover image** + custom page icon, and use the `Simple` or `Default` font with small text mode enabled.

---

## Weekly Reset Workflow

At the start of each week (Monday morning, ~2 minutes):

1. Open `Agenda Semanal Pro`
2. Click `···` → `Duplicate` on the page
3. Rename the duplicate to the new week (e.g., "Semana 17 · 21–25 Abril")
4. Update the week header callout text
5. The board auto-filters to show only new tasks — old tasks stay in history

Alternatively: create a **Template button** inside Notion that pre-fills recurring weekly tasks automatically.

---

## Template Button (Optional Enhancement)

A Notion Template Button block at the top of the page lets the user add recurring weekly tasks with one click:

- Button label: `+ Iniciar Semana`
- Action: Creates a set of pre-configured tasks (e.g., "Atualizar indicadores", "Relatório semanal") with `Status = A Fazer` and the appropriate `Dia` pre-filled

---

## Out of Scope

- Push/email notifications (not supported by Notion natively)
- Automatic week rollover (Notion has no automation triggers without third-party tools like Zapier/Make)
- Time tracking
- Team collaboration / task assignment
- Mobile-optimized custom layout (Notion mobile renders all views natively)

---

## Success Criteria

- [ ] User can add tasks to any day of the week in under 5 seconds
- [ ] Checking off a task immediately removes it from the Pendentes count
- [ ] Any task with a deadline ≤ 2 days away appears in the Alert Panel automatically
- [ ] The metrics row shows accurate counts at all times
- [ ] The template can be duplicated for a new week in under 2 minutes
- [ ] The design looks visually richer than the original basic board
