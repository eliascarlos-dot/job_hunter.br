"""
Perfil profissional de Elias Carlos Lopes - VERSÃO REFINADA
Fonte de verdade para scoring e análise de fit
"""

CANDIDATE_PROFILE = """
NOME: Elias Carlos Lopes
LOCALIZAÇÃO: São Paulo, SP
SENIORIDADE: Executivo Sênior (15+ anos)

EXPERIÊNCIAS CHAVE:
- Mercado Livre | Tracking Center Manager (nov/2021–mar/2026)
  * Monitoramento de ~10.000 veículos/dia (First Mile + Line Haul)
  * Criou SSOT (Single Source of Truth) — dashboards Looker e Tableau adotados por toda a empresa
  * Real Time Tracking: 95% da frota ativa, redução de perdas de conexão com Last Mile
  * ProdOps: interface entre operações regionais, squads de produto (UX/Produto/Dev) e dados
  * Equipe de ~100 colaboradores

- Leo Madeiras | Gerente de Planejamento e Transportes (jul/2020–nov/2021)
  * Torre de Controle do zero: -35% no tempo de atendimento, -15% reclamações pós-venda
  * Implantação Routeasy: +8% entregas/rota
  * 130 pontos de distribuição

- Grupo Imediato (Ambev) | Gerente Regional de Transportes (fev/2018–jul/2020)
  * P&L de R$120M — 5 cervejarias Ambev (SP, SC, MG, PR)
  * Last Mile: 2.500 clientes/dia — CD Ambev Embu, Zona Sul SP
  * S&OP operação empurrada

- Raízen | Gestor de Programação Agroindustrial (out/2017–fev/2018)
  * OBZ Safra 18/19 (R$300M): -25% custos, -20% panes secas

- Ambev | Coordenador de Operações (set/2009–out/2013)
  * 4 promoções em 4 anos

STACK TÉCNICO: Looker, Tableau, SAP, WMS TOTVS, Routeasy, Roadnet, TMS
CERTIFICAÇÕES: Black Belt Lean Six Sigma, AI for Business, Gestão Ágil
FORMAÇÃO: MBA Gestão Ágil e Inovação (Vanzolini/USP em curso), Pós Logística FIA, Adm UFLA
IDIOMAS: Inglês B2, Espanhol Avançado
"""

# Scoring model — pesos por dimensão (total = 100pts)
SCORING_WEIGHTS = {
    "senioridade": 20,
    "setor": 20,
    "escopo": 20,
    "localizacao": 15,
    "stack": 15,
    "porte": 10,
}

FIT_THRESHOLD = 65

TARGET_COMPANIES = [
    "amazon", "shopee", "mercado livre", "mercadolivre",
    "ifood", "rappi", "magalu", "magazine luiza",
    "nestlé", "nestle", "whirlpool", "lg electronics", "lg",
    "quintoandar", "nubank", "totvs", "vtex",
    "dhl", "fedex", "loggi", "jadlog",
]

# FILTRO LÉXICO REFINADO - baseado em análise de falsos positivos
DISCARD_KEYWORDS = [
    # Vendas/Comercial
    "vendas", "comercial", "representante", "account executive",
    "consultor de vendas", "inside sales", "sdr", "bdr",
    "sales manager", "point of sale", "pos", "key account",
    
    # Cargos Júnior/Iniciantes
    "analista junior", "assistente", "estagiário", "estágio",
    "trainee", "aprendiz", "auxiliar",
    
    # TI/Dev (se não for operações de produto)
    "desenvolvedor", "developer", "engenheiro de software",
    "programador", "frontend", "backend", "fullstack",
    
    # Áreas completamente fora
    "jurídico", "legal", "advogado", "compliance legal",
    "imunologia", "farmacêutico", "médico", "enfermeiro",
    "recursos humanos", "rh business partner", "recrutamento",
    "financeiro", "controller", "contabilidade", "fiscal",
    "marketing", "designer", "social media",
    
    # SSMA/Segurança (não é operações logísticas)
    "saúde", "segurança", "meio ambiente", "ssma", "hse",
    "segurança do trabalho", "ehs",
    
    # Locação/Imobiliário (confunde com locação de veículos)
    "locação de imóveis", "locação residencial", "imobiliária",
    "gerente de locação", "location manager",
    
    # Agro/Grãos (muito específico, fora do perfil)
    "originação de grãos", "agrícola", "plantio", "colheita",
    "safra", "fertilizante",
    
    # Varejo físico tradicional (lojas, não e-commerce)
    "gerente de loja", "gerente de filial", "supervisor de loja",
    "vendedor de loja", "balconista",
]

RELEVANT_KEYWORDS = [
    # Senioridade
    "gerente", "head", "manager", "diretor", "director",
    "sênior", "senior manager", "sr manager", "gerente senior",
    "coordenador", "supervisor", "consultor",
    
    # Logística/Supply Chain
    "logística", "logistica", "logistics", "supply chain",
    "operações", "operations", "transportes", "transport",
    "distribuição", "distribuicao", "distribution",
    
    # Áreas específicas (experiência do Elias)
    "last mile", "first mile", "middle mile", "fulfillment",
    "armazém", "armazenagem", "warehouse", "cd",
    "centro de distribuição", "hub",
    
    # Tecnologia/Ferramentas
    "torre de controle", "control tower", "rastreamento",
    "tracking", "monitoramento", "roteirização", "routing",
    "wms", "tms", "oms", "sap", "totvs",
    
    # Contexto E-commerce/Digital
    "e-commerce", "ecommerce", "marketplace", "varejo digital",
    "digital", "tech", "startup",
    
    # Product Operations (experiência MeLi)
    "prodops", "product operations", "ops",
    
    # Frota/Veículos
    "frota", "fleet", "veículos", "motorista", "entregador",
]

# Palavras que EXIGEM contexto adicional (não descarta nem aprova sozinhas)
CONTEXT_REQUIRED = [
    "regional",  # Pode ser logística regional (BOM) ou vendas regional (RUIM)
    "filial",    # Pode ser CD (BOM) ou loja de varejo (RUIM)
    "turno",     # Pode ser operação 24/7 (BOM) ou chão de fábrica (DEPENDE)
]
