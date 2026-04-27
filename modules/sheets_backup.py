"""
Google Sheets Backup Module
Salva TODAS as vagas (aprovadas + reprovadas) em planilha permanente
Funciona SEMPRE, mesmo se Telegram/Email falharem
"""

import os
import json
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


# Configurações
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.environ.get('GOOGLE_SHEETS_ID', '')


def get_sheets_service():
    """
    Cria serviço Google Sheets usando Service Account
    Credenciais vêm da variável de ambiente GOOGLE_SERVICE_ACCOUNT_JSON
    """
    try:
        creds_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        if not creds_json:
            print("   ⚠️ GOOGLE_SERVICE_ACCOUNT_JSON não configurado")
            print("   ℹ️  Google Sheets desabilitado (dados salvos localmente)")
            return None
        
        creds_dict = json.loads(creds_json)
        credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)
        return service
    
    except json.JSONDecodeError as e:
        print(f"   ❌ Erro ao parsear JSON das credenciais: {e}")
        return None
    except Exception as e:
        print(f"   ❌ Erro ao conectar Google Sheets: {e}")
        return None


def save_to_sheets(approved: list[dict], rejected: list[dict], run_date: str):
    """
    Salva vagas aprovadas e reprovadas em abas separadas
    + adiciona ao histórico completo (nunca apaga)
    
    Returns: bool (True se salvou, False se falhou)
    """
    
    service = get_sheets_service()
    
    if not service:
        print("   ⚠️ Google Sheets não disponível - salvando apenas local")
        _save_local_backup(approved, rejected, run_date)
        return False
    
    if not SPREADSHEET_ID:
        print("   ⚠️ GOOGLE_SHEETS_ID não configurado")
        print("   ℹ️  Configure a variável no Railway")
        _save_local_backup(approved, rejected, run_date)
        return False
    
    try:
        # Preparar dados
        approved_rows = _prepare_rows(approved, run_date, status="APROVADA")
        rejected_rows = _prepare_rows(rejected, run_date, status="REPROVADA")
        
        # Escrever aba APROVADAS (limpa antes)
        if approved_rows:
            _write_to_sheet(service, "Aprovadas", approved_rows)
            print(f"   ✅ Google Sheets: {len(approved_rows)-1} aprovadas salvas")
        
        # Escrever aba REPROVADAS (limpa antes)
        if rejected_rows:
            _write_to_sheet(service, "Reprovadas", rejected_rows)
            print(f"   ✅ Google Sheets: {len(rejected_rows)-1} reprovadas salvas")
        
        # Adicionar ao HISTÓRICO (append, nunca limpa)
        all_rows = approved_rows[1:] + rejected_rows[1:]  # Remove headers
        if all_rows:
            _append_to_history(service, all_rows)
            print(f"   ✅ Google Sheets: {len(all_rows)} vagas no histórico permanente")
        
        # Backup local também (redundância)
        _save_local_backup(approved, rejected, run_date)
        
        return True
    
    except Exception as e:
        print(f"   ❌ Erro ao salvar no Google Sheets: {e}")
        print(f"   ℹ️  Salvando backup local...")
        _save_local_backup(approved, rejected, run_date)
        return False


def _prepare_rows(jobs: list[dict], run_date: str, status: str) -> list[list]:
    """
    Converte lista de vagas em linhas prontas para Google Sheets
    
    Formato: 20 colunas com todos os dados relevantes
    """
    
    # Header (sempre o mesmo)
    header = [
        "Data Execução",
        "Status",
        "Score",
        "Título",
        "Empresa",
        "Localização",
        "Modelo Trabalho",
        "Link Vaga",           # ← LINK AQUI
        "Fonte",
        "Empresa Alvo",
        "Resumo Fit",
        "Insight BP",
        "Gaps",
        "Destaque CV",
        "Score Senioridade",
        "Score Setor",
        "Score Escopo",
        "Score Localização",
        "Score Stack",
        "Score Porte",
    ]
    
    rows = [header]
    
    for job in jobs:
        row = [
            datetime.fromisoformat(run_date).strftime("%d/%m/%Y %H:%M"),
            status,
            job.get("score_total", 0),
            job.get("title", ""),
            job.get("company", ""),
            job.get("location", ""),
            job.get("work_model", ""),
            job.get("apply_url", ""),  # ← LINK DA VAGA
            job.get("source", ""),
            "SIM" if job.get("is_target_company") else "NÃO",
            job.get("resumo_fit", ""),
            job.get("bp_insight", ""),
            job.get("gaps", "") if job.get("gaps") and str(job.get("gaps")).lower() != "null" else "",
            job.get("destaque", ""),
            job.get("scores", {}).get("senioridade", ""),
            job.get("scores", {}).get("setor", ""),
            job.get("scores", {}).get("escopo", ""),
            job.get("scores", {}).get("localizacao", ""),
            job.get("scores", {}).get("stack", ""),
            job.get("scores", {}).get("porte", ""),
        ]
        rows.append(row)
    
    return rows


def _write_to_sheet(service, sheet_name: str, rows: list[list]):
    """
    Escreve dados em uma aba específica
    LIMPA a aba antes de escrever (substitui conteúdo anterior)
    """
    
    # Limpar aba completamente
    service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet_name}!A:Z"
    ).execute()
    
    # Escrever novos dados
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet_name}!A1",
        valueInputOption="RAW",
        body={"values": rows}
    ).execute()


