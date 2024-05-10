CONTROLES = """
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

<|Backup|expandable|expand={expand_backup_ctrl}|partial={elem_config_backup}|>

"""

ELEMENTO_BACKUP = """
Clique no símbolo de **+** abaixo para adicionar um **Local de backup**:

<|{df_locais_de_backup}|table|page_size=5|page_size_options=[3,5,10,15]|on_add={btn_add_local_de_backup}|on_delete={btn_rm_local_de_backup}|>
"""