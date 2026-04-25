"""
Módulo 3 — Scorer
Usa Claude API para analisar vagas filtradas e gerar:
- Score de fit 0-100
- Justificativa por dimensão
- Insights estratégicos do BP (Business Partner)
- Gaps identificados
"""

import json
import time
import requests
import os
from datetime import datetime
from config.profile import CANDIDATE_PROFILE, SCORING_WEIGHTS, FIT_THRESHOLD


CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1000
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


SCORING_PROMPT = """Você é um Business Partner de Carreira especializado em logística executiva no Brasil.

Analise o fit entre a vaga abaixo e o perfil do candidato. Responda APENAS em JSON válido, sem texto antes ou depois.

=== PERFIL DO CANDIDATO ===
{profile}

=== VAGA ===
Título: {title}
Empresa: {company}
Localização: {location}
Modelo de trabalho: {work_model}
Empresa-alvo prioritária: {is_target}
Descrição/contexto: {raw_block}

=== INSTRUÇÕES DE SCORING ===
Avalie cada dimensão com nota de 0 até o peso máximo:
- senioridade: máx 20pts (Gerente Sênior/Head/Director = 18-20 | Gerente = 15-17 | Coord Sênior = 12-14 | abaixo = 0-11)
- setor: máx 20pts (Tech/E-commerce/Logtech = 18-20 | FMCG digital/Supply Chain = 14-17 | Industrial = 10-13 | outro = 0-9)
- escopo: máx 20pts (Operações/ProdOps/Last Mile/Torre de Controle/WMS-TMS = 17-20 | Logística geral = 13-16 | Supply Chain estratégico = 10-12 | outro = 0-9)
- localizacao: máx 15pts (SP híbrido=15 | Remoto=15 | Presencial SP=10 | Grande SP presencial=7 | Fora SP=3)
- stack: máx 15pts (Lean Six Sigma + dados/BI + WMS/TMS = 13-15 | Lean + operações = 9-12 | básico = 5-8 | nenhum = 0-4)
- porte: máx 10pts (Big Tech/Unicórnio=10 | Multinacional grande=8 | Scale-up=7 | Média empresa=5 | Pequena=3)

Se empresa-alvo prioritária = true, adicione +5 ao total final (max 100).

Retorne este JSON exato:
{{
  "score_total": <número 0-100>,
  "scores": {{
    "senioridade": <número>,
    "setor": <número>,
    "escopo": <número>,
    "localizacao": <número>,
    "stack": <número>,
    "porte": <número>
  }},
  "aprovado": <true se score_total >= 65, false se não>,
  "resumo_fit": "<1 frase explicando o fit principal>",
  "bp_insight": "<2-3 frases: dica estratégica concreta para abordagem, networking ou discurso na entrevista>",
  "gaps": "<1 frase sobre o principal gap ou null se não houver>",
  "destaque": "<o argumento mais forte do CV para esta vaga específica>"
}}"""


def score_job(job: dict) -> dict:
    """Envia uma vaga para o Claude API e retorna o score completo."""
    prompt = SCORING_PROMPT.format(
        profile=CANDIDATE_PROFILE,
        title=job.get("title", ""),
        company=job.get("company", ""),
        location=job.get("location", ""),
        work_model=job.get("work_model", "A verificar"),
        is_target=str(job.get("is_target_company", False)),
        raw_block=job.get("raw_block", "Sem descrição disponível")[:800],
    )

    payload = {
        "model": CLAUDE_MODEL,
        "max_tokens": MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
    }

    headers = {
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
        "x-api-key": ANTHROPIC_API_KEY,
    }

    try:
        response = requests.post(CLAUDE_API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        raw_text = data["content"][0]["text"].strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        raw_text = raw_text.strip()

        result = json.loads(raw_text)
        result["title"] = job.get("title")
        result["company"] = job.get("company")
        result["location"] = job.get("location")
        result["work_model"] = job.get("work_model")
        result["apply_url"] = job.get("apply_url")
        result["source"] = job.get("source")
        result["collected_at"] = job.get("collected_at")
        result["is_target_company"] = job.get("is_target_company", False)

        return result

    except Exception as e:
        print(f"  ⚠️ Erro ao scorar '{job.get('title')}': {e}")
        return _error_result(job, str(e))


def score_jobs_batch(jobs: list[dict], delay: float = 0.5):
    """Scorea uma lista de vagas com delay entre chamadas."""
    print(f"\n🤖 Iniciando scoring — {len(jobs)} vagas para analisar")
    print(f"   Threshold: {FIT_THRESHOLD}pts | Modelo: {CLAUDE_MODEL}\n")

    all_results = []
    for i, job in enumerate(jobs, 1):
        print(f"  [{i}/{len(jobs)}] Analisando: {job.get('title')} | {job.get('company')}...")
        result = score_job(job)
        score = result.get("score_total", 0)
        status = "✅" if result.get("aprovado") else "❌"
        print(f"         {status} Score: {score}/100")
        all_results.append(result)
        if i < len(jobs):
            time.sleep(delay)

    approved = [r for r in all_results if r.get("aprovado") and not r.get("error")]
    rejected = [r for r in all_results if not r.get("aprovado") or r.get("error")]
    approved.sort(key=lambda x: x.get("score_total", 0), reverse=True)

    print(f"\n✅ Aprovadas (≥{FIT_THRESHOLD}pts): {len(approved)}")
    print(f"❌ Reprovadas: {len(rejected)}")

    return approved, rejected


def _error_result(job: dict, error_msg: str) -> dict:
    return {
        "title": job.get("title"),
        "company": job.get("company"),
        "location": job.get("location"),
        "work_model": job.get("work_model"),
        "apply_url": job.get("apply_url"),
        "source": job.get("source"),
        "score_total": 0,
        "aprovado": False,
        "error": error_msg,
    }
