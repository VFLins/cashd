import threading
import webview
import tkinter as tk
import socket
import pandas as pd
import sys
from pyshortcuts import make_shortcut
from datetime import datetime
from tkinter import filedialog
from typing import Literal, Type, NamedTuple
from os import path

from taipy.gui import Gui, notify, State, navigate, Icon, builder, get_state_id

from cashd_core import data, prefs, backup
from cashd import plot, db
from cashd.pages import transac, contas, analise, configs, dialogo


PYTHON_PATH = path.dirname(sys.executable)

# generalization of Taipy's LoV (list of values)
# https://docs.taipy.io/en/release-4.1/refmans/gui/viselements/generic/selector/#p-lov
LOVItem = NamedTuple("LOVItem", [("Id", str), ("Value", str)])


####################
# BUTTONS
####################


def btn_next_page_customer_search(state: State):
    customers_source = get_customers_datasource(state=state)
    customers_source.fetch_next_page()
    update_search_widgets(state=state)


def btn_prev_page_customer_search(state: State):
    customers_source = get_customers_datasource(state=state)
    customers_source.fetch_previous_page()
    update_search_widgets(state=state)


def btn_next_page_displayed_table(state: State):
    tablename = state.dropdown_table_type_val
    selected_source = get_table_datasource(state=state, tablename=tablename)
    selected_source.fetch_next_page()
    chg_select_table_stats(state=state)


def btn_prev_page_displayed_table(state: State):
    tablename = state.dropdown_table_type_val
    selected_source = get_table_datasource(state=state, tablename=tablename)
    selected_source.fetch_previous_page()
    chg_select_table_stats(state=state)


def show_dialog(state: State, id: str, payload: dict, show: str):
    show_dialogs = {
        "confirm_edit_customer": "show_dialog_confirm_edit_customer",
        "edit_customer": "show_dialog_edit_customer",
    }
    for dialog in show_dialogs.values():
        state.assign(dialog, False)
    state.assign(show_dialogs[show], True)


def btn_mostrar_dialogo_selec_cliente(state: State, id: str, payload: dict):
    btn_mostrar_dialogo(state, id, payload, show="selec_cliente")


def btn_mostrar_dialogo_edita_cliente(state: State, id: str, payload: dict):
    btn_mostrar_dialogo(state, id, payload, show="edita_cliente")


def btn_mostrar_dialogo_selec_transac(state: State, id: str, payload: dict):
    customer = data.tbl_clientes()
    with state as s:
        customer.read(row_id=s.SELECTED_CUSTOMER.Id)
        s.TRANSACS_USUARIO = [
            LOVItem(Id=str(t["id"]), Value=f"{t['data']} | {t['valor']}")
            for t in customer.Transacs
        ]
    btn_mostrar_dialogo(state, id, payload, "selec_transac")


def btn_atualizar_listagem(state: State):
    with db.DB_ENGINE.connect() as conn, conn.begin():
        state.df_clientes = pd.read_sql_query("SELECT * FROM clientes", con=conn)


def btn_gerar_main_plot(state: State | None = None):
    """
    Se `state=None` retorna um `plotly.graph_objects.Figure`, caso contrario, atualiza o valor
    de `'main_plot'`."""

    if state:
        p = state.dropdown_periodo_val[0]
        n = int(state.slider_val[0])
        tipo = state.dropdown_plot_type_val
    else:
        p = dropdown_periodo_val[0]
        n = int(slider_val[0])
        tipo = dropdown_plot_type_val

    if tipo == "Saldo Acumulado":
        fig = plot.saldo_acum(periodo=p, n=n)
    else:
        fig = plot.balancos(periodo=p, n=n)

    if state:
        state.assign("main_plot", fig)
        state.refresh("main_plot")
        return
    return


def get_backup_places() -> pd.DataFrame:
    """Returns a `pd.DataFrame` listing all current backup places."""
    backup_places = backup.settings.read_backup_places()
    return pd.DataFrame(
        {"Id": range(len(backup_places)), "Locais de backup": backup_places}
    )


