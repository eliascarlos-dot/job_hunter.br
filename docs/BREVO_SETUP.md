# 📧 Brevo (ex-Sendinblue) Setup - Guia Completo

## 🎯 Por que Brevo?

**Brevo é MELHOR que SendGrid para Job Intel:**

✅ **300 emails/dia grátis** (vs 100/dia SendGrid)  
✅ **9.000 emails/mês** (vs 5.000 SendGrid)  
✅ Setup mais simples (5 min vs 10 min)  
✅ Não precisa verificar remetente (automático)  
✅ Interface mais amigável  
✅ Suporte em português  

---

## 🚀 Setup em 5 minutos

### 1️⃣ Criar Conta Brevo (2 min)

1. Acesse: **https://app.brevo.com/account/register**
2. Preencha:
   ```
   Email: ecljunior@gmail.com
   Password: Crie uma senha forte
   ```
3. Marque "I agree to the Terms & Conditions"
4. Clique em **"Sign up for free"**
5. **Confirme seu email** (cheque caixa de entrada)

---

### 2️⃣ Criar API Key (2 min)

Após login:

1. Canto superior direito → **Seu nome** → **"SMTP & API"**
2. Aba **"API Keys"**
3. Botão **"Generate a new API key"**
4. Configure:
   ```
   Name: job-intel-railway
   ```
5. Clique em **"Generate"**
6. **⚠️ COPIE A CHAVE AGORA!** (só mostra 1 vez)
   ```
   xkeysib-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-yyyyyyyyyyyyyyyy
   ```
7. Cole em algum lugar seguro

**PRONTO!** ✅ Não precisa verificar remetente (Brevo faz automaticamente)

---

### 3️⃣ Configurar no Railway (1 min)

No Railway, adicione estas variáveis:

```bash
BREVO_API_KEY=xkeysib-sua_chave_copiada_no_passo_2
BREVO_FROM_EMAIL=ecljunior@gmail.com
BREVO_FROM_NAME=Job Intel System
EMAIL_RECIPIENT=ecljunior@gmail.com
```

---

### 4️⃣ Testar (30 segundos)

**Localmente:**
```bash
python -m modules.brevo_sender
```

Você deve ver:
```
🧪 Testando envio Brevo...
✅ Email enviado via Brevo (ID: <202604241234567890>)
✅ Teste concluído! Verifique seu email.
```

**No Railway:**
```bash
python main.py --gmail-only
```

---

## 🔧 Troubleshooting

### ❌ "Unauthorized: Invalid api key"

**Problema:** API Key incorreta ou expirada

**Solução:**
1. Vá em SMTP & API → API Keys
2. Gere uma nova chave
3. Atualize `BREVO_API_KEY` no Railway

---

### ❌ "Invalid email address"

**Problema:** Email remetente inválido

**Solução:**
1. Use um email real em `BREVO_FROM_EMAIL`
2. Formato: `seu.nome@gmail.com`

---

### ⚠️ Emails caindo no SPAM?

**Solução:**
1. Configure SPF/DKIM (opcional mas recomendado)
2. Brevo → Settings → Senders & IP
3. Siga instruções de verificação de domínio

Para Gmail pessoal, não é necessário (Brevo já tem reputação boa)

---

## 📊 Monitoramento

Acompanhe seus envios:

1. **Dashboard Brevo** → **Statistics**
2. Você verá:
   - Emails enviados
   - Taxa de entrega
   - Aberturas
   - Cliques

---

## 🆚 Comparação Completa

| Recurso | Brevo | SendGrid | Gmail SMTP |
|---------|-------|----------|------------|
| **Grátis/dia** | 300 | 100 | 500 |
| **Grátis/mês** | 9.000 | 5.000 | ~15.000 |
| **Railway** | ✅ | ✅ | ❌ |
| **Setup** | 5 min | 10 min | 3 min |
| **Verificação** | Automática | Manual | Manual |
| **UI** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Suporte PT** | ✅ | ❌ | ✅ |
| **Recomendado** | ✅ | ✅ | ❌ (Railway) |

**VEREDITO: Use Brevo!** 🏆

---

## 💡 Dicas

### 1. Economize cota diária
- Configure `MAX_JOBS_TO_ANALYZE=50` no .env
- Você só enviará 1 email/dia (briefing)
- Nunca vai estourar 300/dia

### 2. Template HTML
O Brevo aceita o mesmo HTML que você já usa no sistema.
Não precisa mudar nada!

### 3. Múltiplos destinatários
```python
# No brevo_sender.py, você pode adicionar:
"to": [
    {"email": "ecljunior@gmail.com"},
    {"email": "outro@email.com"}
]
```

---

## 🔐 Segurança

**NUNCA** comite sua API Key no GitHub!

✅ Correto:
```bash
# .env (ignorado pelo git)
BREVO_API_KEY=xkeysib-xxxxx
```

❌ Errado:
```python
# brevo_sender.py (NUNCA!)
BREVO_API_KEY = "xkeysib-xxxxx"
```

Se você expor a chave acidentalmente:
1. Brevo → SMTP & API → API Keys
2. Delete a chave comprometida
3. Gere uma nova

---

## 📈 Upgrade (Opcional)

Se precisar de mais emails:

| Plano | Emails/mês | Custo |
|-------|------------|-------|
| **Free** | 9.000 | R$ 0 |
| **Starter** | 20.000 | R$ 119/mês |
| **Business** | 100.000 | R$ 349/mês |

**Job Intel usa ~30-60/mês** → Free é mais que suficiente! 💰

---

## ✅ Checklist Final

- [ ] Conta Brevo criada
- [ ] Email confirmado
- [ ] API Key gerada e copiada
- [ ] Variáveis configuradas no Railway
- [ ] Teste enviado com sucesso
- [ ] Email recebido na caixa de entrada

**Tudo ok? Sistema 100% funcional! 🎉**

---

## 📞 Suporte

- **Docs:** https://developers.brevo.com/
- **Help Center:** https://help.brevo.com/
- **Status:** https://status.brevo.com/
- **Chat:** Disponível no dashboard

---

## 🔄 Migração SendGrid → Brevo

Se você já configurou SendGrid e quer migrar:

**Vantagens de migrar:**
- 3x mais emails grátis (9k vs 3k)
- Setup mais simples
- UI melhor

**Como migrar:**
1. Configure Brevo (5 min - passos acima)
2. No Railway, mude prioridade:
   ```bash
   # Remova ou comente:
   # SENDGRID_API_KEY=...
   
   # Adicione:
   BREVO_API_KEY=xkeysib-xxxxx
   ```
3. Sistema usa Brevo automaticamente (fallback já implementado)

---

## 🎁 Bônus: Features Extras Brevo

Além de emails transacionais, Brevo oferece:

- 📧 **Email Marketing** (campanhas)
- 💬 **SMS** (pago)
- 📞 **WhatsApp Business** (pago)
- 🤖 **Marketing Automation**
- 📊 **CRM** (básico grátis)

Útil se você quiser expandir o Job Intel no futuro!

---

**Recomendação final: Configure Brevo agora (5 min). É mais rápido e melhor que SendGrid!** 🚀
