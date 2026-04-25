"""
Módulo de Deduplicação
Evita análise repetida de vagas já processadas
Armazena histórico em: output/analyzed_jobs_history.json
"""

import json
import hashlib
import os
from datetime import datetime, timedelta


HISTORY_FILE = "output/analyzed_jobs_history.json"
MAX_HISTORY_DAYS = 30


def generate_job_hash(job: dict) -> str:
    """Gera hash único: título + empresa + localização."""
    title = job.get("title", "").lower().strip()
    company = job.get("company", "").lower().strip()
    location = job.get("location", "").lower().strip()
    
    # Normaliza
    title = " ".join(title.split())
    company = " ".join(company.split())
    
    unique_str = f"{title}|{company}|{location}"
    return hashlib.md5(unique_str.encode()).hexdigest()


def load_history() -> dict:
    """Carrega histórico de vagas analisadas."""
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_history(history: dict):
    """Salva histórico."""
    os.makedirs("output", exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def clean_old_entries(history: dict) -> dict:
    """Remove vagas com mais de 30 dias."""
    cutoff = (datetime.now() - timedelta(days=MAX_HISTORY_DAYS)).isoformat()
    cleaned = {h: d for h, d in history.items() if d.get("analyzed_at", "") >= cutoff}
    removed = len(history) - len(cleaned)
    if removed > 0:
        print(f"   🧹 Removidas {removed} vagas antigas (>30 dias)")
    return cleaned


def filter_new_jobs(jobs: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Separa vagas novas vs já analisadas.
    Returns: (novas, duplicadas)
    """
    history = load_history()
    history = clean_old_entries(history)
    
    new_jobs = []
    duplicates = []
    
    for job in jobs:
        job_hash = generate_job_hash(job)
        
        if job_hash in history:
            # Já foi analisada
            job["_duplicate"] = True
            job["_previous_analysis"] = history[job_hash]
            duplicates.append(job)
        else:
            # Nova
            job["_hash"] = job_hash
            new_jobs.append(job)
    
    print(f"   🆕 Vagas novas: {len(new_jobs)}")
    print(f"   🔁 Já analisadas (puladas): {len(duplicates)}")
    
    return new_jobs, duplicates


def mark_as_analyzed(jobs: list[dict]):
    """Salva vagas no histórico após análise."""
    history = load_history()
    now = datetime.now().isoformat()
    
    for job in jobs:
        job_hash = job.get("_hash") or generate_job_hash(job)
        
        history[job_hash] = {
            "analyzed_at": now,
            "title": job.get("title"),
            "company": job.get("company"),
            "location": job.get("location"),
            "score": job.get("score_total", 0),
            "approved": job.get("aprovado", False),
        }
    
    save_history(history)
    print(f"   💾 Histórico: {len(history)} vagas total")


def get_stats() -> dict:
    """Estatísticas do histórico."""
    history = load_history()
    if not history:
        return {"total": 0, "approved": 0}
    
    approved = sum(1 for h in history.values() if h.get("approved"))
    return {
        "total": len(history),
        "approved": approved,
        "rejected": len(history) - approved,
    }
