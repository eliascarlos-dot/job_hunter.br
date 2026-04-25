#!/usr/bin/env python3
"""
🧪 BREVO API KEY - TESTE RÁPIDO
Valida se sua configuração está correta antes de rodar o pipeline completo
"""

import os
import sys
import requests
from datetime import datetime


# Cores para output bonito
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header():
    print("\n" + "=" * 60)
    print(f"{Colors.BOLD}🧪 BREVO API - TESTE DE CONFIGURAÇÃO{Colors.END}")
    print("=" * 60)
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")


def check_env_vars():
    """Verifica se as variáveis de ambiente estão configuradas"""
    print(f"{Colors.BLUE}📋 ETAPA 1 — Verificando Variáveis de Ambiente{Colors.END}\n")
    
    required_vars = {
        "BREVO_API_KEY": "Chave da API Brevo",
        "BREVO_FROM_EMAIL": "Email remetente",
        "EMAIL_RECIPIENT": "Email destinatário"
    }
    
    missing = []
    configured = []
    
    for var, desc in required_vars.items():
        value = os.environ.get(var)
        if value:
            # Mascara a chave para segurança
            if "KEY" in var:
                display = f"{value[:15]}...{value[-10:]}" if len(value) > 25 else value[:20] + "..."
            else:
                display = value
            
            print(f"   ✅ {var}")
            print(f"      → {desc}: {display}")
            configured.append(var)
        else:
            print(f"   ❌ {var}")
            print(f"      → {desc}: {Colors.RED}NÃO CONFIGURADA{Colors.END}")
            missing.append(var)
    
    print()
    
    if missing:
        print(f"{Colors.RED}❌ Faltam {len(missing)} variável(is):{Colors.END}")
        for var in missing:
            print(f"   - {var}")
        print(f"\n{Colors.YELLOW}💡 Configure no arquivo .env ou nas variáveis de ambiente{Colors.END}\n")
        return False
    
    print(f"{Colors.GREEN}✅ Todas as variáveis configuradas!{Colors.END}\n")
    return True


