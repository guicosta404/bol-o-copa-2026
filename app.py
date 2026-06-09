from __future__ import annotations

import random
from datetime import datetime, timezone
from textwrap import dedent

import streamlit as st

from src.groups import GROUPS, Group, team_lookup
from src.rules import (
    KNOCKOUT_PHASES,
    build_knockout_matches,
    build_qualified,
    serialize_knockout,
    serialize_selections,
    validate_knockout,
    validate_participant,
    validate_selections,
)
from src.storage import save_bet


GROUP_POSITION_OPTIONS: tuple[tuple[str, str], ...] = (
    ("first", "1º"),
    ("second", "2º"),
)
GROUP_POSITION_BY_LABEL = {label: key for key, label in GROUP_POSITION_OPTIONS}
GROUP_POSITION_LABELS = tuple(label for _key, label in GROUP_POSITION_OPTIONS)


st.set_page_config(
    page_title="Bolao Copa 2026",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)


BRACKET_HTML = '<div id="world-cup-bracket"></div>'

BRACKET_CSS = """
#world-cup-bracket {
    font-family: Arial, Helvetica, sans-serif;
}

.bracket-scroll {
    background: #ffffff;
    border: 1px solid #e6e6e6;
    overflow-x: auto;
    width: 100%;
}

.bracket-frame {
    background: #ffffff;
    height: 820px;
    min-width: 1020px;
    position: relative;
}

.connector-layer {
    height: 100%;
    inset: 0;
    pointer-events: none;
    position: absolute;
    width: 100%;
    z-index: 1;
}

.connector-layer path {
    fill: none;
    stroke: #cfcfcf;
    stroke-dasharray: 1.5 1.5;
    stroke-linecap: square;
    stroke-width: .16;
}

.connector-layer path.active {
    stroke: #05bd4c;
    stroke-dasharray: none;
    stroke-width: .24;
}

.bracket-node {
    --node-size: 48px;
    align-items: center;
    background: transparent;
    border: 0;
    color: #1f2a33;
    display: flex;
    gap: 6px;
    padding: 0;
    position: absolute;
    transform: translate(-50%, -50%);
    z-index: 2;
}

.bracket-node.selectable {
    cursor: pointer;
}

.bracket-node:not(.selectable) {
    cursor: default;
}

.bracket-node:focus-visible .flag-circle {
    outline: 3px solid rgba(5, 189, 76, .28);
    outline-offset: 3px;
}

.bracket-node.left .team-code {
    order: 0;
    text-align: right;
}

.bracket-node.left .flag-circle {
    order: 1;
}

.bracket-node.right .flag-circle {
    order: 0;
}

.bracket-node.right .team-code {
    order: 1;
    text-align: left;
}

.team-code {
    color: #1d2b34;
    font-size: 13px;
    font-weight: 800;
    min-width: 34px;
}

.flag-circle {
    align-items: center;
    background: #ffffff;
    border: 2px solid #05bd4c;
    border-radius: 999px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, .12);
    display: flex;
    font-size: calc(var(--node-size) * .54);
    height: var(--node-size);
    justify-content: center;
    line-height: 1;
    overflow: hidden;
    width: var(--node-size);
}

.bracket-node.selectable:hover .flag-circle {
    box-shadow: 0 0 0 5px rgba(5, 189, 76, .14), 0 4px 12px rgba(0, 0, 0, .16);
    transform: translateY(-1px);
}

.bracket-node.selected .flag-circle {
    background: #e9fff0;
    border-color: #00b745;
    box-shadow: 0 0 0 4px rgba(5, 189, 76, .18), 0 5px 14px rgba(0, 0, 0, .18);
}

.bracket-node.placeholder .flag-circle {
    background: #f6f6f6;
    border-color: #d0d0d0;
    box-shadow: none;
}

.bracket-node.placeholder .team-code,
.bracket-node.placeholder .flag-value {
    opacity: 0;
}

.champion-area {
    align-items: center;
    color: #1f2a33;
    display: flex;
    flex-direction: column;
    left: 50%;
    position: absolute;
    text-align: center;
    top: 50%;
    transform: translate(-50%, -50%);
    z-index: 3;
}

.champion-help {
    color: #05bd4c;
    font-size: 13px;
    font-style: italic;
    font-weight: 900;
    line-height: 1.7;
    margin-bottom: 34px;
}

.champion-trophy {
    color: #d5b85c;
    font-size: 56px;
    line-height: 1;
    margin-bottom: 8px;
}

.champion-label {
    font-size: 18px;
    font-weight: 800;
    line-height: 1.2;
}

.champion-node {
    --node-size: 112px;
    align-items: center;
    background: transparent;
    border: 0;
    display: flex;
    justify-content: center;
    padding: 0;
}

.champion-node .flag-circle {
    font-size: 60px;
}

.bracket-empty-copy {
    color: #8a8a8a;
    font-size: 13px;
    font-weight: 700;
    line-height: 1.5;
    margin-top: 10px;
}
"""

