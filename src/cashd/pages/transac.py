PG_TRANSAC = """
<|layout|columns=.68fr auto 1fr|class_name=header_container|

<|part|class_name=header_logo|
<|Cashd|text|height=30px|width=30px|>
|>

<|part|class_name=align_item_stretch|
<|{nav_transac_val}|toggle|lov={nav_transac_lov}|on_change={lambda s: s.elem_transac_form.update_content(s, nav_transac_val[0])}|>
|>

<|part|class_name=text_right|class_name=header_top_right_corner|
<|🗕|button|on_action=btn_mudar_minimizado|>
<|🗖|button|on_action=btn_mudar_maximizado|>
<|✖|button|on_action=btn_encerrar|>
|>

|>

<br /><br />

<|layout|columns=1 1|columns[mobile]=1

<|part|partial={elem_transac_sel}|>

<|part|partial={elem_transac_form}|>

|>
"""


ELEMENTO_FORM = """
<|
__Data__*
<|{display_tr_data}|date|not editable|class_name=invisible|format=e|>

<|{display_tr_data}|date|>

__Valor__*: R$ <|{display_tr_valor}|text|>

<|{form_transac.Valor}|input|on_change=chg_transac_valor|change_delay=0|>

_(*) Obrigatório_
|>

<br />

<|Inserir|button|class_name=plain|on_action=btn_inserir_transac|>
"""


ELEMENTO_HIST = """
<|Excluir uma transação|button|on_action=btn_mostrar_dialogo_selec_transac|>
 
Saldo devedor atual: **R$ <|{SLC_USUARIO_SALDO}|>**

<|{df_transac}|table|paginated|height=300px|>

<|{mostra_selec_transac}|dialog|title=Qual transação será removida?|width=80%|partial={dial_selec_transac}|on_action=chg_dialog_selec_transac|page_id=selecionar_transacao|labels=Cancelar;Continuar|>

<|{mostra_confirma_transac}|dialog|title=Confirma remoção desta transação?|width=80%|partial={dial_transac_confirmar}|on_action=chg_dialog_confirma_transac|page_id=confirma_remover_transacao|labels=Voltar;Confirmar|>
"""


ELEMENTO_SELEC_CONTA = """
__Cliente__: _<|{nome_cliente_selec}|text|>_

__Local__: _<|{SLC_USUARIO_LOCAL}|text|>_

__Saldo devedor__: R$ <|{SLC_USUARIO_SALDO}|>

<|{SLC_USUARIO}|selector|lov={NOMES_USUARIOS}|filter|propagate|height=300px|width=450px|on_change=chg_cliente_selecionado|>
"""
