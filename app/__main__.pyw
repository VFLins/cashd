import db
import backup
from pages import transac, contas, analise, configs, dialogo 

from taipy.gui import Gui, notify, State, navigate, Icon, builder
from datetime import datetime
from os import path
import pandas as pd
import threading
import webview
import socket


####################
# BOTOES
####################

def btn_mostrar_dialogo(state: State, id: str, payload: dict, show: str):
    show_dialogs = {
        "confirma_conta": "mostra_confirma_conta",
        "confirma_transac": "mostra_confirma_transac",
        "selec_cliente": "mostra_selec_cliente",
        "edita_cliente": "mostra_form_editar_cliente"
    }
    for dialog in show_dialogs.values():
        state.assign(dialog, False)
    state.assign(show_dialogs[show], True)

def btn_mostrar_dialogo_selec_cliente(state: State, id: str, payload: dict):
    btn_mostrar_dialogo(state, id, payload, show="selec_cliente")

def btn_mostrar_dialogo_edita_cliente(state: State, id: str, payload: dict):
    btn_mostrar_dialogo(state, id, payload, show="edita_cliente")


def btn_atualizar_listagem(state: State):
    with db.DB_ENGINE.connect() as conn, conn.begin():
        state.df_clientes = pd.read_sql_query("SELECT * FROM clientes", con=conn)


def btn_inserir_transac(state: State):
    carregar_lista_transac(state=state)
    try:
        nova_transac: dict = state.form_transac.despejar(IdCliente = SLC_USUARIO[0])

        db.adicionar_transac(db.tbl_transacoes(CarimboTempo=datetime.now(), **nova_transac))
        notify(state, "success", f"Nova transação adicionada!")

        id_selecionado = int(nova_transac["IdCliente"])
        state.assign("SLC_USUARIO", state.NOMES_USUARIOS[id_selecionado-1])
        state.assign("display_tr_valor", "0,00")
        state.refresh("form_transac")

    except Exception as msg_erro:
        notify(state, "error", str(msg_erro))


def btn_inserir_cliente(state: State):
    try:
        novo_cliente: db.FormContas = state.form_contas.despejar()
        db.adicionar_cliente(db.tbl_clientes(**novo_cliente))

        nome_completo = f"{novo_cliente['PrimeiroNome']} {novo_cliente['Sobrenome']}"
        notify(state, "success", message=f"Novo cliente adicionado!\n{nome_completo}")
        state.refresh("form_contas")
        state.NOMES_USUARIOS = sel_listar_clientes()

    except Exception as msg_erro:
        notify(state, "error", str(msg_erro))


def btn_encerrar():
    window.destroy()
    backup.run()
    raise KeyboardInterrupt("Encerrando...")


def btn_mudar_maximizado():
        window.toggle_fullscreen()


def btn_mudar_minimizado():
    window.minimize()


####################
# UTILS
####################

def carregar_lista_transac(state: State):
    elems = db.listar_transac_cliente(state.SLC_USUARIO[0])
    state.df_transac = elems["df"]
    state.SLC_USUARIO_SALDO = elems["saldo"]
    state.refresh("df_transac")
    state.refresh("SLC_USUARIO_SALDO")


def sel_listar_clientes():
    clientes = db.listar_clientes()
    return [(str(i["id"]), i["nome"]) for i in clientes]


def menu_lateral(state, action, info):
    page = info["args"][0]
    navigate(state, to=page)


####################
# ON ACTION
####################

def chg_dialog_selec_cliente_conta(state: State, id: str, payload: dict):
    with state as s:
        if payload["args"][0] < 1:
            s.assign("mostra_selec_cliente", False)

        if payload["args"][0] == 1:
            if s.SLC_USUARIO[0] == "0":
                notify(s, "error", "Nenhuma conta foi selecionada")
            else:
                cliente_selec = db.cliente_por_id(s.SLC_USUARIO[0])
                s.form_conta_selec.carregar_valores(cliente_selec)
                s.refresh("form_conta_selec")
                s.assign("mostra_selec_cliente", False)
                s.assign("mostra_form_editar_cliente", True)