def btn_fazer_backups(state: State):
    try:
        backup.run(force=True, _raise=True)
        notify(state, "success", "Backup concluído!")
    except Exception as xpt:
        notify(state, "error", str(xpt))


def btn_add_local_de_backup(state: State):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    folder = tk.filedialog.askdirectory()
    backup.settings.add_backup_place(folder)
    state.df_backup_places = get_backup_places()


def btn_rm_local_de_backup(state: State, var_name, payload):
    idx = int(payload["index"])
    backup.settings.rm_backup_place(idx)
    state.df_backup_places = get_backup_places()


def btn_carregar_backup(state: State):
    filename = tk.filedialog.askopenfilename()
    try:
        backup.load(file=filename, _raise=True)
        notify(state, "success", "Dados carregados com sucesso")
    except OSError:
        notify(state, "error", "Arquivo selecionado não é um banco de dados SQLite")
    except Exception as xpt:
        notify(state, "error", f"Erro inesperado carregando arquivo: {xpt}")


def btn_criar_atalho(state: State):
    if sys.platform == "win32":
        python_runner = path.join(PYTHON_PATH, "pythonw.exe")
        icon_file = path.join(backup.SCRIPT_PATH, "assets", "ICO_LogoIcone.ico")
    else:
        python_runner = path.join(PYTHON_PATH, "python3")
        icon_file = path.join(backup.SCRIPT_PATH, "assets", "PNG_LogoIcone.png")
    startup_script = path.join(backup.SCRIPT_PATH, "startup.pyw")
    make_shortcut(
        executable=python_runner,
        script=startup_script,
        icon=icon_file,
        name="Cashd",
        description="Registre seu fluxo de caixa rapidamente e tenha total controle dos seus dados!",
        terminal=False,
        desktop=True,
        startmenu=True,
    )
    notify(state, "success", "Atalho criado com sucesso!")


def add_transaction(state: State):
    """Adds a transaction to the database, uses currently selected customer and data
    filled by the user.
    """
    customer = data.tbl_clientes()
    if customer.table_is_empty():
        notify(
            state,
            "error",
            "Você deve cadastrar um cliente antes de registrar uma transação",
        )
        return
    try:
        if is_empty_currency_input(state.form_transac.Valor):
            notify(state, "error", "Valor não pode ser zero")
            return
        if not is_valid_currency_input(state.form_transac.Valor):
            notify(state, "error", "Valor inválido, insira apenas números")
            return
        state.form_transac.IdCliente = state.SELECTED_CUSTOMER.Id
        state.form_transac.CarimboTempo = datetime.now()
        state.form_transac.write()
        print(f"state user {get_state_id(state)} added {state.form_transac}")
        reset_transac_form_widgets(state=state)
    except Exception as err:
        notify(state, "error", str(err))
        print(f"Unexpected {type(err)}: {err}")
    else:
        notify(state, "success", "Nova transação adicionada")
    finally:
        state.df_transac = get_customer_transacs(state=state)


def add_customer(state: State):
    customer = state.form_customer
    if not customer.required_fields_are_filled():
        notify(state, "error", "Algum campo obrigatório (*) ainda não foi preenchido")
        return
    try:
        customer.write()
        notify(state, "success", message=f"Novo cliente adicionado: {customer.NomeCompleto}")
        state.refresh("form_customer")
        state.NOMES_USUARIOS = get_customer_lov(state=state)
    except Exception as msg_erro:
        notify(state, "error", str(msg_erro))


def btn_chg_prefs_main_state(state: State):
    val = state.dropdown_uf_val
    try:
        prefs.settings.default_state = val
        state.form_contas.Estado = val
        state.refresh("form_contas")
        notify(state, "success", f"Estado preferido atualizado para {val}")
    except Exception as xpt:
        notify(state, "error", f"Erro inesperado: {str(xpt)}")


def btn_chg_prefs_main_city(state: State):
    val = state.input_cidade_val
    try:
        val = val.title()
        prefs.settings.default_city = val
        state.input_cidade_val = val
        state.form_contas.Cidade = val
        state.refresh("form_contas")
        notify(state, "success", f"Cidade preferida atualizada para {val}")
    except Exception as xpt:
        notify(state, "error", f"Erro inesperado: {str(xpt)}")


