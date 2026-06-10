from __future__ import annotations

import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.groups import GROUPS, Group, team_lookup
from src.rules import (
    KNOCKOUT_PHASES,
    build_knockout_matches,
    build_official_knockout_order,
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
ACTIVE_GROUP_KEY = "active_group_code"
KNOCKOUT_SCROLL_KEY = "knockout_scroll_left"


st.set_page_config(
    page_title="Bolao Copa 2026",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)


GROUPS_SELECTOR_HTML = '<div id="world-cup-groups-selector"></div>'

GROUPS_SELECTOR_CSS = """
#world-cup-groups-selector {
    color: #111111;
    font-family: Arial, Helvetica, sans-serif;
}

.groups-picker {
    width: 100%;
}

.groups-tabs {
    display: none;
}

.groups-track {
    display: grid;
    gap: 28px 24px;
    grid-template-columns: repeat(3, minmax(0, 1fr));
}

.group-card {
    min-width: 0;
}

.group-card-heading {
    border-bottom: 2px solid #111111;
    color: #111111;
    font-size: 23px;
    font-weight: 900;
    line-height: 1;
    margin: 0 0 14px;
    padding-bottom: 13px;
    text-align: center;
}

.group-card-head,
.group-card-row {
    align-items: center;
    display: grid;
    gap: 8px;
    grid-template-columns: minmax(0, 1fr) 104px;
}

.group-card-head {
    color: #737b82;
    font-size: 13px;
    min-height: 25px;
}

.group-position-title {
    line-height: 1.2;
}

.group-position-head {
    align-items: center;
    display: grid;
    gap: 6px;
    grid-template-columns: 1fr 1fr;
    text-align: center;
}

.group-position-head b {
    color: #6d7580;
    font-size: 13px;
}

.group-card-list {
    display: grid;
    gap: 6px;
}

.group-team {
    align-items: center;
    background: #eeeeee;
    color: #050505;
    display: flex;
    font-size: 16px;
    gap: 10px;
    min-height: 46px;
    min-width: 0;
    padding: 0 12px;
}

.group-flag {
    flex: 0 0 28px;
    font-size: 21px;
    line-height: 1;
}

.flag-art {
    border: 1px solid rgba(0, 0, 0, .18);
    border-radius: 2px;
    display: inline-block;
    overflow: hidden;
    position: relative;
}

.group-flag .flag-art {
    height: 18px;
    width: 28px;
}

.flag-circle .flag-art {
    height: calc(var(--node-size) * .34);
    width: calc(var(--node-size) * .52);
}

.flag-england {
    background: #ffffff;
}

.flag-england::before,
.flag-england::after,
.flag-scotland::before {
    content: "";
    position: absolute;
}

.flag-england::before {
    background: #cf142b;
    height: 28%;
    left: 0;
    top: 36%;
    width: 100%;
}

.flag-england::after {
    background: #cf142b;
    height: 100%;
    left: 42%;
    top: 0;
    width: 16%;
}

.flag-scotland {
    background: #005eb8;
}

.flag-scotland::before {
    background:
        linear-gradient(to bottom right, transparent 43%, #ffffff 43%, #ffffff 57%, transparent 57%),
        linear-gradient(to top right, transparent 43%, #ffffff 43%, #ffffff 57%, transparent 57%);
    inset: 0;
}

.group-name {
    line-height: 1.15;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.group-options {
    background: #eeeeee;
    display: grid;
    gap: 6px;
    grid-template-columns: 1fr 1fr;
    min-height: 46px;
    padding: 4px;
}

.group-option {
    appearance: none;
    background: transparent;
    border: 0;
    cursor: pointer;
    display: grid;
    min-height: 38px;
    padding: 0;
    place-items: center;
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;
}

.group-option-circle {
    background: #eeeeee;
    border: 3px solid #04ad50;
    border-radius: 999px;
    display: block;
    height: 34px;
    position: relative;
    width: 34px;
}

.group-option.selected .group-option-circle::after {
    background: #04ad50;
    border-radius: 999px;
    content: "";
    height: 18px;
    left: 50%;
    position: absolute;
    top: 50%;
    transform: translate(-50%, -50%);
    width: 18px;
}

.group-option:hover .group-option-circle,
.group-option:focus-visible .group-option-circle {
    box-shadow: 0 0 0 4px rgba(4, 173, 80, .16);
}

.group-random {
    align-items: center;
    appearance: none;
    background: #08ad4e;
    border: 0;
    border-radius: 4px;
    color: #6d7580;
    cursor: pointer;
    display: flex;
    gap: 10px;
    justify-content: center;
    margin-top: 12px;
    min-height: 58px;
    padding: 0 18px;
    touch-action: manipulation;
    width: 100%;
    -webkit-tap-highlight-color: transparent;
}

.group-random-icon {
    color: #ffffff;
    font-size: 28px;
    font-weight: 800;
    line-height: 1;
}

.group-random-text {
    color: #ffffff;
    font-size: 16px;
    font-weight: 400;
    letter-spacing: 0;
    text-transform: uppercase;
}

@media (max-width: 760px) {
    .groups-picker {
        margin-left: -1rem;
        margin-right: -1rem;
        overflow: hidden;
    }

    .groups-tabs {
        border-bottom: 1px solid #dddddd;
        display: flex;
        gap: 0;
        margin: 2px 0 28px;
        min-width: max-content;
        overflow-x: auto;
        padding: 0 1rem;
        scrollbar-width: none;
    }

    .groups-tabs::-webkit-scrollbar {
        display: none;
    }

    .group-tab {
        appearance: none;
        background: transparent;
        border: 0;
        border-radius: 12px 12px 0 0;
        color: #2f2f2f;
        cursor: pointer;
        flex: 0 0 48px;
        font-size: 28px;
        font-weight: 400;
        height: 58px;
        padding: 0;
        position: relative;
        touch-action: manipulation;
    }

    .group-tab.active {
        background: #f1f1f1;
        font-weight: 800;
    }

    .group-tab.active::after {
        background: #08ad4e;
        bottom: 0;
        content: "";
        height: 3px;
        left: 0;
        position: absolute;
        right: 0;
    }

    .groups-track {
        display: flex;
        gap: 16px;
        overflow-x: auto;
        overflow-y: visible;
        padding: 0 1rem 10px;
        scroll-padding-left: 1rem;
        scroll-snap-type: x mandatory;
        -webkit-overflow-scrolling: touch;
    }

    .group-card {
        flex: 0 0 min(86vw, 360px);
        scroll-snap-align: start;
    }

    .group-card-heading {
        display: none;
    }

    .group-card-head {
        gap: 10px;
        grid-template-columns: minmax(0, 1fr) 104px;
        margin-bottom: 8px;
    }

    .group-card-head,
    .group-position-head b {
        font-size: 18px;
    }

    .group-position-title {
        max-width: 92px;
    }

    .group-card-row {
        gap: 0;
        grid-template-columns: minmax(0, 1fr) 104px;
    }

    .group-team {
        font-size: 24px;
        min-height: 74px;
        padding: 0 14px;
    }

    .group-flag {
        flex-basis: 44px;
        font-size: 27px;
    }

    .group-flag .flag-art {
        height: 24px;
        width: 36px;
    }

    .group-name {
        overflow: visible;
        text-overflow: clip;
        white-space: normal;
    }

    .group-options {
        gap: 4px;
        min-height: 74px;
        padding: 0 8px 0 0;
    }

    .group-option-circle {
        border-width: 4px;
        height: 34px;
        width: 34px;
    }

    .group-random {
        border-radius: 4px;
        margin-top: 12px;
        min-height: 66px;
    }

    .group-random-text {
        font-size: 20px;
    }

    .group-random-icon {
        font-size: 30px;
    }
}
"""

GROUPS_SELECTOR_JS = """
export default function (component) {
  const { data, parentElement, setTriggerValue } = component
  const root = parentElement.querySelector("#world-cup-groups-selector")
  if (!root || !data) return

  const groups = Array.isArray(data.groups) ? data.groups : []
  const positions = Array.isArray(data.positions) ? data.positions : []
  const selectedByGroup = data.selected_by_group ?? {}
  const currentGroup = groups.some((group) => group.code === data.current_group)
    ? data.current_group
    : groups[0]?.code

  root.innerHTML = ""

  const picker = el("div", "groups-picker")
  const tabs = el("div", "groups-tabs")
  const track = el("div", "groups-track")

  groups.forEach((group, index) => {
    const tab = el("button", ["group-tab", group.code === currentGroup ? "active" : ""])
    tab.type = "button"
    tab.textContent = group.code ?? ""
    tab.onclick = () => {
      root.querySelectorAll(".group-tab").forEach((item) => item.classList.remove("active"))
      tab.classList.add("active")
      root.querySelector(`#group-card-${group.code}`)?.scrollIntoView({
        behavior: "smooth",
        block: "nearest",
        inline: "start",
      })
    }
    tabs.appendChild(tab)
    track.appendChild(groupCard(group, positions, selectedByGroup[group.code] ?? {}))
  })

  picker.appendChild(tabs)
  picker.appendChild(track)
  root.appendChild(picker)
  requestAnimationFrame(() => scrollToGroup(currentGroup))

  function groupCard(group, positionLabels, selectedByTeam) {
    const card = el("div", "group-card")
    card.id = `group-card-${group.code}`

    const heading = el("div", "group-card-heading")
    heading.textContent = `Grupo ${group.code ?? ""}`
    card.appendChild(heading)

    const head = el("div", "group-card-head")
    const selectionHead = el("div")
    selectionHead.textContent = "Seleção"
    head.appendChild(selectionHead)

    const positionWrap = el("div")
    const title = el("div", "group-position-title")
    title.textContent = "Posição no grupo:"
    const positionHead = el("div", "group-position-head")
    for (const label of positionLabels) {
      const item = el("b")
      item.textContent = label
      positionHead.appendChild(item)
    }
    positionWrap.appendChild(title)
    positionWrap.appendChild(positionHead)
    head.appendChild(positionWrap)
    card.appendChild(head)

    const list = el("div", "group-card-list")
    for (const team of group.teams ?? []) {
      list.appendChild(teamRow(group.code, team, positionLabels, selectedByTeam[team.code]))
    }
    card.appendChild(list)

    const random = el("button", "group-random")
    random.type = "button"
    random.setAttribute("aria-label", `Sorteio aleatório do Grupo ${group.code}`)
    random.onclick = () => {
      setTriggerValue("action", {
        action: "randomize",
        group_code: group.code,
        nonce: Date.now(),
      })
    }
    const icon = el("span", "group-random-icon")
    icon.textContent = "↝"
    const copy = el("span", "group-random-text")
    copy.textContent = "Sorteio aleatório"
    random.appendChild(icon)
    random.appendChild(copy)
    card.appendChild(random)
    return card
  }

  function teamRow(groupCode, team, positionLabels, selectedLabel) {
    const row = el("div", "group-card-row")

    const teamCell = el("div", "group-team")

    const flag = el("span", "group-flag")
    flag.appendChild(flagContent(team.flag, team.code))
    teamCell.appendChild(flag)

    const name = el("span", "group-name")
    name.textContent = team.name ?? team.code ?? ""
    teamCell.appendChild(name)
    row.appendChild(teamCell)

    const options = el("div", "group-options")
    options.setAttribute("role", "radiogroup")
    options.setAttribute("aria-label", `${team.name ?? team.code} no grupo`)

    for (const label of positionLabels) {
      const option = el("button")
      const selected = selectedLabel === label
      option.className = ["group-option", selected ? "selected" : ""].filter(Boolean).join(" ")
      option.type = "button"
      option.setAttribute("aria-pressed", selected ? "true" : "false")
      option.setAttribute("aria-label", `${team.name ?? team.code} em ${label} lugar`)
      option.appendChild(el("span", "group-option-circle"))
      option.onclick = () => {
        setTriggerValue("action", {
          action: "pick",
          group_code: groupCode,
          team_code: team.code,
          selected_label: label,
          nonce: Date.now(),
        })
      }
      options.appendChild(option)
    }

    row.appendChild(options)
    return row
  }

  function el(tagName, className) {
    const node = document.createElement(tagName)
    if (Array.isArray(className)) {
      node.className = className.filter(Boolean).join(" ")
    } else if (className) {
      node.className = className
    }
    return node
  }

  function scrollToGroup(groupCode) {
    if (!groupCode || !window.matchMedia("(max-width: 760px)").matches) return

    const card = root.querySelector(`#group-card-${groupCode}`)
    if (card) {
      track.scrollLeft = card.offsetLeft - track.offsetLeft
    }

    const activeTab = Array.from(root.querySelectorAll(".group-tab"))
      .find((tab) => tab.textContent === groupCode)
    if (activeTab) {
      tabs.scrollLeft = activeTab.offsetLeft - tabs.offsetLeft - 16
    }
  }
}
"""

GROUPS_SELECTOR_COMPONENT = st.components.v2.component(
    "world_cup_groups_selector",
    html=GROUPS_SELECTOR_HTML,
    css=GROUPS_SELECTOR_CSS,
    js=GROUPS_SELECTOR_JS,
)


BRACKET_HTML = '<div id="world-cup-bracket"></div>'

BRACKET_CSS = """
#world-cup-bracket {
    font-family: Arial, Helvetica, sans-serif;
}

.bracket-scroll {
    background: #ffffff;
    border: 1px solid #e6e6e6;
    overflow: visible;
    width: 100%;
}

.bracket-frame {
    background: #ffffff;
    height: 820px;
    margin: 0 auto;
    min-width: 0;
    position: relative;
    width: min(1020px, 100%);
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
    appearance: none;
    background: transparent;
    border: 0;
    color: #1f2a33;
    display: flex;
    gap: 6px;
    min-height: max(44px, var(--node-size));
    padding: 0;
    position: absolute;
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;
    z-index: 2;
}

.bracket-node.left {
    transform: translate(calc(-100% + var(--node-size) / 2), -50%);
}

.bracket-node.right {
    transform: translate(calc(var(--node-size) / -2), -50%);
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
    pointer-events: none;
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
    pointer-events: none;
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

.mobile-bracket-node,
.mobile-champion-node {
    --node-size: 52px;
    align-items: center;
    appearance: none;
    background: transparent;
    border: 0;
    display: flex;
    justify-content: center;
    min-height: max(44px, var(--node-size));
    min-width: max(44px, var(--node-size));
    padding: 0;
    position: absolute;
    transform: translate(-50%, -50%);
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;
    z-index: 2;
}

.mobile-bracket-node.selectable {
    cursor: pointer;
}

.mobile-bracket-node .flag-circle,
.mobile-champion-node .flag-circle {
    background: #f5f5f5;
    border-color: #d2d2d2;
    box-shadow: none;
}

.mobile-bracket-node.filled .flag-circle {
    background: #ffffff;
}

.mobile-bracket-node.selected .flag-circle {
    border-color: #05bd4c;
    box-shadow: 0 0 0 4px rgba(5, 189, 76, .16);
}

.mobile-bracket-node:focus-visible .flag-circle {
    outline: 3px solid rgba(5, 189, 76, .28);
    outline-offset: 3px;
}

.mobile-seed-label {
    color: #8a8a8a;
    font-size: 20px;
    font-weight: 600;
    left: 50%;
    line-height: 1;
    position: absolute;
    transform: translateX(-50%);
    white-space: nowrap;
}

.mobile-seed-label.top {
    bottom: calc(100% + 9px);
}

.mobile-seed-label.bottom {
    top: calc(100% + 9px);
}

.mobile-help {
    color: #05bd4c;
    font-size: 24px;
    font-style: italic;
    font-weight: 900;
    left: 29%;
    line-height: 1.55;
    position: absolute;
    text-align: center;
    top: 49%;
    transform: translate(-50%, -50%);
    z-index: 3;
}

.mobile-champion-area {
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

.mobile-trophy {
    color: #cfcfcf;
    font-size: 62px;
    line-height: 1;
    pointer-events: none;
}

@media (max-width: 760px) {
    .bracket-scroll {
        border: 0;
        margin-left: -1rem;
        margin-right: -1rem;
        overflow-x: auto;
        overflow-y: hidden;
        padding: 0 1rem;
        -webkit-overflow-scrolling: touch;
    }

    .bracket-frame {
        height: 1260px;
        margin: 0;
        min-width: 980px;
        width: 980px;
    }

    .bracket-node {
        --node-size: var(--node-size-mobile, 32px);
        gap: 0;
        min-height: 40px;
        min-width: 40px;
    }

    .team-code {
        display: none;
    }

    .champion-area {
        max-width: 90px;
    }

    .champion-help {
        font-size: 11px;
        line-height: 1.45;
        margin-bottom: 18px;
    }

    .champion-trophy {
        font-size: 34px;
        margin-bottom: 4px;
    }

    .champion-label {
        font-size: 13px;
    }

    .champion-node {
        --node-size: 50px;
    }

    .champion-node .flag-circle {
        font-size: 28px;
    }

    .bracket-empty-copy {
        font-size: 11px;
    }

    .mobile-bracket-node {
        --node-size: var(--mobile-node-size, 52px);
    }

    .mobile-bracket-node .flag-circle,
    .mobile-champion-node .flag-circle {
        font-size: calc(var(--node-size) * .52);
    }

    .mobile-champion-node {
        --node-size: 116px;
        position: static;
        transform: none;
    }
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
  const initialLabels = normalizeArray(data.initial_labels, 32)
  const scrollLeft = Number(data.scroll_left ?? 0)
  const winners = data.winners ?? {}
  const winnerArrays = {
    dezesseis_avos: normalizeArray(winners.dezesseis_avos, 16),
    oitavas: normalizeArray(winners.oitavas, 8),
    quartas: normalizeArray(winners.quartas, 4),
    semifinais: normalizeArray(winners.semifinais, 2),
    final: normalizeArray(winners.final, 1),
  }

  const compact = root.getBoundingClientRect().width < 700
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

  if (compact) {
    drawMobileBracket(scroll)
    root.appendChild(scroll)
    restoreScroll(scroll)
    return
  }

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
  restoreScroll(scroll)

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

  function mobileXPositions(count) {
    if (count === 1) return [50]
    return Array.from({ length: count }, (_, index) => 4 + index * (92 / (count - 1)))
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
          scroll_left: scroll.scrollLeft,
          nonce: Date.now(),
        })
      }
    }

    const item = team(code)
    if (side === "left") {
      node.appendChild(codeLabel(item.code))
      node.appendChild(flagCircle(item.flag, item.code))
    } else {
      node.appendChild(flagCircle(item.flag, item.code))
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

  function flagCircle(flag, code = "") {
    const circle = document.createElement("span")
    circle.className = "flag-circle"
    circle.appendChild(flagContent(flag, code))
    return circle
  }

  function flagContent(flag, code = "") {
    const custom = customFlag(code)
    if (custom) return custom

    const value = document.createElement("span")
    value.className = "flag-value"
    value.textContent = flag ?? ""
    return value
  }

  function customFlag(code = "") {
    const normalized = String(code ?? "").toUpperCase()
    if (normalized !== "ENG" && normalized !== "SCO") return null

    const value = document.createElement("span")
    value.className = `flag-value flag-art ${normalized === "ENG" ? "flag-england" : "flag-scotland"}`
    value.setAttribute("aria-hidden", "true")
    return value
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

  function drawMobileBracket(scrollElement) {
    const frame = document.createElement("div")
    frame.className = "bracket-frame mobile-bracket-frame"

    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
    svg.setAttribute("class", "connector-layer")
    svg.setAttribute("viewBox", "0 0 100 100")
    svg.setAttribute("preserveAspectRatio", "none")

    const mobileRounds = {
      top: [
        normalizeArray(initial.slice(0, 16), 16),
        winnerArrays.dezesseis_avos.slice(0, 8),
        winnerArrays.oitavas.slice(0, 4),
        winnerArrays.quartas.slice(0, 2),
        winnerArrays.semifinais.slice(0, 1),
      ],
      bottom: [
        normalizeArray(initial.slice(16, 32), 16),
        winnerArrays.dezesseis_avos.slice(8, 16),
        winnerArrays.oitavas.slice(4, 8),
        winnerArrays.quartas.slice(2, 4),
        winnerArrays.semifinais.slice(1, 2),
      ],
    }
    const yBySide = {
      top: [7, 15, 25, 35, 43],
      bottom: [93, 85, 75, 65, 57],
    }
    const sizes = [48, 58, 66, 82, 76]

    for (const side of ["top", "bottom"]) {
      for (let roundIndex = 0; roundIndex < 4; roundIndex += 1) {
        const current = mobileRounds[side][roundIndex]
        const next = mobileRounds[side][roundIndex + 1]
        for (let matchIndex = 0; matchIndex < current.length / 2; matchIndex += 1) {
          const first = mobileCoords(mobileRounds, yBySide, roundIndex, side, matchIndex * 2)
          const second = mobileCoords(mobileRounds, yBySide, roundIndex, side, matchIndex * 2 + 1)
          const target = mobileCoords(mobileRounds, yBySide, roundIndex + 1, side, matchIndex)
          const active = Boolean(next[matchIndex])
          appendMobileConnector(svg, first, target, active)
          appendMobileConnector(svg, second, target, active)
        }
      }
    }

    const topFinalist = mobileRounds.top[4][0]
    const bottomFinalist = mobileRounds.bottom[4][0]
    const champion = winnerArrays.final[0]
    appendMobileConnector(svg, mobileCoords(mobileRounds, yBySide, 4, "top", 0), { x: 50, y: 50 }, Boolean(champion && topFinalist))
    appendMobileConnector(svg, mobileCoords(mobileRounds, yBySide, 4, "bottom", 0), { x: 50, y: 50 }, Boolean(champion && bottomFinalist))

    frame.appendChild(svg)

    for (const side of ["top", "bottom"]) {
      for (let roundIndex = 0; roundIndex < mobileRounds[side].length; roundIndex += 1) {
        const values = mobileRounds[side][roundIndex]
        values.forEach((code, index) => {
          const labelIndex = side === "top" ? index : index + 16
          frame.appendChild(
            createMobileNode(
              code,
              roundIndex,
              side,
              index,
              mobileCoords(mobileRounds, yBySide, roundIndex, side, index),
              sizes[roundIndex],
              roundIndex === 0 ? initialLabels[labelIndex] : "",
              mobileRounds,
            )
          )
        })
      }
    }

    drawMobileChampion(frame, champion)
    scrollElement.appendChild(frame)
  }

  function mobileCoords(mobileRounds, yBySide, roundIndex, side, index) {
    return {
      x: mobileXPositions(mobileRounds[side][roundIndex].length)[index],
      y: yBySide[side][roundIndex],
    }
  }

  function appendMobileConnector(svgElement, start, end, active) {
    const elbowY = (start.y + end.y) / 2
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path")
    path.setAttribute("d", `M ${start.x} ${start.y} V ${elbowY} H ${end.x} V ${end.y}`)
    if (active) path.setAttribute("class", "active")
    svgElement.appendChild(path)
  }

  function createMobileNode(code, roundIndex, side, index, position, size, seedLabel, mobileRounds) {
    const clickInfo = mobileClickPayload(roundIndex, side, index, mobileRounds)
    const isSelectable = Boolean(code && clickInfo)
    const selected = Boolean(clickInfo && currentWinner(clickInfo.phase_key, clickInfo.match_number) === code)
    const node = document.createElement(isSelectable ? "button" : "div")
    node.className = [
      "mobile-bracket-node",
      side,
      code ? "filled" : "placeholder",
      isSelectable ? "selectable" : "",
      selected ? "selected" : "",
    ].filter(Boolean).join(" ")
    node.style.left = `${position.x}%`
    node.style.top = `${position.y}%`
    node.style.setProperty("--mobile-node-size", `${size}px`)

    if (isSelectable) {
      const item = team(code)
      node.type = "button"
      node.title = `Escolher ${item.name}`
      node.setAttribute("aria-label", `Escolher ${item.name}`)
      node.onclick = () => {
        setTriggerValue("pick", {
          ...clickInfo,
          winner_code: code,
          scroll_left: scroll.scrollLeft,
          nonce: Date.now(),
        })
      }
    }

    if (seedLabel) {
      const label = document.createElement("span")
      label.className = `mobile-seed-label ${side}`
      label.textContent = seedLabel
      node.appendChild(label)
    }

    const item = team(code)
    node.appendChild(flagCircle(item.flag, item.code))
    return node
  }

  function mobileClickPayload(roundIndex, side, index, mobileRounds) {
    if (roundIndex === 4) {
      const finalists = [mobileRounds.top[4][0], mobileRounds.bottom[4][0]]
      if (!finalists[0] || !finalists[1]) return null
      return { phase_key: "final", match_number: 1 }
    }

    const phaseKey = phases[roundIndex]
    const current = mobileRounds[side][roundIndex]
    const matchInSide = Math.floor(index / 2)
    const pair = [current[matchInSide * 2], current[matchInSide * 2 + 1]]
    if (!phaseKey || !pair[0] || !pair[1]) return null
    const matchesPerSide = current.length / 2
    const matchNumber = matchInSide + 1 + (side === "bottom" ? matchesPerSide : 0)
    return { phase_key: phaseKey, match_number: matchNumber }
  }

  function drawMobileChampion(frameElement, championCode) {
    const help = document.createElement("div")
    help.className = "mobile-help"
    help.innerHTML = "Clique nos vencedores<br>de cada confronto, para<br>fazer a sua simulação."
    frameElement.appendChild(help)

    const area = document.createElement("div")
    area.className = "mobile-champion-area"
    const championNode = document.createElement("div")
    championNode.className = "mobile-champion-node"
    if (championCode) {
      const item = team(championCode)
      championNode.appendChild(flagCircle(item.flag, item.code))
    } else {
      const circle = flagCircle("")
      const trophy = document.createElement("span")
      trophy.className = "mobile-trophy"
      trophy.textContent = "🏆"
      circle.appendChild(trophy)
      championNode.appendChild(circle)
    }
    area.appendChild(championNode)
    frameElement.appendChild(area)
  }

  function restoreScroll(scrollElement) {
    if (!scrollLeft) return
    requestAnimationFrame(() => {
      scrollElement.scrollLeft = scrollLeft
    })
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
    championNode.appendChild(flagCircle(item.flag, item.code))
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
            div[data-testid="stHorizontalBlock"] {
                flex-direction: column;
            }
            div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
                flex: 1 1 100% !important;
                min-width: 100% !important;
                width: 100% !important;
            }
            .topbar {
                margin-left: -1rem;
                margin-right: -1rem;
            }
            .hero h1 {
                font-size: 30px;
            }
            .section-title.mobile-reference-title {
                border-bottom: 0;
                font-size: 44px;
                font-weight: 500;
                margin: 30px 0 22px;
                padding-bottom: 0;
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


def read_component_trigger(component_key: str, trigger_key: str) -> dict[str, object] | None:
    component_state = st.session_state.get(component_key)
    trigger_value = getattr(component_state, trigger_key, None)
    if trigger_value is None and isinstance(component_state, dict):
        trigger_value = component_state.get(trigger_key)
    return trigger_value if isinstance(trigger_value, dict) else None


def handle_groups_action() -> None:
    event = read_component_trigger("groups_selector", "action")
    if not event:
        return

    action = str(event.get("action", ""))
    group_code = str(event.get("group_code", ""))
    if group_code not in {group.code for group in GROUPS}:
        return

    st.session_state[ACTIVE_GROUP_KEY] = group_code
    group = find_group(group_code)
    valid_team_codes = {team.code for team in group.teams}

    if action == "randomize":
        randomize_group(group_code)
        return

    if action == "pick":
        team_code = str(event.get("team_code", ""))
        selected_label = str(event.get("selected_label", ""))
        if team_code not in valid_team_codes or selected_label not in GROUP_POSITION_BY_LABEL:
            return

        st.session_state[group_rank_key(group_code, team_code)] = selected_label
        sync_group_position(group_code, team_code)


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


def groups_payload() -> list[dict[str, object]]:
    return [
        {
            "code": group.code,
            "teams": [
                {"code": team.code, "flag": team.flag, "name": team.name}
                for team in group.teams
            ],
        }
        for group in GROUPS
    ]


def selected_by_group_payload() -> dict[str, dict[str, str | None]]:
    return {
        group.code: {
            team.code: st.session_state.get(group_rank_key(group.code, team.code))
            for team in group.teams
        }
        for group in GROUPS
    }


def render_groups_selector() -> dict[str, dict[str, str | None]]:
    if st.session_state.get(ACTIVE_GROUP_KEY) not in {group.code for group in GROUPS}:
        st.session_state[ACTIVE_GROUP_KEY] = GROUPS[0].code

    GROUPS_SELECTOR_COMPONENT(
        key="groups_selector",
        data={
            "groups": groups_payload(),
            "positions": GROUP_POSITION_LABELS,
            "selected_by_group": selected_by_group_payload(),
            "current_group": st.session_state[ACTIVE_GROUP_KEY],
        },
        on_action_change=handle_groups_action,
    )
    return {group.code: group_selection(group) for group in GROUPS}


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
    return read_component_trigger("knockout_bracket_component", "pick")


def handle_bracket_pick() -> None:
    pick = read_component_pick()
    if not pick:
        return

    phase_key = str(pick.get("phase_key", ""))
    winner_code = str(pick.get("winner_code", ""))
    try:
        st.session_state[KNOCKOUT_SCROLL_KEY] = max(0, int(float(pick.get("scroll_left", 0))))
    except (TypeError, ValueError):
        st.session_state[KNOCKOUT_SCROLL_KEY] = 0

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


def initial_labels_for_codes(initial_codes: list[str], selections: dict[str, dict[str, str | None]]) -> list[str]:
    group_by_team = {team.code: group.code for group in GROUPS for team in group.teams}
    labels: list[str] = []

    for code in initial_codes:
        group_code = group_by_team.get(code, "")
        group_selection = selections.get(group_code, {})
        if group_selection.get("first") == code:
            labels.append(f"1{group_code}")
        elif group_selection.get("second") == code:
            labels.append(f"2{group_code}")
        else:
            labels.append("3º")

    return labels


def render_knockout(initial_codes: list[str], initial_labels: list[str]) -> dict[str, list[str | None]]:
    winners_by_phase = build_knockout_state(initial_codes)
    KNOCKOUT_BRACKET_COMPONENT(
        key="knockout_bracket_component",
        data={
            "initial": initial_codes,
            "initial_labels": initial_labels,
            "scroll_left": st.session_state.get(KNOCKOUT_SCROLL_KEY, 0),
            "phases": [phase_key for phase_key, _phase_label in KNOCKOUT_PHASES],
            "winners": component_winners(winners_by_phase),
            "teams": teams_payload(),
        },
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

    render_html('<div class="section-title mobile-reference-title">Grupos</div>')
    selections = render_groups_selector()

    participant_errors = validate_participant(name, phone, email)
    selection_errors = validate_selections(selections)
    knockout_winners: dict[str, list[str | None]] = {}
    initial_codes: list[str] = []

    render_html('<div class="section-title">Classificados</div>')
    qualified = None
    if not selection_errors:
        qualified = build_qualified(selections, seed=2026)
        render_qualified(qualified)
        render_html('<div class="section-title mobile-reference-title">Mata-mata</div>')
        initial_codes = build_official_knockout_order(
            selections,
            [team["code"] for team in qualified["thirds"]],
        )
        knockout_winners = render_knockout(initial_codes, initial_labels_for_codes(initial_codes, selections))
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
            initial_codes = build_official_knockout_order(
                selections,
                [team["code"] for team in qualified["thirds"]],
            )

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
