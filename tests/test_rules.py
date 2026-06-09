from __future__ import annotations

import pytest

from src.groups import GROUPS
from src.rules import (
    KNOCKOUT_PHASES,
    build_knockout_matches,
    build_qualified,
    draw_best_thirds,
    serialize_knockout,
    validate_knockout,
    validate_participant,
    validate_selections,
)


def valid_selections() -> dict[str, dict[str, str]]:
    selections = {}
    for group in GROUPS:
        selections[group.code] = {
            "first": group.teams[0].code,
            "second": group.teams[1].code,
        }
    return selections


def valid_knockout_winners(initial_codes: list[str]) -> dict[str, list[str]]:
    winners = {}
    current_codes = initial_codes
    for phase_key, _phase_label in KNOCKOUT_PHASES:
        matches = build_knockout_matches(current_codes)
        phase_winners = [team_a for team_a, _team_b in matches]
        winners[phase_key] = phase_winners
        current_codes = phase_winners
    return winners


def test_validate_participant_requires_contact_fields() -> None:
    errors = validate_participant("", "", "email-invalido")

    assert "Informe seu nome." in errors
    assert "Informe seu telefone." in errors
    assert "Informe um e-mail valido." in errors


def test_validate_selections_accepts_complete_unique_picks() -> None:
    assert validate_selections(valid_selections()) == []


def test_validate_selections_rejects_duplicate_group_pick() -> None:
    selections = valid_selections()
    selections["A"]["second"] = selections["A"]["first"]

    assert "Grupo A" in " ".join(validate_selections(selections))


def test_draw_best_thirds_is_deterministic_with_seed() -> None:
    selections = valid_selections()

    first_draw = draw_best_thirds(selections, seed=2026)
    second_draw = draw_best_thirds(selections, seed=2026)

    assert first_draw == second_draw
    assert len(first_draw) == 8


def test_draw_best_thirds_excludes_selected_firsts_and_seconds() -> None:
    selections = valid_selections()
    direct_qualifier_codes = {
        code
        for selection in selections.values()
        for code in (selection["first"], selection["second"])
    }

    draw = draw_best_thirds(selections, seed=2026)

    assert {team.code for team in draw}.isdisjoint(direct_qualifier_codes)


def test_build_qualified_returns_32_teams() -> None:
    qualified = build_qualified(valid_selections(), seed=2026)

    assert len(qualified["firsts"]) == 12
    assert len(qualified["seconds"]) == 12
    assert len(qualified["thirds"]) == 8
    assert len(qualified["all"]) == 32


def test_build_qualified_raises_for_invalid_selection() -> None:
    selections = valid_selections()
    selections["B"]["second"] = selections["B"]["first"]

    with pytest.raises(ValueError):
        build_qualified(selections)


def test_build_knockout_matches_pairs_teams_in_order() -> None:
    matches = build_knockout_matches(["A", "B", "C", "D"])

    assert matches == [("A", "B"), ("C", "D")]


def test_validate_knockout_requires_all_phase_winners() -> None:
    qualified = build_qualified(valid_selections(), seed=2026)
    initial_codes = [team["code"] for team in qualified["all"]]

    errors = validate_knockout(initial_codes, {"dezesseis_avos": [initial_codes[0]]})

    assert "16 avos de final" in " ".join(errors)


def test_validate_knockout_rejects_winner_outside_match() -> None:
    qualified = build_qualified(valid_selections(), seed=2026)
    initial_codes = [team["code"] for team in qualified["all"]]
    winners = valid_knockout_winners(initial_codes)
    winners["dezesseis_avos"][0] = initial_codes[2]

    errors = validate_knockout(initial_codes, winners)

    assert "Vencedor invalido" in " ".join(errors)


def test_serialize_knockout_returns_all_phases_and_champion() -> None:
    qualified = build_qualified(valid_selections(), seed=2026)
    initial_codes = [team["code"] for team in qualified["all"]]
    winners = valid_knockout_winners(initial_codes)

    bracket = serialize_knockout(initial_codes, winners)

    assert len(bracket["dezesseis_avos"]) == 16
    assert len(bracket["oitavas"]) == 8
    assert len(bracket["quartas"]) == 4
    assert len(bracket["semifinais"]) == 2
    assert len(bracket["final"]) == 1
    assert bracket["campeao"]["code"] == winners["final"][0]