def btn_chg_max_highest_balances(state: State, val: int):
    try:
        val = int(val)
        prefs.settings.data_tables_rows_per_page = val
        state.df_maiores_saldos = db.rank_maiores_saldos(val)
        notify(
            state,
            "success",
            f"Limite de entradas em 'Maiores saldos' atualizado para {val}",
        )
    except Exception as xpt:
        notify(state, "error", f"Erro inesperado: {str(xpt)}")


def tggl_backup_on_exit(state: State | None = None):
    if not state:
        return backup.settings.read_backup_on_exit()
    val = state.toggle_backup_on_exit
    backup.settings.write_backup_on_exit(val)


def btn_encerrar():
    try:
        backup.run(force=False, _raise=False)
        window.destroy()
    except NameError:
        window = webview.active_window()
        window.destroy()
    finally:
        raise KeyboardInterrupt("Encerrando...")


def btn_mudar_maximizado():
    window.toggle_fullscreen()


def btn_mudar_minimizado():
    window.minimize()


####################
# UTILS
####################


def fmt_currency_input(inp: str) -> str:
    """Formats a numeric string to currency, returns '0,00' if zeroed or invalid."""
    try:
        return f"{int(inp)/100:_.2f}".replace("_", " ").replace(".", ",")
    except ValueError:
        return "0,00"


def is_valid_currency_input(inp: str) -> bool:
    """Returns a boolean value indicating if `inp` is a valid currency input."""
    try:
        _ = int(inp)
    except ValueError:
        return False
    else:
        return inp.replace("-", "").isdigit()


def is_empty_currency_input(inp: str) -> bool:
    """Retuns a boolean value indicating if `inp` is an empty currency input."""
    if inp is None:
        return True
    inp = inp.strip()
    if inp == "":
        return True
    try:
        inp = int(inp)
    except ValueError:
        pass
    if inp == 0:
        return True
    return False


def adapt_lovitem(item: LOVItem | str) -> tuple | None:
    """Handles LOVItem objetcs when they are handed to Taipy widgets."""
    try:
        if type(item) in [LOVItem, tuple]:
            return tuple(item[:2])
    except IndexError:
        return (None, None)


def get_customer_transacs(state: State | None = None) -> pd.DataFrame:
    """When `state` is defined:
    - Refreshes customer transaction data on `pages.ELEMENTO_SELEC_CONTA`;
    - Returns a `pd.DataFrame` with the transaction history of the selected customer.

    When `state` is _not_ defined:
    - Returns a `pd.DataFrame` with the transaction history of the first customer, or
      an empty one if there are no customers.
    """
    customer = data.tbl_clientes()
    if customer.table_is_empty():
        return pd.DataFrame(columns=["Id", "Data", "Valor"])
    customer_id = state.SELECTED_CUSTOMER.Id if state else 1
    customer.read(row_id=customer_id)
    if (state is not None) and (customer.Id is not None):
        state.SELECTED_CUSTOMER_BALANCE = customer.Saldo
        state.SELECTED_CUSTOMER_PLACE = customer.Local
    return pd.DataFrame(data=customer.Transacs).rename(
        columns={"id": "Id", "data": "Data", "valor": "Valor"}
    )


def get_customers_datasource(state: State | None = None) -> data.CustomerListSource:
    """Initializes or get a `data.CustomerListSource` from `state`, if `state` is
    not None, adds it to state.
    """
    customers = getattr(state, "customers_source", data.CustomerListSource())
    if state:
        state.assign("customers_source", customers)
    return customers


def get_customer_lov(state: State | None = None) -> list[LOVItem]:
    customers = get_customers_datasource(state=state)
    return [
        LOVItem(Id=str(c[0]), Value=f"{c[1]} - {c[2]}") for c in customers.current_data
    ]


def menu_lateral(state, action, info):
    page = info["args"][0]
    navigate(state, to=page)


def update_search_widgets(state: State):
    with state as s:
        customers_source = get_customers_datasource(state=s)
        s.NOMES_USUARIOS = get_customer_lov(state=s)
        s.search_user_pagination_legend = (
            f"{customers_source.nrows} itens, "
            f"mostrando {customers_source.min_idx + 1} até {customers_source.max_idx}"
        )


