"""Clinical pharmacy executive dashboard with real-time KPIs and sales analytics."""

from datetime import date
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from app.utils.session import is_authenticated, get_current_user
from app.components.styles import inject_custom_styles
from app.components.sidebar import render_sidebar
from app.components.metric_card import render_metric_card
from app.services.dashboard_service import DashboardService
from app.services.notification_service import NotificationService
from app.utils.formatters import format_currency

if not is_authenticated():
    st.warning("Please log in to access the pharmacy management system.")
    st.stop()

inject_custom_styles()

try:
    NotificationService.sync_inventory_alerts()
    unread_alerts_count = NotificationService.get_unread_count()
except Exception:
    unread_alerts_count = 0

render_sidebar(unread_notifications_count=unread_alerts_count)

user = get_current_user()

# Compact Greeting and Page Header
st.markdown("## Pharmacy Executive Dashboard")
st.caption(f"Welcome back, **{user.get('full_name', 'User')}** | Operational Overview & Real-Time Analytics")

# Fetch Aggregated Data
kpis = DashboardService.get_kpis()
urgent_alerts = DashboardService.get_urgent_alerts()

# -------------------------------------------------------------
# 1. Four Core KPI Metrics
# -------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    render_metric_card(
        title="Today's Sales",
        value=format_currency(kpis["today_revenue"]),
        subtext=f"{kpis['today_orders']} completed orders today",
        accent="teal",
    )

with c2:
    render_metric_card(
        title="Products in Stock",
        value=f"{kpis['total_stock_units']:,}",
        subtext=f"Across {kpis['total_medicines']} catalog products",
        accent="green",
    )

with c3:
    exp_accent = "red" if kpis["expired_batches_count"] > 0 else "amber"
    render_metric_card(
        title="Batches Approaching Expiry",
        value=f"{kpis['expiring_soon_count']}",
        subtext=f"{kpis['expiring_soon_count']} within 30d | {kpis['expired_batches_count']} quarantined",
        accent=exp_accent,
    )

with c4:
    low_accent = "red" if kpis["out_of_stock_count"] > 0 else "blue"
    render_metric_card(
        title="Medicines Requiring Replenishment",
        value=f"{kpis['low_stock_count']}",
        subtext=f"{kpis['out_of_stock_count']} completely out of stock",
        accent=low_accent,
    )

st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. Four Prominent Quick Action Shortcuts
# -------------------------------------------------------------
q1, q2, q3, q4 = st.columns(4)

with q1:
    if st.button("New Sale", icon=":material/point_of_sale:", use_container_width=True, type="primary"):
        st.switch_page("pages/billing.py")

with q2:
    if st.button("Receive Stock", icon=":material/inventory_2:", use_container_width=True):
        st.switch_page("pages/purchases.py")

with q3:
    if st.button("Find Medicine", icon=":material/search:", use_container_width=True):
        st.switch_page("pages/medicines.py")

with q4:
    if st.button("View Reports", icon=":material/analytics:", use_container_width=True):
        st.switch_page("pages/reports.py")

st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 3. Actionable Inventory Alerts Section
# -------------------------------------------------------------
has_critical = (
    len(urgent_alerts["near_expiry"]) > 0
    or len(urgent_alerts["low_stock"]) > 0
    or kpis["expired_batches_count"] > 0
)

