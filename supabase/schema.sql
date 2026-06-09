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

grant insert on public.palpites to anon;

drop policy if exists "anon can insert palpites" on public.palpites;

create policy "anon can insert palpites"
on public.palpites
for insert
to anon
with check (true);