def reset_transac_form_widgets(state: State):
    """Reset all fields of pages.transac.ELEMENTO_FORM to their default state."""
    with state as s:
        s.form_transac.DataTransac = datetime.today()
        s.form_transac.Valor = ""
        s.display_tr_valor = "0,00"
        s.refresh("form_transac")


def get_table_datasource(
    state: State | None = None,
    tablename=Literal["Últimas transações", "Maiores saldos", "Clientes inativos"],
) -> Type[data._DataSource]:
    """Returns an instance of datasource according to the `tablename`. Assigns this
    datasource to the `state` if provided.
    """
    source_names = {
        "Últimas transações": "datasource_last_transacs",
        "Clientes inativos": "datasource_inactive_customers",
        "Maiores saldos": "datasource_highest_amounts",
    }
    sources = {
        "Últimas transações": data.LastTransactionsSource(),
        "Clientes inativos": data.InactiveCustomersSource(),
        "Maiores saldos": data.HighestAmountsSource(),
    }
    if not state:
        return sources.get(tablename)
    datasource = getattr(state, source_names[tablename], None)
    if datasource is None:
        state.assign(source_names[tablename], datasource)
    return datasource


def update_displayed_table_pagination(
    state: State,
    tablename=Literal["Últimas transações", "Maiores saldos", "Clientes inativos"],
):
    selected_source = get_table_datasource(state=state, tablename=tablename)
    state.stats_tables_pagination_legend = (
        f"{selected_source.nrows} itens, "
        f"mostrando {selected_source.min_idx + 1} "
        f"até {selected_source.max_idx}"
    )


####################
# ON ACTION
####################


def rm_transaction(state: State, var_name: str, payload: dict):
    """Removes the selected transaction of the selected customer when the user
    interacts with the table widget.
    """
    selected_customer = data.tbl_clientes()
    selected_transaction = data.tbl_transacoes()
    table_row_id: int = payload["index"]
    try:
        with state as s:
            selected_customer.read(row_id=s.SELECTED_CUSTOMER.Id)
            rm_transac_data: dict = tuple(selected_customer.Transacs)[table_row_id]
            selected_transaction.read(row_id=rm_transac_data["id"])
            selected_transaction.delete()
            notify(s, "success", f"Transação de R$ {selected_transaction.Valor/100} removida".replace(".", ","))
            print(f"state user {get_state_id(s)} removed {selected_transaction}")
    except Exception as err:
        notify(s, "error", f"Erro inesperado removendo esta transação: {str(err)}")
    finally:
        state.df_transac = get_customer_transacs(state=state)


def btn_edit_customer(state: State):
    customer = state.selected_customer_handler
    customer.read(row_id=state.SELECTED_CUSTOMER.Id)
    state.refresh("selected_customer_handler")
    state.show_dialog_edit_customer = True


def set_rows_per_page(state: State):
    state.rows_per_page = int(state.rows_per_page)
    prefs.settings.data_tables_rows_per_page = state.rows_per_page
    n_rows = prefs.settings.data_tables_rows_per_page
    with state as s:
        s.NOMES_USUARIOS = get_customer_lov(state=s)
    notify(state, "warning", f"Esta mudança só terá efeito após reiniciar o Cashd")


def dialog_edit_customer_action(state: State, id: str, payload: dict):
    customer = state.selected_customer_handler
    match payload["args"][0]:
        # click 'x' button
        case -1:
            state.show_dialog_edit_customer = False
        # click 'save changes' button
        case 0:
            if not customer.required_fields_are_filled():
                notify(state, "error", "Algum campo obrigatório (*) ainda não foi preenchido")
                btn_edit_customer(state=state)
            else:
                show_dialog(state=state, id=id, payload=payload, show="confirm_edit_customer")


