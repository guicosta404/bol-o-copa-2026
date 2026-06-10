from __future__ import annotations

import random
from dataclasses import asdict
from typing import Any, Literal, Mapping, NamedTuple, Sequence

from src.groups import GROUPS, Team, team_lookup

SelectionMap = Mapping[str, Mapping[str, str | None]]
KnockoutWinners = Mapping[str, Sequence[str | None]]
DirectSlot = tuple[Literal["first", "second"], str]
ThirdSlot = tuple[Literal["third"], frozenset[str]]
KnockoutSlot = DirectSlot | ThirdSlot

GROUP_CODES = tuple(group.code for group in GROUPS)

KNOCKOUT_PHASES: tuple[tuple[str, str], ...] = (
    ("dezesseis_avos", "16 avos de final"),
    ("oitavas", "Oitavas de final"),
    ("quartas", "Quartas de final"),
    ("semifinais", "Semifinais"),
    ("final", "Final"),
)


class OfficialRoundOf32Match(NamedTuple):
    match_number: int
    home: KnockoutSlot
    away: KnockoutSlot


OFFICIAL_ROUND_OF_32_MATCHES: tuple[OfficialRoundOf32Match, ...] = (
    OfficialRoundOf32Match(73, ("second", "A"), ("second", "B")),
    OfficialRoundOf32Match(75, ("first", "F"), ("second", "C")),
    OfficialRoundOf32Match(74, ("first", "E"), ("third", frozenset("ABCDF"))),
    OfficialRoundOf32Match(77, ("first", "I"), ("third", frozenset("CDFGH"))),
    OfficialRoundOf32Match(83, ("second", "K"), ("second", "L")),
    OfficialRoundOf32Match(84, ("first", "H"), ("second", "J")),
    OfficialRoundOf32Match(81, ("first", "D"), ("third", frozenset("BEFIJ"))),
    OfficialRoundOf32Match(82, ("first", "G"), ("third", frozenset("AEHIJ"))),
    OfficialRoundOf32Match(76, ("first", "C"), ("second", "F")),
    OfficialRoundOf32Match(78, ("second", "E"), ("second", "I")),
    OfficialRoundOf32Match(79, ("first", "A"), ("third", frozenset("CEFHI"))),
    OfficialRoundOf32Match(80, ("first", "L"), ("third", frozenset("EHIJK"))),
    OfficialRoundOf32Match(86, ("first", "J"), ("second", "H")),
    OfficialRoundOf32Match(88, ("second", "D"), ("second", "G")),
    OfficialRoundOf32Match(85, ("first", "B"), ("third", frozenset("EFGIJ"))),
    OfficialRoundOf32Match(87, ("first", "K"), ("third", frozenset("DEIJL"))),
)

