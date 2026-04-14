# Agenda Semanal Pro — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete Notion weekly agenda template with a task board grouped by day, automatic deadline-urgency formula, visual alert panel for urgent tasks, and metrics via table footer.

**Architecture:** One Notion page per week, each containing a child `Tarefas` database (created by duplicating the template). All views on the dashboard page are Linked Views of that database — board grouped by `Dia`, alert panel filtered by `Urgência`, calendar by `Prazo`. The `Urgência` formula recalculates on every page open to give real-time deadline feedback.

**Tech Stack:** Notion (databases, linked views, formulas, template buttons, callout blocks). No code. No third-party integrations.

**Spec:** `docs/superpowers/specs/2026-04-14-agenda-semanal-notion-design.md`

**Implementation method:** Manual Notion UI steps (or Notion MCP API calls if available). Each task can be executed directly in Notion.

---

## Page Structure to Create

```
📅 Agenda Semanal Pro (Template)      ← Main weekly page
  ├── [Callout] Header da Semana
  ├── [Callout] Métricas (manual)
  ├── [Toggle] Ver contagens detalhadas
  │     └── [Linked View - Table] Tarefas por Status
  ├── [Linked View - List] ⚠️ Alertas
  ├── [Linked View - Board] Board Semanal
  ├── [Toggle] Calendário
  │     └── [Linked View - Calendar] Tarefas no Calendário
  └── 🗄️ Tarefas (child database)
```

---

## Task 1: Create the Main Template Page

**Files / Notion objects:**
- Create: Page `📅 Agenda Semanal Pro` (template root)
- Create: Child database `Tarefas` (inside the template page)

- [ ] **Step 1: Create the template page**

In Notion, create a new page titled `📅 Agenda Semanal Pro`. Set the icon to 📅. Add a cover image (use any abstract/minimal Notion cover from the built-in gallery — choose one with dark/neutral tones for visual impact).

Enable **Small text** mode (click `···` → View options → Small text: On).

- [ ] **Step 2: Create the child database**

Inside the page, type `/database` and create a **Full-page database** titled `🗄️ Tarefas`. This is the single source of truth for the week.

> **Important:** The database must be created *inside* the template page (as a child page), not as a standalone database. This ensures it gets duplicated with the page when you start a new week.

- [ ] **Step 3: Verify structure**

The page should now show `🗄️ Tarefas` as a child page at the bottom. Open it — you should see an empty database with only the default `Name` property.

- [ ] **Step 4: Confirm and note the database URL**

Open `Tarefas`, copy the database URL from the browser. You'll need this when creating Linked Views.

---

## Task 2: Configure Database Properties

**Files / Notion objects:**
- Modify: `Tarefas` database — add 6 properties, configure values

- [ ] **Step 1: Rename the default Title property**

Click the `Name` column header → Rename → `Nome`. Type: Title (keep as is).

- [ ] **Step 2: Add `Status` property**

Add property → Select → Name: `Status`.

Add these options in order (use matching colors):
- `A Fazer` (light gray)
- `Em Andamento` (blue)
- `Concluída` (green)
- `Cancelada` (red)

- [ ] **Step 3: Add `Dia` property**

Add property → Select → Name: `Dia`.

Add these options (plain names — no emoji in the stored value):
- `Segunda`
- `Terça`
- `Quarta`
- `Quinta`
- `Sexta`
- `Fim de Semana`

- [ ] **Step 4: Add `Prazo` property**

Add property → Date → Name: `Prazo`.
Enable "Include time" in the property settings.

- [ ] **Step 5: Add `Prioridade` property**

Add property → Select → Name: `Prioridade`.

Add these options:
- `🔴 Alta` (red)
- `🟡 Média` (yellow)
- `🟢 Baixa` (green)

- [ ] **Step 6: Add `Categoria` property**

Add property → Multi-select → Name: `Categoria`.

Add these default tags:
- `Reunião`
- `Entrega`
- `Admin`
- `Pessoal`

(The user can add more tags as needed — multi-select is open.)

- [ ] **Step 7: Add `Urgência` formula property**

Add property → Formula → Name: `Urgência`.

Paste this formula exactly:

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

Click Confirm. The formula column should appear in the database.

- [ ] **Step 8: Verify all properties**

