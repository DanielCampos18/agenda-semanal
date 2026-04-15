# Agenda Semanal Pro — App Design Spec

**Date:** 2026-04-15
**Status:** Approved
**Approach:** Supabase + GitHub Pages (multi-device web app)

---

## Goal

Build a beautiful, interactive weekly agenda web app accessible from any device (phone, home PC, work PC) via a public URL. The app replaces the Notion-based agenda with a fully custom, zero-cost solution that requires no installation on any device.

---

## Architecture

### Supabase + GitHub Pages

```
[Any device — phone / home PC / work PC]
        ↓  opens public URL
[GitHub Pages — serves index.html]
        ↓  JavaScript calls Supabase REST API
[Supabase — PostgreSQL in the cloud (free tier)]
        ↑  returns data + real-time subscriptions
```

**Why this architecture:**
- GitHub Pages hosts the app for free, permanently, no server to manage
- Supabase provides a free PostgreSQL database accessible via REST API from any browser
- Real-time subscriptions push updates to all open tabs instantly (no page reload needed)
- Zero installation on any device — open browser, go to URL, done
- Data persists in the cloud indefinitely regardless of whether any local device is on or off
- Free tier covers years of personal use: 500MB storage, unlimited API calls

**Single file deployment:** The entire app lives in `index.html` (HTML + embedded CSS + embedded JS). This makes GitHub Pages deployment trivial: push one file, it's live.

---

## Database Schema

### Table: `tarefas`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, default gen_random_uuid() | Auto-generated unique ID |
| `nome` | TEXT | NOT NULL | Task name |
| `descricao` | TEXT | nullable | Optional description |
| `status` | TEXT | NOT NULL, default 'pendente' | `pendente` · `em_andamento` · `concluida` · `cancelada` |
| `prioridade` | TEXT | NOT NULL, default 'media' | `alta` · `media` · `baixa` |
| `categoria` | TEXT | nullable | Free text: Reunião, Entrega, Admin, Pessoal, etc. |
| `data_tarefa` | DATE | nullable | Planned execution date (drives calendar + weekly board) |
| `prazo` | TIMESTAMPTZ | nullable | Deadline — base for urgency alerts |
| `criado_em` | TIMESTAMPTZ | NOT NULL, default now() | Auto-set on insert |
| `concluido_em` | TIMESTAMPTZ | nullable | Auto-set when status changes to 'concluida' |

**Row Level Security:** Enabled on `tarefas`. A single anon-key policy allows read/write — this is a personal app with no multi-user auth requirement. The anon key is safe to embed in client-side JS for personal apps.

---

## Urgency Logic

Computed client-side in JavaScript on every render. No database column needed.

```javascript
function getUrgency(prazo, status) {
  if (status === 'concluida')  return { label: '✅ Concluída',  level: 0, css: 'done' };
  if (status === 'cancelada')  return { label: '🚫 Cancelada',  level: 0, css: 'cancelled' };
  if (!prazo)                  return { label: '— Sem prazo',   level: 1, css: 'none' };

  const days = Math.ceil((new Date(prazo) - new Date()) / 86400000);
  if (days < 0)  return { label: '🚨 ATRASADA',       level: 5, css: 'overdue' };
  if (days === 0) return { label: '🔴 HOJE',           level: 4, css: 'today' };
  if (days === 1) return { label: '🟠 Amanhã',         level: 3, css: 'tomorrow' };
  if (days <= 3)  return { label: `🟡 ${days} dias`,   level: 2, css: 'soon' };
  return           { label: `🟢 ${days} dias`,          level: 1, css: 'ok' };
}
```

The `css` field maps to a CSS class applied to the badge, controlling color and style.

---

## App Structure

### Four Tabs + Persistent Alert Banner

```
┌──────────────────────────────────────────────────────┐
│  📅 Agenda Semanal Pro          Semana 16 · Abr 2026 │
│  [🚨 Alertas: 2 atrasadas · 1 vence hoje]  [✕]      │
├──────────────────────────────────────────────────────┤
│  [📊 Dashboard]  [📋 Semana]  [📆 Calendário]  [🏁 Histórico] │
└──────────────────────────────────────────────────────┘
```