BRACKET_JS = """
export default function (component) {
  const { data, parentElement, setTriggerValue } = component
  const root = parentElement.querySelector("#world-cup-bracket")
  if (!root || !data) return

  const phases = data.phases ?? []
  const teams = data.teams ?? {}
  const initial = data.initial ?? []
  const winners = data.winners ?? {}
  const winnerArrays = {
    dezesseis_avos: normalizeArray(winners.dezesseis_avos, 16),
    oitavas: normalizeArray(winners.oitavas, 8),
    quartas: normalizeArray(winners.quartas, 4),
    semifinais: normalizeArray(winners.semifinais, 2),
    final: normalizeArray(winners.final, 1),
  }

  const xLeft = [5.4, 14.8, 24.3, 33.5, 42.0]
  const xRight = [94.6, 85.2, 75.7, 66.5, 58.0]
  const nodeSizes = [42, 54, 62, 70, 78]
  const rounds = [
    {
      left: normalizeArray(initial.slice(0, 16), 16),
      right: normalizeArray(initial.slice(16, 32), 16),
    },
    {
      left: winnerArrays.dezesseis_avos.slice(0, 8),
      right: winnerArrays.dezesseis_avos.slice(8, 16),
    },
    {
      left: winnerArrays.oitavas.slice(0, 4),
      right: winnerArrays.oitavas.slice(4, 8),
    },
    {
      left: winnerArrays.quartas.slice(0, 2),
      right: winnerArrays.quartas.slice(2, 4),
    },
    {
      left: winnerArrays.semifinais.slice(0, 1),
      right: winnerArrays.semifinais.slice(1, 2),
    },
  ]

  root.innerHTML = ""
  const scroll = document.createElement("div")
  scroll.className = "bracket-scroll"
  const frame = document.createElement("div")
  frame.className = "bracket-frame"
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
  svg.setAttribute("class", "connector-layer")
  svg.setAttribute("viewBox", "0 0 100 100")
  svg.setAttribute("preserveAspectRatio", "none")

  drawConnectors(svg, rounds, xLeft, xRight)
  frame.appendChild(svg)
  drawNodes(frame, rounds, xLeft, xRight, nodeSizes)
  drawChampion(frame, winnerArrays.final[0])
  scroll.appendChild(frame)
  root.appendChild(scroll)

  function normalizeArray(value, length) {
    const source = Array.isArray(value) ? value : []
    return Array.from({ length }, (_, index) => source[index] ?? null)
  }

  function team(code) {
    return teams[code] ?? { code, name: code ?? "", flag: "" }
  }

  function yPositions(count) {
    if (count === 1) return [50]
    return Array.from({ length: count }, (_, index) => 3 + index * (94 / (count - 1)))
  }

  function coords(roundIndex, side, index) {
    const sideRound = rounds[roundIndex][side]
    const y = yPositions(sideRound.length)[index]
    const x = side === "left" ? xLeft[roundIndex] : xRight[roundIndex]
    return { x, y }
  }

  function drawConnectors(svgElement, roundValues, leftXs, rightXs) {
    for (let roundIndex = 0; roundIndex < 4; roundIndex += 1) {
      for (const side of ["left", "right"]) {
        const current = roundValues[roundIndex][side]
        const next = roundValues[roundIndex + 1][side]
        for (let matchIndex = 0; matchIndex < current.length / 2; matchIndex += 1) {
          const first = coords(roundIndex, side, matchIndex * 2)
          const second = coords(roundIndex, side, matchIndex * 2 + 1)
          const target = coords(roundIndex + 1, side, matchIndex)
          const active = Boolean(next[matchIndex])
          appendConnector(svgElement, first, target, side, active)
          appendConnector(svgElement, second, target, side, active)
        }
      }
    }

    const leftFinalist = rounds[4].left[0]
    const rightFinalist = rounds[4].right[0]
    const champion = winnerArrays.final[0]
    appendConnector(svgElement, coords(4, "left", 0), { x: 50, y: 50 }, "left", Boolean(champion && leftFinalist))
    appendConnector(svgElement, coords(4, "right", 0), { x: 50, y: 50 }, "right", Boolean(champion && rightFinalist))
  }

  function appendConnector(svgElement, start, end, side, active) {
    const elbow = (start.x + end.x) / 2
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path")
    path.setAttribute("d", `M ${start.x} ${start.y} H ${elbow} V ${end.y} H ${end.x}`)
    if (active) path.setAttribute("class", "active")
    svgElement.appendChild(path)
  }

  function drawNodes(frameElement, roundValues, leftXs, rightXs, sizes) {
    for (let roundIndex = 0; roundIndex < roundValues.length; roundIndex += 1) {
      for (const side of ["left", "right"]) {
        const values = roundValues[roundIndex][side]
        const ys = yPositions(values.length)
        values.forEach((code, index) => {
          const position = {
            x: side === "left" ? leftXs[roundIndex] : rightXs[roundIndex],
            y: ys[index],
          }
          frameElement.appendChild(createNode(code, roundIndex, side, index, position, sizes[roundIndex]))
        })
      }
    }
  }

  function createNode(code, roundIndex, side, index, position, size) {
    const clickInfo = clickPayload(roundIndex, side, index)
    const isSelectable = Boolean(code && clickInfo)
    const selected = Boolean(clickInfo && currentWinner(clickInfo.phase_key, clickInfo.match_number) === code)
    const node = document.createElement(isSelectable ? "button" : "div")
    node.className = [
      "bracket-node",
      side,
      code ? "filled" : "placeholder",
      isSelectable ? "selectable" : "",
      selected ? "selected" : "",
    ].filter(Boolean).join(" ")
    node.style.left = `${position.x}%`
    node.style.top = `${position.y}%`
    node.style.setProperty("--node-size", `${size}px`)
    if (isSelectable) {
      const item = team(code)
      node.type = "button"
      node.title = `Escolher ${item.name}`
      node.setAttribute("aria-label", `Escolher ${item.name}`)
      node.onclick = () => {
        setTriggerValue("pick", {
          ...clickInfo,
          winner_code: code,
          nonce: Date.now(),
        })
      }
    }

    const item = team(code)
    if (side === "left") {
      node.appendChild(codeLabel(item.code))
      node.appendChild(flagCircle(item.flag))
    } else {
      node.appendChild(flagCircle(item.flag))
      node.appendChild(codeLabel(item.code))
    }
    return node
  }

  function codeLabel(code) {
    const label = document.createElement("span")
    label.className = "team-code"
    label.textContent = code ?? ""
    return label
  }

  function flagCircle(flag) {
    const circle = document.createElement("span")
    circle.className = "flag-circle"
    const value = document.createElement("span")
    value.className = "flag-value"
    value.textContent = flag ?? ""
    circle.appendChild(value)
    return circle
  }

  function clickPayload(roundIndex, side, index) {
    if (roundIndex === 4) {
      const finalists = [rounds[4].left[0], rounds[4].right[0]]
      if (!finalists[0] || !finalists[1]) return null
      return { phase_key: "final", match_number: 1 }
    }

    const phaseKey = phases[roundIndex]
    const current = rounds[roundIndex][side]
    const matchInSide = Math.floor(index / 2)
    const pair = [current[matchInSide * 2], current[matchInSide * 2 + 1]]
    if (!phaseKey || !pair[0] || !pair[1]) return null
    const matchesPerSide = current.length / 2
    const matchNumber = matchInSide + 1 + (side === "right" ? matchesPerSide : 0)
    return { phase_key: phaseKey, match_number: matchNumber }
  }

  function currentWinner(phaseKey, matchNumber) {
    const phaseWinners = winnerArrays[phaseKey] ?? []
    return phaseWinners[matchNumber - 1] ?? null
  }

  function drawChampion(frameElement, championCode) {
    const area = document.createElement("div")
    area.className = "champion-area"
    if (!championCode) {
      const help = document.createElement("div")
      help.className = "champion-help"
      help.innerHTML = "Clique nos vencedores<br>de cada confronto<br>para fazer a sua simulação."
      const empty = document.createElement("div")
      empty.className = "bracket-empty-copy"
      empty.textContent = "A campeã aparece aqui."
      area.appendChild(help)
      area.appendChild(empty)
      frameElement.appendChild(area)
      return
    }

    const item = team(championCode)
    const trophy = document.createElement("div")
    trophy.className = "champion-trophy"
    trophy.textContent = "🏆"
    const championNode = document.createElement("div")
    championNode.className = "champion-node"
    championNode.appendChild(flagCircle(item.flag))
    const label = document.createElement("div")
    label.className = "champion-label"
    label.innerHTML = `Campeã<br>${item.name}`
    area.appendChild(trophy)
    area.appendChild(championNode)
    area.appendChild(label)
    frameElement.appendChild(area)
  }
}
"""

