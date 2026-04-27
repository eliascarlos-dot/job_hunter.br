"""
Módulo 4 — Briefing Formatter
Formata o output do scorer em 3 versões e gerencia o envio para o Telegram.
ATUALIZADO: Inclui links das vagas
"""

import json
import os
import requests
from datetime import datetime


def format_telegram(approved: list[dict], stats: dict, run_date: str) -> str:
    """
    Formata briefing para Telegram usando MarkdownV2.
    ATUALIZADO: Inclui link da vaga + formato limpo
    """
    date_str = datetime.fromisoformat(run_date).strftime("%d/%m/%Y")
    lines = []

    lines.append(f"📦 *JOB INTEL — {date_str}*")
    lines.append(f"`{stats['analyzed']} analisadas → {stats['approved']} aprovadas`")
    lines.append("")

    if not approved:
        lines.append("😶 Nenhuma vaga acima de 65pts hoje\\.")
        return "\n".join(lines)

    for i, job in enumerate(approved[:10], 1):  # Top 10 vagas
        score = job.get("score_total", 0)
        target = "⭐ " if job.get("is_target_company") else ""

        # Emoji de prioridade
        if score >= 90:
            priority = "🔴"
        elif score >= 80:
            priority = "🟡"
        else:
            priority = "🟢"

        title = _escape_telegram(job.get("title", ""))
        company = _escape_telegram(job.get("company", ""))
        location = _escape_telegram(job.get("location", ""))
        work_model = _escape_telegram(job.get("work_model", "A verificar"))
        url = job.get("apply_url", "")

        lines.append(f"{priority} *{i}\\. {title}*")
        lines.append(f"{target}{company} \\| {location}")
        
        # LINK DA VAGA - PRIMEIRO! ← NOVO
        if url:
            lines.append(f"🔗 [CANDIDATAR AGORA]({url})")
        
        lines.append(f"📍 {work_model} \\| ✅ Fit: *{score}/100*")
        
        # Gap apenas se score 70-85
        gap = job.get("gaps", "")
        if gap and str(gap).lower() != "null" and 70 <= score < 85:
            lines.append(f"⚠️ Gap: {_escape_telegram(gap)}")
        
        lines.append("")

    lines.append(f"_📊 Sistema automático \\| Vagas filtradas por IA_")
    return "\n".join(lines)


def format_whatsapp(approved: list[dict], stats: dict, run_date: str) -> str:
    """
    Formata briefing para WhatsApp.
    Texto limpo com emojis — sem markdown complexo.
    ATUALIZADO: Inclui links
    """
    date_str = datetime.fromisoformat(run_date).strftime("%d/%m/%Y")
    lines = []

    lines.append(f"📦 *JOB INTEL — {date_str}*")
    lines.append(f"━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"📊 {stats['analyzed']} vagas analisadas → {stats['approved']} aprovadas")
    lines.append("")

    if not approved:
        lines.append("😶 Nenhuma vaga acima de 65pts hoje.")
        lines.append("O sistema seguirá monitorando.")
        return "\n".join(lines)

    lines.append("🔥 *TOP VAGAS DO DIA*")
    lines.append("")

    for i, job in enumerate(approved[:5], 1):
        score = job.get("score_total", 0)
        target = "⭐ " if job.get("is_target_company") else ""

        if score >= 80:
            priority = "🔴"
        elif score >= 70:
            priority = "🟡"
        else:
            priority = "🟢"

        lines.append(f"{priority} *{i}. {job.get('title')}*")
        lines.append(f"{target}{job.get('company')} | {job.get('location')}")
        lines.append(f"📍 {job.get('work_model', 'A verificar')}")
        lines.append(f"✅ Fit: *{score}/100*")
        
        # LINK DA VAGA ← NOVO
        if job.get("apply_url"):
            lines.append(f"🔗 {job.get('apply_url')}")

        lines.append("─" * 20)
        lines.append("")

    lines.append(f"_Fonte: LinkedIn + Gupy_")
    return "\n".join(lines)


def format_email_html(approved: list[dict], stats: dict, run_date: str) -> str:
    """
    Formata briefing como HTML rico para e-mail.
    ATUALIZADO: Inclui links clicáveis
    """
    date_str = datetime.fromisoformat(run_date).strftime("%d de %B de %Y")
    jobs_html = ""
    
    for i, job in enumerate(approved[:5], 1):
        score = job.get("score_total", 0)
        score_color = "#dc2626" if score >= 80 else "#d97706" if score >= 70 else "#16a34a"
        target_badge = '<span style="color:#f59e0b;font-weight:700">⭐ Empresa-alvo</span>' if job.get("is_target_company") else ""
        apply_url = job.get("apply_url", "")

        jobs_html += f"""
        <div style="border:1px solid #e5e7eb;border-radius:8px;padding:20px;margin-bottom:16px">
            <h3 style="margin:0;font-size:16px;color:#111827">{i}. {job.get('title')}</h3>
            <p style="margin:4px 0;color:#6b7280;font-size:14px">{job.get('company')} · {job.get('location')}</p>
            <div style="background:#e5e7eb;border-radius:4px;height:8px;margin:8px 0">
                <div style="background:{score_color};width:{score}%;height:8px;border-radius:4px"></div>
            </div>
            <p style="font-size:13px"><strong>Fit:</strong> {score}/100 | {job.get('work_model', '')}</p>
            {f'<a href="{apply_url}" style="display:inline-block;padding:8px 16px;background:#1d4ed8;color:white;text-decoration:none;border-radius:6px;font-size:13px;margin-top:8px">🔗 Candidatar-se</a>' if apply_url else ''}
        </div>"""

    return f"""
    <html>
    <body style='font-family:sans-serif;max-width:640px;margin:20px auto;'>
        <h2>Job Intel — {date_str}</h2>
        <p>{stats['analyzed']} vagas analisadas → <strong>{stats['approved']} aprovadas</strong></p>
        {jobs_html}
        <hr style='margin:30px 0;border:none;border-top:1px solid #e5e7eb'>
        <p style='color:#6b7280;font-size:12px;text-align:center'>
            Sistema automático de análise de vagas executivas
        </p>
    </body>
    </html>"""


def _escape_telegram(text: str) -> str:
    """Escapa caracteres especiais do MarkdownV2"""
    if not text:
        return ""
    special = r'_*[]()~`>#+-=|{}.!'
    for c in special:
        text = text.replace(c, f'\\{c}')
    return text


def send_telegram(token: str, chat_id: str, message: str):
    """Envia a mensagem formatada para o bot do Telegram."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": False  # Mostrar preview dos links
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise Exception(f"Erro Telegram: {response.text}")
    return response.json()


def save_briefings(approved: list[dict], rejected: list[dict], run_date: str):
    """Salva os 3 formatos de briefing em caminhos relativos."""
    stats = {
        "analyzed": len(approved) + len(rejected),
        "approved": len(approved),
        "rejected": len(rejected),
    }

    whatsapp = format_whatsapp(approved, stats, run_date)
    telegram = format_telegram(approved, stats, run_date)
    email_html = format_email_html(approved, stats, run_date)

    base = "output"
    os.makedirs(base, exist_ok=True)

    with open(f"{base}/briefing_whatsapp.txt", "w", encoding="utf-8") as f:
        f.write(whatsapp)
    with open(f"{base}/briefing_telegram.txt", "w", encoding="utf-8") as f:
        f.write(telegram)
    with open(f"{base}/briefing_email.html", "w", encoding="utf-8") as f:
        f.write(email_html)

    return {"whatsapp": whatsapp, "telegram": telegram, "email_html": email_html}
