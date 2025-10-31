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
<|Informações do cliente|button|on_action={btn_edit_customer}|>

<|{df_transac}|table|editable|paginated|on_delete=rm_transaction|on_edit=False|on_add=False|columns=Data;Valor|height=300px|>


<|{show_dialog_edit_customer}|dialog|title=Editando...|width=80%|partial={dialog_edit_customer}|on_action={dialog_edit_customer_action}|page_id=editar_conta|labels=Salvar alterações|>

<|{show_dialog_confirm_edit_customer}|dialog|title=Confirma alterações?|width=80%|partial={dialog_confirm_edit_customer}|on_action={dialog_confirm_edit_customer_action}|page_id=confirmar_alteracoes_conta|labels=Voltar;Confirmar|>
"""


ELEMENTO_SELEC_CONTA = """

<|{search_user_input_value}|input|label=Pesquisa|on_change={chg_cliente_pesquisa}|class_name=sel-user user-search-input|>

<|{SELECTED_CUSTOMER}|selector|lov={NOMES_USUARIOS}|propagate|height=300px|width=450px|adapter={adapt_lovitem}|on_change={chg_selected_customer}|class_name=sel-user user-selector|>

<|{search_user_pagination_legend}|text|class_name=small-text|>
<|Anterior|button|class_name=small-button|on_action=btn_prev_page_customer_search|>
<|Próxima|button|class_name=small-button|on_action=btn_next_page_customer_search|>
"""