KNOCKOUT_BRACKET_COMPONENT = st.components.v2.component(
    "world_cup_knockout_bracket",
    html=BRACKET_HTML,
    css=BRACKET_CSS,
    js=BRACKET_JS,
)


def render_html(html: str) -> None:
    st.html(dedent(html))


def inject_styles() -> None:
    render_html(
        """
        <style>
        :root {
            --green: #3fa246;
            --green-dark: #2d7d32;
            --green-bright: #04b84b;
            --ink: #3e3e3e;
            --ink-strong: #111111;
            --muted: #8a8a8a;
            --line: #dddddd;
            --line-dark: #1f1f1f;
            --panel: #f3f3f3;
            --panel-soft: #eeeeee;
        }

        .stApp {
            background: #f7f7f7;
            color: var(--ink);
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        .block-container {
            max-width: 1180px;
            padding-top: 0;
            padding-bottom: 3rem;
        }

        .topbar {
            margin: 0 -2rem 2rem;
            background: var(--green);
            color: white;
            text-align: center;
            padding: 13px 16px;
            font-size: 15px;
            font-weight: 700;
            letter-spacing: 0;
        }

        .ad-box {
            height: 150px;
            background: #e6e6e6;
            margin: 0 auto 42px;
            max-width: 760px;
        }

        .hero h1 {
            color: var(--ink);
            font-size: 38px;
            line-height: 1.1;
            margin: 0 0 10px;
        }

        .hero p {
            color: var(--muted);
            font-size: 15px;
            max-width: 700px;
            margin-bottom: 24px;
        }

        .section-title {
            border-bottom: 2px solid var(--line);
            color: var(--ink);
            font-size: 22px;
            font-weight: 800;
            margin: 24px 0 16px;
            padding-bottom: 8px;
        }

        .group-shell {
            margin-bottom: 28px;
        }

        .group-heading {
            border-bottom: 2px solid var(--ink-strong);
            color: var(--ink-strong);
            font-size: 23px;
            font-weight: 900;
            line-height: 1;
            margin: 0 0 22px;
            padding-bottom: 13px;
            text-align: center;
        }

        .group-table-head {
            align-items: center;
            color: #737b82;
            display: flex;
            font-size: 13px;
            gap: 10px;
            min-height: 25px;
        }

        .group-position-head {
            justify-content: flex-end;
        }

        .group-position-head span {
            font-weight: 400;
            margin-right: 6px;
        }

        .group-position-head b {
            color: #6d7580;
            font-size: 13px;
            margin-left: 8px;
        }

        .team-band {
            align-items: center;
            background: var(--panel-soft);
            color: #050505;
            display: flex;
            font-size: 16px;
            gap: 12px;
            min-height: 46px;
            padding: 0 16px;
        }

        .team-band .flag {
            font-size: 21px;
            line-height: 1;
            width: 30px;
        }

        div[data-testid="stRadio"] {
            align-items: center;
            background: var(--panel-soft);
            display: flex;
            min-height: 46px;
            padding: 0 8px;
        }

        div[data-testid="stRadio"] > label {
            display: none;
        }

        div[data-testid="stRadio"] [role="radiogroup"] {
            display: flex;
            gap: 8px;
            justify-content: flex-end;
            width: 100%;
        }

        div[data-testid="stRadio"] label[data-baseweb="radio"] {
            margin: 0;
            min-width: 32px;
        }

        div[data-testid="stRadio"] label[data-baseweb="radio"] p {
            color: #6d7580;
            font-size: 12px;
            font-weight: 800;
        }

        .random-copy {
            align-items: center;
            display: flex;
            gap: 8px;
            justify-content: center;
            text-transform: uppercase;
        }

        .qualified-box {
            background: #eeeeee;
            border-left: 4px solid var(--green);
            color: #555;
            font-size: 14px;
            line-height: 1.55;
            padding: 14px 18px;
        }

        .seed-board {
            align-items: stretch;
            background: #ffffff;
            border: 1px solid var(--line);
            display: grid;
            gap: 18px;
            grid-template-columns: 1fr 190px 1fr;
            margin: 18px 0 26px;
            min-height: 430px;
            padding: 18px;
        }

        .seed-side {
            display: grid;
            gap: 8px;
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }

        .seed-node {
            align-items: center;
            background: #f5f5f5;
            border: 2px solid #d4d4d4;
            border-radius: 999px;
            color: #555;
            display: flex;
            font-size: 12px;
            gap: 6px;
            min-height: 42px;
            min-width: 0;
            overflow: hidden;
            padding: 0 12px;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .seed-center {
            align-items: center;
            color: var(--green-bright);
            display: flex;
            flex-direction: column;
            font-size: 13px;
            font-style: italic;
            font-weight: 900;
            justify-content: center;
            line-height: 1.75;
            text-align: center;
        }

        .seed-center-mark {
            color: var(--green-bright);
            font-size: 52px;
            font-style: normal;
            font-weight: 900;
            line-height: 1;
            margin-top: 28px;
        }

        .phase-heading {
            color: var(--ink);
            font-size: 18px;
            font-weight: 800;
            margin: 20px 0 10px;
        }

        .match-title {
            color: var(--green-dark);
            font-size: 12px;
            font-weight: 800;
            margin-bottom: 7px;
            text-transform: uppercase;
        }

        .match-card-copy {
            color: #626262;
            font-size: 12px;
            line-height: 1.4;
            margin: -2px 0 10px;
            min-height: 34px;
        }

        .phase-status {
            color: var(--muted);
            font-size: 13px;
            margin: 4px 0 14px;
        }

        .champion-box {
            background: var(--green);
            border-radius: 4px;
            color: white;
            font-size: 18px;
            font-weight: 800;
            margin: 18px 0 8px;
            padding: 16px 18px;
            text-align: center;
        }

        .footer-note {
            border-top: 1px solid var(--line);
            color: var(--muted);
            font-size: 12px;
            margin-top: 28px;
            padding-top: 18px;
            text-align: center;
        }

        div.stButton > button {
            border: 1px solid var(--green-bright);
            border-radius: 4px;
            color: var(--green-dark);
            font-weight: 800;
            min-height: 44px;
            transition: background .15s ease, border-color .15s ease, color .15s ease;
        }

        div.stButton > button:hover {
            background: #e9f8ee;
            border-color: var(--green-dark);
            color: var(--green-dark);
        }

        div.stButton > button[kind="primary"],
        div.stButton > button[data-testid="stBaseButton-primary"] {
            background: var(--green-dark);
            border-color: var(--green-dark);
            color: white;
        }

        div.stButton > button[kind="primary"]:hover,
        div.stButton > button[data-testid="stBaseButton-primary"]:hover {
            background: var(--green-bright);
            border-color: var(--green-bright);
            color: white;
        }

        @media (max-width: 760px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            .topbar {
                margin-left: -1rem;
                margin-right: -1rem;
            }
            .hero h1 {
                font-size: 30px;
            }
            .seed-board {
                grid-template-columns: 1fr;
                min-height: auto;
            }
            .seed-side {
                grid-template-columns: 1fr;
            }
            .seed-center {
                order: -1;
            }
        }
        </style>
        """
    )


