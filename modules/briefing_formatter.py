"""
Módulo 4 — Briefing Formatter
Formata o output do scorer em 3 versões e gerencia o envio para o Telegram.
"""

import json
import os
import requests
from datetime import datetime


def format_telegram(approved: list[dict], stats: dict, run_date: str) -> str:
    """Formata briefing para Telegram usando MarkdownV2."""
    date_str = datetime.fromisoformat(run_date).strftime("%d/%m/%Y")
    lines = []

    lines.append(f"📦 *JOB INTEL — {date_str}*")
    lines.append(f"`{stats['analyzed']} analisadas → {stats['approved']} aprovadas`")
    lines.append("")

    if not approved:
        lines.append("😶 Nenhuma vaga acima de 65pts hoje\\.")
        return "\n".join(lines)

    for i, job in enumerate(approved[:5], 1):
        score = job.get("score_total", 0)
        target = "⭐ " if job.get("is_target_company") else ""

        if score >= 80:
            priority = "🔴"
        elif score >= 70:
            priority = "🟡"
        else:
            priority = "🟢"

        title = _escape_telegram(job.get("title", ""))
        company = _escape_telegram(job.get("company", ""))
        location = _escape_telegram(job.get("location", ""))
        work_model = _escape_telegram(job.get("work_model", "A verificar"))
        resumo = _escape_telegram(job.get("resumo_fit", ""))
        insight = _escape_telegram(job.get("bp_insight", ""))
        gap = _escape_telegram(job.get("gaps", ""))
        url = job.get("apply_url", "")

        lines.append(f"{priority} *{i}\\. {title}*")
        lines.append(f"{target}{company} \\| {location}")
        lines.append(f"📍 {work_model} \\| ✅ Fit: *{score}/100*")

        if resumo:
            lines.append(f"💬 _{resumo}_")
        if insight:
            lines.append(f"💡 {insight}")
        if gap:
            lines.append(f"⚠️ Gap: {gap}")
        if url:
            lines.append(f"[Candidatar\\-se]({url})")
        lines.append("")

    lines.append(f"_Fontes: {_escape_telegram(_format_sources(approved))}_")
    return "\n".join(lines)


def _format_sources(jobs: list[dict]) -> str:
    sources = set(j.get("source", "") for j in jobs)
    labels = {"linkedin_email": "LinkedIn", "gupy": "Gupy", "indeed": "Indeed"}
    return " + ".join(labels.get(s, s) for s in sources if s)


def _escape_telegram(text: str) -> str:
    if not text: return ""
    special = r'_*[]()~`>#+-=|{}.!'
    for c in special:
        text = text.replace(c, f'\\{c}')
    return text


def send_telegram(token: str, chat_id: str, message: str):
    """Envia a mensagem formatada para o bot do Telegram."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "MarkdownV2"}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise Exception(f"Erro Telegram: {response.text}")
    return response.json()


def save_briefings(approved: list[dict], rejected: list[dict], run_date: str):
    """Salva os briefings."""
    stats = {
        "analyzed": len(approved) + len(rejected),
        "approved": len(approved),
        "rejected": len(rejected),
    }

    telegram = format_telegram(approved, stats, run_date)

    base = "output"
    os.makedirs(base, exist_ok=True)

    with open(f"{base}/briefing_telegram.txt", "w", encoding="utf-8") as f:
        f.write(telegram)

    return {"telegram": telegram}
