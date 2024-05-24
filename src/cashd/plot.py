import plotly.graph_objects as pg
import pandas as pd

from cashd import db


CORES = ["#478eff", "gray"]

def balancos_por_periodo():
    data = db.saldos_transac_periodo()
    data["Data"] = pd.to_datetime(data.Data)
    data["SomasDisplay"] = data["Somas"]\
        .apply(lambda x: f"{x:_.2f}".replace(".", ",").replace("_", " "))
    data["AbatDisplay"] = data["Abatimentos"]\
        .apply(lambda x: f"{x:_.2f}".replace(".", ",").replace("_", " "))

    layout = pg.Layout(
        margin=dict(l=0, r=0, t=0, b=0),
        template="none",
        showlegend=False,
        hovermode="x unified",
        xaxis=dict(
            tickmode="array",
            tickvals=[i for i in data["Data"]],
            ticktext=[i.strftime("%B de %Y") for i in data["Data"]]
        )
    )

    fig = pg.Figure(layout=layout)
    fig.add_trace(pg.Bar(
        x=data["Data"], y=data["Somas"], name="Somas",
        customdata=data[["SomasDisplay"]],
        hovertemplate="<b>R$ %{customdata[0]}</b>",
        offsetgroup=0,
        marker=dict(color=CORES[0])
    ))
    fig.add_trace(pg.Bar(
        x=data["Data"], y=data["Abatimentos"], name="Abatimentos",
        customdata=data[["AbatDisplay"]],
        hovertemplate="<b>R$ %{customdata[0]}</b>",
        offsetgroup=0,
        marker=dict(color=CORES[1])
    ))

    return fig