def team_label(code: str) -> str:
    team = team_lookup()[code]
    return f"{team.flag} {team.name}"


def find_group(group_code: str) -> Group:
    return next(group for group in GROUPS if group.code == group_code)


def group_rank_key(group_code: str, team_code: str) -> str:
    return f"group_{group_code}_{team_code}_position"


def knockout_key(phase_key: str, match_number: int) -> str:
    return f"knockout_{phase_key}_{match_number}"


def clear_knockout_state(start_phase_key: str | None = None) -> None:
    phase_keys = [phase_key for phase_key, _phase_label in KNOCKOUT_PHASES]
    if start_phase_key is None:
        phases_to_clear = set(phase_keys)
    else:
        start_index = phase_keys.index(start_phase_key) + 1
        phases_to_clear = set(phase_keys[start_index:])

    for key in list(st.session_state):
        if not str(key).startswith("knockout_"):
            continue
        if any(str(key).startswith(f"knockout_{phase_key}_") for phase_key in phases_to_clear):
            del st.session_state[key]


def sync_group_position(group_code: str, team_code: str) -> None:
    selected_label = st.session_state.get(group_rank_key(group_code, team_code))
    if selected_label is None:
        clear_knockout_state()
        return

    group = find_group(group_code)
    for other_team in group.teams:
        if other_team.code == team_code:
            continue
        other_key = group_rank_key(group_code, other_team.code)
        if st.session_state.get(other_key) == selected_label:
            st.session_state[other_key] = None

    clear_knockout_state()