The alert banner only renders when there are tasks with urgency level ≥ 3 (overdue, today, tomorrow). It is dismissible per session via a close button.

---

### Tab 1 — Dashboard

The landing tab. Shows the week at a glance.

**KPI Tiles (3 cards):**
- Total Pendentes (status = pendente OR em_andamento)
- Concluídas esta semana (status = concluida AND concluido_em in current week)
- Atrasadas (prazo < now AND status != concluida/cancelada)

**Charts (Chart.js):**
- Donut chart: task distribution by status (pendente, em_andamento, concluida, cancelada)
- Bar chart: task count by day of week (Mon–Sun), colored by priority

**Floating Action Button:** `+ Nova Tarefa` button (bottom-right), opens the Add Task modal.

---

### Tab 2 — Semana (Weekly Board)

Kanban-style columns, one per day.

**Columns:** Segunda · Terça · Quarta · Quinta · Sexta · Fim de Semana

**Column source:** Tasks are grouped by `data_tarefa` field mapped to day-of-week. Tasks without a date appear in a "Sem data" column.

**Filter applied:** Only shows tasks with `status != 'concluida'` and `status != 'cancelada'`. Completed tasks disappear from this view automatically.

**Task Card displays:** task name, urgency badge, category pill, priority dot (🔴/🟡/🟢), "+ Nova" button at bottom of each column.

**Click behavior:** Clicking a task card opens the Edit Task modal (same form as Add, pre-populated). From there the user can mark complete, edit fields, or delete.

**Real-time:** Supabase Realtime subscription refreshes the board instantly when any task changes (no page reload needed).

---

### Tab 3 — Calendário

Monthly calendar with task indicators.

**Layout:** Standard month grid (7 columns × 5-6 rows). Navigation: prev/next month arrows.

**Task dots:** Each day cell shows colored dots for tasks on that date:
- 🔴 Red dot = overdue or due today
- 🟠 Orange dot = due tomorrow
- 🔵 Blue dot = pending/in-progress
- ✅ Green dot = completed

**Click a day:** Reveals a panel below the calendar listing all tasks for that date with full urgency badges, status, and category.

**Date field used:** `data_tarefa` (planned execution day). Tasks without a date are not shown in the calendar.

---

### Tab 4 — Histórico (History)

Archive of all completed and cancelled tasks.

**Purpose:** "The tasks disappear from the main view but the progress feeling stays." The History tab shows everything you've finished — your personal record.

**Display:** Reverse-chronological list. Each entry shows: task name, category, completion date, how many days it took from creation to completion.

**Progress summary (top of tab):**
- This week: `X of Y tasks completed (Z%)`
- This month: `X of Y tasks completed`
- Progress bar visual

**Filters:** By week/month range (using `concluido_em` as the date anchor), by category, by priority. Tasks without a `data_tarefa` are filtered by `concluido_em` — this is always populated when a task is marked complete.

**No deletion** from history — records are permanent. (User can only delete from the Edit modal on active tasks.)

---

### Add/Edit Task Modal

A centered modal overlay with the following form fields:

| Field | Type | Required |
|---|---|---|
| Nome | Text input | Yes |
| Descrição | Textarea | No |
| Status | Select: Pendente / Em Andamento / Concluída / Cancelada | Yes |
| Prioridade | Radio/Select: 🔴 Alta / 🟡 Média / 🟢 Baixa | Yes |
| Categoria | Text input with `<datalist>` suggestions (dynamically queried from distinct `categoria` values in Supabase — shows previously-used categories) | No |
| Data da Tarefa | Date picker | No |
| Prazo | Datetime-local picker | No |

**On save (new task):** INSERT into Supabase → Realtime fires → all tabs refresh → modal closes.

**On save (edit):** UPDATE in Supabase → same flow. If status changed to `concluida`, `concluido_em` is set to `now()`.

**On delete (edit mode only):** Confirmation dialog → DELETE from Supabase → modal closes.

---

## Visual Design