def dialog_confirm_edit_customer_action(state: State, id: str, payload: dict):
    match payload["args"][0]:
        # click 'x' button
        case -1: state.show_dialog_confirm_edit_customer = False
        # click 'return' button
        case 0: show_dialog(state=state, id=id, payload=payload, show="edit_customer")
        # click 'confirm' button
        case 1:
            state.selected_customer_handler.update()
            state.show_dialog_confirm_edit_customer = False
            notify(state, "success", f"Informações atualizadas com sucesso")
            state.NOMES_USUARIOS = get_customer_lov(state=state)


def chg_dialog_selec_cliente_conta(state: State, id: str, payload: dict):
    with state as s:
        if payload["args"][0] < 1:
            s.assign("mostra_selec_cliente", False)

        if payload["args"][0] == 1:
            if s.SELECTED_CUSTOMER.Id == "0":
                notify(s, "error", "Nenhuma conta foi selecionada")
            else:
                selected_customer = data.tbl_clientes()
                selected_customer.read(row_id=s.SELECTED_CUSTOMER.Id)
                s.refresh("selected_customer_handler")
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
                db.atualizar_cliente(state.SELECTED_CUSTOMER[0], state.form_conta_selec)
                state.NOMES_USUARIOS = sel_listar_clientes(state)
                notify(s, "success", "Cadastro atualizado com sucesso!")
            except Exception as xpt:
                notify(s, "error", f"Erro ao atualizar cadastro: {str(xpt)}")
                s.assign("mostra_confirma_conta", False)
        s.assign("mostra_confirma_conta", False)


def chg_transac_valor(state: State) -> None:
    state.display_tr_valor = fmt_currency_input(inp=state.form_transac.Valor)
    state.refresh("form_transac")
    return


def update_displayed_table(state: State):
    source_names = {
        "Últimas transações": "datasource_last_transacs",
        "Clientes inativos": "datasource_inactive_customers",
        "Maiores saldos": "datasource_highest_amounts",
    }
    sources = {
        "Últimas transações": datasource_last_transacs,
        "Clientes inativos": datasource_inactive_customers,
        "Maiores saldos": datasource_highest_amounts,
    }
    table_partials = {
        "Últimas transações": analise.ELEM_TABLE_TRANSAC_HIST,
        "Clientes inativos": analise.ELEM_TABLE_INACTIVE_CUSTOMERS,
        "Maiores saldos": analise.ELEM_TABLE_HIGHEST_AMOUNTS,
    }
    dataframe_names = {
        "Últimas transações": "df_last_transacs",
        "Maiores saldos": "df_highest_amounts",
        "Clientes inativos": "df_inactive_customers",
    }
    tablename = state.dropdown_table_type_val
    datasource = get_table_datasource(state=state, tablename=tablename)
    # Update data
    df = getattr(state, dataframe_names[tablename])
    df = pd.DataFrame(data=datasource.current_data, columns=df.columns)
    state.assign(dataframe_names[tablename], df)
    # Update pagination label
    update_displayed_table_pagination(state=state, tablename=tablename)
    # Update Taipy partial
    state.part_stats_displayed_table.update_content(state, table_partials[tablename])


def chg_selected_customer(state: State) -> None:
    """Update customer information widgets when the user interacts with the customer
    selector.
    """
    customer = state.selected_customer_handler
    with state as s:
        customer_id = int(s.SELECTED_CUSTOMER.Id)
        customer.read(row_id=customer_id)
        s.df_transac = get_customer_transacs(state=s)
        s.nome_cliente_selec = customer.NomeCompleto
        s.refresh("form_transac")
        s.refresh("selected_customer_handler")
    print(f"state user {get_state_id(state)} selected: {customer.NomeCompleto}")


def chg_cliente_pesquisa(state: State, id, payload):
    customers_source = get_customers_datasource(state=state)
    with state as s:
        customers_source.search_text = s.search_user_input_value
        update_search_widgets(state=s)


####################
# VALORES INICIAIS
####################

# visibilidade de dialogos
show_dialog_confirm_edit_customer = False
show_dialog_edit_customer = False

# controles dos graficos
slider_elems = list(range(10, 51)) + [None]
slider_lov = [(str(i), str(i)) if i is not None else (i, "Tudo") for i in slider_elems]
slider_val = slider_lov[0]

