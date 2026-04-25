# 🎯 Job Intel System

**Sistema automatizado de busca e análise de vagas executivas usando Claude API**

Monitora alertas do LinkedIn/Indeed via Gmail, filtra vagas relevantes, analisa fit com IA e envia alertas diários via Telegram e email.

---

## ✨ Features

- 🤖 **Scoring Inteligente** - Claude API analisa fit 0-100 pts por dimensão
- 📧 **Multi-Source** - Gmail (LinkedIn/Indeed alerts) + Gupy scraper
- 🎯 **Filtros Avançados** - Keywords, empresas-alvo, senioridade
- 📊 **Deduplicação** - Não analisa vagas repetidas (economiza $$$)
- 🔔 **Alertas** - Telegram + Email HTML profissional
- ☁️ **Cloud-Ready** - Deploy Railway com 1 clique

---

## 🚀 Quick Start (5 minutos)

### 1. Clone e Configure

```bash
git clone https://github.com/seu-usuario/job-intel.git
cd job-intel
cp .env.example .env
# Edite .env com suas credenciais
```

### 2. Instale Dependências

```bash
pip install -r requirements.txt
```

### 3. Configure Seu Perfil

Edite `config/profile.py` com suas informações:
- Experiências profissionais
- Stack técnico
- Empresas-alvo
- Keywords relevantes

### 4. Teste

```bash
# Teste configuração Brevo
python test_brevo.py

# Execução teste (não consome API)
python main.py --gmail-only --dry-run

# Execução real
python main.py --gmail-only
```

---

## 📊 Como Funciona

```
┌─────────────┐
│ Gmail IMAP  │──┐
└─────────────┘  │
                 ├──> Filtro      ──> Deduplicação ──> Claude    ──> Alertas
┌─────────────┐  │    Léxico          (MD5 hash)       Scorer        (Telegram
│ Gupy Scraper│──┘    (keywords)                       (0-100pts)     + Email)
└─────────────┘
```

### Pipeline Completo:

1. **Coleta** - Lê emails não lidos do Gmail + busca ativa no Gupy
2. **Filtro Léxico** - Descarta vagas irrelevantes (vendas, júnior, etc.)
3. **Deduplicação** - Pula vagas já analisadas (hash MD5)
4. **Scoring IA** - Claude avalia fit em 6 dimensões:
   - Senioridade (20pts)
   - Setor (20pts)
   - Escopo (20pts)
   - Localização (15pts)
   - Stack técnico (15pts)
   - Porte da empresa (10pts)
5. **Insights BP** - Dicas estratégicas de abordagem
6. **Notificação** - Envia top vagas (≥65pts) via Telegram + Email

---

## 📋 Variáveis de Ambiente

Copie `.env.production` (valores reais de produção) ou `.env.example` (template):

```bash
# Claude API
ANTHROPIC_API_KEY=sk-ant-...

# Gmail IMAP
GMAIL_USER=seu@email.com
GMAIL_APP_PASSWORD=abcd1234

# Brevo Email
BREVO_API_KEY=xkeysib-...
BREVO_FROM_EMAIL=seu@email.com

# Telegram
TELEGRAM_TOKEN=123456:ABC...
TELEGRAM_CHAT_ID=123456789
```

Veja `docs/SETUP.md` para guia completo.

---

## 🔧 Comandos

```bash
# Apenas Gmail
python main.py --gmail-only

# Apenas Gupy
python main.py --gupy-only

# Ambos (recomendado)
python main.py

# Modo teste (não gasta API)
python main.py --dry-run

# Teste email Brevo
python test_brevo.py
```

---

## ☁️ Deploy Railway

### 1-Click Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/job-intel)

### Manual

1. Criar projeto no Railway
2. Conectar repositório GitHub
3. Adicionar variáveis de ambiente (Settings → Variables)
4. Deploy automático!

**Cron Job Diário:**
```
Settings → Cron
Schedule: 0 7 * * 1-5  (segunda a sexta, 7h)
Command: python main.py
```

---

## 📊 Custos Estimados

| Serviço | Plano | Custo |
|---------|-------|-------|
| **Claude API** | Pay-as-go | ~R$3-10/mês* |
| **Railway** | Free | R$0 |
| **Brevo** | Free | R$0 (300 emails/dia) |
| **Telegram** | Free | R$0 |
| **Total** | | **R$3-10/mês** |

*Baseado em ~30-100 vagas/dia com deduplicação ativa

---

## 🎯 Resultados Reais

**Última execução (24/04/2026):**
- 📧 160 vagas brutas extraídas (Gmail)
- 🎯 76 vagas relevantes (pós-filtro)
- ✅ 23 vagas aprovadas (≥65pts)
- 🏆 Top scores: 95, 90, 88 pts

**Economia com deduplicação:**
- 1º dia: 76 vagas → R$0,75 Claude API
- 2º dia: 0 vagas repetidas → R$0,00
- **Redução: 100%** após primeiro run

---

## 📚 Documentação

- 📖 [Setup Completo](docs/SETUP.md)
- 📧 [Configurar Brevo](docs/BREVO_SETUP.md)
- 🧪 [Testar Brevo](docs/TEST_BREVO.md)
- 🏗️ [Estrutura do Projeto](STRUCTURE.md)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 Licença

MIT License - veja [LICENSE](LICENSE)

---

## 👤 Autor

**Elias Carlos Lopes**  
📧 ecljunior@gmail.com  
💼 [LinkedIn](https://linkedin.com/in/eclopesjr)

---

## ⭐ Dê uma Estrela!

Se este projeto te ajudou, deixe uma ⭐ no GitHub!

---

**Status:** ✅ Produção (Railway)  
**Versão:** 1.0.0  
**Última atualização:** 25/04/2026
