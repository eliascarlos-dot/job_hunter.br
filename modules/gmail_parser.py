"""
Módulo 1 — Gmail Parser
Extrai vagas dos alertas do LinkedIn recebidos via Gmail
ATUALIZADO: Extração melhorada de URLs, empresa e localização
"""

import re
import json
import imaplib
import email
import os
from email.header import decode_header
from datetime import datetime
from config.profile import DISCARD_KEYWORDS, RELEVANT_KEYWORDS, TARGET_COMPANIES


def fetch_gmail_alerts():
    """
    Conecta ao Gmail via IMAP e extrai vagas dos alertas do LinkedIn.
    Processa os 200 emails mais recentes para garantir cobertura completa.
    """
    user = os.environ.get("GMAIL_USER")
    pw = os.environ.get("GMAIL_APP_PASSWORD")

    if not user or pw:
        print("   ❌ Erro: Credenciais do Gmail ausentes no Railway.")
        return

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, pw)
        mail.select("inbox")

        # Busca emails do LinkedIn (não apenas não lidos)
        status, messages = mail.search(None, '(FROM "linkedin.com")')
        
        if status != "OK":
            print("   ❌ Erro ao buscar emails do LinkedIn")
            return
        
        ids = messages[0].split()
        total_emails = len(ids)
        print(f"   🔍 Total de emails na inbox: {total_emails}")
        
        # Pega os 200 mais recentes
        recent_ids = ids[-200:] if len(ids) > 200 else ids
        print(f"   🔍 Processando {len(recent_ids)} emails mais recentes")

        all_jobs = []
        emails_processados = 0
        
        for e_id in recent_ids:
            _, data = mail.fetch(e_id, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            
            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            
            # Filtra apenas emails de alerta de vagas
            if not _is_job_alert(subject):
                continue
            
            emails_processados += 1
            
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode()
                            break
                        except:
                            continue
            else:
                try:
                    body = msg.get_payload(decode=True).decode()
                except:
                    continue

            jobs = parse_linkedin_alert(body, msg["Date"], subject)
            
            if jobs:
                print(f"   📧 [{emails_processados}] {subject[:60]}...")
                print(f"      ✅ Extraiu {len(jobs)} vaga(s)")
                all_jobs.extend(jobs)

        os.makedirs("output", exist_ok=True)
        with open("output/parsed_jobs.json", "w", encoding="utf-8") as f:
            json.dump({"relevant_jobs": all_jobs}, f, ensure_ascii=False, indent=2)
        
        print(f"\n   ✅ Total extraído: {len(all_jobs)} vagas de {emails_processados} emails")
        mail.logout()
        
    except Exception as e:
        print(f"   ❌ Erro IMAP: {e}")


def _is_job_alert(subject: str) -> bool:
    """
    Verifica se o email é um alerta de vaga do LinkedIn.
    """
    subject_lower = subject.lower()
    
    # Palavras-chave que indicam alerta de vaga
    job_keywords = [
        "vaga", "job", "hiring", "oportunidade", "opportunity",
        "candidate-se", "apply", "position", "gerente", "manager",
        "diretor", "director", "head", "coordenador"
    ]
    
    # Ignora newsletters e outros tipos de email
    ignore_keywords = [
        "newsletter", "resumo semanal", "weekly digest",
        "networking", "aniversário", "birthday", "conexão",
        "visualizou seu perfil", "viewed your profile"
    ]
    
    # Se tem palavra de ignore, pula
    if any(keyword in subject_lower for keyword in ignore_keywords):
        return False
    
    # Se tem palavra de job alert, processa
    return any(keyword in subject_lower for keyword in job_keywords)


def parse_linkedin_alert(body: str, date: str, subject: str) -> list[dict]:
    """
    Extrai vagas individuais do corpo do email.
    ATUALIZADO: Extração melhorada de URLs, empresa e localização.
    """
    jobs = []
    
    # Split por separadores comuns em emails do LinkedIn
    blocks = re.split(r'-{20,}|\n\n\n+', body)
    
    for block in blocks:
        block = block.strip()
        
        # Ignora blocos muito curtos
        if len(block) < 50:
            continue
        
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        
        if len(lines) < 2:
            continue
        
        # Primeira linha geralmente é o título
        title = lines[0]
        
        # Ignora blocos que não são vagas
        if any(x in title.lower() for x in [
            "cancelar", "unsubscribe", "linkedin", "visualizar",
            "privacidade", "privacy", "configurações", "settings"
        ]):
            continue
        
        # Extrai URL (prioriza LinkedIn)
        apply_url = _extract_url_from_block(block)
        
        # Extrai empresa e localização
        company, location = _extract_company_location(lines, block)
        
        # Detecta modelo de trabalho
        work_model = _detect_work_model(block)
        
        job = {
            "title": title,
            "company": company,
            "location": location,
            "work_model": work_model,
            "apply_url": apply_url,
            "source": "linkedin_email",
            "collected_at": datetime.now().strftime("%Y-%m-%d"),
            "raw_block": block[:500],  # Primeiros 500 chars para análise
        }
        
        jobs.append(job)
    
    return jobs


def _extract_url_from_block(block: str) -> str:
    """
    Extrai URL do LinkedIn do bloco de email.
    Prioriza links diretos de vagas.
    """
    # Prioridade 1: Link direto LinkedIn jobs/view
    linkedin_job = re.search(r'https://(?:www\.)?linkedin\.com/jobs/view/\d+/?[^\s<>"]*', block)
    if linkedin_job:
        url = linkedin_job.group(0)
        # Remove tracking params mas mantém o ID
        url = re.sub(r'\?.*$', '', url)
        return url
    
    # Prioridade 2: Link de candidatura LinkedIn
    linkedin_apply = re.search(r'https://(?:www\.)?linkedin\.com/job/apply/\d+/?[^\s<>"]*', block)
    if linkedin_apply:
        url = linkedin_apply.group(0)
        url = re.sub(r'\?.*$', '', url)
        return url
    
    # Prioridade 3: Qualquer link LinkedIn relacionado a jobs
    linkedin_jobs = re.search(r'https://(?:www\.)?linkedin\.com/jobs/[^\s<>"]+', block)
    if linkedin_jobs:
        url = linkedin_jobs.group(0)
        url = re.sub(r'\?.*$', '', url)
        return url
    
    # Prioridade 4: Qualquer link LinkedIn
    linkedin_any = re.search(r'https://(?:www\.)?linkedin\.com/[^\s<>"]+', block)
    if linkedin_any:
        url = linkedin_any.group(0)
        url = re.sub(r'\?.*$', '', url)
        return url
    
    # Prioridade 5: Qualquer HTTP (último recurso)
    any_url = re.search(r'https?://[^\s<>"]+', block)
    if any_url:
        return any_url.group(0)
    
    return ""


def _extract_company_location(lines: list[str], block: str) -> tuple[str, str]:
    """
    Extrai empresa e localização do email.
    """
    company = "Empresa não identificada"
    location = "Brasil"
    
    # Tenta extrair das primeiras linhas (formato comum do LinkedIn)
    for i, line in enumerate(lines[1:5], 1):  # Linhas 2-5
        # Formato: "Empresa · Localização" ou "Empresa via Recrutador · Local"
        if '·' in line:
            parts = [p.strip() for p in line.split('·')]
            if len(parts) >= 1:
                company_part = parts[0]
                # Remove "via Recrutador" se presente
                company = re.sub(r'\s+via\s+.*$', '', company_part).strip()
            if len(parts) >= 2:
                location = parts[1].strip()
            break
        
        # Formato alternativo: "Empresa | Localização"
        elif '|' in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 1:
                company = re.sub(r'\s+via\s+.*$', '', parts[0]).strip()
            if len(parts) >= 2:
                location = parts[1].strip()
            break
    
    # Se não achou, tenta regex no bloco inteiro
    if company == "Empresa não identificada":
        # Padrão: "na empresa XYZ" ou "at XYZ"
        company_match = re.search(r'(?:na empresa|at)\s+([A-Z][^\n·|]{2,40})', block)
        if company_match:
            company = company_match.group(1).strip()
    
    # Normaliza localização
    if location and location != "Brasil":
        # Remove extras como "Brasil ·" ou emojis
        location = re.sub(r'[·•].*$', '', location).strip()
        if not location:
            location = "Brasil"
    
    return company, location


def _detect_work_model(block: str) -> str:
    """
    Detecta modelo de trabalho (Remoto, Híbrido, Presencial).
    """
    block_lower = block.lower()
    
    # Keywords para cada modelo
    remote_keywords = ["remoto", "remote", "home office", "trabalho remoto"]
    hybrid_keywords = ["híbrido", "hybrid", "semi-presencial", "flexível"]
    
    if any(keyword in block_lower for keyword in remote_keywords):
        return "Remoto"
    elif any(keyword in block_lower for keyword in hybrid_keywords):
        return "Híbrido"
    else:
        return "Presencial"


def apply_lexical_filter(jobs: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Filtra vagas por palavras-chave de descarte e relevância.
    """
    relevant = []
    discarded = []
    
    for job in jobs:
        text = f"{job['title']} {job['company']}".lower()
        
        # Descarta se tem keyword de descarte
        if any(keyword.lower() in text for keyword in DISCARD_KEYWORDS):
            discarded.append(job)
            continue
        
        # Aprova se tem keyword relevante
        if any(keyword.lower() in text for keyword in RELEVANT_KEYWORDS):
            relevant.append(job)
        else:
            discarded.append(job)
    
    return relevant, discarded


def deduplicate_jobs(jobs: list[dict]) -> list[dict]:
    """
    Remove vagas duplicadas (mesmo título + empresa).
    """
    seen = set()
    unique = []
    
    for job in jobs:
        key = f"{job['title']}-{job['company']}".lower()
        if key not in seen:
            seen.add(key)
            unique.append(job)
    
    return unique


def boost_target_companies(jobs: list[dict]) -> list[dict]:
    """
    Marca vagas de empresas-alvo prioritárias.
    """
    for job in jobs:
        company_lower = job['company'].lower()
        job['is_target_company'] = any(
            target.lower() in company_lower 
            for target in TARGET_COMPANIES
        )
    
    return jobs
