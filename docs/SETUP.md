# 📋 Guia de Setup Completo

Este guia te levará do zero até ter o Job Intel rodando automaticamente.

---

## 🔑 Pré-requisitos

- [ ] Conta Gmail
- [ ] Conta Anthropic (Claude API)
- [ ] Conta Railway (deploy gratuito)
- [ ] Conta Telegram (opcional, mas recomendado)
- [ ] Python 3.8+ (se rodar localmente)

---

## 1️⃣ Configurar Gmail App Password

### Por que preciso disso?
O sistema lê seus alertas de vaga do LinkedIn/Indeed via IMAP. Para segurança, o Gmail não aceita sua senha normal — você precisa criar uma "senha de app".

### Passo a passo:

1. **Ative 2FA no Gmail**:
   - Acesse: https://myaccount.google.com/security
   - Clique em "Verificação em duas etapas"
   - Siga o processo (SMS ou app autenticador)

2. **Crie App Password**:
   - Acesse: https://myaccount.google.com/apppasswords
   - Selecione "App": **Mail**
   - Selecione "Dispositivo": **Outro (nome personalizado)**
   - Digite: **Job Intel**
   - Clique em **Gerar**
   - **COPIE** a senha de 16 caracteres (ex: `abcd efgh ijkl mnop`)

3. **Salve**:
   ```
   GMAIL_USER=seu-email@gmail.com
   GMAIL_APP_PASSWORD=abcdefghijklmnop  (sem espaços)
   ```

---

## 2️⃣ Obter Claude API Key

### Custo:
- ~R$0,10 por execução (30 vagas)
- ~R$3-7/mês com uso diário

### Passo a passo:

1. **Crie conta Anthropic**:
   - Acesse: https://console.anthropic.com
   - Sign up (aceita cartão de crédito internacional)

2. **Adicione créditos**:
   - Settings → Billing
   - Adicione $5-10 (suficiente para 1-2 meses)

3. **Crie API Key**:
   - Settings → API Keys
   - Create Key
   - **COPIE** a chave (ex: `sk-ant-api03-xxx`)