def _append_to_history(service, rows: list[list]):
    """
    Adiciona vagas ao histórico permanente
    NÃO limpa antes - sempre adiciona no final
    Acumula TUDO desde o início
    """
    
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="Historico!A:Z",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": rows}
    ).execute()


def _save_local_backup(approved: list[dict], rejected: list[dict], run_date: str):
    """
    Backup local em JSON (fallback se Sheets falhar)
    Sempre salva, mesmo que Sheets funcione (redundância)
    """
    
    import os
    os.makedirs("output", exist_ok=True)
    
    backup = {
        "run_date": run_date,
        "timestamp": datetime.now().isoformat(),
        "stats": {
            "approved": len(approved),
            "rejected": len(rejected),
            "total": len(approved) + len(rejected),
        },
        "approved_jobs": approved,
        "rejected_jobs": rejected,
    }
    
    # Salvar arquivo timestamped
    filename = f"output/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(backup, f, ensure_ascii=False, indent=2)
    
    # Também salvar como latest (sobrescreve)
    with open("output/latest_run.json", "w", encoding="utf-8") as f:
        json.dump(backup, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ Backup local salvo: {filename}")


def create_spreadsheet_template():
    """
    Cria planilha inicial do zero (executar UMA VEZ)
    Retorna o SPREADSHEET_ID para configurar no Railway
    
    USO:
    python -c "from modules.sheets_backup import create_spreadsheet_template; create_spreadsheet_template()"
    """
    
    service = get_sheets_service()
    if not service:
        print("❌ Não foi possível conectar ao Google Sheets")
        print("   Configure GOOGLE_SERVICE_ACCOUNT_JSON primeiro")
        return None
    
    try:
        # Estrutura da planilha
        spreadsheet = {
            'properties': {
                'title': 'Job Intel - Histórico de Vagas',
                'locale': 'pt_BR',
                'timeZone': 'America/Sao_Paulo',
            },
            'sheets': [
                {
                    'properties': {
                        'title': 'Aprovadas',
                        'gridProperties': {
                            'frozenRowCount': 1,  # Congelar header
                            'frozenColumnCount': 1,  # Congelar data
                        }
                    }
                },
                {
                    'properties': {
                        'title': 'Reprovadas',
                        'gridProperties': {
                            'frozenRowCount': 1,
                        }
                    }
                },
                {
                    'properties': {
                        'title': 'Historico',
                        'gridProperties': {
                            'frozenRowCount': 1,
                        }
                    }
                },
                {
                    'properties': {
                        'title': 'Dashboard',
                    }
                },
            ]
        }
        
        # Criar planilha
        result = service.spreadsheets().create(body=spreadsheet).execute()
        spreadsheet_id = result['spreadsheetId']
        
        print("\n" + "="*60)
        print("✅ PLANILHA CRIADA COM SUCESSO!")
        print("="*60)
        print(f"\n📊 ID da Planilha:")
        print(f"   {spreadsheet_id}")
        print(f"\n🔗 Link da Planilha:")
        print(f"   https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        print(f"\n⚙️  PRÓXIMO PASSO:")
        print(f"   1. Abra o link acima")
        print(f"   2. Compartilhe com o service account:")
        print(f"      (email está no arquivo JSON, campo 'client_email')")
        print(f"   3. Dê permissão de EDITOR")
        print(f"   4. Configure no Railway:")
        print(f"      GOOGLE_SHEETS_ID={spreadsheet_id}")
        print("="*60 + "\n")
        
        return spreadsheet_id
    
    except Exception as e:
        print(f"❌ Erro ao criar planilha: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
# TESTE
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🧪 Teste do módulo Google Sheets Backup\n")
    
    # Dados de exemplo
    test_approved = [
        {
            "title": "Gerente de Logística Sênior",
            "company": "Amazon",
            "location": "São Paulo, SP",
            "work_model": "Híbrido",
            "apply_url": "https://linkedin.com/jobs/view/123456",
            "source": "linkedin_email",
            "is_target_company": True,
            "score_total": 92,
            "resumo_fit": "Match perfeito para operações de Last Mile em escala",
            "bp_insight": "Destaque experiência com 10k veículos/dia no Mercado Livre",
            "gaps": None,
            "destaque": "SSOT com Looker adotado por toda empresa",
            "scores": {
                "senioridade": 20,
                "setor": 20,
                "escopo": 19,
                "localizacao": 15,
                "stack": 13,
                "porte": 10,
            }
        }
    ]
    
    test_rejected = [
        {
            "title": "Coordenador de Logística",
            "company": "Empresa XYZ",
            "location": "Curitiba, PR",
            "work_model": "Presencial",
            "apply_url": "https://vagas.com/12345",
            "source": "vagas_com",
            "is_target_company": False,
            "score_total": 48,
            "resumo_fit": "Senioridade abaixo do perfil",
            "scores": {
                "senioridade": 12,
                "setor": 15,
                "escopo": 10,
                "localizacao": 3,
                "stack": 5,
                "porte": 3,
            }
        }
    ]
    
    run_date = datetime.now().isoformat()
    
    # Testar salvamento
    print("Testando save_to_sheets...\n")
    success = save_to_sheets(test_approved, test_rejected, run_date)
    
    if success:
        print("\n✅ Teste concluído com sucesso!")
    else:
        print("\n⚠️ Sheets não configurado, mas backup local funcionou!")