def test_api_connection():
    """Testa conexão com a API Brevo"""
    print(f"{Colors.BLUE}🔌 ETAPA 2 — Testando Conexão API{Colors.END}\n")
    
    api_key = os.environ.get("BREVO_API_KEY")
    
    headers = {
        "api-key": api_key,
        "accept": "application/json"
    }
    
    try:
        print("   🔍 Conectando ao Brevo...")
        response = requests.get(
            "https://api.brevo.com/v3/account",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            account = response.json()
            print(f"   {Colors.GREEN}✅ Conexão estabelecida!{Colors.END}")
            print(f"\n   📊 Informações da Conta:")
            print(f"      Email: {account.get('email', 'N/A')}")
            print(f"      Plan: {account.get('plan', [{}])[0].get('type', 'N/A')}")
            
            # Pega estatísticas de email
            email_stats = account.get('plan', [{}])[0].get('credits', {})
            credits_used = email_stats.get('emails', {}).get('used', 0)
            credits_total = email_stats.get('emails', {}).get('total', 0)
            
            if credits_total > 0:
                remaining = credits_total - credits_used
                print(f"      Emails usados: {credits_used}/{credits_total}")
                print(f"      Restantes: {remaining}")
            else:
                print(f"      Plan: Ilimitado ou Free (300/dia)")
            
            print()
            return True
            
        elif response.status_code == 401:
            print(f"   {Colors.RED}❌ API Key inválida ou expirada{Colors.END}")
            print(f"\n   💡 Solução:")
            print(f"      1. Acesse: https://app.brevo.com/")
            print(f"      2. SMTP & API → API Keys")
            print(f"      3. Gere uma nova chave")
            print(f"      4. Atualize BREVO_API_KEY\n")
            return False
            
        else:
            print(f"   {Colors.RED}❌ Erro na conexão: {response.status_code}{Colors.END}")
            print(f"   Resposta: {response.text}\n")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   {Colors.RED}❌ Timeout - Sem resposta em 10s{Colors.END}\n")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"   {Colors.RED}❌ Erro de conexão: {e}{Colors.END}\n")
        return False


def send_test_email():
    """Envia email de teste"""
    print(f"{Colors.BLUE}📧 ETAPA 3 — Enviando Email de Teste{Colors.END}\n")
    
    api_key = os.environ.get("BREVO_API_KEY")
    from_email = os.environ.get("BREVO_FROM_EMAIL", "test@example.com")
    from_name = os.environ.get("BREVO_FROM_NAME", "Job Intel Test")
    to_email = os.environ.get("EMAIL_RECIPIENT", from_email)
    
    # HTML bonito para teste
    html_content = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 20px auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 28px;">🎉 Brevo Funcionando!</h1>
        </div>
        
        <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
            <p style="font-size: 16px; color: #333;">Olá! 👋</p>
            
            <p style="font-size: 16px; color: #333;">
                Se você está lendo este email, significa que sua configuração do <strong>Brevo</strong> está <strong style="color: #22c55e;">100% correta</strong>!
            </p>
            
            <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #22c55e;">
                <h3 style="margin-top: 0; color: #22c55e;">✅ Tudo Pronto!</h3>
                <ul style="color: #666; line-height: 1.8;">
                    <li>API Key válida e funcionando</li>
                    <li>Email remetente configurado</li>
                    <li>Email destinatário recebendo</li>
                    <li>Job Intel System pronto para rodar!</li>
                </ul>
            </div>
            
            <p style="font-size: 14px; color: #666;">
                <strong>Próximo passo:</strong> Execute o pipeline completo com:
            </p>
            
            <div style="background: #1e293b; padding: 15px; border-radius: 6px; margin: 15px 0;">
                <code style="color: #22c55e; font-family: 'Courier New', monospace;">
                    python main.py --gmail-only
                </code>
            </div>
            
            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            
            <p style="font-size: 12px; color: #999; text-align: center;">
                Job Intel System | Powered by Claude API & Brevo<br>
                Teste enviado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}
            </p>
        </div>
    </body>
    </html>
    """
    
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
        "subject": "✅ Teste Brevo - Job Intel System",
        "htmlContent": html_content
    }
    
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    
    try:
        print(f"   📤 Enviando de: {from_name} <{from_email}>")
        print(f"   📥 Enviando para: {to_email}")
        print(f"   ⏳ Aguarde...\n")
        
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            message_id = result.get("messageId", "N/A")
            
            print(f"   {Colors.GREEN}✅ Email enviado com sucesso!{Colors.END}")
            print(f"\n   📋 Detalhes:")
            print(f"      Message ID: {message_id}")
            print(f"      Status: Entregue para processamento")
            print(f"\n   {Colors.YELLOW}💡 Verifique sua caixa de entrada:{Colors.END}")
            print(f"      → {to_email}")
            print(f"      → Pode levar 1-2 minutos para chegar")
            print(f"      → Cheque SPAM se não aparecer\n")
            return True
            
        elif response.status_code == 400:
            error = response.json()
            print(f"   {Colors.RED}❌ Erro 400 - Dados inválidos{Colors.END}")
            print(f"   Detalhes: {error.get('message', 'N/A')}\n")
            
            if "sender" in str(error).lower():
                print(f"   {Colors.YELLOW}💡 Problema com email remetente:{Colors.END}")
                print(f"      BREVO_FROM_EMAIL deve ser um email válido")
                print(f"      Atual: {from_email}\n")
            
            return False
            
        elif response.status_code == 401:
            print(f"   {Colors.RED}❌ API Key inválida{Colors.END}\n")
            return False
            
        else:
            print(f"   {Colors.RED}❌ Erro {response.status_code}{Colors.END}")
            print(f"   Resposta: {response.text}\n")
            return False
            
    except Exception as e:
        print(f"   {Colors.RED}❌ Erro ao enviar: {e}{Colors.END}\n")
        return False


def print_summary(env_ok, api_ok, email_ok):
    """Mostra resumo final"""
    print("=" * 60)
    print(f"{Colors.BOLD}📊 RESUMO DO TESTE{Colors.END}")
    print("=" * 60 + "\n")
    
    status_env = f"{Colors.GREEN}✅ OK{Colors.END}" if env_ok else f"{Colors.RED}❌ FALHOU{Colors.END}"
    status_api = f"{Colors.GREEN}✅ OK{Colors.END}" if api_ok else f"{Colors.RED}❌ FALHOU{Colors.END}"
    status_email = f"{Colors.GREEN}✅ OK{Colors.END}" if email_ok else f"{Colors.RED}❌ FALHOU{Colors.END}"
    
    print(f"   Variáveis de Ambiente: {status_env}")
    print(f"   Conexão API Brevo:     {status_api}")
    print(f"   Envio de Email:        {status_email}\n")
    
    if env_ok and api_ok and email_ok:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 TUDO FUNCIONANDO PERFEITAMENTE!{Colors.END}\n")
        print(f"{Colors.YELLOW}🚀 Próximos passos:{Colors.END}")
        print(f"   1. Verifique o email de teste")
        print(f"   2. Rode o pipeline completo:")
        print(f"      {Colors.BLUE}python main.py --gmail-only{Colors.END}")
        print(f"   3. Configure agendamento automático (opcional)\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}⚠️  CONFIGURAÇÃO INCOMPLETA{Colors.END}\n")
        print(f"{Colors.YELLOW}📚 Consulte a documentação:{Colors.END}")
        print(f"   → docs/BREVO_SETUP.md\n")
        return 1


def main():
    """Executa todos os testes"""
    print_header()
    
    # Testa variáveis de ambiente
    env_ok = check_env_vars()
    if not env_ok:
        print_summary(False, False, False)
        return 1
    
    # Testa conexão API
    api_ok = test_api_connection()
    if not api_ok:
        print_summary(True, False, False)
        return 1
    
    # Testa envio de email
    email_ok = send_test_email()
    
    # Mostra resumo
    return print_summary(env_ok, api_ok, email_ok)


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Teste interrompido pelo usuário{Colors.END}\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Erro inesperado: {e}{Colors.END}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