*Generated with UI/UX Pro Max — Style: Modern Dark / Financial Dashboard. Product pattern: Productivity Tool + Calendar App.*

### Style System

**Base style:** Modern Dark (Cinema / Financial Dashboard hybrid)
- Deep dark backgrounds with subtle layering
- Cards with glassmorphism-lite: `rgba(255,255,255,0.04)` border, `16px` border-radius
- Accent glow behind primary CTA button
- Flat + Micro-interactions: every interactive element has a 150–300ms hover/press response
- No pure black `#000000` (causes OLED smear) — use `#020617` as deepest background

### Color Tokens (Financial Dashboard Dark — UI/UX Pro Max)

```css
:root {
  /* Backgrounds */
  --bg-deep:    #020617;   /* page background */
  --bg-base:    #0f172a;   /* section backgrounds */
  --bg-card:    #0e1223;   /* card surfaces */
  --bg-muted:   #1a1e2f;   /* subtle backgrounds */
  --bg-elevated:#1e293b;   /* hover/elevated surfaces */

  /* Borders */
  --border:     #334155;
  --border-subtle: rgba(255,255,255,0.06);

  /* Text */
  --text-primary:  #f8fafc;
  --text-muted:    #94a3b8;
  --text-faint:    #475569;

  /* Accents */
  --accent-blue:   #3b82f6;  /* primary actions, active tab */
  --accent-green:  #22c55e;  /* success, completed, ✅ */
  --accent-amber:  #f97316;  /* warning, tomorrow */
  --accent-yellow: #eab308;  /* 2–3 day urgency */
  --accent-red:    #ef4444;  /* danger, overdue, high priority */

  /* Semantic urgency */
  --urgency-overdue:   #ef4444;
  --urgency-today:     #ef4444;
  --urgency-tomorrow:  #f97316;
  --urgency-soon:      #eab308;
  --urgency-ok:        #22c55e;

  /* Spacing scale (4pt system) */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;

  /* Radius */
  --radius-sm:  8px;
  --radius-md:  12px;
  --radius-lg:  16px;
  --radius-xl:  20px;

  /* Easing (premium spring) */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
}
```

### Typography (Inter — all weights via Google Fonts CDN)

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
```

| Element | Size | Weight | Line-height |
|---|---|---|---|
| KPI number | 32px | 700 | 1.1 |
| Section header | 20px | 600 | 1.3 |
| Card title | 16px | 500 | 1.4 |
| Body / task name | 14px | 400 | 1.5 |
| Label / badge | 12px | 500 | 1.3 |
| Micro / helper | 11px | 400 | 1.4 |

*Minimum body: 16px on mobile to prevent iOS auto-zoom.*

### Icons

**Library:** Lucide (CDN) — SVG stroke icons, consistent 1.5px stroke, `24px` default size.
**No emojis as structural icons** — urgency labels use emoji in text only (badges), never as navigation/action icons.

### Responsive Breakpoints

| Breakpoint | Width | Layout behavior |
|---|---|---|
| Mobile | < 640px | Single column; board columns stack vertically; bottom tab bar |
| Tablet | 640–1023px | 2–3 board columns; side-by-side charts |
| Desktop | ≥ 1024px | Full 5–6 column board; sidebar-aware layout; wider modal (560px) |

*Mobile-first implementation: base styles target 375px, then `@media (min-width: 640px)` scales up.*

### Animation & Micro-interactions

| Interaction | Duration | Easing | Property |
|---|---|---|---|
| Tab switch | 150ms | ease-out | opacity + transform (translateY 4px → 0) |
| Modal open | 200ms | `cubic-bezier(0.16,1,0.3,1)` | scale 0.95→1 + opacity |
| Modal close | 130ms | ease-in | scale 1→0.95 + opacity |
| Card hover lift | 150ms | ease-out | box-shadow + translateY(-2px) |
| Button press | 80ms | ease-in | scale 0.97 |
| Toast appear | 200ms | ease-out | translateY + opacity |
| KPI count-up | 600ms | ease-out | counter (JS) |

*All animations respect `prefers-reduced-motion: reduce` — disable transforms/transitions when set.*

### Charts (Chart.js)

| Chart | Type | Config notes |
|---|---|---|
| Status distribution | Doughnut | 4 segments (pendente/em andamento/concluída/cancelada); `cutout: '70%'`; center KPI label |
| Tasks by day | Bar | 7 bars (Mon–Sun, matching the board's 6 weekday columns + "Fim de Semana" split into Sat+Sun); colored by count volume; subtle grid `rgba(255,255,255,0.05)` |
| Completion this week | Progress bar | Custom HTML — no library needed |

Chart colors use the accent palette above. Grid lines: `rgba(255,255,255,0.05)`. Legend positioned above chart. Tooltips on hover showing exact count.

### Accessibility (WCAG AA minimum)

- All text contrast ≥ 4.5:1 against their background
- All interactive elements have visible focus rings (`outline: 2px solid var(--accent-blue)`)
- Touch targets ≥ 44×44px (tap areas extended via padding, not just visual size)
- `aria-label` on all icon-only buttons
- Form fields: visible `<label>` per input, errors shown below field
- `cursor: pointer` on all clickable elements
- `role="alert"` on toast notifications for screen reader announcement

---

## File Structure

```
agenda-semanal/
├── index.html          ← Entire app (HTML + <style> + <script>)
└── README.md           ← One-time setup instructions (Supabase + GitHub Pages)
```

All CSS and JS are embedded in `index.html` to keep deployment as simple as possible (push one file = live update). External dependencies are loaded via CDN:
- `chart.js` — charts
- `@supabase/supabase-js` — database client
- `lucide` — icons
- `Inter` font — Google Fonts

The Supabase URL and anon key are defined as constants at the top of the `<script>` block. They are public-safe for personal apps with Row Level Security enabled.

---

## Real-Time Update Flow

```
User saves task
    ↓