4. **Salve**:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-xxx...
   ```

---

## 3️⃣ Criar Bot do Telegram

### Por que Telegram?
Alerta rápido no celular com as TOP 5 vagas. Mais prático que email.

### Passo a passo:

1. **Abra Telegram** (app ou web)

2. **Busque**: `@BotFather`

3. **Envie**: `/newbot`

4. **Escolha um nome**:
   - Nome: `Job Intel`
   - Username: `JobIntel_SeuNome_bot` (único globalmente)

5. **Copie o TOKEN**:
   ```
   Use this token to access the HTTP API:
   7418366892:AAHGklmzZU4bXODK4iPL7nmcaw1TS1TpTqw
   ```

6. **Inicie conversa com SEU bot**:
   - Busque `@JobIntel_SeuNome_bot`
   - Clique em **INICIAR** ou envie `/start`

7. **Pegue seu Chat ID**:
   - Acesse no navegador:
   ```
   https://api.telegram.org/bot<SEU_TOKEN>/getUpdates
   ```
   - Procure por: `"chat":{"id":123456789`
   - Copie o número

8. **Salve**:
   ```
   TELEGRAM_TOKEN=7418366892:AAHGklmzZU4bXODK4iPL7nmcaw1TS1TpTqw
   TELEGRAM_CHAT_ID=123456789
   ```

---

## 4️⃣ Customizar Perfil

Edite `config/profile.py`:

```python
CANDIDATE_PROFILE = """
NOME: Seu Nome Completo
LOCALIZAÇÃO: Sua Cidade, Estado
SENIORIDADE: Nível atual (ex: Gerente Sênior, 10+ anos)

EXPERIÊNCIAS CHAVE:
- Última Empresa | Cargo (período)
  * Conquista mensurável com número (ex: -30% custos)
  * Tecnologia/processo implementado
  * Tamanho da equipe/operação

- Penúltima Empresa | Cargo
  * ...

STACK TÉCNICO: Ferramentas, Softwares, Certificações
FORMAÇÃO: MBAs, Graduação
IDIOMAS: Inglês (nível), Espanhol (nível)
"""
```

### Exemplo real (você):
```python
CANDIDATE_PROFILE = """
NOME: Elias Carlos Lopes
LOCALIZAÇÃO: São Paulo, SP
SENIORIDADE: Executivo Sênior (15+ anos)

EXPERIÊNCIAS CHAVE:
- Mercado Livre | Tracking Center Manager (nov/2021–mar/2026)
  * Monitoramento de ~10.000 veículos/dia (First Mile + Line Haul)
  * Criou SSOT — dashboards Looker/Tableau adotados empresa-toda
  * Real Time Tracking: 95% da frota ativa
  * Equipe de ~100 colaboradores
...
"""
```

---

## 5️⃣ Ajustar Keywords

Edite ainda em `config/profile.py`:

### Palavras que ELIMINAM vagas:
```python
DISCARD_KEYWORDS = [
    "vendas", "comercial", "junior", "estágio",
    "desenvolvedor", "programador",  # Se não for sua área
]
```

### Palavras que CONFIRMAM relevância:
```python
RELEVANT_KEYWORDS = [
    # Seus cargos-alvo:
    "gerente", "head", "manager", "diretor",
    
    # Suas áreas:
    "logística", "supply chain", "operações",
    "last mile", "fulfillment", "wms", "tms",
]
```

---

## 6️⃣ Deploy no Railway

### Opção A: Via GitHub (Recomendado)

1. **Faça fork** deste repo
2. **Acesse**: https://railway.app
3. **New Project** → **Deploy from GitHub**
4. **Selecione** seu fork

### Opção B: Deploy direto

1. Clone o repo:
```bash
git clone https://github.com/seu-usuario/job-intel.git
cd job-intel
```

2. Conecte ao Railway:
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

---

## 7️⃣ Configurar Variáveis no Railway

1. **Railway Dashboard** → Seu projeto
2. **Settings** → **Variables**
3. **Adicione**:

```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxx...
GMAIL_USER=seu-email@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
TELEGRAM_TOKEN=123456:ABC...
TELEGRAM_CHAT_ID=123456789
EMAIL_RECIPIENT=seu-email@gmail.com  # Opcional
```

4. **Clique em "Add"** para cada uma

---

## 8️⃣ Configurar Agendamento

### No Railway:

1. **Settings** → **Cron**
2. **Schedule**: `0 7 * * 1-5`
   - Significa: 7h da manhã, segunda a sexta
3. **Command**: `python main.py --gmail-only`
4. **Save**

### Outros horários possíveis:

```bash
# 2x por dia (7h e 19h):
0 7,19 * * 1-5

# Todo dia às 8h (incluindo fim de semana):
0 8 * * *

# A cada 6 horas:
0 */6 * * *
```

---

## 9️⃣ Primeiro Teste

### Teste manual (Railway):

1. **Deployments** → **Trigger Deploy**
2. **Deploy Logs** → Acompanhe a execução
3. **Aguarde** ~5 minutos
4. **Verifique**:
   - [ ] Email recebido?
   - [ ] Telegram recebido?

### Teste local (opcional):

```bash
# Instalar dependências
pip install -r requirements.txt

# Criar .env com as variáveis
cp .env.example .env
# Edite .env com suas chaves

# Testar sem consumir API
python main.py --gmail-only --dry-run

# Teste real
python main.py --gmail-only
```

---

## ✅ Checklist Final

- [ ] Gmail App Password configurado
- [ ] Claude API Key com créditos
- [ ] Bot Telegram criado e Chat ID obtido
- [ ] Perfil customizado em `config/profile.py`
- [ ] Keywords ajustadas
- [ ] Deploy no Railway funcionando
- [ ] Variáveis de ambiente configuradas
- [ ] Cron agendado
- [ ] Primeiro teste executado com sucesso
- [ ] Email recebido
- [ ] Telegram recebido

---

## 🆘 Problemas Comuns

### "Chat not found" (Telegram)
- **Causa**: Não iniciou conversa com o bot
- **Solução**: Abra o bot no Telegram e envie `/start`

### "Authentication failed" (Gmail)
- **Causa**: App Password incorreto ou 2FA não ativado
- **Solução**: Recrie App Password, copie sem espaços

### "Invalid API key" (Claude)
- **Causa**: Chave copiada errada ou sem créditos
- **Solução**: Verifique créditos em console.anthropic.com/settings/billing

### "0 vagas extraídas"
- **Causa**: Emails já lidos ou keywords muito restritivas
- **Solução**: Marque emails como não lido, revise RELEVANT_KEYWORDS

---

## 📞 Suporte

- [GitHub Issues](https://github.com/seu-usuario/job-intel/issues)
- [Documentação](https://github.com/seu-usuario/job-intel/tree/main/docs)
- Email: ecljunior@gmail.com
