from random import choice, randint
from datetime import date, datetime, timedelta
from cashd_core.data import tbl_clientes, tbl_transacoes


nomes = [
    "José",
    "Maria",
    "João",
    "Ana",
    "Pedro",
    "Luiza",
    "Carlos",
    "Julia",
]
apelidos = [
    None,
    None,
    None,
    None,
    None,
    None,
    "Nem",
    "Tim",
    "Pepeta",
    "Zé",
]
sobrenomes = [
    "Silva",
    "Oliveira",
    "Santos",
    "Almeida",
    "Ferreira",
    "Ribeiro",
    "Pereira",
    "Costa",
]
cidades = [
    "Palmares",
    "Recife",
    "Olinda",
    "Jaboatão",
    "Paulista",
    "Ipojuca",
    "Cabo de Santo Agostinho",
    "São Lourenço da Mata",
]
bairros = [
    "Centro",
    "Engenho Tambor",
    "Engenho Viola",
    "São José",
    "Nova Descoberta",
    "Pedreiras",
    "Santo Antônio",
    "São Francisco",
]

customer_info = [
    {
        "id": i,
        "title": f"{i}, {choice(nomes)} {choice(sobrenomes)}",
        "subtitle": f"{choice(bairros)} - {choice(cidades)}/PE",
    }
    for i in range(1, 501)
]

customers = [
    dict(
        PrimeiroNome=choice(nomes),
        Sobrenome=choice(sobrenomes),
        Endereco="",
        Bairro=choice(bairros),
        Cidade=choice(cidades),
        Estado="PE",
    )
    for i in range(500)
]

transactions = [
    dict(
        IdCliente=int(i / 4) + 1,
        CarimboTempo=datetime.today() - timedelta(days=2001 - i),
        DataTransac=date.today() - timedelta(days=2001 - i),
        Valor=randint(1, 20000),
    )
    for i in range(2000)
]
