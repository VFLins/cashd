PG_TRANSAC = """
<|layout|columns=.68fr auto 1fr|class_name=header_container|

<|part|class_name=header_logo|
<|Cashd|text|height=30px|width=30px|>
|>

<|part|class_name=align_item_stretch|
<|{nav_transac_val}|toggle|lov={nav_transac_lov}|on_change={lambda s: s.elem_transac_form.update_content(s, s.nav_transac_val[0])}|>
|>

<|part|class_name=text_right header_top_right_corner|
<|🗕|button|on_action=btn_mudar_minimizado|>
<|🗖|button|on_action=btn_mudar_maximizado|>
<|✖|button|on_action=btn_encerrar|>
|>

|>

__Cliente__: _<|{nome_cliente_selec}|text|>_

__Local__: _<|{SELECTED_CUSTOMER_PLACE}|text|>_

__Saldo devedor__: R$ <|{SELECTED_CUSTOMER_BALANCE}|>

<|layout|columns=1 1|columns[mobile]=1

<|part|partial={elem_transac_sel}|>

<|part|partial={elem_transac_form}|>

|>
"""


ELEMENTO_FORM = """
<|
__Data__*

<|{form_transac.DataTransac}|date|format=dd/MM/y|>

__Valor__*: R$ <|{display_tr_valor}|text|>

<|{form_transac.Valor}|input|on_change=chg_transac_valor|on_action=add_transaction|change_delay=0|>

<small><i>(*) Obrigatório</i></small>
|>

<br />

<|Inserir|button|class_name=plain|on_action=add_transaction|>
"""


ELEMENTO_HIST = """
<|Excluir uma transação|button|on_action=btn_mostrar_dialogo_selec_transac|>
 
Saldo devedor atual: **R$ <|{SELECTED_CUSTOMER_BALANCE}|>**

<|{df_transac}|table|editable|paginated|on_delete=rm_transaction|on_edit=False|on_add=False|columns=Data;Valor|height=300px|>

<|{mostra_selec_transac}|dialog|title=Qual transação será removida?|width=80%|partial={dial_selec_transac}|on_action=chg_dialog_selec_transac|page_id=selecionar_transacao|labels=Cancelar;Continuar|>

<|{mostra_confirma_transac}|dialog|title=Confirma remoção desta transação?|width=80%|partial={dial_transac_confirmar}|on_action=chg_dialog_confirma_transac|page_id=confirma_remover_transacao|labels=Voltar;Confirmar|>
"""


ELEMENTO_SELEC_CONTA = """

<|{search_user_input_value}|input|label=Pesquisa|on_change={chg_cliente_pesquisa}|class_name=sel-user user-search-input|>

<|{SELECTED_CUSTOMER}|selector|lov={NOMES_USUARIOS}|propagate|height=300px|width=450px|adapter={adapt_lovitem}|on_change={chg_selected_customer}|class_name=sel-user user-selector|>

<|{search_user_pagination_legend}|text|class_name=small-text|>
<|Anterior|button|class_name=small-button|on_action=btn_prev_page_customer_search|>
<|Próxima|button|class_name=small-button|on_action=btn_next_page_customer_search|>
"""