THIRD_PLACE_ASSIGNMENT_HEADERS: tuple[str, ...] = ("A", "B", "D", "E", "G", "I", "K", "L")
THIRD_PLACE_HEADER_MATCH_INDEX = {
    "A": 10,
    "B": 14,
    "D": 6,
    "E": 2,
    "G": 7,
    "I": 3,
    "K": 15,
    "L": 11,
}
OFFICIAL_THIRD_PLACE_ASSIGNMENTS: dict[str, str] = {
    "EFGHIJKL": "EJIFHGLK",
    "DFGHIJKL": "HGIDJFLK",
    "DEGHIJKL": "EJIDHGLK",
    "DEFHIJKL": "EJIDHFLK",
    "DEFGIJKL": "EGIDJFLK",
    "DEFGHJKL": "EGJDHFLK",
    "DEFGHIKL": "EGIDHFLK",
    "DEFGHIJL": "EGJDHFLI",
    "DEFGHIJK": "EGJDHFIK",
    "CFGHIJKL": "HGICJFLK",
    "CEGHIJKL": "EJICHGLK",
    "CEFHIJKL": "EJICHFLK",
    "CEFGIJKL": "EGICJFLK",
    "CEFGHJKL": "EGJCHFLK",
    "CEFGHIKL": "EGICHFLK",
    "CEFGHIJL": "EGJCHFLI",
    "CEFGHIJK": "EGJCHFIK",
    "CDGHIJKL": "HGICJDLK",
    "CDFHIJKL": "CJIDHFLK",
    "CDFGIJKL": "CGIDJFLK",
    "CDFGHJKL": "CGJDHFLK",
    "CDFGHIKL": "CGIDHFLK",
    "CDFGHIJL": "CGJDHFLI",
    "CDFGHIJK": "CGJDHFIK",
    "CDEHIJKL": "EJICHDLK",
    "CDEGIJKL": "EGICJDLK",
    "CDEGHJKL": "EGJCHDLK",
    "CDEGHIKL": "EGICHDLK",
    "CDEGHIJL": "EGJCHDLI",
    "CDEGHIJK": "EGJCHDIK",
    "CDEFIJKL": "CJEDIFLK",
    "CDEFHJKL": "CJEDHFLK",
    "CDEFHIKL": "CEIDHFLK",
    "CDEFHIJL": "CJEDHFLI",
    "CDEFHIJK": "CJEDHFIK",
    "CDEFGJKL": "CGEDJFLK",
    "CDEFGIKL": "CGEDIFLK",
    "CDEFGIJL": "CGEDJFLI",
    "CDEFGIJK": "CGEDJFIK",
    "CDEFGHKL": "CGEDHFLK",
    "CDEFGHJL": "CGJDHFLE",
    "CDEFGHJK": "CGJDHFEK",
    "CDEFGHIL": "CGEDHFLI",
    "CDEFGHIK": "CGEDHFIK",
    "CDEFGHIJ": "CGJDHFEI",
    "BFGHIJKL": "HJBFIGLK",
    "BEGHIJKL": "EJIBHGLK",
    "BEFHIJKL": "EJBFIHLK",
    "BEFGIJKL": "EJBFIGLK",
    "BEFGHJKL": "EJBFHGLK",
    "BEFGHIKL": "EGBFIHLK",
    "BEFGHIJL": "EJBFHGLI",
    "BEFGHIJK": "EJBFHGIK",
    "BDGHIJKL": "HJBDIGLK",
    "BDFHIJKL": "HJBDIFLK",
    "BDFGIJKL": "IGBDJFLK",
    "BDFGHJKL": "HGBDJFLK",
    "BDFGHIKL": "HGBDIFLK",
    "BDFGHIJL": "HGBDJFLI",
    "BDFGHIJK": "HGBDJFIK",
    "BDEHIJKL": "EJBDIHLK",
    "BDEGIJKL": "EJBDIGLK",
    "BDEGHJKL": "EJBDHGLK",
    "BDEGHIKL": "EGBDIHLK",
    "BDEGHIJL": "EJBDHGLI",
    "BDEGHIJK": "EJBDHGIK",
    "BDEFIJKL": "EJBDIFLK",
    "BDEFHJKL": "EJBDHFLK",
    "BDEFHIKL": "EIBDHFLK",
    "BDEFHIJL": "EJBDHFLI",
    "BDEFHIJK": "EJBDHFIK",
    "BDEFGJKL": "EGBDJFLK",
    "BDEFGIKL": "EGBDIFLK",
    "BDEFGIJL": "EGBDJFLI",
    "BDEFGIJK": "EGBDJFIK",
    "BDEFGHKL": "EGBDHFLK",
    "BDEFGHJL": "HGBDJFLE",
    "BDEFGHJK": "HGBDJFEK",
    "BDEFGHIL": "EGBDHFLI",
    "BDEFGHIK": "EGBDHFIK",
    "BDEFGHIJ": "HGBDJFEI",
    "BCGHIJKL": "HJBCIGLK",
    "BCFHIJKL": "HJBCIFLK",
    "BCFGIJKL": "IGBCJFLK",
    "BCFGHJKL": "HGBCJFLK",
    "BCFGHIKL": "HGBCIFLK",
    "BCFGHIJL": "HGBCJFLI",
    "BCFGHIJK": "HGBCJFIK",
    "BCEHIJKL": "EJBCIHLK",
    "BCEGIJKL": "EJBCIGLK",
    "BCEGHJKL": "EJBCHGLK",
    "BCEGHIKL": "EGBCIHLK",
    "BCEGHIJL": "EJBCHGLI",
    "BCEGHIJK": "EJBCHGIK",
    "BCEFIJKL": "EJBCIFLK",
    "BCEFHJKL": "EJBCHFLK",
    "BCEFHIKL": "EIBCHFLK",
    "BCEFHIJL": "EJBCHFLI",
    "BCEFHIJK": "EJBCHFIK",
    "BCEFGJKL": "EGBCJFLK",
    "BCEFGIKL": "EGBCIFLK",
    "BCEFGIJL": "EGBCJFLI",
    "BCEFGIJK": "EGBCJFIK",
    "BCEFGHKL": "EGBCHFLK",
    "BCEFGHJL": "HGBCJFLE",
    "BCEFGHJK": "HGBCJFEK",
    "BCEFGHIL": "EGBCHFLI",
    "BCEFGHIK": "EGBCHFIK",
    "BCEFGHIJ": "HGBCJFEI",
    "BCDHIJKL": "HJBCIDLK",
    "BCDGIJKL": "IGBCJDLK",
    "BCDGHJKL": "HGBCJDLK",
    "BCDGHIKL": "HGBCIDLK",
    "BCDGHIJL": "HGBCJDLI",
    "BCDGHIJK": "HGBCJDIK",
    "BCDFIJKL": "CJBDIFLK",
    "BCDFHJKL": "CJBDHFLK",
    "BCDFHIKL": "CIBDHFLK",
    "BCDFHIJL": "CJBDHFLI",
    "BCDFHIJK": "CJBDHFIK",
    "BCDFGJKL": "CGBDJFLK",
    "BCDFGIKL": "CGBDIFLK",
    "BCDFGIJL": "CGBDJFLI",
    "BCDFGIJK": "CGBDJFIK",
    "BCDFGHKL": "CGBDHFLK",
    "BCDFGHJL": "CGBDHFLJ",
    "BCDFGHJK": "HGBCJFDK",
    "BCDFGHIL": "CGBDHFLI",
    "BCDFGHIK": "CGBDHFIK",
    "BCDFGHIJ": "HGBCJFDI",
    "BCDEIJKL": "EJBCIDLK",
    "BCDEHJKL": "EJBCHDLK",
    "BCDEHIKL": "EIBCHDLK",
    "BCDEHIJL": "EJBCHDLI",
    "BCDEHIJK": "EJBCHDIK",
    "BCDEGJKL": "EGBCJDLK",
    "BCDEGIKL": "EGBCIDLK",
    "BCDEGIJL": "EGBCJDLI",
    "BCDEGIJK": "EGBCJDIK",
    "BCDEGHKL": "EGBCHDLK",
    "BCDEGHJL": "HGBCJDLE",
    "BCDEGHJK": "HGBCJDEK",
    "BCDEGHIL": "EGBCHDLI",
    "BCDEGHIK": "EGBCHDIK",
    "BCDEGHIJ": "HGBCJDEI",
    "BCDEFJKL": "CJBDEFLK",
    "BCDEFIKL": "CEBDIFLK",
    "BCDEFIJL": "CJBDEFLI",
    "BCDEFIJK": "CJBDEFIK",
    "BCDEFHKL": "CEBDHFLK",
    "BCDEFHJL": "CJBDHFLE",
    "BCDEFHJK": "CJBDHFEK",
    "BCDEFHIL": "CEBDHFLI",
    "BCDEFHIK": "CEBDHFIK",
    "BCDEFHIJ": "CJBDHFEI",
    "BCDEFGKL": "CGBDEFLK",
    "BCDEFGJL": "CGBDJFLE",
    "BCDEFGJK": "CGBDJFEK",
    "BCDEFGIL": "CGBDEFLI",
    "BCDEFGIK": "CGBDEFIK",
    "BCDEFGIJ": "CGBDJFEI",
    "BCDEFGHL": "CGBDHFLE",
    "BCDEFGHK": "CGBDHFEK",
    "BCDEFGHJ": "HGBCJFDE",
    "BCDEFGHI": "CGBDHFEI",
    "AFGHIJKL": "HJIFAGLK",
    "AEGHIJKL": "EJIAHGLK",
    "AEFHIJKL": "EJIFAHLK",
    "AEFGIJKL": "EJIFAGLK",
    "AEFGHJKL": "EGJFAHLK",
    "AEFGHIKL": "EGIFAHLK",
    "AEFGHIJL": "EGJFAHLI",
    "AEFGHIJK": "EGJFAHIK",
    "ADGHIJKL": "HJIDAGLK",
    "ADFHIJKL": "HJIDAFLK",
    "ADFGIJKL": "IGJDAFLK",
    "ADFGHJKL": "HGJDAFLK",
    "ADFGHIKL": "HGIDAFLK",
    "ADFGHIJL": "HGJDAFLI",
    "ADFGHIJK": "HGJDAFIK",
    "ADEHIJKL": "EJIDAHLK",
    "ADEGIJKL": "EJIDAGLK",
    "ADEGHJKL": "EGJDAHLK",
    "ADEGHIKL": "EGIDAHLK",
    "ADEGHIJL": "EGJDAHLI",
    "ADEGHIJK": "EGJDAHIK",
    "ADEFIJKL": "EJIDAFLK",
    "ADEFHJKL": "HJEDAFLK",
    "ADEFHIKL": "HEIDAFLK",
    "ADEFHIJL": "HJEDAFLI",
    "ADEFHIJK": "HJEDAFIK",
    "ADEFGJKL": "EGJDAFLK",
    "ADEFGIKL": "EGIDAFLK",
    "ADEFGIJL": "EGJDAFLI",
    "ADEFGIJK": "EGJDAFIK",
    "ADEFGHKL": "HGEDAFLK",
    "ADEFGHJL": "HGJDAFLE",
    "ADEFGHJK": "HGJDAFEK",
    "ADEFGHIL": "HGEDAFLI",
    "ADEFGHIK": "HGEDAFIK",
    "ADEFGHIJ": "HGJDAFEI",
    "ACGHIJKL": "HJICAGLK",
    "ACFHIJKL": "HJICAFLK",
    "ACFGIJKL": "IGJCAFLK",
    "ACFGHJKL": "HGJCAFLK",
    "ACFGHIKL": "HGICAFLK",
    "ACFGHIJL": "HGJCAFLI",
    "ACFGHIJK": "HGJCAFIK",
    "ACEHIJKL": "EJICAHLK",
    "ACEGIJKL": "EJICAGLK",
    "ACEGHJKL": "EGJCAHLK",
    "ACEGHIKL": "EGICAHLK",
    "ACEGHIJL": "EGJCAHLI",
    "ACEGHIJK": "EGJCAHIK",
    "ACEFIJKL": "EJICAFLK",
    "ACEFHJKL": "HJECAFLK",
    "ACEFHIKL": "HEICAFLK",
    "ACEFHIJL": "HJECAFLI",
    "ACEFHIJK": "HJECAFIK",
    "ACEFGJKL": "EGJCAFLK",
    "ACEFGIKL": "EGICAFLK",
    "ACEFGIJL": "EGJCAFLI",
    "ACEFGIJK": "EGJCAFIK",
    "ACEFGHKL": "HGECAFLK",
    "ACEFGHJL": "HGJCAFLE",
    "ACEFGHJK": "HGJCAFEK",
    "ACEFGHIL": "HGECAFLI",
    "ACEFGHIK": "HGECAFIK",
    "ACEFGHIJ": "HGJCAFEI",
    "ACDHIJKL": "HJICADLK",
    "ACDGIJKL": "IGJCADLK",
    "ACDGHJKL": "HGJCADLK",
    "ACDGHIKL": "HGICADLK",
    "ACDGHIJL": "HGJCADLI",
    "ACDGHIJK": "HGJCADIK",
    "ACDFIJKL": "CJIDAFLK",
    "ACDFHJKL": "HJFCADLK",
    "ACDFHIKL": "HFICADLK",
    "ACDFHIJL": "HJFCADLI",
    "ACDFHIJK": "HJFCADIK",
    "ACDFGJKL": "CGJDAFLK",
    "ACDFGIKL": "CGIDAFLK",
    "ACDFGIJL": "CGJDAFLI",
    "ACDFGIJK": "CGJDAFIK",
    "ACDFGHKL": "HGFCADLK",
    "ACDFGHJL": "CGJDAFLH",
    "ACDFGHJK": "HGJCAFDK",
    "ACDFGHIL": "HGFCADLI",
    "ACDFGHIK": "HGFCADIK",
    "ACDFGHIJ": "HGJCAFDI",
    "ACDEIJKL": "EJICADLK",
    "ACDEHJKL": "HJECADLK",
    "ACDEHIKL": "HEICADLK",
    "ACDEHIJL": "HJECADLI",
    "ACDEHIJK": "HJECADIK",
    "ACDEGJKL": "EGJCADLK",
    "ACDEGIKL": "EGICADLK",
    "ACDEGIJL": "EGJCADLI",
    "ACDEGIJK": "EGJCADIK",
    "ACDEGHKL": "HGECADLK",
    "ACDEGHJL": "HGJCADLE",
    "ACDEGHJK": "HGJCADEK",
    "ACDEGHIL": "HGECADLI",
    "ACDEGHIK": "HGECADIK",
    "ACDEGHIJ": "HGJCADEI",
    "ACDEFJKL": "CJEDAFLK",
    "ACDEFIKL": "CEIDAFLK",
    "ACDEFIJL": "CJEDAFLI",
    "ACDEFIJK": "CJEDAFIK",
    "ACDEFHKL": "HEFCADLK",
    "ACDEFHJL": "HJFCADLE",
    "ACDEFHJK": "HJECAFDK",
    "ACDEFHIL": "HEFCADLI",
    "ACDEFHIK": "HEFCADIK",
    "ACDEFHIJ": "HJECAFDI",
    "ACDEFGKL": "CGEDAFLK",
    "ACDEFGJL": "CGJDAFLE",
    "ACDEFGJK": "CGJDAFEK",
    "ACDEFGIL": "CGEDAFLI",
    "ACDEFGIK": "CGEDAFIK",
    "ACDEFGIJ": "CGJDAFEI",
    "ACDEFGHL": "HGFCADLE",
    "ACDEFGHK": "HGECAFDK",
    "ACDEFGHJ": "HGJCAFDE",
    "ACDEFGHI": "HGECAFDI",
    "ABGHIJKL": "HJBAIGLK",
    "ABFHIJKL": "HJBAIFLK",
    "ABFGIJKL": "IJBFAGLK",
    "ABFGHJKL": "HJBFAGLK",
    "ABFGHIKL": "HGBAIFLK",
    "ABFGHIJL": "HJBFAGLI",
    "ABFGHIJK": "HJBFAGIK",
    "ABEHIJKL": "EJBAIHLK",
    "ABEGIJKL": "EJBAIGLK",
    "ABEGHJKL": "EJBAHGLK",
    "ABEGHIKL": "EGBAIHLK",
    "ABEGHIJL": "EJBAHGLI",
    "ABEGHIJK": "EJBAHGIK",
    "ABEFIJKL": "EJBAIFLK",
    "ABEFHJKL": "EJBFAHLK",
    "ABEFHIKL": "EIBFAHLK",
    "ABEFHIJL": "EJBFAHLI",
    "ABEFHIJK": "EJBFAHIK",
    "ABEFGJKL": "EJBFAGLK",
    "ABEFGIKL": "EGBAIFLK",
    "ABEFGIJL": "EJBFAGLI",
    "ABEFGIJK": "EJBFAGIK",
    "ABEFGHKL": "EGBFAHLK",
    "ABEFGHJL": "HJBFAGLE",
    "ABEFGHJK": "HJBFAGEK",
    "ABEFGHIL": "EGBFAHLI",
    "ABEFGHIK": "EGBFAHIK",
    "ABEFGHIJ": "HJBFAGEI",
    "ABDHIJKL": "IJBDAHLK",
    "ABDGIJKL": "IJBDAGLK",
    "ABDGHJKL": "HJBDAGLK",
    "ABDGHIKL": "IGBDAHLK",
    "ABDGHIJL": "HJBDAGLI",
    "ABDGHIJK": "HJBDAGIK",
    "ABDFIJKL": "IJBDAFLK",
    "ABDFHJKL": "HJBDAFLK",
    "ABDFHIKL": "HIBDAFLK",
    "ABDFHIJL": "HJBDAFLI",
    "ABDFHIJK": "HJBDAFIK",
    "ABDFGJKL": "FJBDAGLK",
    "ABDFGIKL": "IGBDAFLK",
    "ABDFGIJL": "FJBDAGLI",
    "ABDFGIJK": "FJBDAGIK",
    "ABDFGHKL": "HGBDAFLK",
    "ABDFGHJL": "HGBDAFLJ",
    "ABDFGHJK": "HGBDAFJK",
    "ABDFGHIL": "HGBDAFLI",
    "ABDFGHIK": "HGBDAFIK",
    "ABDFGHIJ": "HGBDAFIJ",
    "ABDEIJKL": "EJBAIDLK",
    "ABDEHJKL": "EJBDAHLK",
    "ABDEHIKL": "EIBDAHLK",
    "ABDEHIJL": "EJBDAHLI",
    "ABDEHIJK": "EJBDAHIK",
    "ABDEGJKL": "EJBDAGLK",
    "ABDEGIKL": "EGBAIDLK",
    "ABDEGIJL": "EJBDAGLI",
    "ABDEGIJK": "EJBDAGIK",
    "ABDEGHKL": "EGBDAHLK",
    "ABDEGHJL": "HJBDAGLE",
    "ABDEGHJK": "HJBDAGEK",
    "ABDEGHIL": "EGBDAHLI",
    "ABDEGHIK": "EGBDAHIK",
    "ABDEGHIJ": "HJBDAGEI",
    "ABDEFJKL": "EJBDAFLK",
    "ABDEFIKL": "EIBDAFLK",
    "ABDEFIJL": "EJBDAFLI",
    "ABDEFIJK": "EJBDAFIK",
    "ABDEFHKL": "HEBDAFLK",
    "ABDEFHJL": "HJBDAFLE",
    "ABDEFHJK": "HJBDAFEK",
    "ABDEFHIL": "HEBDAFLI",
    "ABDEFHIK": "HEBDAFIK",
    "ABDEFHIJ": "HJBDAFEI",
    "ABDEFGKL": "EGBDAFLK",
    "ABDEFGJL": "EGBDAFLJ",
    "ABDEFGJK": "EGBDAFJK",
    "ABDEFGIL": "EGBDAFLI",
    "ABDEFGIK": "EGBDAFIK",
    "ABDEFGIJ": "EGBDAFIJ",
    "ABDEFGHL": "HGBDAFLE",
    "ABDEFGHK": "HGBDAFEK",
    "ABDEFGHJ": "HGBDAFEJ",
    "ABDEFGHI": "HGBDAFEI",
    "ABCHIJKL": "IJBCAHLK",
    "ABCGIJKL": "IJBCAGLK",
    "ABCGHJKL": "HJBCAGLK",
    "ABCGHIKL": "IGBCAHLK",
    "ABCGHIJL": "HJBCAGLI",
    "ABCGHIJK": "HJBCAGIK",
    "ABCFIJKL": "IJBCAFLK",
    "ABCFHJKL": "HJBCAFLK",
    "ABCFHIKL": "HIBCAFLK",
    "ABCFHIJL": "HJBCAFLI",
    "ABCFHIJK": "HJBCAFIK",
    "ABCFGJKL": "CJBFAGLK",
    "ABCFGIKL": "IGBCAFLK",
    "ABCFGIJL": "CJBFAGLI",
    "ABCFGIJK": "CJBFAGIK",
    "ABCFGHKL": "HGBCAFLK",
    "ABCFGHJL": "HGBCAFLJ",
    "ABCFGHJK": "HGBCAFJK",
    "ABCFGHIL": "HGBCAFLI",
    "ABCFGHIK": "HGBCAFIK",
    "ABCFGHIJ": "HGBCAFIJ",
    "ABCEIJKL": "EJBAICLK",
    "ABCEHJKL": "EJBCAHLK",
    "ABCEHIKL": "EIBCAHLK",
    "ABCEHIJL": "EJBCAHLI",
    "ABCEHIJK": "EJBCAHIK",
    "ABCEGJKL": "EJBCAGLK",
    "ABCEGIKL": "EGBAICLK",
    "ABCEGIJL": "EJBCAGLI",
    "ABCEGIJK": "EJBCAGIK",
    "ABCEGHKL": "EGBCAHLK",
    "ABCEGHJL": "HJBCAGLE",
    "ABCEGHJK": "HJBCAGEK",
    "ABCEGHIL": "EGBCAHLI",
    "ABCEGHIK": "EGBCAHIK",
    "ABCEGHIJ": "HJBCAGEI",
    "ABCEFJKL": "EJBCAFLK",
    "ABCEFIKL": "EIBCAFLK",
    "ABCEFIJL": "EJBCAFLI",
    "ABCEFIJK": "EJBCAFIK",
    "ABCEFHKL": "HEBCAFLK",
    "ABCEFHJL": "HJBCAFLE",
    "ABCEFHJK": "HJBCAFEK",
    "ABCEFHIL": "HEBCAFLI",
    "ABCEFHIK": "HEBCAFIK",
    "ABCEFHIJ": "HJBCAFEI",
    "ABCEFGKL": "EGBCAFLK",
    "ABCEFGJL": "EGBCAFLJ",
    "ABCEFGJK": "EGBCAFJK",
    "ABCEFGIL": "EGBCAFLI",
    "ABCEFGIK": "EGBCAFIK",
    "ABCEFGIJ": "EGBCAFIJ",
    "ABCEFGHL": "HGBCAFLE",
    "ABCEFGHK": "HGBCAFEK",
    "ABCEFGHJ": "HGBCAFEJ",
    "ABCEFGHI": "HGBCAFEI",
    "ABCDIJKL": "IJBCADLK",
    "ABCDHJKL": "HJBCADLK",
    "ABCDHIKL": "HIBCADLK",
    "ABCDHIJL": "HJBCADLI",
    "ABCDHIJK": "HJBCADIK",
    "ABCDGJKL": "CJBDAGLK",
    "ABCDGIKL": "IGBCADLK",
    "ABCDGIJL": "CJBDAGLI",
    "ABCDGIJK": "CJBDAGIK",
    "ABCDGHKL": "HGBCADLK",
    "ABCDGHJL": "HGBCADLJ",
    "ABCDGHJK": "HGBCADJK",
    "ABCDGHIL": "HGBCADLI",
    "ABCDGHIK": "HGBCADIK",
    "ABCDGHIJ": "HGBCADIJ",
    "ABCDFJKL": "CJBDAFLK",
    "ABCDFIKL": "CIBDAFLK",
    "ABCDFIJL": "CJBDAFLI",
    "ABCDFIJK": "CJBDAFIK",
    "ABCDFHKL": "HFBCADLK",
    "ABCDFHJL": "CJBDAFLH",
    "ABCDFHJK": "HJBCAFDK",
    "ABCDFHIL": "HFBCADLI",
    "ABCDFHIK": "HFBCADIK",
    "ABCDFHIJ": "HJBCAFDI",
    "ABCDFGKL": "CGBDAFLK",
    "ABCDFGJL": "CGBDAFLJ",
    "ABCDFGJK": "CGBDAFJK",
    "ABCDFGIL": "CGBDAFLI",
    "ABCDFGIK": "CGBDAFIK",
    "ABCDFGIJ": "CGBDAFIJ",
    "ABCDFGHL": "CGBDAFLH",
    "ABCDFGHK": "HGBCAFDK",
    "ABCDFGHJ": "HGBCAFDJ",
    "ABCDFGHI": "HGBCAFDI",
    "ABCDEJKL": "EJBCADLK",
    "ABCDEIKL": "EIBCADLK",
    "ABCDEIJL": "EJBCADLI",
    "ABCDEIJK": "EJBCADIK",
    "ABCDEHKL": "HEBCADLK",
    "ABCDEHJL": "HJBCADLE",
    "ABCDEHJK": "HJBCADEK",
    "ABCDEHIL": "HEBCADLI",
    "ABCDEHIK": "HEBCADIK",
    "ABCDEHIJ": "HJBCADEI",
    "ABCDEGKL": "EGBCADLK",
    "ABCDEGJL": "EGBCADLJ",
    "ABCDEGJK": "EGBCADJK",
    "ABCDEGIL": "EGBCADLI",
    "ABCDEGIK": "EGBCADIK",
    "ABCDEGIJ": "EGBCADIJ",
    "ABCDEGHL": "HGBCADLE",
    "ABCDEGHK": "HGBCADEK",
    "ABCDEGHJ": "HGBCADEJ",
    "ABCDEGHI": "HGBCADEI",
    "ABCDEFKL": "CEBDAFLK",
    "ABCDEFJL": "CJBDAFLE",
    "ABCDEFJK": "CJBDAFEK",
    "ABCDEFIL": "CEBDAFLI",
    "ABCDEFIK": "CEBDAFIK",
    "ABCDEFIJ": "CJBDAFEI",
    "ABCDEFHL": "HFBCADLE",
    "ABCDEFHK": "HEBCAFDK",
    "ABCDEFHJ": "HJBCAFDE",
    "ABCDEFHI": "HEBCAFDI",
    "ABCDEFGL": "CGBDAFLE",
    "ABCDEFGK": "CGBDAFEK",
    "ABCDEFGJ": "CGBDAFEJ",
    "ABCDEFGI": "CGBDAFEI",
    "ABCDEFGH": "HGBCAFDE",
}

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
    group_thirds: list[Team] = []

    for group in GROUPS:
        picked = {
            selections.get(group.code, {}).get("first"),
            selections.get(group.code, {}).get("second"),
        }
        third_candidates = [team for team in group.teams if team.code not in picked]
        group_thirds.append(rng.choice(third_candidates))

    return rng.sample(group_thirds, 8)


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


