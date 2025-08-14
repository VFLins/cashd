PG_ANALISE = """
<|layout|columns=.68fr auto 1fr|class_name=header_container|

<|part|class_name=header_logo|
<|Cashd|text|height=30px|width=30px|>
|>

<|part|class_name=align_item_stretch|
<|{nav_analise_val}|toggle|lov={nav_analise_lov}|on_change={lambda s: s.elem_analise.update_content(s, s.nav_analise_val[0])}|>
|>

<|part|class_name=text_right|class_name=header_top_right_corner|
<|🗕|button|on_action=btn_mudar_minimizado|>
<|🗖|button|on_action=btn_mudar_maximizado|>
<|✖|button|on_action=btn_encerrar|>
|>

|>

<|part|partial={elem_analise}|class_name=container|>
"""


ELEM_PLOT = """
<|layout|columns=1fr 1fr 2fr|class_name=top_controls|


<|{dropdown_tipo_val}|selector|lov={dropdown_tipo_lov}|dropdown|>

<|{dropdown_periodo_val}|selector|lov={dropdown_periodo_lov}|dropdown|>

<|{slider_val}|slider|lov={slider_lov}|text_anchor=botom|>

|>

<center>
<|Atualizar|button|on_action={btn_gerar_main_plot}|>
</center>

<br />

<|chart|figure={main_plot}|height=360px|>
"""

ELEM_HIST = """
<br />

<|layout|columns=1.2fr .7fr|

<|part|
<|layout|columns=.9 .1fr|class_name=interactive_header|
# Últimas transações

<|↻|button|on_action={btn_atualizar_df_ult_transac}|>
|>
<|{df_ult_transac}|table|paginated|page_size=10|page_size_options={[25, 50]}|height=360px|>
|>

<|part|
# Maiores saldos

<|{df_maiores_saldos}|table|show_all|height=412px|>
|>

|>
"""
