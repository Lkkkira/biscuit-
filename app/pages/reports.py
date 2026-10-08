"""Consolidated Reports, Customer Directory, Notifications, Administration, and Audit Logs Page."""

from datetime import date, timedelta
from typing import Dict, Any, List
import streamlit as st
import pandas as pd

from app.utils.session import is_authenticated, is_admin, get_current_user
from app.components.styles import inject_custom_styles
from app.components.sidebar import render_sidebar
from app.components.metric_card import render_metric_card
from app.components.empty_state import render_empty_state
from app.components.status_badge import render_status_badge
from app.services.report_service import ReportService
from app.services.customer_service import CustomerService
from app.services.notification_service import NotificationService
from app.services.auth_service import AuthService
from app.services.setting_service import SettingService
from app.services.backup_service import BackupService
from app.services.audit_service import AuditService
from app.utils.formatters import format_currency
from app.core.exceptions import AppException, ConflictException

if not is_authenticated():
    st.warning("Please log in to access the pharmacy management system.")
    st.stop()

inject_custom_styles()

try:
    unread_alerts_count = NotificationService.get_unread_count()
except Exception:
    unread_alerts_count = 0

render_sidebar(unread_notifications_count=unread_alerts_count)

current_user = get_current_user()
admin_mode = is_admin()

st.markdown("## Reports, Customer CRM & System Settings")
st.caption("Centralized analytics, customer records, notification alerts, administration, and audit governance")

# Define Tabs dynamically based on role
tab_titles = [
    "Financial & Sales Reports",
    "Patient & Customers",
    "Notification Center",
]
if admin_mode:
    tab_titles.extend(["System Administration", "Security Audit Logs"])

tabs = st.tabs(tab_titles)
tab_reports = tabs[0]
tab_customers = tabs[1]
tab_notifications = tabs[2]
tab_admin = tabs[3] if admin_mode else None
tab_audit = tabs[4] if admin_mode else None

today = date.today()