def randomize_group(group_code: str) -> None:
    group = find_group(group_code)
    shuffled_codes = [team.code for team in group.teams]
    random.shuffle(shuffled_codes)

    for team in group.teams:
        st.session_state[group_rank_key(group_code, team.code)] = None
    for team_code, label in zip(shuffled_codes[:2], GROUP_POSITION_LABELS):
        st.session_state[group_rank_key(group_code, team_code)] = label

    clear_knockout_state()


def group_selection(group: Group) -> dict[str, str | None]:
    selection = {key: None for key, _label in GROUP_POSITION_OPTIONS}
    for team in group.teams:
        selected_label = st.session_state.get(group_rank_key(group.code, team.code))
        if selected_label in GROUP_POSITION_BY_LABEL:
            selection[GROUP_POSITION_BY_LABEL[selected_label]] = team.code
    return selection


def render_group_selector(group: Group) -> dict[str, str | None]:
    render_html(
        f"""
        <div class="group-shell">
            <div class="group-heading">Grupo {group.code}</div>
        </div>
        """
    )
    header_cols = st.columns([1.45, 1], vertical_alignment="center", gap="small")
    with header_cols[0]:
        render_html('<div class="group-table-head">Seleção</div>')
    with header_cols[1]:
        render_html(
            """
            <div class="group-table-head group-position-head">
                <span>Posição:</span><b>1º</b><b>2º</b>
            </div>
            """
        )

    for team in group.teams:
        row_cols = st.columns([1.45, 1], vertical_alignment="center", gap="small")
        with row_cols[0]:
            render_html(
                f"""
                <div class="team-band">
                    <span class="flag">{team.flag}</span>
                    <span>{team.name}</span>
                </div>
                """
            )
        with row_cols[1]:
            st.radio(
                f"{team.name} no Grupo {group.code}",
                GROUP_POSITION_LABELS,
                index=None,
                key=group_rank_key(group.code, team.code),
                horizontal=True,
                label_visibility="collapsed",
                on_change=sync_group_position,
                args=(group.code, team.code),
                width="stretch",
            )

    st.button(
        "SORTEIO ALEATÓRIO",
        key=f"randomize_group_{group.code}",
        icon=":material/shuffle:",
        on_click=randomize_group,
        args=(group.code,),
        type="primary",
        width="stretch",
    )
    return group_selection(group)


