from __future__ import annotations

import pytest

from src.groups import GROUPS
from src.rules import (
    GROUP_CODES,
    KNOCKOUT_PHASES,
    OFFICIAL_ROUND_OF_32_MATCHES,
    assign_third_place_slots,
    build_knockout_matches,
    build_official_knockout_order,
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


def test_draw_best_thirds_uses_eight_distinct_groups() -> None:
    selections = valid_selections()
    group_by_team = {team.code: group.code for group in GROUPS for team in group.teams}

    draw = draw_best_thirds(selections, seed=2026)

    assert len({group_by_team[team.code] for team in draw}) == 8


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


def test_official_round_of_32_order_preserves_fifa_pairing_tree() -> None:
    match_numbers = [match.match_number for match in OFFICIAL_ROUND_OF_32_MATCHES]

    assert match_numbers == [73, 75, 74, 77, 83, 84, 81, 82, 76, 78, 79, 80, 86, 88, 85, 87]
    assert list(zip(match_numbers[::2], match_numbers[1::2])) == [
        (73, 75),
        (74, 77),
        (83, 84),
        (81, 82),
        (76, 78),
        (79, 80),
        (86, 88),
        (85, 87),
    ]


def test_assign_third_place_slots_accepts_every_possible_group_combination() -> None:
    from itertools import combinations

    for third_groups in combinations(GROUP_CODES, 8):
        assignments = assign_third_place_slots(third_groups)

        assert sorted(assignments.values()) == sorted(third_groups)


def test_assign_third_place_slots_uses_annex_c_assignments() -> None:
    header_match_indexes = {"A": 10, "B": 14, "D": 6, "E": 2, "G": 7, "I": 3, "K": 15, "L": 11}

    first_combination = assign_third_place_slots("EFGHIJKL")
    mid_combination = assign_third_place_slots("ABCDEFGH")

    assert {header: first_combination[index] for header, index in header_match_indexes.items()} == {
        "A": "E",
        "B": "J",
        "D": "I",
        "E": "F",
        "G": "H",
        "I": "G",
        "K": "L",
        "L": "K",
    }
    assert {header: mid_combination[index] for header, index in header_match_indexes.items()} == {
        "A": "H",
        "B": "G",
        "D": "B",
        "E": "C",
        "G": "A",
        "I": "F",
        "K": "D",
        "L": "E",
    }


def test_build_official_knockout_order_uses_fifa_round_of_32_slots() -> None:
    selections = valid_selections()
    third_codes = [group.teams[2].code for group in GROUPS[:8]]

    initial_codes = build_official_knockout_order(selections, third_codes)

    assert len(initial_codes) == 32
    assert len(set(initial_codes)) == 32
    assert build_knockout_matches(initial_codes)[:2] == [
        ("RSA", "BIH"),
        ("NED", "MAR"),
    ]


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