# ==============================================================================
# TAB 1: FINANCIAL & SALES REPORTS
# ==============================================================================
with tab_reports:
    subtab_sales, subtab_profit, subtab_valuation, subtab_loss = st.tabs([
        "Sales Statements",
        "Profit Margins",
        "Inventory Valuation",
        "Expiry Loss Audit",
    ])

    # 1. Sales & Revenue
    with subtab_sales:
        st.markdown("### Financial Sales & Invoicing Statements")
        col_date1, col_date2, col_quick = st.columns([1.2, 1.2, 2.0])
        with col_date1:
            start_d = st.date_input("Start Date", value=today - timedelta(days=30), key="sales_start_d")
        with col_date2:
            end_d = st.date_input("End Date", value=today, key="sales_end_d")
        with col_quick:
            st.markdown("<label style='font-size:0.85rem; color:#64748B;'>Quick Date Range</label>", unsafe_allow_html=True)
            q1, q2, q3 = st.columns(3)
            with q1:
                if st.button("Today", use_container_width=True, key="rep_q_today"):
                    st.session_state["sales_start_d"] = today
                    st.session_state["sales_end_d"] = today
                    st.rerun()
            with q2:
                if st.button("7 Days", use_container_width=True, key="rep_q_7d"):
                    st.session_state["sales_start_d"] = today - timedelta(days=7)
                    st.session_state["sales_end_d"] = today
                    st.rerun()
            with q3:
                if st.button("30 Days", use_container_width=True, key="rep_q_30d"):
                    st.session_state["sales_start_d"] = today - timedelta(days=30)
                    st.session_state["sales_end_d"] = today
                    st.rerun()

        if start_d > end_d:
            st.error("Start date cannot be after end date.")
        else:
            sales_rep = ReportService.get_sales_report(start_d, end_d)
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                render_metric_card("Net Realized Sales", format_currency(sales_rep["net_sales"]), f"{sales_rep['total_invoices']} orders billed", accent="navy")
            with m2:
                render_metric_card("Gross Invoiced", format_currency(sales_rep["gross_sales"]), f"Discounts: {format_currency(sales_rep['total_discount'])}", accent="teal")
            with m3:
                render_metric_card("GST Tax Collected", format_currency(sales_rep["total_tax"]), "Statutory tax component", accent="slate")
            with m4:
                render_metric_card("Estimated Net Profit", format_currency(sales_rep["total_profit"]), f"Avg order: {format_currency(sales_rep['avg_order_value'])}", accent="teal")

            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

            c_exp1, c_exp2, _ = st.columns([1.2, 1.4, 2.5])
            with c_exp1:
                csv_data = ReportService.export_to_csv(
                    sales_rep["daily_breakdown"],
                    fieldnames=["date", "invoices", "gross_sales", "discount", "tax", "net_revenue"],
                )
                st.download_button(
                    label="Download Sales CSV",
                    data=csv_data,
                    file_name=f"pharmacare_sales_report_{start_d}_to_{end_d}.csv",
                    mime="text/csv",
                    icon=":material/download:",
                    use_container_width=True,
                    key="sales_csv_btn",
                )
            with c_exp2:
                try:
                    pdf_bytes = ReportService.generate_sales_report_pdf(sales_rep)
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"pharmacare_executive_report_{start_d}_to_{end_d}.pdf",
                        mime="application/pdf",
                        icon=":material/picture_as_pdf:",
                        type="primary",
                        use_container_width=True,
                        key="sales_pdf_btn",
                    )
                except Exception as e:
                    st.error(f"PDF generation error: {e}")

            st.markdown("##### Daily Revenue Breakdown")
            if sales_rep["daily_breakdown"]:
                df_daily = pd.DataFrame(sales_rep["daily_breakdown"])
                df_daily.columns = ["Sale Date", "Invoices", "Gross Subtotal (₹)", "Discount (₹)", "Tax GST (₹)", "Net Revenue (₹)"]
                st.dataframe(df_daily, use_container_width=True, hide_index=True)
            else:
                render_empty_state("No Sales Found", "No sales transactions recorded in this date range.")

    # 2. Profit Margins
    with subtab_profit:
        st.markdown("### Itemized Profitability & Product Margins")
        col_p1, col_p2 = st.columns([1.2, 1.2])
        with col_p1:
            p_start_d = st.date_input("Start Date", value=today - timedelta(days=30), key="profit_start_d")
        with col_p2:
            p_end_d = st.date_input("End Date", value=today, key="profit_end_d")

        profit_items = ReportService.get_profit_margin_report(p_start_d, p_end_d)
        if profit_items:
            tot_profit = sum(item["net_profit"] for item in profit_items)
            tot_revenue = sum(item["total_revenue"] for item in profit_items)
            tot_units = sum(item["units_sold"] for item in profit_items)
            overall_margin = round((tot_profit / tot_revenue) * 100, 1) if tot_revenue > 0 else 0.0

            p1, p2, p3 = st.columns(3)
            with p1:
                render_metric_card("Total Product Profit", format_currency(tot_profit), f"{tot_units} units dispensed", accent="teal")
            with p2:
                render_metric_card("Total Dispensed Revenue", format_currency(tot_revenue), f"Cost: {format_currency(tot_revenue - tot_profit)}", accent="navy")
            with p3:
                render_metric_card("Overall Margin %", f"{overall_margin}%", "Weighted return on sales", accent="slate")

            csv_profit = ReportService.export_to_csv(
                profit_items,
                fieldnames=["medicine", "category", "units_sold", "total_cost", "total_revenue", "net_profit", "margin_percent"],
            )
            st.download_button(
                label="Download Profitability CSV",
                data=csv_profit,
                file_name=f"pharmacare_profit_margins_{p_start_d}_to_{p_end_d}.csv",
                mime="text/csv",
                icon=":material/download:",
                key="profit_csv_btn",
            )
            df_prof = pd.DataFrame(profit_items)
            df_prof.columns = ["Medicine", "Category", "Units Sold", "Total Cost (₹)", "Total Revenue (₹)", "Net Profit (₹)", "Margin %"]
            st.dataframe(df_prof, use_container_width=True, hide_index=True)
        else:
            render_empty_state("No Margin Data", "No items sold during this period.")

    # 3. Inventory Valuation
    with subtab_valuation:
        st.markdown("### Live Inventory Valuation & Capital Realization")
        val_rep = ReportService.get_inventory_valuation_report()
        v1, v2, v3 = st.columns(3)
        with v1:
            render_metric_card("Stock Valuation (Cost)", format_currency(val_rep["total_cost_value"]), f"{val_rep['total_units']:,} units in stock", accent="slate")
        with v2:
            render_metric_card("Stock Valuation (Retail MRP)", format_currency(val_rep["total_retail_value"]), "Retail realization", accent="navy")
        with v3:
            render_metric_card("Unrealized Profit Margin", format_currency(val_rep["total_potential_margin"]), "Gross markup", accent="teal")

        csv_val = ReportService.export_to_csv(
            val_rep["items"],
            fieldnames=["medicine", "category", "dosage_form", "active_stock", "min_stock", "cost_valuation", "retail_valuation", "unrealized_profit"],
        )
        st.download_button(
            label="Download Inventory Valuation CSV",
            data=csv_val,
            file_name=f"pharmacare_inventory_valuation_{today}.csv",
            mime="text/csv",
            icon=":material/download:",
            key="val_csv_btn",
        )
        if val_rep["items"]:
            df_val = pd.DataFrame(val_rep["items"])
            df_val.columns = ["Medicine", "Category", "Form", "Stock Units", "Min Threshold", "Cost Value (₹)", "Retail Value (₹)", "Unrealized Profit (₹)"]
            st.dataframe(df_val, use_container_width=True, hide_index=True)

    # 4. Expiry Loss Audit
    with subtab_loss:
        st.markdown("### Expiry Loss Audit & Financial Exposure")
        risk_rep = ReportService.get_expiry_risk_report()

        e1, e2, e3, e4 = st.columns(4)
        with e1:
            render_metric_card("Quarantined Expired Loss", format_currency(risk_rep["total_expired_loss"]), f"{risk_rep['expired_count']} batches", accent="critical")
        with e2:
            render_metric_card("At-Risk Stock (<30 Days)", format_currency(risk_rep["total_at_risk_value"]), f"{risk_rep['near_expiry_count']} batches near expiry", accent="warning")
        with e3:
            render_metric_card("Total High-Risk Batches", str(risk_rep["expired_count"] + risk_rep["near_expiry_count"]), "Batches requiring action", accent="slate")
        with e4:
            render_metric_card("Total Risk Capital", format_currency(risk_rep["total_expired_loss"] + risk_rep["total_at_risk_value"]), "Financial exposure", accent="critical")

        col_exp_sec, col_near_sec = st.columns(2)
        with col_exp_sec:
            st.markdown("##### 🔴 Quarantined Expired Batches")
            if risk_rep["expired_batches"]:
                df_exp = pd.DataFrame(risk_rep["expired_batches"])[["medicine", "batch_no", "expiry_date", "quantity", "financial_value"]]
                df_exp.columns = ["Medicine", "Batch", "Expiry Date", "Qty", "Loss (₹)"]
                st.dataframe(df_exp, use_container_width=True, hide_index=True)
            else:
                st.info("No expired batches in quarantine.")

        with col_near_sec:
            st.markdown("##### 🟠 Near-Expiry Batches (<30 Days)")
            if risk_rep["near_expiry_batches"]:
                df_near = pd.DataFrame(risk_rep["near_expiry_batches"])[["medicine", "batch_no", "expiry_date", "days_remaining", "quantity", "financial_value"]]
                df_near.columns = ["Medicine", "Batch", "Expiry Date", "Days Left", "Qty", "Risk Value (₹)"]
                st.dataframe(df_near, use_container_width=True, hide_index=True)
            else:
                st.info("No near-expiry batches detected.")


