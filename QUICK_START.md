# ⚡ Quick Start - Job Intel System

## 🚀 Instalação Rápida (5 minutos)

### 1. Clone
```bash
git clone https://github.com/eclopesjr/job-intel.git
cd job-intel
```

### 2. Configure
```bash
cp .env.example .env
# Edite .env com suas credenciais
```

### 3. Instale
```bash
pip install -r requirements.txt
```

### 4. Teste
```bash
python test_brevo.py
python main.py --gmail-only --dry-run
```

### 5. Rode
```bash
python main.py --gmail-only
```

## ✅ Deploy Railway

1. Push para GitHub
2. Railway → New Project → Import from GitHub
3. Adicionar variáveis (Settings → Variables)
4. Configurar Cron: `0 7 * * 1-5` → `python main.py`

**Pronto!** 🎉

Documentação completa: `docs/SETUP.md`
