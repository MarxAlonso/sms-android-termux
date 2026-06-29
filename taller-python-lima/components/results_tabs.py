"""Pestañas de resultados — usa Streamlit nativo (st.dataframe, st.plotly_chart)."""

import plotly.express as px
import streamlit as st


def render_table_tab(df) -> None:
    """Muestra la tabla de datos."""
    nrows, ncols = df.shape
    st.markdown(
        f'<div class="data-info">'
        f'<span>📊 {nrows:,} filas × {ncols} columnas</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.dataframe(
        df,
        use_container_width=True,
        height=min(420, 40 + nrows * 35),
    )


def render_chart_tab(df) -> None:
    """Muestra gráfico interactivo."""
    if df.empty:
        st.info("No hay datos para graficar.")
        return

    num_cols = df.select_dtypes(include=["number"]).columns
    text_cols = df.select_dtypes(include=["object", "string"]).columns

    if len(num_cols) == 0:
        st.info("Se necesitan columnas numéricas para graficar.")
        return

    # Auto-detectar tipo
    if len(text_cols) >= 1 and len(num_cols) >= 1:
        n_cat = df[text_cols[0]].nunique()
        default = "pie" if n_cat <= 5 else "bar"
    elif len(num_cols) >= 2:
        default = "scatter"
    else:
        default = "histogram"

    opts = ["bar", "line", "scatter", "pie", "histogram", "box"]
    selected = st.selectbox(
        "Tipo de gráfico",
        opts,
        index=opts.index(default) if default in opts else 0,
        key="chart_type",
        label_visibility="collapsed",
    )

    try:
        fig = _build_chart(df, selected, num_cols, text_cols)
        if fig:
            st.plotly_chart(fig, use_container_width=True, config={
                "displayModeBar": True,
                "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                "displaylogo": False,
                "toImageButtonOptions": {"format": "png", "filename": "chart"},
            })
    except Exception as e:
        st.error(f"Error al generar gráfico: {e}")


def _build_chart(df, chart_type, num_cols, text_cols):
    color_seq = px.colors.sequential.Oranges_r

    if chart_type == "bar" and len(text_cols) >= 1:
        fig = px.bar(df, x=text_cols[0], y=num_cols[0],
                     color=text_cols[0] if df[text_cols[0]].nunique() <= 15 else None,
                     color_discrete_sequence=color_seq)
    elif chart_type == "line" and len(text_cols) >= 1:
        fig = px.line(df, x=text_cols[0], y=num_cols[0],
                      color_discrete_sequence=["#D97757"])
    elif chart_type == "scatter" and len(num_cols) >= 2:
        fig = px.scatter(df, x=num_cols[0], y=num_cols[1],
                         color=text_cols[0] if len(text_cols) >= 1 and df[text_cols[0]].nunique() <= 15 else None,
                         color_discrete_sequence=color_seq)
    elif chart_type == "pie" and len(text_cols) >= 1:
        fig = px.pie(df, names=text_cols[0], values=num_cols[0],
                     color_discrete_sequence=color_seq)
    elif chart_type == "histogram":
        fig = px.histogram(df, x=num_cols[0], nbins=20,
                           color_discrete_sequence=["#D97757"])
    elif chart_type == "box":
        x = text_cols[0] if len(text_cols) >= 1 and df[text_cols[0]].nunique() <= 15 else None
        fig = px.box(df, x=x, y=num_cols[0],
                     color_discrete_sequence=["#D97757"])
    else:
        return None

    fig.update_layout(
        template="none",
        font_family="Inter, sans-serif",
        font_size=12,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=30, b=40),
        hovermode="x unified",
        xaxis=dict(gridcolor="rgba(0,0,0,0.06)", linecolor="rgba(0,0,0,0.1)"),
        yaxis=dict(gridcolor="rgba(0,0,0,0.06)", linecolor="rgba(0,0,0,0.1)"),
    )
    return fig


def render_stats_tab(df) -> None:
    """Muestra estadísticas descriptivas."""
    if df.empty:
        st.info("No hay datos.")
        return

    num_cols = df.select_dtypes(include=["number"])
    cards = [("Filas", f"{len(df):,}"), ("Columnas", str(len(df.columns)))]

    for col in num_cols.columns[:3]:
        cards.append((f"Prom. {col}", f"{df[col].mean():,.2f}"))
        cards.append((f"Mín {col}", f"{df[col].min():,.2f}"))
        cards.append((f"Máx {col}", f"{df[col].max():,.2f}"))

    st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, (label, value) in enumerate(cards):
        with cols[i % 4]:
            st.markdown(
                f'<div class="stat-card">'
                f'<div class="stat-label">{label}</div>'
                f'<div class="stat-value">{value}</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

    if not num_cols.empty:
        st.markdown(
            '<div style="font-size:0.8rem;font-weight:600;margin:12px 0 6px;">📈 Estadísticas descriptivas</div>',
            unsafe_allow_html=True,
        )
        desc = num_cols.describe().T.reset_index()
        desc.columns = ["Columna", "Conteo", "Media", "Desv.Est.", "Mín", "25%", "50%", "75%", "Máx"]
        st.dataframe(desc, use_container_width=True, height=min(220, 40 + len(desc) * 35))