def render_qualified(qualified: dict[str, list[dict[str, str]]]) -> None:
    thirds = ", ".join(f"{team['flag']} {team['name']}" for team in qualified["thirds"])
    render_html(
        f"""
        <div class="qualified-box">
            <strong>Terceiros sorteados automaticamente para completar os 32 classificados:</strong><br>
            {thirds}
        </div>
        """
    )


def set_knockout_winner(phase_key: str, match_number: int, winner_code: str) -> None:
    st.session_state[knockout_key(phase_key, match_number)] = winner_code
    clear_knockout_state(start_phase_key=phase_key)


def read_component_pick() -> dict[str, object] | None:
    component_state = st.session_state.get("knockout_bracket_component")
    pick = getattr(component_state, "pick", None)
    if pick is None and isinstance(component_state, dict):
        pick = component_state.get("pick")
    return pick if isinstance(pick, dict) else None


def handle_bracket_pick() -> None:
    pick = read_component_pick()
    if not pick:
        return

    phase_key = str(pick.get("phase_key", ""))
    winner_code = str(pick.get("winner_code", ""))
    try:
        match_number = int(pick.get("match_number", 0))
    except (TypeError, ValueError):
        return

    valid_phase_keys = {phase_key for phase_key, _phase_label in KNOCKOUT_PHASES}
    if phase_key in valid_phase_keys and match_number > 0 and winner_code:
        set_knockout_winner(phase_key, match_number, winner_code)