def chg_dialog_editar_cliente(state: State, id: str, payload: dict):
    with state as s:
        if payload["args"][0] == -1:
            s.assign("mostra_selec_cliente", False)
        
        if payload["args"][0] == 0:
            s.assign("mostra_form_editar_cliente", False)
            s.assign("mostra_selec_cliente", True)

        if payload["args"][0] == 1:
            s.assign("mostra_form_editar_cliente", False)
            s.assign("mostra_confirma_conta", True)


def chg_dialog_confirma_cliente(state: State, id: str, payload: dict):
    with state as s:
        if payload["args"][0] == 1:
            try:
                db.atualizar_cliente(
                    state.SLC_USUARIO[0],
                    state.form_conta_selec
                    )
                state.NOMES_USUARIOS = sel_listar_clientes()
                notify(s, "success", "Cadastro atualizado com sucesso!")

            except Exception as xpt:
                notify(s, "error", f"Erro ao atualizar cadastro: {str(xpt)}")
                s.assign("mostra_confirma_conta", False)

        s.assign("mostra_confirma_conta", False)


def chg_dialog_selec_cliente_transac(state: State, id: str, payload: dict):
    with state as s:
        if payload["args"][0] < 1:
            s.assign("mostra_selec_cliente", False)
        
        if payload["args"][0] == 1:
            if s.SLC_USUARIO == "0":
                notify(s, "error", "Nenhum usuário foi selecionado")
            else:
                s.TRANSACS_USUARIO = db.listar_transac_cliente(s.SLC_USUARIO[0], False)
                s.assign("mostra_selec_cliente", False)
                s.assign("mostra_selec_transac", True)


def chg_dialog_selec_transac(state: State, id: str, payload: dict):
    with state as s:
        if payload["args"][0] == 0:
            s.assign("mostra_selec_cliente", True)

        if payload["args"][0] == 1:
            if s.SLC_TRANSAC == "0":
                notify(s, "error", "Nenhuma transação foi selecionada")
            elif not db.id_transac_pertence_a_cliente(s.SLC_TRANSAC[0], s.SLC_USUARIO[0]):
                notify(s, "error", "Selecione uma transação antes de continuar")
                return
            else:
                transac_selec = db.transac_por_id(s.SLC_TRANSAC[0])
                s.form_transac_selec.carregar_valores(transac_selec)
                s.refresh("form_transac_selec")
                s.assign("mostra_confirma_transac", True)
        s.assign("mostra_selec_transac", False)


def chg_dialog_confirma_transac(state: State, id: str, payload: dict):
    with state as s:
        s.assign("mostra_confirma_transac", False)
        
        if payload["args"][0] == 0:
            s.assign("mostra_selec_transac", True)

        if payload["args"][0] == 1:
            db.remover_transac(s.SLC_TRANSAC[0])
            notify(s, "success", "Transação removida.")
            s.assign("SLC_TRANSAC", "0")
            

def chg_transac_valor(state: State) -> None:
    state.display_tr_valor = db.fmt_moeda(
        state.form_transac.Valor,
        para_mostrar=True)
    state.refresh("form_transac")
    return


def chg_cliente_selecionado(state: State) -> None:
    carregar_lista_transac(state=state)
    state.form_transac.IdCliente = int(state.SLC_USUARIO[0])
    state.nome_cliente_selec = state.SLC_USUARIO[1]
    state.refresh("form_transac")


####################
# VALORES INICIAIS
####################

# visibilidade de dialogos
mostra_selec_cliente = False
mostra_selec_transac = False
mostra_form_editar_cliente = False
mostra_confirma_conta = False
mostra_confirma_transac = False

# listagem de clientes
with db.DB_ENGINE.connect() as conn, conn.begin():
    df_clientes = pd.read_sql_query("SELECT * FROM clientes", con=conn)

# valor inicial do campo "Valor" no menu "Adicionar Transacao"
display_tr_valor = "0,00"

# valor inicial do seletor de conta global
NOMES_USUARIOS = sel_listar_clientes()
if len(NOMES_USUARIOS) > 0:
    SLC_USUARIO = NOMES_USUARIOS[0]
else:
    SLC_USUARIO = "0"

# formularios
form_contas = db.FormContas()
form_transac = db.FormTransac(IdCliente=SLC_USUARIO[0])
form_conta_selec = db.FormContas()
form_transac_selec = db.FormTransac(IdCliente=SLC_USUARIO[0])


# nome do cliente selecionado
nome_cliente_selec = ""

