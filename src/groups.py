from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Team:
    code: str
    name: str
    flag: str


@dataclass(frozen=True)
class Group:
    code: str
    teams: tuple[Team, ...]


SCOTLAND_FLAG = "\U0001F3F4\U000E0067\U000E0062\U000E0073\U000E0063\U000E0074\U000E007F"
ENGLAND_FLAG = "\U0001F3F4\U000E0067\U000E0062\U000E0065\U000E006E\U000E0067\U000E007F"

GROUPS: tuple[Group, ...] = (
    Group(
        "A",
        (
            Team("MEX", "Mexico", "🇲🇽"),
            Team("RSA", "Africa do Sul", "🇿🇦"),
            Team("KOR", "Coreia do Sul", "🇰🇷"),
            Team("CZE", "Republica Tcheca", "🇨🇿"),
        ),
    ),
    Group(
        "B",
        (
            Team("CAN", "Canada", "🇨🇦"),
            Team("BIH", "Bosnia", "🇧🇦"),
            Team("QAT", "Catar", "🇶🇦"),
            Team("SUI", "Suica", "🇨🇭"),
        ),
    ),
    Group(
        "C",
        (
            Team("BRA", "Brasil", "🇧🇷"),
            Team("MAR", "Marrocos", "🇲🇦"),
            Team("HAI", "Haiti", "🇭🇹"),
            Team("SCO", "Escocia", SCOTLAND_FLAG),
        ),
    ),
    Group(
        "D",
        (
            Team("USA", "Estados Unidos", "🇺🇸"),
            Team("PAR", "Paraguai", "🇵🇾"),
            Team("AUS", "Australia", "🇦🇺"),
            Team("TUR", "Turquia", "🇹🇷"),
        ),
    ),
    Group(
        "E",
        (
            Team("GER", "Alemanha", "🇩🇪"),
            Team("CUW", "Curacao", "🇨🇼"),
            Team("CIV", "Costa do Marfim", "🇨🇮"),
            Team("ECU", "Equador", "🇪🇨"),
        ),
    ),
    Group(
        "F",
        (
            Team("NED", "Holanda", "🇳🇱"),
            Team("JPN", "Japao", "🇯🇵"),
            Team("SWE", "Suecia", "🇸🇪"),
            Team("TUN", "Tunisia", "🇹🇳"),
        ),
    ),
    Group(
        "G",
        (
            Team("BEL", "Belgica", "🇧🇪"),
            Team("EGY", "Egito", "🇪🇬"),
            Team("IRN", "Ira", "🇮🇷"),
            Team("NZL", "Nova Zelandia", "🇳🇿"),
        ),
    ),
    Group(
        "H",
        (
            Team("ESP", "Espanha", "🇪🇸"),
            Team("CPV", "Cabo Verde", "🇨🇻"),
            Team("KSA", "Arabia Saudita", "🇸🇦"),
            Team("URU", "Uruguai", "🇺🇾"),
        ),
    ),
    Group(
        "I",
        (
            Team("FRA", "Franca", "🇫🇷"),
            Team("SEN", "Senegal", "🇸🇳"),
            Team("IRQ", "Iraque", "🇮🇶"),
            Team("NOR", "Noruega", "🇳🇴"),
        ),
    ),
    Group(
        "J",
        (
            Team("ARG", "Argentina", "🇦🇷"),
            Team("ALG", "Argelia", "🇩🇿"),
            Team("AUT", "Austria", "🇦🇹"),
            Team("JOR", "Jordania", "🇯🇴"),
        ),
    ),
    Group(
        "K",
        (
            Team("POR", "Portugal", "🇵🇹"),
            Team("COD", "RD Congo", "🇨🇩"),
            Team("UZB", "Uzbequistao", "🇺🇿"),
            Team("COL", "Colombia", "🇨🇴"),
        ),
    ),
    Group(
        "L",
        (
            Team("ENG", "Inglaterra", ENGLAND_FLAG),
            Team("CRO", "Croacia", "🇭🇷"),
            Team("GHA", "Gana", "🇬🇭"),
            Team("PAN", "Panama", "🇵🇦"),
        ),
    ),
)


def team_lookup() -> dict[str, Team]:
    return {team.code: team for group in GROUPS for team in group.teams}