def build_knockout_state(initial_codes: list[str]) -> dict[str, list[str | None]]:
    winners_by_phase: dict[str, list[str | None]] = {}
    current_codes = initial_codes

    for phase_key, _phase_label in KNOCKOUT_PHASES:
        matches = build_knockout_matches(current_codes)
        phase_winners: list[str | None] = []

        for match_number, (team_a, team_b) in enumerate(matches, start=1):
            state_key = knockout_key(phase_key, match_number)
            selected = st.session_state.get(state_key)
            if selected not in (team_a, team_b):
                selected = None
                st.session_state.pop(state_key, None)
            phase_winners.append(selected if isinstance(selected, str) else None)

        winners_by_phase[phase_key] = phase_winners
        if any(winner is None for winner in phase_winners):
            break
        current_codes = [winner for winner in phase_winners if winner is not None]

    return winners_by_phase


def component_winners(winners_by_phase: dict[str, list[str | None]]) -> dict[str, list[str | None]]:
    lengths = {
        "dezesseis_avos": 16,
        "oitavas": 8,
        "quartas": 4,
        "semifinais": 2,
        "final": 1,
    }
    return {
        phase_key: [
            *(winners_by_phase.get(phase_key, [])),
            *([None] * lengths[phase_key]),
        ][: lengths[phase_key]]
        for phase_key, _phase_label in KNOCKOUT_PHASES
    }


