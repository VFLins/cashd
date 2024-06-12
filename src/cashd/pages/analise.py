PG_ANALISE = """
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

<|part|partial={elem_analise}|class_name=container|>
"""


ELEM_MAIN = """
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
<|layout|columns=1fr 1fr|

<|part|class_name=header_logo|
# Últimas transações

<|{df_ult_transac}|table|paginated|filter|page_size=6|page_size_options={[12,24,36]}|>
|>

<|part|class_name=header_logo|
# Maiores saldos


|>

|>
"""