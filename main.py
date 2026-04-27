import os
import sys
import json
import argparse
from datetime import datetime

# Importa configurações do perfil
try:
    from config.profile import FIT_THRESHOLD
except ImportError:
    FIT_THRESHOLD = 65

# Importar Google Sheets (se disponível)
try:
    from modules.sheets_backup import save_to_sheets
    SHEETS_ENABLED = True
except ImportError:
    SHEETS_ENABLED = False

def run_pipeline(gmail_only=False, gupy_only=False, dry_run=False):
    emails_lidos = 0
    vagas_processadas = 0

    print("=" * 55)
    print("   JOB INTEL SYSTEM — Pipeline Completo")
    print(f"   Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 55)

    all_relevant = []
    all_discarded = []
    run_date = datetime.now().isoformat()

    # ── ETAPA 1: Gmail Parser ────────────────────────────────
    if not gupy_only:
        print("\n📧 ETAPA 1 — Gmail Parser (LinkedIn Alerts)")
        try:
            from modules.gmail_parser import (
                fetch_gmail_alerts,
                apply_lexical_filter,
                deduplicate_jobs,
                boost_target_companies
            )
            
            # Executa a busca real no Gmail
            fetch_gmail_alerts()
            
            # Carrega os dados processados
            gmail_jobs = _load_gmail_jobs()
            emails_lidos = len(gmail_jobs)
            
            if gmail_jobs:
                unique = deduplicate_jobs(gmail_jobs)
                relevant, discarded = apply_lexical_filter(unique)
                relevant = boost_target_companies(relevant)
                all_relevant.extend(relevant)
                all_discarded.extend(discarded)
                print(f"   ✅ Vagas extraídas: {emails_lidos}")
                print(f"   ✅ Vagas relevantes após filtros: {len(relevant)}")
            else:
                print("   ⚠️ Nenhuma vaga nova (não lida) encontrada no Gmail.")
        except Exception as e:
            print(f"   ❌ Erro na Etapa 1: {e}")

    # ── ETAPA 2: Gupy Scraper ────────────────────────────────
    if not gmail_only:
        print("\n🕷  ETAPA 2 — Gupy Scraper")
        try:
            from modules.gupy_scraper import run_gupy_search
            gupy_result = run_gupy_search()
            all_relevant.extend(gupy_result["relevant_jobs"])
            all_discarded.extend(gupy_result["discarded_jobs"])
            print(f"   ✅ Gupy: {len(gupy_result['relevant_jobs'])} vagas encontradas")
        except Exception as e:
            print(f"   ❌ Erro na Etapa 2: {e}")

    # ── ETAPA 3: Consolidação ────────────────────────────────
    print(f"\n🔀 ETAPA 3 — Consolidação Global")
    from modules.gmail_parser import deduplicate_jobs
    all_relevant = deduplicate_jobs(all_relevant)
    print(f"   ✅ Total para análise da IA: {len(all_relevant)} vagas")

    if not all_relevant:
        print("\n😶 Nenhuma vaga relevante para processar hoje.")
        _save_results(run_date, dry_run, [], [], [])
        return

    # ── ETAPA 4: Scorer (IA) ──────────────────────────────────
    print(f"\n🤖 ETAPA 4 — Scorer (Claude API)")
    approved, rejected_score = [], []
    if dry_run:
        print("   ⚠️  MODO TESTE (Dry Run): Aprovando vagas automaticamente.")
        approved = all_relevant[:3]
        rejected_score = all_relevant[3:]
        for j in approved:
            j.update({"score_total": 80, "aprovado": True, "resumo_fit": "Simulação de teste"})
    else:
        try:
            from modules.scorer import score_jobs_batch
            approved, rejected_score = score_jobs_batch(all_relevant)
        except Exception as e:
            print(f"   ❌ Erro no Scorer: {e}")

    # ── ETAPA 5: Google Sheets Backup ────────────────────────
    if SHEETS_ENABLED:
        print(f"\n📊 ETAPA 5 — Backup Google Sheets")
        try:
            all_rejected = all_discarded + rejected_score
            save_to_sheets(approved, all_rejected, run_date)
        except Exception as e:
            print(f"   ⚠️ Erro no Sheets: {e}")
    else:
        print(f"\n⚠️ Google Sheets não configurado (dados salvos localmente)")

    # ── ETAPA 6: Formatter e Notificação ──────────────────────
    print(f"\n📋 ETAPA 6 — Notificação")
    try:
        from modules.briefing_formatter import save_briefings, send_telegram
        all_rejected = all_discarded + rejected_score
        briefings = save_briefings(approved, all_rejected, run_date)
        
        token = os.environ.get("TELEGRAM_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        
        if briefings.get('telegram') and token and chat_id and not dry_run:
            send_telegram(token, chat_id, briefings['telegram'])
            print("   ✅ Alerta enviado para o Telegram!")
    except Exception as e:
        print(f"   ❌ Erro no envio: {e}")

    _save_results(run_date, dry_run, all_relevant, approved, all_discarded + rejected_score)
    print("\n" + "=" * 55)
    print("   📊 DASHBOARD FINAL")
    print(f"   📩 Vagas brutas (Gmail): {emails_lidos}")
    print(f"   🔍 Analisadas pela IA: {len(all_relevant)}")
    print(f"   🎯 Aprovadas para você: {len(approved)}")
    print("=" * 55)

def _save_results(run_date, dry_run, total, app, rej):
    res = {"run_date": run_date, "stats": {"total": len(total), "app": len(app), "rej": len(rej)}, "jobs": app}
    os.makedirs("output", exist_ok=True)
    with open("output/latest_run.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

def _load_gmail_jobs():
    path = "output/parsed_jobs.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("relevant_jobs", [])
    return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gmail-only", action="store_true")
    parser.add_argument("--gupy-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run_pipeline(args.gmail_only, args.gupy_only, args.dry_run)