The `Tarefas` database should now have these 7 properties:
`Nome` (Title), `Status` (Select), `Dia` (Select), `Prazo` (Date), `Prioridade` (Select), `Categoria` (Multi-select), `Urgência` (Formula)

- [ ] **Step 9: Add 2 test tasks and verify formula**

Add a test task:
- Nome: `Teste urgente`, Status: `A Fazer`, Prazo: today's date

The `Urgência` column should show `🔴 HOJE`.

Add another:
- Nome: `Teste futuro`, Status: `A Fazer`, Prazo: 5 days from today

The `Urgência` column should show `🟢 5 dias`.

Add another:
- Nome: `Teste concluída`, Status: `Concluída`

The `Urgência` column should show `✅ Concluída`.

Delete the test tasks after verifying.

---

## Task 3: Create the Alert Panel View

**Files / Notion objects:**
- Create: Linked View of `Tarefas` → List layout, filtered by Urgência

- [ ] **Step 1: Go to the main template page**

Navigate back to `📅 Agenda Semanal Pro`.

- [ ] **Step 2: Add a Linked View**

Type `/linked` → **Create linked view of database** → select `Tarefas` (the child database you created).

- [ ] **Step 3: Configure as List layout**

In the view settings, change layout to **List**.

- [ ] **Step 4: Rename the view**

Name it: `⚠️ Atenção — Prazo Próximo`

- [ ] **Step 5: Add filter — Urgência contains 🔴**

Click Filter → Add filter → Property: `Urgência` → Filter type: `Contains` → Value: `🔴`

- [ ] **Step 6: Add OR filter — Urgência contains 🟠**

Click `Add filter` again → Property: `Urgência` → Contains → `🟠`
Change the AND/OR toggle to **OR** between these two conditions.

- [ ] **Step 7: Add OR filter — Urgência contains 🚨**

Add a third filter → `Urgência` Contains `🚨`, connected with **OR**.

The combined filter is: `Urgência contains 🔴` OR `Urgência contains 🟠` OR `Urgência contains 🚨`

- [ ] **Step 8: Add sort**

Sort by `Prazo` → Ascending (most urgent first).

- [ ] **Step 9: Configure visible properties**

Show: `Nome`, `Urgência`, `Prioridade`, `Dia`
Hide all other properties.

- [ ] **Step 10: Style the view container**

Add a `/callout` block **above** the Alert Panel linked view. Set its background color to **Red**. Then drag the linked view block inside the callout by grabbing its drag handle (⠿) and dropping it onto the callout block.

> **Note:** Notion does not allow converting a linked database view into a callout via the `···` menu — the callout must be created separately and the view dragged inside it.

---

## Task 4: Create the Weekly Board View

**Files / Notion objects:**
- Create: Linked View of `Tarefas` → Board layout, grouped by Dia

- [ ] **Step 1: Add another Linked View below the Alert Panel**

On the main template page, type `/linked` → select `Tarefas`.

- [ ] **Step 2: Set layout to Board**

Change layout to **Board**.

- [ ] **Step 3: Group by `Dia`**

In Board settings → Group by → `Dia`.

The board should show columns: `Segunda`, `Terça`, `Quarta`, `Quinta`, `Sexta`, `Fim de Semana` (matching the exact stored values in the `Dia` property).

- [ ] **Step 4: Add filter — exclude Cancelada**

Filter → `Status` → `does not equal` → `Cancelada`

- [ ] **Step 5: Sort by Prioridade**

Sort → `Prioridade` → **Descending**.

Notion sorts Select options by their defined order in the property (not alphabetically). Since `🔴 Alta` was defined first in Task 2, Descending will place it at the top of each column.

- [ ] **Step 6: Configure card properties**

Show on cards:
- `Status`
- `Urgência`
- `Prioridade`
- `Categoria`

Hide all other properties.

- [ ] **Step 7: Rename the view**

Name it: `📋 Board Semanal`

- [ ] **Step 8: Verify board looks correct**

Add a test task with `Dia = Segunda`, `Status = A Fazer`, `Prioridade = 🔴 Alta`. It should appear in the `Segunda` column with the Urgência label visible on the card.

Delete test task after verifying.

---

## Task 5: Create the Metrics Table View (in Toggle)

**Files / Notion objects:**
- Create: Linked View → Table layout, grouped by Status, with Count footer
- Wrap in a Notion Toggle block