dropdown_periodo_lov = [("mes", "Mensal"), ("sem", "Semanal"), ("dia", "Diário")]
dropdown_periodo_val = dropdown_periodo_lov[0]

dropdown_plot_type_val = "Balanço"

dropdown_uf_lov = [
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PE",
    "PI",
    "PR",
    "RJ",
    "RN",
    "RO",
    "RR",
    "RS",
    "SC",
    "SE",
    "SP",
    "TO",
]
dropdown_uf_val = prefs.settings.default_state

main_plot = btn_gerar_main_plot()

# campo de pesquisa de clientes
search_user_input_value = ""

# listagem de clientes
with db.DB_ENGINE.connect() as conn, conn.begin():
    df_clientes = pd.read_sql_query("SELECT * FROM clientes", con=conn)

# valor inicial dos campos "Valor" e "Data" no menu "Adicionar Transacao"
display_tr_valor = "0,00"
display_tr_date = datetime.now()

# valor inicial do seletor de conta global
customers_source = data.CustomerListSource()
customers_source.search_text = search_user_input_value

# formularios
form_customer = data.get_default_customer()
form_transac = data.tbl_transacoes(DataTransac=datetime.today())
selected_customer_handler = data.tbl_clientes()

NOMES_USUARIOS = get_customer_lov(state=None)
if len(NOMES_USUARIOS) > 0:
    SELECTED_CUSTOMER = NOMES_USUARIOS[0]
    selected_customer_handler.read(row_id=SELECTED_CUSTOMER.Id)
else:
    SELECTED_CUSTOMER = LOVItem(Id="0", Value="")

# texto de paginação da pesquisa de clientes
search_user_pagination_legend = (
    f"{customers_source.nrows} itens, mostrando 1 até {customers_source.max_idx}"
)

# nome do cliente selecionado
nome_cliente_selec = selected_customer_handler.NomeCompleto

# valor inicial do seletor de transacao global
# TRANSACS_USUARIO = tuple(selected_customer_handler.Transacs)
# if len(TRANSACS_USUARIO) > 0:
#    SLC_TRANSAC = TRANSACS_USUARIO[0]
# else:
#    SLC_TRANSAC = "0"

# define se a webview vai iniciar em tela cheia
maximizado = False

# valor inicial da tabela de transacoes do usuario selecionado em SELECTED_CUSTOMER
datasource_last_transacs = get_table_datasource(tablename="Últimas transações")
datasource_highest_amounts = get_table_datasource(tablename="Maiores saldos")
datasource_inactive_customers = get_table_datasource(tablename="Clientes inativos")

df_last_transacs = pd.DataFrame(
    data=datasource_last_transacs.current_data,
    columns=["Data", "Cliente", "Valor"],
)
df_highest_amounts = pd.DataFrame(
    data=datasource_highest_amounts.current_data,
    columns=["Nome", "Saldo devedor"],
)
df_inactive_customers = pd.DataFrame(
    data=datasource_inactive_customers.current_data,
    columns=["Nome", "Última transação", "Saldo devedor"],
)

dropdown_table_type_val = "Últimas transações"
stats_tables_pagination_legend = (
    f"{datasource_last_transacs.nrows} itens, mostrando "
    f"{datasource_last_transacs.min_idx +
        1} até {datasource_last_transacs.max_idx}"
)

# valor inicial do saldo do usuario selecionado em SELECTED_CUSTOMER
# init_meta_cliente = db.listar_transac_cliente(SELECTED_CUSTOMER[0])
selected_customer = data.tbl_clientes()
if not selected_customer.table_is_empty():
    selected_customer.read(row_id=SELECTED_CUSTOMER.Id)

# df_transac = init_meta_cliente["df"]
# SELECTED_CUSTOMER_BALANCE = init_meta_cliente["saldo"]
# SELECTED_CUSTOMER_PLACE = init_meta_cliente["local"]
df_transac = get_customer_transacs(state=None)
SELECTED_CUSTOMER_BALANCE = selected_customer.Saldo
SELECTED_CUSTOMER_PLACE = selected_customer.Local