app.js calls supabase.from('tarefas').insert(data)
    ↓
Supabase writes to PostgreSQL
    ↓
Supabase Realtime fires event to all subscribed clients
    ↓
app.js receives event → calls refreshAll()
    ↓
refreshAll() re-queries tarefas → updates:
  - KPI tiles
  - Charts
  - Weekly board
  - Alert banner
  - Calendar dots
(History tab only updates when user navigates to it)
```

This means: you add a task on your phone → your PC at home (if browser is open) updates within ~1 second without any reload.

---

## One-Time Setup (User Instructions)

### Step 1 — Create Supabase project (~5 minutes)
1. Go to supabase.com → New project
2. Copy the Project URL and anon public key
3. Run the SQL script from README.md to create the `tarefas` table

### Step 2 — Configure the app (~1 minute)
1. Open `index.html`
2. Set `SUPABASE_URL` and `SUPABASE_KEY` constants at the top of the script

### Step 3 — Deploy to GitHub Pages (~5 minutes)
1. Create a new GitHub repository
2. Upload `index.html`
3. Go to Settings → Pages → Source: main branch
4. Your app is live at `username.github.io/repo-name`

### Updating the app
Push a new `index.html` to GitHub → GitHub Pages auto-deploys within ~30 seconds.

---

## Out of Scope

- Multi-user / team features (single personal account only)
- Push notifications to phone (browser-only, no native mobile notifications)
- Offline mode (requires internet connection to Supabase)
- Native mobile app (PWA installable but not native)
- Task recurrence / auto-repeat
- File attachments
- Time tracking

---

## Success Criteria

- [ ] App loads from a public URL on phone, home PC, and work PC
- [ ] Adding a task via form persists to Supabase and appears on all open tabs within 2 seconds
- [ ] Task with `prazo` in the past shows 🚨 ATRASADA badge automatically
- [ ] Marking a task as Concluída removes it from the Weekly Board and Semana tab
- [ ] Completed tasks are visible in Histórico with completion date
- [ ] Dashboard KPI tiles and charts update without page reload when tasks change
- [ ] Calendar shows task dots on correct dates; clicking a day lists those tasks
- [ ] App is usable on a phone screen (responsive layout)
- [ ] One-time setup from scratch completes in under 15 minutes