- [ ] **Step 1: Add a toggle block above the Alert Panel**

On the main page, click above the Alert Panel view and add a **Toggle block** (`/toggle`).
Label it: `📊 Ver contagens detalhadas`

- [ ] **Step 2: Inside the toggle, add a Linked View**

Inside the toggle, type `/linked` → select `Tarefas`.

- [ ] **Step 3: Set layout to Table**

- [ ] **Step 4: Group by Status**

Table settings → Group by → `Status`

This creates sections: A Fazer, Em Andamento, Concluída, Cancelada — each with their tasks listed.

- [ ] **Step 5: Enable Count footer**

At the bottom of each group section, hover over the footer row → click `Calculate` → `Count`. Repeat for each Status group.

This shows "N tasks" per status automatically.

- [ ] **Step 6: Hide unnecessary columns**

In table view, show only: `Nome`, `Dia`, `Urgência`. Hide Prazo, Prioridade, Categoria, Status (already the group header).

- [ ] **Step 7: Name the view**

Name it: `Contagens por Status`

---

## Task 6: Create the Calendar View (in Toggle)

**Files / Notion objects:**
- Create: Linked View → Calendar layout, filtered to rolling 28 days

- [ ] **Step 1: Add a second toggle block below the Board**

Toggle label: `📆 Calendário`

- [ ] **Step 2: Inside the toggle, add a Linked View → Calendar layout**

- [ ] **Step 3: Set calendar to show by `Prazo`**

Calendar settings → Show as → `Prazo`

- [ ] **Step 4: Add filter for rolling window**

Filter → `Prazo` → `is within` → `the next 28 days`
(This prevents tasks from distant past weeks from cluttering the calendar as the database grows.)

- [ ] **Step 5: Name the view**

Name it: `Calendário de Prazos`

---

## Task 7: Build the Dashboard Header

**Files / Notion objects:**
- Modify: Main template page — add header callout + metrics callout

- [ ] **Step 1: Add the Week Header callout at the very top of the page**

At the top of `📅 Agenda Semanal Pro`, before any views, add a **Callout block** (`/callout`).

Icon: 📅
Background color: **Blue** (or another neutral accent)
Text:
```
Semana XX  ·  DD–DD Mês Ano
Foco nas entregas críticas. Verifique os alertas abaixo.
```

- [ ] **Step 2: Add a divider below the header**

`/divider`

- [ ] **Step 3: Add the Metrics callout**

Below the divider, add another **Callout block**.
Icon: 📊
Background color: **Blue**
Text:
```
📊 Progresso da Semana
✅ 0 concluídas  ·  ⏳ 0 pendentes  ·  🚨 0 urgentes
```

This block is updated manually each morning (~10 seconds). The exact counts come from the toggle table view created in Task 5.

- [ ] **Step 4: Add a divider, then the section label for alerts**

```
/divider
⚠️ Alertas de Prazo
```

(The Alert Panel linked view from Task 3 goes here.)

- [ ] **Step 5: Add section labels for remaining sections**

Add these text headers between views:
- `📋 Board da Semana` (above the Board view)
- No header needed for the toggle blocks — they are self-labeled

- [ ] **Step 6: Final page order check**

Page should read top-to-bottom:
1. Cover image + page icon
2. 📅 Week Header callout (blue)
3. `+ Iniciar Semana` Template Button
4. Divider
5. 📊 Metrics callout (blue)
6. 📊 Toggle: Ver contagens detalhadas (collapsed by default)
7. Divider
8. ⚠️ Alertas de Prazo label
9. ⚠️ Alert Panel (List view, red callout background)
10. Divider
11. 📋 Board da Semana label
12. 📋 Board view (grouped by Dia)
13. 📆 Toggle: Calendário (collapsed by default)

---

## Task 8: Add Template Button for Recurring Tasks

**Files / Notion objects:**
- Create: Notion Template Button block

- [ ] **Step 1: Add a Template Button block at the top of the page**

After the Week Header callout, add a **Button block** (`/button` or `/template`).

> **Note:** In Notion this is called a "Template button" — it creates pre-configured database entries when clicked.

- [ ] **Step 2: Configure the button**

Button label: `+ Iniciar Semana`

