# dashboard-comercial/tests/fixtures.py
import pandas as pd
from datetime import date

EMPRESAS = pd.DataFrame({
    "ID": ["EMP001", "EMP002", "EMP003"],
    "Nome da Empresa": ["Metalúrgica Souza", "Distribuidora Norte", "Alpha Contabilidade"],
    "CNPJ": ["12.345.678/0001-99", None, "55.123.456/0001-77"],
    "Segmento": ["Indústria", "Comércio", "Contabilidade"],
    "Cidade": ["São Paulo", "Campinas", "São Paulo"],
    "Estado": ["SP", "SP", "SP"],
    "Nome Contato": ["Carlos Souza", "Ana Lima", "Roberto Alves"],
    "Cargo": ["Diretor", "Gerente Financeiro", "Sócio"],
    "Telefone": ["(11) 99999-0001", "(19) 98888-0002", "(11) 97777-0003"],
    "E-mail": ["carlos@souza.com", "ana@dnorte.com.br", "roberto@alpha.cnt"],
    "Temperatura": ["Quente", "Normal", "Quente"],
    "Porte": ["Médio", "Grande", "Pequeno"],
    "Origem Lead": ["Indicação", "Prospecção ativa", "LinkedIn"],
    "Observações Gerais": ["Interesse REFIS", "Aguarda diretoria", "Reunião marcada"],
    "Ativo?": ["SIM", "SIM", "SIM"],
})

VISITAS = pd.DataFrame({
    "Data": [
        date(2026, 1, 2), date(2026, 1, 15), date(2026, 2, 10),
        date(2026, 3, 20),
    ],
    "ID Empresa": ["EMP001", "EMP002", "EMP002", "EMP003"],
    "Etapa": ["1ª Visita", "1ª Visita", "2ª Visita", "Reunião de Fechamento"],
    "Visita Realizada?": ["SIM", "SIM", "SIM", "SIM"],
    "Procuração Assinada?": ["NÃO", "NÃO", "NÃO", "SIM"],
    "Proposta Enviada?": ["NÃO", "NÃO", "SIM", "SIM"],
    "Contrato Fechado?": ["NÃO", "NÃO", "NÃO", "NÃO"],
    "Duração (min)": [45, 30, 60, 90],
    "Resultado": ["Positivo", "Neutro", "Positivo", "Positivo"],
    "Interesse (1-5)": [5, 3, 4, 5],
    "Próxima Ação": ["Agendar 2ª visita", "Aguardar retorno", "Aguardar procuração", "Reunião assinatura"],
    "Data Próx. Ação": [date(2026, 2, 15), date(2026, 2, 1), date(2026, 2, 25), date(2026, 4, 15)],
    "Obstáculo": [None, "Decisão em comitê", "Aguarda jurídico", None],
    "Relatório Resumido": ["Diretor receptivo", "Gerente receptiva", "Apresentou simulação", "Sócio aprovou"],
    "Registrado por": ["João Silva"] * 4,
})

CONFIG = {
    "nome_agente": "João Silva",
    "sla_quente_dias": 30,
    "sla_normal_dias": 90,
    "ano_filtro": 2026,
    "empresa_nome": "Inteligência Tributária Ltda",
    "cor_primaria": "#001b47",
    "cor_acento": "#af946c",
    "alerta_amarelo_pct": 75,
    "mostrar_cnpj": "SIM",
    "mostrar_telefone": "NÃO",
}
