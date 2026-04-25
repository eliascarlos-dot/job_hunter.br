import re
import json
import imaplib
import email
import os
from email.header import decode_header
from datetime import datetime, timedelta
from config.profile import DISCARD_KEYWORDS, RELEVANT_KEYWORDS, TARGET_COMPANIES

def fetch_gmail_alerts():
    import imaplib
    import email
    import os
    from email.header import decode_header
    from datetime import datetime, timedelta
    
    user = os.environ.get("GMAIL_USER")
    pw = os.environ.get("GMAIL_APP_PASSWORD")

    if not user or not pw:
        print("   ❌ Credenciais ausentes.")
        return []

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, pw)
        mail.select("inbox", readonly=True)

        # Busca simples que SEMPRE funciona
        status, messages = mail.search(None, 'ALL')
        
        all_ids = messages[0].split()
        print(f"   🔍 Total de emails na inbox: {len(all_ids)}")
        
        # Pega os 200 mais recentes
        recent_ids = all_ids[-200:] if len(all_ids) > 200 else all_ids
        print(f"   🔍 Processando {len(recent_ids)} emails mais recentes")

        all_jobs = []
        linkedin_count = 0
        indeed_count = 0
        
        for e_id in recent_ids:
            try:
                _, data = mail.fetch(e_id, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])
                
                # Pega remetente
                from_addr = str(msg.get("From", "")).lower()
                
                # Filtra apenas LinkedIn e Indeed
                is_linkedin = "linkedin" in from_addr
                is_indeed = "indeed" in from_addr
                
                if not (is_linkedin or is_indeed):
                    continue
                
                if is_linkedin:
                    linkedin_count += 1
                if is_indeed:
                    indeed_count += 1
                
                # Decode subject
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes): 
                    subject = subject.decode(errors='ignore')
                
                # Filtra por assunto relevante
                subject_lower = subject.lower()
                if not any(kw in subject_lower for kw in ["vaga", "job", "gerente", "manager", "contratando", "hiring"]):
                    continue
                
                print(f"   📧 [{linkedin_count + indeed_count}] {subject[:60]}...")
                
                # Extrai body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            payload = part.get_payload(decode=True)
                            if payload:
                                body = payload.decode(errors='ignore')
                                break
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode(errors='ignore')
                
                # Parse
                parsed = parse_linkedin_alert(body, msg.get("Date", ""), subject)
                if parsed:
                    print(f"      ✅ Extraiu {len(parsed)} vaga(s)")
                    all_jobs.extend(parsed)
                
            except Exception as e:
                print(f"      ⚠️ Erro processando email: {e}")
                continue

        print(f"\n   📊 LinkedIn: {linkedin_count} | Indeed: {indeed_count}")
        
        # Salva
        import json
        os.makedirs("output", exist_ok=True)
        with open("output/parsed_jobs.json", "w", encoding="utf-8") as f:
            json.dump({"relevant_jobs": all_jobs}, f, ensure_ascii=False, indent=2)
        
        mail.logout()
        print(f"   ✅ {len(all_jobs)} vagas extraídas no total\n")
        return all_jobs
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return []

def parse_linkedin_alert(body, date, subject):
    jobs = []
    urls = re.findall(r'https?://(?:www\.)?(?:linkedin\.com/jobs/view/|indeed\.com/[^\s]+)', body)
    
    if not urls:
        lines = [l.strip() for l in body.split('\n') if l.strip()]
        for i, line in enumerate(lines):
            if len(line) < 10 or any(x in line.lower() for x in ["cancelar", "unsubscribe", "linkedin", "indeed", "visualizar"]):
                continue
            if any(cargo in line.lower() for cargo in ["gerente", "manager", "head", "diretor", "coordenador", "supervisor"]):
                job = {
                    "title": line[:100],
                    "company": "Empresa não identificada",
                    "location": "Brasil",
                    "apply_url": "",
                    "source": "linkedin_email",
                    "work_model": "A verificar",
                    "raw_block": line + " " + " ".join(lines[i+1:i+4]) if i+1 < len(lines) else line,
                }
                if i+1 < len(lines):
                    next_line = lines[i+1]
                    if "·" in next_line or " - " in next_line:
                        parts = re.split(r'[·\-]', next_line)
                        job["company"] = parts[0].strip()
                        if len(parts) > 1:
                            job["location"] = parts[1].strip()
                jobs.append(job)
    else:
        for url in urls[:10]:
            context_start = max(0, body.find(url) - 200)
            context_end = min(len(body), body.find(url) + 200)
            context = body[context_start:context_end]
            lines_before = context[:context.find(url)].split('\n')
            title = "Vaga do LinkedIn"
            for line in reversed(lines_before):
                line = line.strip()
                if len(line) > 15 and not line.startswith('http'):
                    title = line
                    break
            jobs.append({
                "title": title[:100],
                "company": "Via LinkedIn" if "linkedin" in url else "Via Indeed",
                "location": "Brasil",
                "apply_url": url,
                "source": "linkedin_email" if "linkedin" in url else "indeed_email",
                "work_model": "A verificar",
                "raw_block": context[:300],
            })
    return jobs

def apply_lexical_filter(jobs):
    rel, disc = [], []
    for j in jobs:
        txt = f"{j['title']} {j['company']}".lower()
        if any(w.lower() in txt for w in DISCARD_KEYWORDS):
            disc.append(j)
        elif any(w.lower() in txt for w in RELEVANT_KEYWORDS):
            rel.append(j)
        else:
            disc.append(j)
    return rel, disc

def deduplicate_jobs(jobs):
    seen = set()
    res = []
    for j in jobs:
        key = f"{j['title']}-{j['company']}".lower()
        if key not in seen:
            seen.add(key)
            res.append(j)
    return res

def boost_target_companies(jobs):
    for j in jobs:
        j["is_target_company"] = any(t.lower() in j["company"].lower() for t in TARGET_COMPANIES)
    return jobs
