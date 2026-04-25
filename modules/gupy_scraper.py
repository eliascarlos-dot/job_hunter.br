"""
Módulo 2 — Gupy Scraper
Busca ativa de vagas no endpoint público da Gupy
Sem autenticação necessária
"""

import json
import time
import requests
from datetime import datetime
from config.profile import DISCARD_KEYWORDS, RELEVANT_KEYWORDS, TARGET_COMPANIES, FIT_THRESHOLD


GUPY_API_URL = "https://portal.gupy.io/api/job"

SEARCH_QUERIES = [
    "Gerente Logística",
    "Head Logística",
    "Gerente Supply Chain",
    "Gerente Operações",
    "Head Operations",
    "Senior Manager Operations",
    "Gerente Transportes",
    "Torre de Controle",
    "Last Mile Manager",
    "Control Tower",
]

DEFAULT_LOCATION = "São Paulo"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
    "Accept-Language": "pt-BR,pt;q=0.9",
}


def search_gupy(query: str, city: str = DEFAULT_LOCATION, limit: int = 20) -> list[dict]:
    """Busca vagas na Gupy para um termo específico."""
    params = {"jobName": query, "city": city, "limit": limit, "offset": 0}

    try:
        response = requests.get(GUPY_API_URL, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()

        jobs = []
        for item in data.get("data", []):
            job = _normalize_gupy_job(item)
            if job:
                jobs.append(job)
        return jobs

    except requests.exceptions.RequestException as e:
        print(f"  ⚠️ Erro ao buscar '{query}': {e}")
        return []


def _normalize_gupy_job(item: dict) -> dict | None:
    """Converte um item da API Gupy para o formato padronizado."""
    try:
        title = item.get("name", "").strip()
        company = item.get("company", {}).get("name", "Empresa não informada")
        city = item.get("city", "")
        state = item.get("state", "")
        location = f"{city}, {state}".strip(", ") if city or state else "SP"

        workplace = item.get("workplaceType", "").lower()
        if "remote" in workplace or "remoto" in workplace:
            work_model = "Remoto"
        elif "hybrid" in workplace or "híbrido" in workplace:
            work_model = "Híbrido"
        else:
            work_model = "Presencial"

        job_id = str(item.get("id", ""))
        company_slug = item.get("company", {}).get("urlName", "")
        apply_url = f"https://{company_slug}.gupy.io/jobs/{job_id}" if company_slug and job_id else None

        published_at = item.get("publishedDate", item.get("createdAt", ""))
        if published_at:
            try:
                dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                published_at = dt.strftime("%Y-%m-%d")
            except Exception:
                pass

        return {
            "title": title,
            "company": company,
            "location": location,
            "work_model": work_model,
            "apply_url": apply_url,
            "job_id": f"gupy_{job_id}",
            "source": "gupy",
            "collected_at": datetime.now().strftime("%Y-%m-%d"),
            "published_at": published_at,
            "signals": {"growing": False, "actively_hiring": True, "connections": None},
            "raw_block": f"{title} {company} {item.get('description', '')[:300]}",
        }
    except Exception as e:
        print(f"  ⚠️ Erro ao normalizar vaga Gupy: {e}")
        return None


def run_gupy_search(queries: list[str] = SEARCH_QUERIES) -> dict:
    """Executa buscas para todos os termos e retorna resultado consolidado."""
    from modules.gmail_parser import apply_lexical_filter, deduplicate_jobs, boost_target_companies

    print(f"🔍 Iniciando busca Gupy — {len(queries)} termos")
    print(f"   Localização: {DEFAULT_LOCATION}\n")

    all_jobs = []
    for i, query in enumerate(queries, 1):
        print(f"  [{i}/{len(queries)}] Buscando: '{query}'...")
        jobs = search_gupy(query)
        print(f"         → {len(jobs)} vagas encontradas")
        all_jobs.extend(jobs)
        time.sleep(0.5)

    print(f"\n✅ Total bruto: {len(all_jobs)} vagas")

    unique_jobs = deduplicate_jobs(all_jobs)
    print(f"✅ Após deduplicação: {len(unique_jobs)} vagas")

    relevant, discarded = apply_lexical_filter(unique_jobs)
    print(f"✅ Relevantes: {len(relevant)} vagas")
    print(f"❌ Descartadas: {len(discarded)} vagas")

    relevant = boost_target_companies(relevant)

    return {
        "run_date": datetime.now().isoformat(),
        "source": "gupy",
        "stats": {
            "raw": len(all_jobs),
            "unique": len(unique_jobs),
            "relevant": len(relevant),
            "discarded": len(discarded),
        },
        "relevant_jobs": relevant,
        "discarded_jobs": discarded,
    }
