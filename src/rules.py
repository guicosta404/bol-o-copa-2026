from __future__ import annotations

import random
from dataclasses import asdict
from typing import Any, Mapping, Sequence

from src.groups import GROUPS, Team, team_lookup

SelectionMap = Mapping[str, Mapping[str, str | None]]
KnockoutWinners = Mapping[str, Sequence[str | None]]

KNOCKOUT_PHASES: tuple[tuple[str, str], ...] = (
    ("dezesseis_avos", "16 avos de final"),
    ("oitavas", "Oitavas de final"),
    ("quartas", "Quartas de final"),
    ("semifinais", "Semifinais"),
    ("final", "Final"),
)


def validate_participant(name: str, phone: str, email: str) -> list[str]:
    errors: list[str] = []
    if not name.strip():
        errors.append("Informe seu nome.")
    if not phone.strip():
        errors.append("Informe seu telefone.")
    if "@" not in email or "." not in email:
        errors.append("Informe um e-mail valido.")
    return errors


def validate_selections(selections: SelectionMap) -> list[str]:
    errors: list[str] = []
    valid_codes = set(team_lookup())

    for group in GROUPS:
        group_selection = selections.get(group.code, {})
        first = group_selection.get("first")
        second = group_selection.get("second")

        if not first or not second:
            errors.append(f"Selecione 1o e 2o lugar do Grupo {group.code}.")
            continue
        if first == second:
            errors.append(f"O Grupo {group.code} tem a mesma selecao em 1o e 2o.")
        if first not in valid_codes or second not in valid_codes:
            errors.append(f"O Grupo {group.code} possui uma selecao invalida.")

    return errors


def draw_best_thirds(selections: SelectionMap, seed: int | None = None) -> list[Team]:
    rng = random.Random(seed)
    candidates: list[Team] = []

    for group in GROUPS:
        picked = {
            selections.get(group.code, {}).get("first"),
            selections.get(group.code, {}).get("second"),
        }
        candidates.extend(team for team in group.teams if team.code not in picked)

    return rng.sample(candidates, 8)


def build_qualified(selections: SelectionMap, seed: int | None = None) -> dict[str, list[dict[str, str]]]:
    errors = validate_selections(selections)
    if errors:
        raise ValueError(" ".join(errors))

    lookup = team_lookup()
    firsts = [lookup[selections[group.code]["first"]] for group in GROUPS]
    seconds = [lookup[selections[group.code]["second"]] for group in GROUPS]
    thirds = draw_best_thirds(selections, seed=seed)

    return {
        "firsts": [asdict(team) for team in firsts],
        "seconds": [asdict(team) for team in seconds],
        "thirds": [asdict(team) for team in thirds],
        "all": [asdict(team) for team in [*firsts, *seconds, *thirds]],
    }


def build_knockout_matches(team_codes: Sequence[str]) -> list[tuple[str, str]]:
    if len(team_codes) % 2 != 0:
        raise ValueError("O mata-mata precisa de uma quantidade par de selecoes.")

    return [(team_codes[index], team_codes[index + 1]) for index in range(0, len(team_codes), 2)]


def validate_knockout(initial_codes: Sequence[str], winners_by_phase: KnockoutWinners) -> list[str]:
    errors: list[str] = []
    valid_codes = set(team_lookup())
    current_codes = list(initial_codes)

    if len(current_codes) != 32:
        return ["O mata-mata precisa de 32 classificados."]
    if len(set(current_codes)) != len(current_codes):
        return ["O mata-mata possui selecoes repetidas."]
    if any(code not in valid_codes for code in current_codes):
        return ["O mata-mata possui uma selecao invalida."]

    for phase_key, phase_label in KNOCKOUT_PHASES:
        matches = build_knockout_matches(current_codes)
        winners = list(winners_by_phase.get(phase_key, []))
        if len(winners) != len(matches) or any(not winner for winner in winners):
            errors.append(f"Selecione todos os vencedores em {phase_label}.")
            break

        next_codes: list[str] = []
        for match_number, ((team_a, team_b), winner) in enumerate(zip(matches, winners), start=1):
            if winner not in (team_a, team_b):
                errors.append(f"Vencedor invalido no jogo {match_number} de {phase_label}.")
                continue
            next_codes.append(winner)

        if errors:
            break
        current_codes = next_codes

    return errors


def serialize_knockout(initial_codes: Sequence[str], winners_by_phase: KnockoutWinners) -> dict[str, Any]:
    errors = validate_knockout(initial_codes, winners_by_phase)
    if errors:
        raise ValueError(" ".join(errors))

    lookup = team_lookup()
    current_codes = list(initial_codes)
    bracket: dict[str, Any] = {}

    for phase_key, _phase_label in KNOCKOUT_PHASES:
        matches = build_knockout_matches(current_codes)
        winners = list(winners_by_phase[phase_key])
        phase_matches = []

        for match_number, ((team_a, team_b), winner) in enumerate(zip(matches, winners), start=1):
            assert winner is not None
            phase_matches.append(
                {
                    "jogo": match_number,
                    "time_a": asdict(lookup[team_a]),
                    "time_b": asdict(lookup[team_b]),
                    "vencedor": asdict(lookup[winner]),
                }
            )

        bracket[phase_key] = phase_matches
        current_codes = [winner for winner in winners if winner is not None]

    bracket["campeao"] = asdict(lookup[current_codes[0]])
    return bracket


def serialize_selections(selections: SelectionMap) -> dict[str, dict[str, str]]:
    return {
        group.code: {
            "first": str(selections[group.code]["first"]),
            "second": str(selections[group.code]["second"]),
        }
        for group in GROUPS
    }