def team_group_lookup() -> dict[str, str]:
    return {team.code: group.code for group in GROUPS for team in group.teams}


def assign_third_place_slots(third_group_codes: Sequence[str]) -> dict[int, str]:
    selected_groups = set(third_group_codes)
    if len(third_group_codes) != 8 or len(selected_groups) != 8:
        raise ValueError("O mata-mata oficial precisa de oito terceiros de grupos diferentes.")
    if not selected_groups.issubset(set(GROUP_CODES)):
        raise ValueError("O mata-mata possui um grupo de terceiro colocado invalido.")

    combination_key = "".join(group_code for group_code in GROUP_CODES if group_code in selected_groups)
    assignment = OFFICIAL_THIRD_PLACE_ASSIGNMENTS.get(combination_key)
    if assignment is None:
        raise ValueError("Nao foi possivel encaixar os terceiros no chaveamento oficial da FIFA.")

    return {
        THIRD_PLACE_HEADER_MATCH_INDEX[group_code]: third_group
        for group_code, third_group in zip(THIRD_PLACE_ASSIGNMENT_HEADERS, assignment)
    }


def build_official_knockout_order(selections: SelectionMap, third_codes: Sequence[str]) -> list[str]:
    errors = validate_selections(selections)
    if errors:
        raise ValueError(" ".join(errors))

    group_by_team = team_group_lookup()
    third_groups_by_code = {
        code: group_by_team[code]
        for code in third_codes
        if code in group_by_team
    }
    if len(third_groups_by_code) != len(third_codes):
        raise ValueError("O mata-mata possui um terceiro colocado invalido.")

    third_codes_by_group = {group_code: code for code, group_code in third_groups_by_code.items()}
    third_assignments = assign_third_place_slots(list(third_codes_by_group))

    initial_codes: list[str] = []
    for match_index, match in enumerate(OFFICIAL_ROUND_OF_32_MATCHES):
        for slot in (match.home, match.away):
            if slot[0] == "third":
                initial_codes.append(third_codes_by_group[third_assignments[match_index]])
            else:
                selected_code = selections[slot[1]][slot[0]]
                assert selected_code is not None
                initial_codes.append(selected_code)

    return initial_codes


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