if has_critical:
    with st.container(border=True):
        st.markdown("#### Actionable Inventory Alerts")
        col_exp, col_low = st.columns(2)

        with col_exp:
            st.markdown("##### Near-Expiry Priority Batches (FEFO)")
            if urgent_alerts["near_expiry"]:
                exp_df = pd.DataFrame(
                    [
                        {
                            "Medicine": item["medicine"],
                            "Batch": item["batch_no"],
                            "Expiry Date": item["expiry_date"],
                            "Days Left": f"{item['days_remaining']} days",
                            "Stock": f"{item['quantity']} units",
                        }
                        for item in urgent_alerts["near_expiry"]
                    ]
                )
                st.dataframe(exp_df, use_container_width=True, hide_index=True)
                if st.button("Inspect in Inventory", key="dash_link_expiry", icon=":material/arrow_forward:"):
                    st.switch_page("pages/medicines.py")
            else:
                st.info("No near-expiry batches detected.")

        with col_low:
            st.markdown("##### Low-Stock Replenishment Queue")
            if urgent_alerts["low_stock"]:
                low_df = pd.DataFrame(
                    [
                        {
                            "Medicine": item["medicine"],
                            "Current Stock": f"{item['current_stock']} units",
                            "Min Safety Threshold": f"{item['min_stock']} units",
                            "Deficit": f"+{item['deficit']} units",
                        }
                        for item in urgent_alerts["low_stock"]
                    ]
                )
                st.dataframe(low_df, use_container_width=True, hide_index=True)
                if st.button("Order Stock Inward", key="dash_link_purchases", icon=":material/add_shopping_cart:"):
                    st.switch_page("pages/purchases.py")
            else:
                st.info("All medicine stocks are within safe operational limits.")

st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 4. Sales Trend Visualization & Compact Recent Transactions
# -------------------------------------------------------------
col_chart, col_recent = st.columns([1.5, 1.1])

with col_chart:
    st.markdown("#### Sales Revenue & Order Trend")
    timeline_data = DashboardService.get_sales_timeline(days=30)
    timeline_df = pd.DataFrame(timeline_data)

    if not timeline_df.empty:
        fig_timeline = go.Figure()

        # Revenue Area / Bar Chart
        fig_timeline.add_trace(
            go.Bar(
                x=timeline_df["day_name"],
                y=timeline_df["revenue"],
                name="Revenue (₹)",
                marker_color="#0F766E",
                opacity=0.9,
                hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.2f}<extra></extra>",
            )
        )

        # Invoices / Orders Line
        fig_timeline.add_trace(
            go.Scatter(
                x=timeline_df["day_name"],
                y=timeline_df["orders"],
                name="Orders Billed",
                yaxis="y2",
                mode="lines+markers",
                line=dict(color="#2563EB", width=2),
                marker=dict(size=4, color="#2563EB"),
                hovertemplate="<b>%{x}</b><br>Orders: %{y}<extra></extra>",
            )
        )

        # Sample max 5 evenly-spaced tick labels under x-axis to prevent clutter
        total_pts = len(timeline_df)
        if total_pts > 5:
            indices = [int(i * (total_pts - 1) / 4) for i in range(5)]
            tick_vals = [timeline_df["day_name"].iloc[idx] for idx in indices]
        else:
            tick_vals = timeline_df["day_name"].tolist()

        fig_timeline.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color="#1C1917"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(
                showgrid=False,
                tickmode="array",
                tickvals=tick_vals,
                tickangle=0,
                tickfont=dict(color="#78716C", size=10),
            ),
            yaxis=dict(
                title=dict(text="Revenue (₹)", font=dict(color="#0F766E", size=11)),
                tickfont=dict(color="#0F766E"),
                showgrid=True,
                gridcolor="#E6E2DA",
            ),
            yaxis2=dict(
                title=dict(text="Orders", font=dict(color="#2563EB", size=11)),
                tickfont=dict(color="#2563EB"),
                overlaying="y",
                side="right",
                showgrid=False,
            ),
            hovermode="x unified",
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("No sales transactions recorded for this period.")

with col_recent:
    st.markdown("#### Recent Transactions")
    recent_sales = DashboardService.get_recent_sales(limit=5)
    if recent_sales:
        rec_df = pd.DataFrame(
            [
                {
                    "Invoice": s["invoice_no"],
                    "Customer": s["customer"],
                    "Date": s["created_at"],
                    "Amount": format_currency(s["total_amount"]),
                    "Payment": s["payment_mode"],
                }
                for s in recent_sales
            ]
        )
        st.dataframe(rec_df, use_container_width=True, hide_index=True)
    else:
        st.info("No recent sales records.")
