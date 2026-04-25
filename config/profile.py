"""
Perfil profissional de Elias Carlos Lopes
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

DISCARD_KEYWORDS = [
    "vendas", "comercial", "representante", "account executive",
    "analista junior", "assistente", "estagiário", "estágio",
    "consultor de vendas", "inside sales", "sdr", "bdr",
    "desenvolvedor", "developer", "engenheiro de software",
    "imunologia", "farmacêutico", "médico",
    "recursos humanos", "rh business partner",
]

RELEVANT_KEYWORDS = [
    "gerente", "head", "manager", "diretor", "director",
    "sênior", "senior manager", "sr manager", "gerente senior", "consultor",
    "logística", "logistica", "logistics", "supply chain",
    "operações", "operations", "transportes", "transport",
    "last mile", "first mile", "fulfillment", "armazém",
    "torre de controle", "control tower", "rastreamento",
    "wms", "tms", "roteirização", "frota",
    "e-commerce", "ecommerce", "marketplace", "varejo digital",
    "prodops", "product operations",
]
