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
# Título do gráfico

<|chart|figure={main_plot}|config={dict(displayModeBar=False)}|>
"""