def teams_payload() -> dict[str, dict[str, str]]:
    return {
        code: {"code": team.code, "name": team.name, "flag": team.flag}
        for code, team in team_lookup().items()
    }


def render_knockout(initial_codes: list[str]) -> dict[str, list[str | None]]:
    winners_by_phase = build_knockout_state(initial_codes)
    KNOCKOUT_BRACKET_COMPONENT(
        key="knockout_bracket_component",
        data={
            "initial": initial_codes,
            "phases": [phase_key for phase_key, _phase_label in KNOCKOUT_PHASES],
            "winners": component_winners(winners_by_phase),
            "teams": teams_payload(),
        },
        height=850,
        on_pick_change=handle_bracket_pick,
    )
    return winners_by_phase


def main() -> None:
    inject_styles()
    render_html('<div class="topbar">COPA DO MUNDO DA FIFA 2026</div>')
    render_html('<div class="ad-box"></div>')
    render_html(
        """
        <div class="hero">
            <h1>Bolão da Copa do Mundo 2026</h1>
            <p>Preencha seus dados, escolha 1º e 2º colocados de cada grupo e complete o mata-mata clicando nas seleções da chave. Os oito melhores terceiros serão sorteados automaticamente.</p>
        </div>
        """
    )

    render_html('<div class="section-title">Participante</div>')
    col_name, col_phone, col_email = st.columns([1.2, 0.8, 1.2])
    with col_name:
        name = st.text_input("Nome")
    with col_phone:
        phone = st.text_input("Telefone")
    with col_email:
        email = st.text_input("E-mail")

    render_html('<div class="section-title">Grupos</div>')
    selections: dict[str, dict[str, str | None]] = {}
    for row_start in range(0, len(GROUPS), 3):
        cols = st.columns(3)
        for col, group in zip(cols, GROUPS[row_start : row_start + 3]):
            with col:
                selections[group.code] = render_group_selector(group)

    participant_errors = validate_participant(name, phone, email)
    selection_errors = validate_selections(selections)
    knockout_winners: dict[str, list[str | None]] = {}
    initial_codes: list[str] = []

    render_html('<div class="section-title">Classificados</div>')
    qualified = None
    if not selection_errors:
        qualified = build_qualified(selections, seed=2026)
        render_qualified(qualified)
        render_html('<div class="section-title">Mata-mata</div>')
        initial_codes = [team["code"] for team in qualified["all"]]
        knockout_winners = render_knockout(initial_codes)
    else:
        st.info("Complete 1º e 2º lugar em todos os grupos para ver os classificados.")

    submitted = st.button("Salvar palpite", icon=":material/save:", type="primary", width="stretch")

    if submitted:
        knockout_errors = validate_knockout(initial_codes, knockout_winners) if initial_codes else []
        errors = [*participant_errors, *selection_errors, *knockout_errors]
        if errors:
            for error in errors:
                st.error(error)
            return

        if qualified is None:
            qualified = build_qualified(selections, seed=2026)
            initial_codes = [team["code"] for team in qualified["all"]]

        knockout = serialize_knockout(initial_codes, knockout_winners)

        payload = {
            "nome": name.strip(),
            "telefone": phone.strip(),
            "email": email.strip().lower(),
            "selecoes": serialize_selections(selections),
            "terceiros_sorteados": qualified["thirds"],
            "classificados": qualified["all"],
            "mata_mata": {phase_key: knockout[phase_key] for phase_key, _phase_label in KNOCKOUT_PHASES},
            "campeao": knockout["campeao"],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        ok, message = save_bet(payload)
        if ok:
            st.success(message)
        else:
            st.warning(message)

    render_html(
        '<div class="footer-note">Projeto educacional em Streamlit. Dados oficiais podem ser atualizados em src/groups.py.</div>'
    )


if __name__ == "__main__":
    main()
