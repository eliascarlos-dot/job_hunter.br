# 🧪 Teste Brevo - Guia Rápido

## O que este script faz?

Valida sua configuração Brevo **ANTES** de rodar o pipeline completo.

**Testa:**
1. ✅ Variáveis de ambiente configuradas
2. ✅ Conexão com API Brevo
3. ✅ Envio de email de teste

---

## 🚀 Como Usar

### Localmente

```bash
# Certifique-se que as variáveis estão no .env
python test_brevo.py
```

### No Railway

```bash
# As variáveis já estão no Railway
railway run python test_brevo.py
```

---

## 📊 Output Esperado

Se tudo estiver correto:

```
============================================================
🧪 BREVO API - TESTE DE CONFIGURAÇÃO
============================================================
Data: 24/04/2026 22:30

📋 ETAPA 1 — Verificando Variáveis de Ambiente

   ✅ BREVO_API_KEY
      → Chave da API Brevo: xkeysib-abc123...xyz789
   ✅ BREVO_FROM_EMAIL
      → Email remetente: ecljunior@gmail.com
   ✅ EMAIL_RECIPIENT
      → Email destinatário: ecljunior@gmail.com

✅ Todas as variáveis configuradas!

🔌 ETAPA 2 — Testando Conexão API

   🔍 Conectando ao Brevo...
   ✅ Conexão estabelecida!

   📊 Informações da Conta:
      Email: ecljunior@gmail.com
      Plan: Free
      Plan: Ilimitado ou Free (300/dia)

📧 ETAPA 3 — Enviando Email de Teste

   📤 Enviando de: Job Intel Test <ecljunior@gmail.com>
   📥 Enviando para: ecljunior@gmail.com
   ⏳ Aguarde...

   ✅ Email enviado com sucesso!

   📋 Detalhes:
      Message ID: <202604242230.12345@smtp-relay.brevo.com>
      Status: Entregue para processamento

   💡 Verifique sua caixa de entrada:
      → ecljunior@gmail.com
      → Pode levar 1-2 minutos para chegar
      → Cheque SPAM se não aparecer

============================================================
📊 RESUMO DO TESTE
============================================================

   Variáveis de Ambiente: ✅ OK
   Conexão API Brevo:     ✅ OK
   Envio de Email:        ✅ OK

🎉 TUDO FUNCIONANDO PERFEITAMENTE!

🚀 Próximos passos:
   1. Verifique o email de teste
   2. Rode o pipeline completo:
      python main.py --gmail-only
   3. Configure agendamento automático (opcional)
```

---

## ❌ Problemas Comuns

### Erro: "BREVO_API_KEY não configurada"

**Solução:**
```bash
# No .env (localmente)
BREVO_API_KEY=xkeysib-sua_chave_aqui

# No Railway
Adicione a variável nas Settings → Variables
```

### Erro: "API Key inválida ou expirada"

**Solução:**
1. Acesse https://app.brevo.com/
2. SMTP & API → API Keys
3. Gere uma nova chave
4. Atualize a variável

### Erro: "Dados inválidos - sender"

**Solução:**
```bash
# BREVO_FROM_EMAIL deve ser um email válido
BREVO_FROM_EMAIL=seu.email@gmail.com
```

### Email não chegou

**Checklist:**
- ✅ Aguardou 2-3 minutos?
- ✅ Verificou pasta SPAM?
- ✅ Email destinatário está correto?
- ✅ Caixa de entrada não está cheia?

---

## 📧 Email de Teste

O script envia um email HTML bonito com:

- ✅ Visual profissional (gradiente roxo)
- ✅ Confirmação de configuração
- ✅ Checklist do que está funcionando
- ✅ Próximos passos
- ✅ Data/hora do teste

**Exemplo:**

```
🎉 Brevo Funcionando!
━━━━━━━━━━━━━━━━━━━

Olá! 👋

Se você está lendo este email, significa que sua
configuração do Brevo está 100% correta!

✅ Tudo Pronto!
• API Key válida e funcionando
• Email remetente configurado
• Email destinatário recebendo
• Job Intel System pronto para rodar!

Próximo passo: Execute o pipeline completo com:
python main.py --gmail-only
```

---

## 🔧 Modo Debug

Para ver mais detalhes dos requests:

```python
# No test_brevo.py, adicione antes dos imports:
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## ✅ Checklist de Sucesso

Depois de rodar o teste:

- [ ] Script completou sem erros
- [ ] Viu "✅ TUDO FUNCIONANDO PERFEITAMENTE!"
- [ ] Recebeu email de teste na caixa de entrada
- [ ] Email não foi para SPAM
- [ ] Pronto para rodar `main.py`

---

## 🎯 Próximos Passos

**Teste passou? Perfeito!**

1. **Rode o pipeline completo:**
   ```bash
   python main.py --gmail-only
   ```

2. **Configure no Railway:**
   - Adicione as mesmas variáveis
   - Faça deploy
   - Configure cron job diário

3. **Relaxe:**
   - Sistema rodando
   - Emails chegando
   - Vagas sendo filtradas automaticamente 🎉

---

## 📚 Documentação

- **Setup completo:** `docs/BREVO_SETUP.md`
- **Configuração geral:** `docs/SETUP.md`
- **Estrutura do projeto:** `STRUCTURE.md`

---

**Dúvidas?** Abra uma issue no GitHub ou consulte a documentação!
