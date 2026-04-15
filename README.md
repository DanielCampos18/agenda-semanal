# Agenda Semanal Pro

App de agenda semanal com dashboards interativos, alertas de prazo e histórico.
Acesse de qualquer dispositivo via URL pública (GitHub Pages + Supabase).

## Setup (uma única vez, ~15 minutos)

### 1. Supabase

1. Crie conta em https://supabase.com
2. Novo projeto → nome `agenda-semanal`
3. Vá em **SQL Editor** → cole e execute:

```sql
CREATE TABLE tarefas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nome TEXT NOT NULL,
  descricao TEXT,
  status TEXT NOT NULL DEFAULT 'pendente'
    CHECK (status IN ('pendente','em_andamento','concluida','cancelada')),
  prioridade TEXT NOT NULL DEFAULT 'media'
    CHECK (prioridade IN ('alta','media','baixa')),
  categoria TEXT,
  data_tarefa DATE,
  prazo TIMESTAMPTZ,
  criado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
  concluido_em TIMESTAMPTZ
);
ALTER TABLE tarefas ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all_anon" ON tarefas
  FOR ALL TO anon USING (true) WITH CHECK (true);
ALTER PUBLICATION supabase_realtime ADD TABLE tarefas;
```

4. Vá em **Settings → API** → copie:
   - `Project URL`
   - `anon public` key

### 2. Configurar o app

Abra `index.html` e edite as duas linhas no topo do `<script>`:
```javascript
const SUPABASE_URL = 'COLE_SUA_URL_AQUI';
const SUPABASE_KEY = 'COLE_SUA_CHAVE_AQUI';
```

### 3. GitHub Pages

1. Crie repositório no GitHub (ex: `agenda-semanal`)
2. Faça upload de `index.html`
3. **Settings → Pages → Source: main branch → Save**
4. Aguarde ~1 min → acesse `seuusuario.github.io/agenda-semanal`

## Atualizações

Para atualizar o app: edite `index.html` → faça push para o GitHub → aguarde ~30 segundos.

## Uso

- **Dashboard** — visão geral da semana com gráficos e KPIs
- **Semana** — quadro kanban com colunas por dia da semana
- **Calendário** — calendário mensal com pontos coloridos por urgência
- **Histórico** — todas as tarefas concluídas e progresso

Clique no **+** para adicionar tarefas. Clique em qualquer tarefa para editar ou concluir.

## Arquitetura

```
[Qualquer dispositivo — celular / PC / trabalho]
        ↓  abre URL pública
[GitHub Pages — serve index.html]
        ↓  JavaScript chama a API REST do Supabase
[Supabase — PostgreSQL na nuvem (free tier)]
        ↑  retorna dados + subscriptions em tempo real
```
