# chamado em:
#   contas.ELEMENTO_REGS
SELECIONAR_CLIENTE_ETAPA = """
<|{search_user_input_value}|input|label=Pesquisa|on_change={chg_cliente_pesquisa}|class_name=sel-user user-search-input|>

<|{SELECTED_CUSTOMER}|selector|lov={NOMES_USUARIOS}|propagate|height=300px|width=450px|adapter={adapt_lovitem}|on_change={chg_selected_customer}|class_name=sel-user user-selector|>

<|{search_user_pagination_legend}|text|class_name=small-text|>
<|Anterior|button|class_name=small-button|on_action=btn_prev_page_customer_search|>
<|Próxima|button|class_name=small-button|on_action=btn_next_page_customer_search|>
"""

FORM_EDITAR_CLIENTE = """
<|layout|columns=1 1|columns[mobile]=1 1|class_name=container
__Primeiro Nome__*

__Sobrenome__*

<|{selected_customer_handler.PrimeiroNome}|input|>

<|{selected_customer_handler.Sobrenome}|input|>

__Apelido__

__Telefone__

<|{selected_customer_handler.Apelido}|input|>

<|{selected_customer_handler.Telefone}|input|label=DDD + 9 dígitos|>

__Endereço__

__Bairro__

<|{selected_customer_handler.Endereco}|input|>

<|{selected_customer_handler.Bairro}|input|>

__Cidade__*

__Estado__*

<|{selected_customer_handler.Cidade}|input|>

<|{selected_customer_handler.Estado}|input|>

_(*) Obrigatório_
|>
"""

CONFIRMAR_CONTA = """
<|layout|columns=1 1|columns[mobile]=1 1|class_name=container
Primeiro Nome: *<|{selected_customer_handler.PrimeiroNome}|>*

Sobrenome: *<|{selected_customer_handler.Sobrenome}|>*

Apelido: *<|{selected_customer_handler.Apelido}|>*

Telefone: *<|{selected_customer_handler.Telefone}|>*

Endereço: *<|{selected_customer_handler.Endereco}|>*

Bairro: *<|{selected_customer_handler.Bairro}|>*

Cidade: *<|{selected_customer_handler.Cidade}|>*

Estado: *<|{selected_customer_handler.Estado}|>*
|>
"""