# ==============================================================================
# TAB 2: PATIENT & CUSTOMER DIRECTORY
# ==============================================================================
with tab_customers:
    st.markdown("### Patient & Customer Registry")
    st.caption("Manage patient contact records, recurring prescriptions, and purchase histories")

    all_customers = CustomerService.list_customers()
    total_customers = len(all_customers)
    total_dispensed_sales = sum(c["sale_count"] for c in all_customers)
    total_cust_revenue = sum(c["total_spent"] for c in all_customers)

    ck1, ck2, ck3 = st.columns(3)
    with ck1:
        render_metric_card("Registered Patients", str(total_customers), "Active customer profiles", accent="navy")
    with ck2:
        render_metric_card("Completed Invoices", str(total_dispensed_sales), "Billing invoices", accent="slate")
    with ck3:
        render_metric_card("Customer Turnover", f"₹{total_cust_revenue:,.2f}", "Total patient spend", accent="teal")

    st.markdown("---")

    c_btn, _, c_search = st.columns([2, 1, 3])
    with c_btn:
        if st.button("Add New Patient / Customer", icon=":material/person_add:", type="primary", use_container_width=True, key="rep_add_cust_btn"):
            add_customer_dialog(current_user)

    with c_search:
        search_q = st.text_input("Search directory", placeholder="Search by name, phone, email...", label_visibility="collapsed", key="rep_cust_search")

    customers = CustomerService.list_customers(search=search_q)

    if not customers:
        render_empty_state("No Customers Found", "No patient records match the search query.")
    else:
        c_table = []
        for c in customers:
            c_table.append({
                "Customer ID": c["id"],
                "Patient / Customer Name": c["name"],
                "Phone Number": c["phone"],
                "Email Address": c["email"],
                "Address": c["address"],
                "Prescriptions": f"{c['rx_count']} Rx",
                "Invoices": f"{c['sale_count']} sales",
                "Total Spent": f"₹{c['total_spent']:,.2f}",
            })

        st.dataframe(pd.DataFrame(c_table), use_container_width=True, hide_index=True)

        st.markdown("### Patient Profile & History Inspection")
        cust_choices = {f"{c['name']} (Phone: {c['phone']}) - Spent: ₹{c['total_spent']:,.2f}": c["id"] for c in customers}
        sel_c_label = st.selectbox("Select patient to view history:", options=list(cust_choices.keys()), key="rep_cust_select")
        sel_c_id = cust_choices[sel_c_label]

        if sel_c_id:
            c_detail = CustomerService.get_customer(sel_c_id)
            with st.container(border=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"#### {c_detail['name']}")
                    st.write(f"📞 Phone: **{c_detail['phone']}**")
                    st.write(f"✉️ Email: **{c_detail['email'] or 'N/A'}**")
                with col2:
                    st.write(f"📍 Address: **{c_detail['address'] or 'N/A'}**")
                    st.write(f"💰 Total Billed: **₹{c_detail['total_spent']:,.2f}**")

                st.markdown("##### Past Sales Invoices:")
                if not c_detail["sales"]:
                    st.info("No sales transactions recorded for this patient.")
                else:
                    sales_df = pd.DataFrame(c_detail["sales"])
                    st.dataframe(sales_df, use_container_width=True, hide_index=True)

                col_act1, col_act2, _ = st.columns([1.5, 1.5, 3])
                with col_act1:
                    if st.button("Edit Patient Info", icon=":material/edit:", key=f"edit_cust_btn_{sel_c_id}"):
                        edit_customer_dialog(current_user, c_detail)
                with col_act2:
                    if st.button("Delete Customer", icon=":material/delete:", type="secondary", key=f"del_cust_btn_{sel_c_id}"):
                        delete_customer_dialog(current_user, c_detail)