# valor inicial do seletor de transacao global
TRANSACS_USUARIO = db.listar_transac_cliente(SLC_USUARIO[0], para_mostrar=False)
if len(TRANSACS_USUARIO) > 0:
    SLC_TRANSAC = TRANSACS_USUARIO[0]
else:
    SLC_TRANSAC = "0"

# define se a webview vai iniciar em tela cheia
maximizado = False

# valor inicial da tabela de transacoes do usuario selecionado em SLC_USUARIO
df_transac = db.listar_transac_cliente(SLC_USUARIO[0])["df"]

# valor inicial do saldo do usuario selecionado em SLC_USUARIO
SLC_USUARIO_SALDO = db.listar_transac_cliente(SLC_USUARIO[0])["saldo"]

# dados de entradas e abatimentos
df_entradas_abatimentos = db.saldos_transac_periodo()
layout_df_entradas_abatimentos = {
    "x":"Data",
    "y[1]": "Somas",
    "y[2]": "Abatimentos",
    "layout": {
        "barmode": "overlay",
        "barcornerradius": "20%",
        "hovermode": "x unified",
        "hovertemplate": "<b>Total</b>: R$ %{y:.2f}"
    }}
config_df_entradas_abatimentos = {
    "displaymodebar": False
}


RAIZ = """
<|menu|label=Menu|width=200px|lov={("adicionar_transacao", Icon("assets/SVG_TransacaoBranco.svg", "Transações")), ("criar_uma_conta", Icon("assets/SVG_ContasBranco.svg", "Clientes")), ("analise", Icon("assets/SVG_DadosBranco.svg", "Estatísticas")), ("controles_do_programa", Icon("assets/SVG_ConfiguracaoBranco.svg", "Configurações"))}|on_action=menu_lateral|>
"""


if __name__ == "__main__":
    paginas = {
        "/": RAIZ,
        "adicionar_transacao": transac.PG_ADICIONAR_TRANSAC,
        "registro_de_contas": contas.PG_REGISTRO_CONTAS,
        "historico_transacoes": transac.PG_HIST_TRANSAC,
        "criar_uma_conta": contas.PG_CRIAR_CONTA,
        "analise": analise.GRAFICO_ENTRADAS_ABAT,
        "controles_do_programa": configs.CONTROLES
        }

    app = Gui(pages=paginas, css_file="__main__.css")

    elem_transac_sel = Gui.add_partial(app, transac.ELEMENTO_SELEC_CONTA)
    elem_transac_form = Gui.add_partial(app, transac.ELEMENTO_FORM)
    elem_transac_hist = Gui.add_partial(app, transac.ELEMENTO_HIST)

    elem_conta_form = Gui.add_partial(app, contas.ELEMENTO_FORM)
    elem_conta_regs = Gui.add_partial(app, contas.ELEMENTO_REGS)

    dial_selec_cliente = Gui.add_partial(app, dialogo.SELECIONAR_CLIENTE_ETAPA)
    dial_selec_transac = Gui.add_partial(app, dialogo.SELECIONAR_TRANSAC_ETAPA)
    dial_form_editar_cliente = Gui.add_partial(app, dialogo.FORM_EDITAR_CLIENTE)
    dial_transac_confirmar = Gui.add_partial(app, dialogo.CONFIRMAR_TRANSAC)
    dial_conta_confirmar = Gui.add_partial(app, dialogo.CONFIRMAR_CONTA)

    def start_cashd(with_webview: bool = False):
        port = 5000

        # https://stackoverflow.com/questions/2470971/fast-way-to-test-if-a-port-is-in-use-using-python
        def porta_esta_ocupada() -> bool:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', port)) == 0

        def run_taipy_gui():
            if not porta_esta_ocupada():
                app.run(
                    title="Cashd",
                    run_browser=False,
                    dark_mode=False,
                    stylekit={
                        "color_primary": "#478eff",
                        "color_background_light": "#ffffff"},
                    run_server=True,
                    port=port
                )

        if with_webview:
            taipy_thread = threading.Thread(target=run_taipy_gui)
            taipy_thread.start()

            global window
            window = webview.create_window(
                title="Cashd", 
                url=f"http://localhost:{port}", 
                frameless=True,
                maximized=maximizado,
                easy_drag=False,
                min_size=(900, 600))

            webview.start()
        
        else:
            run_taipy_gui()
    
    start_cashd(with_webview=True)
