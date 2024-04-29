PG_ADICIONAR_TRANSAC = """
<|layout|columns=1fr auto 1fr|class_name=header_container|

<|part|class_name=header_logo|
<|Cashd|text|height=30px|width=30px|>
|>

<|part|class_name=align_item_stretch|
<|navbar|lov={[("/adicionar_transacao", "Adicionar Transação"), ("/historico_transacoes", "Ver Histórico")]}|>
|>

<|part|class_name=text_right|class_name=header_top_right_corner|
<|🗕|button|on_action=btn_mudar_minimizado|>
<|🗖|button|on_action=btn_mudar_maximizado|>
<|✖|button|on_action=btn_encerrar|>
|>

|>

<br />

<|layout|columns=1 1|columns[mobile]=1

<|part|partial={elem_transac_sel}|>

<|part|partial={elem_transac_form}|>

|>
"""


PG_HIST_TRANSAC = """
<|layout|columns=1fr auto 1fr|class_name=header_container|

<|part|class_name=header_logo|
<|Cashd|text|height=30px|width=30px|>
|>

<|part|class_name=align_item_stretch|
<|navbar|lov={[("/adicionar_transacao", "Adicionar Transação"), ("/historico_transacoes", "Ver Histórico")]}|>
|>

<|part|class_name=text_right|class_name=header_top_right_corner|
<|🗕|button|on_action=btn_mudar_minimizado|>
<|🗖|button|on_action=btn_mudar_maximizado|>
<|✖|button|on_action=btn_encerrar|>
|>

|>


<br />

<|layout|columns=1 1|columns[mobile]=1

<|part|partial={elem_transac_sel}|>

<|part|partial={elem_transac_hist}|>

|>
"""


ELEMENTO_FORM = """
<|
__Data__*

<|{form_transac.DataTransac}|date|format="d-M-y"|>

__Valor__*: R$ <|{display_tr_valor}|text|>

<|{form_transac.Valor}|input|on_change=chg_transac_valor|change_delay=0|>

_(*) Obrigatório_
|>

<br />

<|Inserir|button|class_name=plain|on_action=btn_inserir_transac|>
"""


ELEMENTO_HIST = """
<|Excluir uma transação|button|class_name=plain|on_action={lambda s: s.assign("mostra_selec_cliente", True)}|>
 
Saldo devedor atual: **R$ <|{SLC_USUARIO_SALDO}|>**

<|{df_transac}|table|paginated|height=300px|>

<|{mostra_selec_cliente}|dialog|title=De quem devemos remover esta transação?|width=80%|partial={dial_selec_cliente}|on_action=chg_dialog_selec_cliente_transac|page_id=selecionar_conta|labels=Fechar;Continuar|>

<|{mostra_selec_transac}|dialog|title=Qual transação será removida?|width=80%|partial={dial_selec_transac}|on_action=chg_dialog_selec_transac|page_id=selecionar_transacao|labels=Voltar;Continuar|>

<|{mostra_confirma_transac}|dialog|title=Confirma remoção desta transação?|width=80%|partial={dial_transac_confirmar}|on_action=chg_dialog_confirma_transac|page_id=confirma_remover_transacao|labels=Voltar;Confirmar|>
"""


ELEMENTO_SELEC_CONTA = """
__Cliente__: _<|{form_transac.IdCliente}|text|>_, _<|{nome_cliente_selec}|text|>_

__Saldo devedor__: R$ <|{SLC_USUARIO_SALDO}|>

<|{SLC_USUARIO}|selector|lov={NOMES_USUARIOS}|filter|propagate|height=300px|width=450px|on_change=chg_cliente_selecionado|>
"""
