PG_CONFIG = """
<|layout|columns=.68fr auto 1fr|persistent|class_name=header_container|

<|part|class_name=header_logo|
<|Cashd|text|height=30px|width=30px|>
|>

<|part|class_name=align_item_stretch|
<|{nav_config_val}|toggle|lov={nav_config_lov}|on_change={lambda s: s.elem_config.update_content(s, nav_config_val[0])}|>
|>

<|part|class_name=text_right|class_name=header_top_right_corner|
<|🗕|button|on_action=btn_mudar_minimizado|>
<|🗖|button|on_action=btn_mudar_maximizado|>
<|✖|button|on_action=btn_encerrar|>
|>

|>

<br />

<|part|partial={elem_config}|class_name=narrow_element|>

<br />
"""

ELEMENTO_BACKUP = """
# Locais de backup

Clique no símbolo de **+** abaixo para adicionar um **Local de backup**:

<br />

<|{df_locais_de_backup}|table|page_size=5|on_add={btn_add_local_de_backup}|on_delete={btn_rm_local_de_backup}|>

# Ações

<|Fazer backup|button|on_action={btn_fazer_backups}|>

*_Backups serão salvos nos Locais de backup._

<br />

<|Carregar backup|button|on_action={btn_carregar_backup}|class_name=plain|>

*_Não se preocupe, esta operação é reversível. Consulte a documentação._
"""

ELEMENTO_ATALHO = """
# Atalhos

<|Adicionar atalho|button|on_action={btn_criar_atalho}|class_name=plain|>

*_Atalhos serão adicionados ao menu iniciar e à área de trabalho._

<br />

# Sessão

Executando em http://127.0.0.1:<|{port}|text|>
"""
