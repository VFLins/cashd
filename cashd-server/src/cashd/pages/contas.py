PG_CONTAS = """
<|layout|columns=1fr 1fr|class_name=header_container|

<|part|class_name=header_logo|
<|Cashd|text|height=30px|width=30px|>
|>

<|part|class_name=text_right|class_name=header_top_right_corner|
<|🗕|button|on_action=btn_mudar_minimizado|>
<|🗖|button|on_action=btn_mudar_maximizado|>
<|✖|button|on_action=btn_encerrar|>
|>

|>

<br />

<|part|partial={elem_conta}|class_name=container|>
"""


ELEMENTO_FORM = """
<|layout|columns=1 1|columns[mobile]=1 1|class_name=container
__Primeiro Nome__*

__Sobrenome__*

<|{form_customer.PrimeiroNome}|input|>

<|{form_customer.Sobrenome}|input|>

__Apelido__

__Telefone__*

<|{form_customer.Apelido}|input|>

<|{form_customer.Telefone}|input|label=DDD + 9 dígitos|>

__Endereço__

__Bairro__

<|{form_customer.Endereco}|input|>

<|{form_customer.Bairro}|input|>

__Cidade__*

__Estado__*

<|{form_customer.Cidade}|input|>

<|{form_customer.Estado}|selector|lov={dropdown_uf_lov}|dropdown|>

_(*) Obrigatório_

<|Inserir|button|class_name=plain|on_action=add_customer|>

|>
"""

