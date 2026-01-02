import plotly.graph_objects as pg
import pandas as pd

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from typing import Literal
from numbers import Number

from cashd import db
from cashd_core import data


CORES = ["#478eff", "gray"]


def _preprocess_value(tbl: pd.DataFrame, value_cols: list[str]) -> pd.DataFrame:
    """Returns `tbl` with `value_cols` formatted as `Decimal` with two decimal
    places.
    """
    def handle_currency(val: str | Number):
        return Decimal(val).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    for value_col in value_cols:
        if tbl[value_col].dtype in ["object", "string"]:
            tbl[value_col] = tbl[value_col].apply(
                lambda val: handle_currency(val.replace(",", "."))
            )
    return tbl


def _gerar_layout(
    tbl: pd.DataFrame, periodo: Literal["m", "w", "d"], date_col: str = "Data"
) -> pg.Layout:
    """
    Retorna um `plotly.graph_objects.Layout` gerado para o conjunto de dados `tbl`
    """
    datestr = "%B de %Y"
    if periodo == "d":
        datestr = "%d de %B de %Y"
    elif periodo == "w":
        datestr = "%Y, semana %W"
    return pg.Layout(
        margin=dict(l=0, r=0, t=0, b=0),
        template="plotly_white",
        separators=", ",
        showlegend=False,
        hovermode="x unified",
        xaxis=dict(
            tickmode="array",
            tickvals=tbl[date_col],
            ticktext=tbl[date_col],
            showticklabels=False,
        ),
        yaxis_tickprefix="R$",
        yaxis_tickformat=" ",
    )


def _gerar_layout_vazio():
    """
    Retorna um `plotly.graph_objects.Layout` sem marcadores de eixos
    """
    return pg.Layout(
        margin=dict(l=0, r=0, t=0, b=0),
        template="none",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
    )


def mensagem(msg: str):
    layout = _gerar_layout_vazio()
    fig = pg.Figure(layout=layout)
    fig.add_annotation(
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        text="Nenhum dado disponível",
        showarrow=False,
        font=dict(size=20),
    )
    return fig


def balancos(periodo: Literal["m", "w", "d"], n: int) -> pg.Figure:
    datasource = data.TransactionBalanceSource()
    datasource.update_date_format(date_freq=periodo)
    tbl = pd.DataFrame(datasource.get_data_slice([n, 0])) # 0 after to revert order
    if tbl.shape[0] == 0:
        return mensagem("Sem dados para exibir")
    tbl = _preprocess_value(tbl, value_cols=["Sums", "Deductions"])
    layout = _gerar_layout(tbl, periodo, date_col="Date")
    fig = pg.Figure(layout=layout)
    fig.add_trace(
        pg.Bar(
            x=tbl["Date"],
            y=tbl["Sums"],
            name="Somas",
            customdata=tbl[["Sums"]],
            hovertemplate="<b>R$ %{customdata[0]:,.2f}</b>",
            offsetgroup=0,
            marker=dict(color=CORES[1]),
        )
    )
    fig.add_trace(
        pg.Bar(
            x=tbl["Date"],
            y=tbl["Deductions"],
            name="Abatimentos",
            customdata=tbl[["Deductions"]],
            hovertemplate="<b>R$ %{customdata[0]:,.2f}</b>",
            offsetgroup=0,
            marker=dict(color=CORES[0]),
        )
    )
    fig._config["displayModeBar"] = False
    return fig


def saldo_acum(periodo, n):
    datasource = data.AggregatedAmountSource()
    datasource.update_date_format(date_freq=periodo)
    tbl = pd.DataFrame(datasource.get_data_slice([n, 0])) # 0 after to revert order
    if tbl.shape[0] == 0:
        return mensagem("Sem dados para exibir")
    tbl = _preprocess_value(tbl, value_cols=["AcumBalance"])
    layout = _gerar_layout(tbl, periodo, "Date")
    fig = pg.Figure(layout=layout)
    fig.add_trace(
        pg.Scatter(
            x=tbl["Date"],
            y=tbl["AcumBalance"],
            name="Saldo",
            mode="lines+markers",
            customdata=tbl[["AcumBalance"]],
            hovertemplate="<b>R$ %{customdata[0]:,.2f}</b>",
            offsetgroup=0,
            marker=dict(color=CORES[0]),
        )
    )
    fig.update_xaxes(showgrid=False)
    fig._config["displayModeBar"] = False
    return fig
