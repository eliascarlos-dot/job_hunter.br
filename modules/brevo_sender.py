"""
Envio de emails via Brevo (ex-Sendinblue) API
Alternativa ao SendGrid - 300 emails/dia grátis
"""

import os
import requests


def send_email_brevo(subject: str, html_content: str, to_email: str = None):
    """
    Envia email via Brevo API v3.
    
    Args:
        subject: Assunto do email
        html_content: Conteúdo HTML do email
        to_email: Email destinatário (default: EMAIL_RECIPIENT env var)
    
    Returns:
        dict: Resposta da API ou None em caso de erro
    """
    api_key = os.environ.get("BREVO_API_KEY")
    from_email = os.environ.get("BREVO_FROM_EMAIL", "ecljunior@gmail.com")
    from_name = os.environ.get("BREVO_FROM_NAME", "Job Intel System")
    
    if not to_email:
        to_email = os.environ.get("EMAIL_RECIPIENT", from_email)
    
    if not api_key:
        print("   ⚠️  BREVO_API_KEY não configurada")
        return None
    
    # Payload Brevo API v3
    payload = {
        "sender": {
            "name": from_name,
            "email": from_email
        },
        "to": [
            {
                "email": to_email,
                "name": to_email.split('@')[0].title()
            }
        ],
        "subject": subject,
        "htmlContent": html_content
    }
    
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    
    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            message_id = result.get("messageId", "N/A")
            print(f"   ✅ Email enviado via Brevo (ID: {message_id})")
            return {"status": "sent", "to": to_email, "message_id": message_id}
        else:
            print(f"   ❌ Erro Brevo ({response.status_code}): {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Erro ao enviar email: {e}")
        return None


def send_job_intel_email(html_content: str, approved_count: int):
    """
    Envia o briefing diário de vagas via Brevo.
    
    Args:
        html_content: HTML formatado do briefing
        approved_count: Número de vagas aprovadas
    """
    subject = f"🎯 Job Intel — {approved_count} vagas aprovadas hoje"
    
    if approved_count == 0:
        subject = "📭 Job Intel — Nenhuma vaga nova hoje"
    elif approved_count >= 10:
        subject = f"🔥 Job Intel — {approved_count} EXCELENTES vagas!"
    
    return send_email_brevo(subject, html_content)


def send_test_email():
    """
    Envia email de teste para verificar configuração.
    """
    html = """
    <html>
    <body style="font-family: sans-serif; max-width: 600px; margin: 20px auto;">
        <h2 style="color: #1d4ed8;">🎉 Brevo funcionando!</h2>
        <p>Se você recebeu este email, a configuração do Brevo está <strong>correta</strong>.</p>
        <p>O Job Intel System está pronto para enviar alertas diários!</p>
        <hr>
        <p style="color: #6b7280; font-size: 12px;">
            Job Intel System | Powered by Claude API
        </p>
    </body>
    </html>
    """
    
    return send_email_brevo(
        subject="✅ Teste Brevo - Job Intel System",
        html_content=html
    )


# ──────────────────────────────────────────────────────────────────
# FALLBACK: Tenta Brevo → SendGrid → SMTP
# ──────────────────────────────────────────────────────────────────

def send_email_with_fallback(html_content: str, approved_count: int):
    """
    Envia email via Brevo (com fallback para SMTP local se necessário).
    """
    # Tenta Brevo
    if os.environ.get("BREVO_API_KEY"):
        print("   📧 Enviando via Brevo...")
        result = send_job_intel_email(html_content, approved_count)
        if result:
            return result
    
    # Fallback para SMTP (só local, não funciona no Railway)
    if not os.environ.get("RAILWAY_ENVIRONMENT"):
        print("   📧 Brevo falhou, tentando SMTP local...")
        try:
            from modules.email_sender import send_email_smtp
            return send_email_smtp(html_content, approved_count)
        except Exception as e:
            print(f"   ⚠️ SMTP também falhou: {e}")
    
    print("   ❌ Envio de email falhou")
    return None


if __name__ == "__main__":
    # Teste rápido
    print("🧪 Testando envio Brevo...")
    result = send_test_email()
    
    if result:
        print("✅ Teste concluído! Verifique seu email.")
    else:
        print("❌ Teste falhou. Verifique as variáveis de ambiente:")
        print("   - BREVO_API_KEY")
        print("   - BREVO_FROM_EMAIL")
        print("   - EMAIL_RECIPIENT")