# ==============================================================================
# TAB 3: NOTIFICATION & ALERT CENTER
# ==============================================================================
with tab_notifications:
    st.markdown("### Notification & Alert Center")
    st.caption("Real-time clinical triggers: expiry warnings, low-stock safety limits, and system notices")

    col_filters, col_actions = st.columns([1.5, 1.2])
    with col_filters:
        filter_tab = st.segmented_control(
            "Filter Alerts",
            options=["All Alerts", "Unread Only", "Critical / Warnings", "Resolved"],
            default="Unread Only" if unread_alerts_count > 0 else "All Alerts",
            label_visibility="collapsed",
            key="notif_filter_ctrl",
        )

    with col_actions:
        na1, na2, na3 = st.columns([1, 1, 1.2])
        with na1:
            if st.button("Mark All Read", icon=":material/done_all:", use_container_width=True, key="notif_mark_all_btn"):
                updated = NotificationService.mark_all_as_read()
                st.toast(f"Marked {updated} alerts as read.", icon="✅")
                st.rerun()
        with na2:
            if st.button("Clear Read", icon=":material/delete_sweep:", use_container_width=True, key="notif_clear_btn"):
                cleared = NotificationService.clear_read_notifications()
                st.toast(f"Cleared {cleared} read notifications.", icon="🗑️")
                st.rerun()
        with na3:
            if admin_mode:
                if st.button("Broadcast Notice", icon=":material/campaign:", type="primary", use_container_width=True, key="notif_bcast_btn"):
                    broadcast_dialog()

    if filter_tab == "Unread Only":
        notifications = NotificationService.get_notifications(is_read=False, limit=60)
    elif filter_tab == "Resolved":
        notifications = NotificationService.get_notifications(is_read=True, limit=60)
    elif filter_tab == "Critical / Warnings":
        all_notifs = NotificationService.get_notifications(limit=100)
        notifications = [n for n in all_notifs if n["severity"] in ["critical", "warning"]]
    else:
        notifications = NotificationService.get_notifications(limit=60)

    if not notifications:
        render_empty_state("No Notifications Found", "Your notification inbox is clean. No active alerts match the filter.")
    else:
        severity_colors = {
            "critical": {"border": "#EF4444", "badge": "badge-critical", "label": "CRITICAL"},
            "warning": {"border": "#F59E0B", "badge": "badge-warning", "label": "WARNING"},
            "info": {"border": "#0D9488", "badge": "badge-info", "label": "INFO"},
            "system": {"border": "#64748B", "badge": "badge-neutral", "label": "SYSTEM"},
        }

        for n in notifications:
            s_info = severity_colors.get(n["severity"], severity_colors["info"])
            border_color = s_info["border"] if not n["is_read"] else "#E2E8F0"
            bg_color = "#FFFFFF" if not n["is_read"] else "#F8FAFC"
            opacity = "1.0" if not n["is_read"] else "0.75"

            with st.container():
                col_content, col_btns = st.columns([4, 1.2])
                with col_content:
                    st.markdown(
                        f"""
                        <div style="background: {bg_color}; border: 1px solid {border_color}; border-left: 5px solid {s_info['border']}; border-radius: 8px; padding: 0.85rem 1.1rem; margin-bottom: 0.5rem; opacity: {opacity};">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                                <div style="display: flex; align-items: center; gap: 0.5rem;">
                                    <strong style="color: #0F172A; font-size: 0.95rem;">{n['title']}</strong>
                                    <span class="status-badge {s_info['badge']}">{n['severity'].upper()}</span>
                                    {"<span class='status-badge badge-safe'>READ</span>" if n['is_read'] else "<span class='status-badge badge-critical'>NEW</span>"}
                                </div>
                                <span style="color: #64748B; font-size: 0.75rem;">{n['created_at']}</span>
                            </div>
                            <div style="color: #334155; font-size: 0.85rem; line-height: 1.4;">
                                {n['message']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col_btns:
                    b1, b2 = st.columns(2)
                    with b1:
                        if not n["is_read"]:
                            if st.button("Read", key=f"read_{n['id']}", icon=":material/check:", use_container_width=True):
                                NotificationService.mark_as_read(n["id"])
                                st.rerun()
                        else:
                            st.caption("Resolved")
                    with b2:
                        if st.button("Delete", key=f"del_{n['id']}", icon=":material/delete:", use_container_width=True):
                            NotificationService.delete_notification(n["id"])
                            st.rerun()


# ==============================================================================
# TAB 4: SYSTEM ADMINISTRATION & RBAC (ADMIN ONLY)
# ==============================================================================
if admin_mode and tab_admin is not None:
    with tab_admin:
        subtab_u, subtab_s, subtab_b = st.tabs([
            "User Accounts & RBAC",
            "Pharmacy Settings",
            "Database Backup & Restore",
        ])

        with subtab_u:
            st.markdown("### Registered Pharmacy Staff Accounts")
            col_add, _ = st.columns([1.5, 3])
            with col_add:
                if st.button("Add New Staff Account", icon=":material/person_add:", type="primary", use_container_width=True, key="adm_add_usr_btn"):
                    add_user_dialog(current_user)

            users_list = AuthService.list_users()
            if users_list:
                df_u = pd.DataFrame([
                    {
                        "ID": u["id"],
                        "Username": u["username"],
                        "Full Name": u["full_name"],
                        "Email": u["email"],
                        "Role": u["role"].upper(),
                        "Phone": u["phone"] or "-",
                        "Status": "ACTIVE" if u["is_active"] else "DEACTIVATED",
                        "Created": u["created_at"],
                    }
                    for u in users_list
                ])
                st.dataframe(df_u, use_container_width=True, hide_index=True)

                st.markdown("##### Quick Staff Account Actions")
                c_sel_user, c_toggle, c_reset = st.columns([2, 1.2, 1.2])
                with c_sel_user:
                    selected_user_id = st.selectbox(
                        "Select Staff Member",
                        options=[u["id"] for u in users_list],
                        format_func=lambda uid: next(f"#{u['id']} - {u['full_name']} ({u['username']}) - {u['role'].upper()}" for u in users_list if u["id"] == uid),
                        key="adm_usr_select",
                    )
                target_user = next((u for u in users_list if u["id"] == selected_user_id), None)
                with c_toggle:
                    if target_user:
                        btn_label = "Deactivate" if target_user["is_active"] else "Activate"
                        btn_type = "secondary" if target_user["is_active"] else "primary"
                        if st.button(f"{btn_label} User", type=btn_type, use_container_width=True, key="adm_toggle_usr_btn"):
                            try:
                                AuthService.toggle_user_status(current_user, target_user["id"])
                                st.toast(f"Status updated for '{target_user['username']}'.", icon="✅")
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))
                with c_reset:
                    if target_user:
                        if st.button("Reset Password", icon=":material/lock_reset:", use_container_width=True, key="adm_reset_pwd_btn"):
                            reset_pwd_dialog(current_user, target_user)

        with subtab_s:
            st.markdown("### Pharmacy Configuration & Statutory Metadata")
            current_settings = SettingService.get_all_settings()
            with st.form("pharmacy_settings_form_tab"):
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    st.markdown("##### Dispensary Profile")
                    pharmacy_name = st.text_input("Pharmacy Name *", value=current_settings.get("pharmacy_name", ""))
                    pharmacy_address = st.text_area("Dispensary Address *", value=current_settings.get("pharmacy_address", ""))
                    pharmacy_phone = st.text_input("Contact Phone *", value=current_settings.get("pharmacy_phone", ""))
                    pharmacy_email = st.text_input("Contact Email *", value=current_settings.get("pharmacy_email", ""))
                with col_s2:
                    st.markdown("##### Licensing & Tax Defaults")
                    pharmacy_dl_no = st.text_input("Drug License No. (DL) *", value=current_settings.get("pharmacy_dl_no", ""))
                    pharmacy_gstin = st.text_input("GSTIN Number *", value=current_settings.get("pharmacy_gstin", ""))
                    default_gst_rate = st.text_input("Default GST Rate (%) *", value=current_settings.get("default_gst_rate", "5.0"))
                    expiry_warning_days = st.text_input("Expiry Alert Window (Days) *", value=current_settings.get("expiry_warning_days", "30"))
                    default_min_stock = st.text_input("Default Low-Stock Threshold *", value=current_settings.get("default_min_stock", "15"))

                st.markdown("##### Invoice Footer Terms & Conditions")
                invoice_footer_note = st.text_input("Invoice Terms Note", value=current_settings.get("invoice_footer_note", "Medicines sold are non-refundable."))

                if st.form_submit_button("Save Pharmacy Configuration", type="primary", use_container_width=True):
                    new_config = {
                        "pharmacy_name": pharmacy_name,
                        "pharmacy_address": pharmacy_address,
                        "pharmacy_phone": pharmacy_phone,
                        "pharmacy_email": pharmacy_email,
                        "pharmacy_dl_no": pharmacy_dl_no,
                        "pharmacy_gstin": pharmacy_gstin,
                        "default_gst_rate": default_gst_rate,
                        "expiry_warning_days": expiry_warning_days,
                        "default_min_stock": default_min_stock,
                        "invoice_footer_note": invoice_footer_note,
                    }
                    try:
                        SettingService.update_settings(current_user, new_config)
                        st.toast("Pharmacy configuration saved successfully!", icon="✅")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

        with subtab_b:
            st.markdown("### Database Snapshot Backup & Hot Restore")
            db_stats = BackupService.get_database_statistics()

            b1, b2, b3, b4 = st.columns(4)
            with b1:
                render_metric_card("Database Size", f"{db_stats['file_size_kb']} KB", "SQLite binary on disk", accent="slate")
            with b2:
                render_metric_card("Total Sales Invoices", str(db_stats["total_sales"]), "Dispensed records", accent="navy")
            with b3:
                render_metric_card("Catalog & Batches", f"{db_stats['total_medicines']} / {db_stats['total_batches']}", "Meds / Batches", accent="teal")
            with b4:
                render_metric_card("Registered Users", str(db_stats["total_users"]), "Staff accounts", accent="slate")

            st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
            col_bk_down, col_bk_up = st.columns(2)
            with col_bk_down:
                with st.container(border=True):
                    st.markdown("#### 📥 Create Hot Backup Snapshot")
                    st.write("Export an instant binary snapshot of the active SQLite database.")
                    if st.button("Generate Downloadable Backup", icon=":material/download:", type="primary", use_container_width=True, key="adm_gen_bk_btn"):
                        try:
                            bk_bytes, bk_filename = BackupService.create_database_backup(current_user)
                            st.download_button(
                                label=f"Save {bk_filename}",
                                data=bk_bytes,
                                file_name=bk_filename,
                                mime="application/x-sqlite3",
                                icon=":material/save:",
                                type="primary",
                                use_container_width=True,
                                key="adm_save_bk_btn",
                            )
                            st.toast("Backup snapshot generated!", icon="✅")
                        except Exception as e:
                            st.error(f"Backup failed: {str(e)}")

            with col_bk_up:
                with st.container(border=True):
                    st.markdown("#### 📤 Restore Database from Snapshot")
                    uploaded_db = st.file_uploader("Select SQLite Backup (.db)", type=["db", "sqlite", "sqlite3"], key="adm_db_uploader")
                    confirm_restore = st.checkbox("I understand this will overwrite live pharmacy data.", key="adm_confirm_restore")
                    if st.button("Execute Restore", icon=":material/restore:", type="secondary", disabled=not (uploaded_db and confirm_restore), use_container_width=True, key="adm_exec_restore_btn"):
                        try:
                            raw_bytes = uploaded_db.read()
                            BackupService.restore_database_backup(current_user, raw_bytes)
                            st.success("Database restored successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Restore failed: {str(e)}")


# ==============================================================================
# TAB 5: SECURITY AUDIT LOGS (ADMIN ONLY)
# ==============================================================================
if admin_mode and tab_audit is not None:
    with tab_audit:
        st.markdown("### Compliance & Audit Logs")
        st.caption("Immutable tamper-evident log of system operations, authentications, and stock adjustments")

        col_mod, col_act, col_user, col_search = st.columns([1.2, 1.2, 1.2, 1.6])
        with col_mod:
            module_filter = st.selectbox("Module", options=["All", "AUTH", "BILLING", "PURCHASES", "INVENTORY", "USERS", "SETTINGS", "DATABASE"], key="audit_mod_filter")
        with col_act:
            action_filter = st.selectbox("Action", options=["All", "LOGIN", "CREATE", "UPDATE", "DELETE", "DISPOSE", "BACKUP", "RESTORE", "CHANGE_PASSWORD"], key="audit_act_filter")
        with col_user:
            user_search = st.text_input("Username", placeholder="e.g. admin", key="audit_usr_search")
        with col_search:
            keyword = st.text_input("Search Description", placeholder="e.g. invoice, batch, Paracetamol...", key="audit_kw_search")

        all_logs = AuditService.get_audit_logs(limit=250)
        filtered_logs = []
        for log in all_logs:
            if module_filter != "All" and log.get("module") != module_filter:
                continue
            if action_filter != "All" and log.get("action") != action_filter:
                continue
            if user_search and user_search.lower() not in (log.get("username") or "").lower():
                continue
            if keyword and keyword.lower() not in (log.get("description") or "").lower():
                continue
            filtered_logs.append(log)

        col_count, col_dl = st.columns([3, 1.2])
        with col_count:
            st.caption(f"Showing **{len(filtered_logs)}** audit events")
        with col_dl:
            if filtered_logs:
                csv_logs = ReportService.export_to_csv(
                    filtered_logs,
                    fieldnames=["timestamp", "username", "module", "action", "description", "ip_address"],
                )
                st.download_button(
                    label="Export Audit Trail (CSV)",
                    data=csv_logs,
                    file_name="pharmacare_audit_trail.csv",
                    mime="text/csv",
                    icon=":material/download:",
                    use_container_width=True,
                    key="audit_csv_btn",
                )

        if not filtered_logs:
            render_empty_state("No Audit Events Found", "No system actions match the selected criteria.", icon="🔍")
        else:
            df_logs = pd.DataFrame(filtered_logs)[["timestamp", "username", "module", "action", "description", "ip_address"]]
            df_logs.columns = ["Timestamp", "User", "Module", "Action", "Description", "IP Address"]
            st.dataframe(df_logs, use_container_width=True, hide_index=True)


# ==============================================================================
# MODAL DIALOGS
# ==============================================================================

@st.dialog("Register New Patient / Customer")
def add_customer_dialog(curr_user):
    with st.form("add_customer_form_dlg"):
        name = st.text_input("Full Name *", placeholder="e.g. Ramesh Sharma")
        c1, c2 = st.columns(2)
        with c1:
            phone = st.text_input("Phone Number *", placeholder="e.g. +91 98765 43210")
        with c2:
            email = st.text_input("Email Address", placeholder="e.g. ramesh@example.com")
        addr = st.text_area("Residential Address", placeholder="Apartment, Street, City...")

        if st.form_submit_button("Save Customer Record", type="primary", use_container_width=True):
            try:
                CustomerService.create_customer(curr_user, {"name": name, "phone": phone, "email": email, "address": addr})
                st.toast(f"Patient '{name}' created!", icon="✅")
                st.rerun()
            except AppException as e:
                st.error(e.message)


@st.dialog("Edit Patient Profile")
def edit_customer_dialog(curr_user, cust_data):
    with st.form("edit_customer_form_dlg"):
        name = st.text_input("Full Name *", value=cust_data["name"])
        c1, c2 = st.columns(2)
        with c1:
            phone = st.text_input("Phone Number *", value=cust_data["phone"])
        with c2:
            email = st.text_input("Email Address", value=cust_data["email"])
        addr = st.text_area("Residential Address", value=cust_data["address"])

        if st.form_submit_button("Update Profile", type="primary", use_container_width=True):
            try:
                CustomerService.update_customer(curr_user, cust_data["id"], {"name": name, "phone": phone, "email": email, "address": addr})
                st.toast("Profile updated!", icon="✅")
                st.rerun()
            except AppException as e:
                st.error(e.message)


@st.dialog("Delete Customer Profile")
def delete_customer_dialog(curr_user, cust_data):
    st.write(f"Delete record for **{cust_data['name']}**?")
    if st.button("Confirm Delete", type="primary", use_container_width=True):
        try:
            CustomerService.delete_customer(curr_user, cust_data["id"])
            st.toast("Customer deleted.", icon="✅")
            st.rerun()
        except ConflictException as ce:
            st.error(ce.message)
        except AppException as e:
            st.error(e.message)


@st.dialog("Broadcast System Notice")
def broadcast_dialog():
    with st.form("broadcast_notice_form_dlg"):
        title = st.text_input("Notice Title *", placeholder="e.g. Scheduled Stock Audit")
        message = st.text_area("Notice Details *", placeholder="Operational instructions...")
        severity = st.selectbox("Severity Level", options=["info", "warning", "critical"], format_func=lambda s: s.capitalize())

        if st.form_submit_button("Broadcast Notice", type="primary", use_container_width=True):
            if not title or not message:
                st.error("Please fill in both title and details.")
            else:
                try:
                    NotificationService.create_notification(title=title, message=message, severity=severity, notif_type="system")
                    st.toast("Notice broadcasted!", icon="📢")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))


@st.dialog("Create Staff User Account")
def add_user_dialog(curr_user):
    with st.form("add_user_form_dlg"):
        username = st.text_input("Username *", placeholder="e.g. jdoe")
        full_name = st.text_input("Full Name *", placeholder="e.g. John Doe")
        email = st.text_input("Email Address *", placeholder="e.g. jdoe@pharmacare.local")
        password = st.text_input("Temporary Password *", type="password")
        role = st.selectbox("Role *", options=["pharmacist", "admin"], index=0)
        phone = st.text_input("Phone Number", placeholder="e.g. +91 98765 43210")

        if st.form_submit_button("Create Account", type="primary", use_container_width=True):
            try:
                AuthService.create_user(curr_user, username, email, password, full_name, role, phone)
                st.toast(f"User '{username}' created!", icon="✅")
                st.rerun()
            except Exception as e:
                st.error(str(e))


@st.dialog("Admin Password Reset")
def reset_pwd_dialog(curr_user, target_user):
    st.write(f"Reset password for **{target_user['full_name']}** (`{target_user['username']}`):")
    with st.form("reset_pwd_form_dlg"):
        new_pwd = st.text_input("New Temporary Password *", type="password")
        confirm_pwd = st.text_input("Confirm New Password *", type="password")
        if st.form_submit_button("Set New Password", type="primary", use_container_width=True):
            if not new_pwd or not confirm_pwd:
                st.error("Please enter and confirm password.")
            elif new_pwd != confirm_pwd:
                st.error("Passwords do not match.")
            elif len(new_pwd) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                try:
                    AuthService.admin_reset_password(curr_user, target_user["id"], new_pwd)
                    st.toast(f"Password reset for '{target_user['username']}'!", icon="✅")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