# valor inicial da lista de locais de backup
df_backup_places = get_backup_places()

# valor inicial do campo "cidade preferida"
input_cidade_val = prefs.settings.default_city

# valor inicial da configuracao Limite de linhas na tabela "Últimas transações"
rows_per_page = prefs.settings.data_tables_rows_per_page

# valor inicial do toggle "backup ao sair"
toggle_backup_on_exit = tggl_backup_on_exit()

# dados de entradas e abatimentos
df_entradas_abatimentos = db.saldos_transac_periodo()
layout_df_entradas_abatimentos = {
    "x": "Data",
    "y[1]": "Somas",
    "y[2]": "Abatimentos",
    "layout": {
        "barmode": "overlay",
        "barcornerradius": "20%",
        "hovermode": "x unified",
        "hovertemplate": "<b>Total</b>: R$ %{y:.2f}",
    },
}
config_df_entradas_abatimentos = {"displaymodebar": False}


RAIZ = """
<|menu|label=Menu|width=200px|lov={("transacoes", Icon("assets/SVG_TransacaoBranco.svg", "Transações")), ("clientes", Icon("assets/SVG_ContasBranco.svg", "Clientes")), ("analise", Icon("assets/SVG_DadosBranco.svg", "Estatísticas")), ("configs", Icon("assets/SVG_ConfiguracaoBranco.svg", "Configurações"))}|on_action=menu_lateral|>
"""


paginas = {
    "/": RAIZ,
    "transacoes": transac.PG_TRANSAC,
    "clientes": contas.PG_CONTAS,
    "analise": analise.PG_ANALISE,
    "configs": configs.PG_CONFIG,
}

app = Gui(pages=paginas)

elem_transac_sel = Gui.add_partial(app, transac.ELEMENTO_SELEC_CONTA)
elem_transac_form = Gui.add_partial(app, transac.ELEMENTO_FORM)
elem_conta = Gui.add_partial(app, contas.ELEMENTO_FORM)
elem_config = Gui.add_partial(app, configs.ELEMENTO_PREFS)
elem_analise = Gui.add_partial(app, analise.ELEM_TABLES)

# dial_selec_cliente = Gui.add_partial(app, dialogo.SELECIONAR_CLIENTE_ETAPA)
dialog_edit_customer = Gui.add_partial(app, dialogo.FORM_EDITAR_CLIENTE)
dialog_confirm_edit_customer= Gui.add_partial(app, dialogo.CONFIRMAR_CONTA)

part_stats_displayed_table = Gui.add_partial(app, analise.ELEM_TABLE_TRANSAC_HIST)

### menus de navegacao ###
# transacoes
nav_transac_lov = [
    (transac.ELEMENTO_FORM, "Adicionar transação"),
    (transac.ELEMENTO_HIST, "Ver histórico"),
]
nav_transac_val = nav_transac_lov[0]
# estatisticas
nav_analise_lov = [(analise.ELEM_TABLES, "Tabelas"), (analise.ELEM_PLOT, "Gráficos")]
nav_analise_val = nav_analise_lov[0]
# configs
nav_config_lov = [
    (configs.ELEMENTO_PREFS, "Preferências"),
    (configs.ELEMENTO_BACKUP, "Backup"),
    (configs.ELEMENTO_ATALHO, "Outros"),
]
nav_config_val = nav_config_lov[0]


def porta_aberta() -> int:
    port = 5000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        for i in range(51):
            if s.connect_ex(("localhost", port + i)) != 0:
                return port + i
        return port + 50


port = porta_aberta()


def start_cashd(with_webview: bool = False):
    with_webview = True if "--webview" in sys.argv else False
    debug = True if "--debug" in sys.argv else False

    def run_taipy_gui():
        app.run(
            title="Cashd",
            run_browser=not with_webview,
            dark_mode=False,
            stylekit={
                "color_primary": "#478eff",
                "color_background_light": "#ffffff",
            },
            run_server=True,
            port=port,
            favicon="assets/PNG_LogoFavicon.png",
            watermark="",
            debug=debug,
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
            min_size=(900, 600),
        )
        webview.start()
    else:
        run_taipy_gui()