Add the following pre-configured tasks (adapt to your real recurring tasks):
- Nome: `Atualizar indicadores` · Dia: `Segunda` · Status: `A Fazer` · Prioridade: `🟡 Média`
- Nome: `Relatório semanal` · Dia: `Sexta` · Status: `A Fazer` · Prioridade: `🟡 Média`
- Nome: `Revisar backlog` · Dia: `Segunda` · Status: `A Fazer` · Prioridade: `🟢 Baixa`

(The user should customize these with their own real recurring tasks.)

- [ ] **Step 3: Test the button**

Click `+ Iniciar Semana` — 3 tasks should appear in the Board view automatically (in the Segunda and Sexta columns). Verify they show `Status = A Fazer` and the correct `Dia`.

Delete the test tasks.

---

## Task 9: Visual Polish Pass

**Files / Notion objects:**
- Modify: Main template page — final aesthetic touches

- [ ] **Step 1: Set a cover image**

Click `Add cover` at the top of the page. Go to **Gallery** → pick a dark, minimal, or abstract image. Alternatively, use `Upload` for a custom image. Adjust the vertical position so it looks balanced.

- [ ] **Step 2: Set a page icon**

If not already set, click the icon area → Emoji → `📅`

- [ ] **Step 3: Enable Small text**

Click `···` (top right) → **Small text: On**. This makes the page more compact and professional.

- [ ] **Step 4: Review card styling on the Board**

Open the Board view. Each day column should have a clean header (e.g., `📅 Segunda`). Cards should show `Status`, `Urgência`, `Prioridade`, `Categoria`. If a column looks cluttered, remove one property.

- [ ] **Step 5: Verify Alert Panel styling**

The Alert Panel callout should have a red/orange background. If it doesn't stand out enough, wrap the linked view in a callout block: type `/callout` above it, set color to Red, then drag the linked view inside the callout.

- [ ] **Step 6: Verify dark mode compatibility**

Switch Notion to dark mode (Settings → Appearance → Dark) and confirm the template looks clean. Emoji-based properties and colored select options render well in both modes.

---

## Task 10: Weekly Reset Test Run

**Files / Notion objects:**
- Test the full weekly reset workflow

- [ ] **Step 1: Add 3-5 realistic tasks to the board**

Add tasks with different `Dia`, `Status`, `Prioridade`, and `Prazo` values. Include one task with a past deadline and one due tomorrow.

- [ ] **Step 2: Verify alert panel**

Confirm the ⚠️ Alert Panel shows only the overdue and near-deadline tasks. Tasks with `Urgência = 🟢` or `✅ Concluída` should NOT appear.

- [ ] **Step 3: Mark one task as Concluída**

Change a task's Status to `Concluída`. Verify it immediately disappears from the Alert Panel and its `Urgência` changes to `✅ Concluída`.

- [ ] **Step 4: Verify metrics toggle**

Open the `📊 Ver contagens detalhadas` toggle. The table should show grouped counts (e.g., "3 A Fazer", "1 Concluída").

- [ ] **Step 5: Test weekly duplication**

Duplicate the template page (`···` → Duplicate). Rename the duplicate `📅 Semana 17 · 21–25 Abril`. Update the header callout. Click `+ Iniciar Semana` button to populate recurring tasks.

Verify: the duplicate has its own isolated `Tarefas` database with only the recurring tasks (not the tasks from the original template page).

- [ ] **Step 6: Verify the Calendar view**

Open the `📆 Calendário` toggle. Tasks with a `Prazo` set should appear on the calendar on their deadline date. Tasks without `Prazo` will not appear (expected). Confirm that tasks with a deadline more than 28 days away do NOT appear (rolling filter working correctly).

- [ ] **Step 7: Clean up test data**

Delete the duplicate page. Delete test tasks from the template. The template should be empty and ready for the user's first real week.

---

## Summary

| Task | What it builds |
|---|---|
| 1 | Template page + child Tarefas database |
| 2 | All 7 database properties + Urgência formula |
| 3 | Alert Panel linked view (filters 🔴/🟠/🚨) |
| 4 | Weekly Board linked view (grouped by Dia) |
| 5 | Metrics table in toggle (grouped by Status with footer count) |
| 6 | Calendar view in toggle (rolling 28-day filter) |
| 7 | Dashboard header: week callout + metrics callout + section labels |
| 8 | Template Button for recurring tasks |
| 9 | Visual polish: cover, small text, card density |
| 10 | End-to-end weekly reset test |
