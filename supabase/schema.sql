create table if not exists public.palpites (
  id uuid primary key default gen_random_uuid(),
  nome text not null,
  telefone text not null,
  email text not null,
  selecoes jsonb not null,
  terceiros_sorteados jsonb not null,
  classificados jsonb not null,
  mata_mata jsonb not null,
  campeao jsonb not null,
  created_at timestamptz not null default now()
);

alter table public.palpites
  add column if not exists mata_mata jsonb not null default '{}'::jsonb,
  add column if not exists campeao jsonb not null default '{}'::jsonb;

alter table public.palpites enable row level security;

revoke all on table public.palpites from public, anon, authenticated;

grant usage on schema public to anon, authenticated;
grant insert on table public.palpites to anon, authenticated;

drop policy if exists "anon can insert palpites" on public.palpites;
drop policy if exists "public can insert palpites" on public.palpites;

create policy "public can insert palpites"
on public.palpites
for insert
to anon, authenticated
with check (
  length(btrim(nome)) > 0
  and length(btrim(telefone)) > 0
  and email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'
  and jsonb_typeof(selecoes) = 'object'
  and jsonb_typeof(terceiros_sorteados) = 'array'
  and jsonb_typeof(classificados) = 'array'
  and jsonb_typeof(mata_mata) = 'object'
  and jsonb_typeof(campeao) = 'object'
);
