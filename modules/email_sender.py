"""
Módulo de Email
Envia briefing diário por email usando Gmail SMTP
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


def send_email_briefing(html_content: str, recipient_email: str = None):
    """
    Envia briefing por email usando Gmail SMTP.
    
    Requer variáveis de ambiente:
    - GMAIL_USER: seu email @gmail.com
    - GMAIL_APP_PASSWORD: senha de app (mesma do IMAP)
    - EMAIL_RECIPIENT: email destino (default: mesmo do GMAIL_USER)
    """
    sender_email = os.environ.get("GMAIL_USER")
    sender_password = os.environ.get("GMAIL_APP_PASSWORD")
    recipient_email = recipient_email or os.environ.get("EMAIL_RECIPIENT") or sender_email
    
    if not sender_email or not sender_password:
        print("   ⚠️  Credenciais Gmail ausentes - email não enviado")
        return False
    
    try:
        # Cria mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🎯 Job Intel — {datetime.now().strftime('%d/%m/%Y')}"
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        # Anexa HTML
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Envia via Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print(f"   ✅ Email enviado para {recipient_email}")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao enviar email: {e}")
        return False


def format_email_html(approved: list[dict], stats: dict, run_date: str) -> str:
    """
    Formata briefing como HTML rico para email.
    Versão melhorada com design profissional.
    """
    from datetime import datetime
    date_str = datetime.fromisoformat(run_date).strftime("%d de %B de %Y")
    
    # Header
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 680px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 32px 24px; color: white; }}
            .header h1 {{ margin: 0; font-size: 28px; font-weight: 700; }}
            .header p {{ margin: 8px 0 0 0; opacity: 0.9; font-size: 14px; }}
            .stats {{ padding: 20px 24px; background: #f8f9fa; border-bottom: 1px solid #e9ecef; }}
            .stats-grid {{ display: flex; gap: 16px; }}
            .stat {{ flex: 1; text-align: center; }}
            .stat-value {{ font-size: 24px; font-weight: 700; color: #667eea; }}
            .stat-label {{ font-size: 12px; color: #6c757d; margin-top: 4px; }}
            .jobs {{ padding: 24px; }}
            .job-card {{ border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; margin-bottom: 16px; transition: all 0.2s; }}
            .job-card:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
            .job-header {{ display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px; }}
            .job-title {{ font-size: 18px; font-weight: 600; color: #212529; margin: 0; }}
            .job-score {{ font-size: 14px; font-weight: 700; padding: 4px 12px; border-radius: 20px; }}
            .score-high {{ background: #fef3f2; color: #dc2626; }}
            .score-mid {{ background: #fef9c3; color: #d97706; }}
            .score-low {{ background: #f0fdf4; color: #16a34a; }}
            .job-meta {{ color: #6c757d; font-size: 14px; margin: 8px 0; }}
            .job-meta span {{ margin-right: 16px; }}
            .job-insight {{ background: #f8f9fa; padding: 12px; border-radius: 6px; margin: 12px 0; font-size: 14px; line-height: 1.6; }}
            .job-insight strong {{ color: #495057; }}
            .job-gap {{ background: #fff3cd; padding: 8px 12px; border-radius: 6px; margin: 8px 0; font-size: 13px; color: #856404; }}
            .btn {{ display: inline-block; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600; margin-top: 8px; }}
            .btn:hover {{ background: #5568d3; }}
            .footer {{ padding: 24px; text-align: center; color: #6c757d; font-size: 13px; border-top: 1px solid #e9ecef; }}
            .empty {{ text-align: center; padding: 40px; color: #6c757d; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 Job Intel</h1>
                <p>{date_str}</p>
            </div>
            
            <div class="stats">
                <div class="stats-grid">
                    <div class="stat">
                        <div class="stat-value">{stats['analyzed']}</div>
                        <div class="stat-label">Analisadas</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{stats['approved']}</div>
                        <div class="stat-label">Aprovadas</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{stats.get('rejected', 0)}</div>
                        <div class="stat-label">Descartadas</div>
                    </div>
                </div>
            </div>
    """
    
    if not approved:
        html += """
            <div class="empty">
                <h3>😶 Nenhuma vaga aprovada hoje</h3>
                <p>O sistema seguirá monitorando e notificará quando encontrar oportunidades relevantes.</p>
            </div>
        """
    else:
        html += '<div class="jobs">'
        
        for i, job in enumerate(approved[:10], 1):  # Top 10
            score = job.get("score_total", 0)
            
            # Score badge
            if score >= 80:
                score_class = "score-high"
                priority = "🔴"
            elif score >= 70:
                score_class = "score-mid"
                priority = "🟡"
            else:
                score_class = "score-low"
                priority = "🟢"
            
            target = "⭐ " if job.get("is_target_company") else ""
            
            html += f"""
            <div class="job-card">
                <div class="job-header">
                    <h3 class="job-title">{priority} {i}. {job.get('title', 'Título não disponível')}</h3>
                    <span class="job-score {score_class}">{score}/100</span>
                </div>
                
                <div class="job-meta">
                    <span>{target}{job.get('company', 'Empresa não informada')}</span>
                    <span>📍 {job.get('location', 'Brasil')}</span>
                    <span>🏢 {job.get('work_model', 'A verificar')}</span>
                </div>
            """
            
            if job.get("resumo_fit"):
                html += f'<div class="job-insight"><strong>💬 Fit:</strong> {job.get("resumo_fit")}</div>'
            
            if job.get("bp_insight"):
                html += f'<div class="job-insight"><strong>💡 Estratégia:</strong> {job.get("bp_insight")}</div>'
            
            if job.get("gaps"):
                html += f'<div class="job-gap">⚠️ Gap: {job.get("gaps")}</div>'
            
            if job.get("apply_url"):
                html += f'<a href="{job.get("apply_url")}" class="btn">Candidatar-se</a>'
            
            html += '</div>'
        
        html += '</div>'
    
    # Footer
    html += f"""
            <div class="footer">
                <p>Job Intel System • Powered by Claude AI</p>
                <p style="margin-top: 8px; font-size: 12px;">
                    Este relatório foi gerado automaticamente às {datetime.now().strftime('%H:%M')}
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


# ─── TESTE ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  TESTE DE ENVIO DE EMAIL")
    print("=" * 55)
    
    # Dados de teste
    test_jobs = [
        {
            "title": "Senior Manager, Operations",
            "company": "Amazon",
            "location": "São Paulo, SP",
            "work_model": "Híbrido",
            "score_total": 90,
            "is_target_company": True,
            "resumo_fit": "Match perfeito: Last Mile + escala Amazon + WMS",
            "bp_insight": "Destaque sua experiência com 10k veículos/dia e SSOT no Mercado Livre",
            "gaps": None,
            "apply_url": "https://linkedin.com/jobs/view/123",
        },
        {
            "title": "Gerente de Transportes",
            "company": "GRF Distribuição",
            "location": "São Paulo, SP",
            "work_model": "Presencial",
            "score_total": 72,
            "is_target_company": False,
            "resumo_fit": "Boa aderência em transportes e torre de controle",
            "bp_insight": "Mencione sua experiência em P&L de R$120M no Grupo Imediato",
            "gaps": "Falta experiência específica em e-commerce",
            "apply_url": "https://linkedin.com/jobs/view/456",
        },
    ]
    
    stats = {"analyzed": 75, "approved": 2, "rejected": 73}
    
    html = format_email_html(test_jobs, stats, datetime.now().isoformat())
    
    # Salva HTML para preview
    with open("output/email_preview.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("\n✅ Preview salvo em output/email_preview.html")
    
    # Testa envio (se credenciais estiverem configuradas)
    if os.environ.get("GMAIL_USER"):
        send_email_briefing(html)
    else:
        print("⚠️  Configure GMAIL_USER para testar envio real")
