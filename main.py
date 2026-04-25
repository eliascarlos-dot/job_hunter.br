import os
import sys
import json
import argparse
from datetime import datetime

try:
    from config.profile import FIT_THRESHOLD
except ImportError:
    FIT_THRESHOLD = 65

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
            
            gmail_jobs = fetch_gmail_alerts()
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
                print("   ⚠️ Nenhuma vaga nova encontrada no Gmail.")
        except Exception as e:
            print(f"   ❌ Erro na Etapa 1: {e}")

    # ── ETAPA 2: Gupy Scraper (desativado por padrão) ────────
    if not gmail_only:
        print("\n🕷  ETAPA 2 — Gupy Scraper")
        try:
            from modules.gupy_scraper import run_gupy_search
            gupy_result = run_gupy_search()
            all_relevant.extend(gupy_result["relevant_jobs"])
            all_discarded.extend(gupy_result["discarded_jobs"])
            print(f"   ✅ Gupy: {len(gupy_result['relevant_jobs'])} vagas")
        except Exception as e:
            print(f"   ❌ Erro na Etapa 2: {e}")

    # ── ETAPA 3: Deduplicação ────────────────────────────────
    print(f"\n🔍 ETAPA 3 — Deduplicação")
    from modules.deduplicator import filter_new_jobs, mark_as_analyzed, get_stats
    
    stats = get_stats()
    if stats["total"] > 0:
        print(f"   📊 Histórico: {stats['total']} vagas já analisadas")
    
    new_jobs, duplicates = filter_new_jobs(all_relevant)
    
    if duplicates:
        print(f"   ⏭️  Puladas {len(duplicates)} vagas repetidas")
    
    all_relevant = new_jobs  # Só processa as novas
    
    print(f"\n🔀 ETAPA 4 — Consolidação Global")
    from modules.gmail_parser import deduplicate_jobs
    all_relevant = deduplicate_jobs(all_relevant)
    print(f"   ✅ Total para análise da IA: {len(all_relevant)} vagas")

    if not all_relevant:
        print("\n😶 Nenhuma vaga nova para processar hoje.")
        _save_results(run_date, dry_run, [], [], [])
        return

    # ── ETAPA 5: Scorer (IA) ──────────────────────────────────
    print(f"\n🤖 ETAPA 5 — Scorer (Claude API)")
    approved, rejected_score = [], []
    if dry_run:
        print("   ⚠️  MODO TESTE (Dry Run): Simulando aprovações.")
        approved = all_relevant[:3]
        rejected_score = all_relevant[3:]
        for j in approved:
            j.update({"score_total": 80, "aprovado": True, "resumo_fit": "Simulação"})
    else:
        try:
            from modules.scorer import score_jobs_batch
            approved, rejected_score = score_jobs_batch(all_relevant)
            
            # Salva no histórico APÓS scoring
            mark_as_analyzed(all_relevant)
            
        except Exception as e:
            print(f"   ❌ Erro no Scorer: {e}")

    # ── ETAPA 6: Formatter e Notificação ──────────────────────
    print(f"\n📋 ETAPA 6 — Notificação")
    try:
        from modules.briefing_formatter import save_briefings, send_telegram
        from modules.email_sender import send_email_briefing, format_email_html
        
        all_rejected = all_discarded + rejected_score
        briefings = save_briefings(approved, all_rejected, run_date)
        
        # Telegram
        token = os.environ.get("TELEGRAM_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        
        if briefings.get('telegram') and token and chat_id and not dry_run:
            send_telegram(token, chat_id, briefings['telegram'])
            print("   ✅ Alerta enviado para o Telegram!")
        
        # Email
        if not dry_run:
            email_html = format_email_html(
                approved, 
                {"analyzed": len(all_relevant), "approved": len(approved), "rejected": len(all_rejected)},
                run_date
            )
            send_email_briefing(email_html)
            
    except Exception as e:
        print(f"   ❌ Erro no envio: {e}")

    _save_results(run_date, dry_run, all_relevant, approved, all_discarded + rejected_score)
    
    # Gera e envia relatório completo
    if approved and not dry_run:
        try:
            from generate_report import generate_consolidated_report
            from modules.email_sender import send_email_briefing
            
            report_html = generate_consolidated_report()
            
            # Salva localmente
            with open("output/relatorio_completo.html", "w", encoding="utf-8") as f:
                f.write(report_html)
            
            # Envia por email
            send_email_briefing(report_html)
            print("   📧 Relatório completo enviado por email")
        except Exception as e:
            print(f"   ⚠️ Erro ao gerar relatório: {e}")
    
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
