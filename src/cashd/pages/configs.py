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

<|{df_locais_de_backup}|table|page_size=5|on_add={btn_add_local_de_backup}|on_delete={btn_rm_local_de_backup}|>

<|Fazer backup|button|on_action={btn_fazer_backups}|>
* _Backups serão salvos nos Locais de backup._

<|Carregar backup|button|on_action={btn_carregar_backup}|>
* _Não se preocupe, esta operação é reversível. Consulte a documentação._
"""