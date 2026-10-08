"""Point of Sale (POS) Counter Billing and live PDF invoice checkout page."""

from datetime import date
from typing import Dict, Any, List
import streamlit as st
import pandas as pd

from app.utils.session import is_authenticated, get_current_user
from app.components.styles import inject_custom_styles
from app.components.sidebar import render_sidebar
from app.components.status_badge import render_status_badge
from app.components.empty_state import render_empty_state
from app.services.sale_service import SaleService
from app.services.medicine_service import MedicineService
from app.services.customer_service import CustomerService
from app.services.prescription_service import PrescriptionService
from app.services.batch_service import BatchService
from app.utils.pdf_invoice import generate_invoice_pdf
from app.core.exceptions import AppException

if not is_authenticated():
    st.warning("Please log in to access the system.")
    st.stop()

inject_custom_styles()
render_sidebar()

current_user = get_current_user()

st.markdown("## Pharmacy Counter Billing & POS")
st.caption("Point of Sale dispensing, barcode search, FEFO batch allocation, GST calculation, and invoice history")

tab_pos, tab_history = st.tabs(["Counter Billing POS", "Sales History & Invoices"])

# ==============================================================================
# TAB 1: COUNTER BILLING POS
# ==============================================================================
with tab_pos:
    # Initialize POS session state
    if "billing_cart" not in st.session_state:
        st.session_state["billing_cart"] = []
    if "last_completed_sale" not in st.session_state:
        st.session_state["last_completed_sale"] = None
    if "is_billing_submitting" not in st.session_state:
        st.session_state["is_billing_submitting"] = False

    # Layout: 2 Columns (Left: Customer/Prescription & Product Selector; Right: Live Cart & Checkout)
    col_left, col_right = st.columns([1.1, 1.4])

    # --------------------------------------------------------------------------
    # LEFT PANEL: CUSTOMER, PRESCRIPTION & PRODUCT SEARCH
    # --------------------------------------------------------------------------
    with col_left:
        # 1. Customer & Prescription Section
        with st.container(border=True):
            st.markdown("##### 👤 Patient & Prescription Details")
            
            customers = CustomerService.list_customers()
            cust_choices = {"Walk-in Retail Customer": None}
            for c in customers:
                cust_choices[f"{c['name']} ({c['phone']})"] = c["id"]

            c_sel_col, c_add_col = st.columns([3, 1])
            with c_sel_col:
                sel_cust_label = st.selectbox("Select Customer", options=list(cust_choices.keys()), key="pos_cust_select")
                selected_cust_id = cust_choices[sel_cust_label]
            with c_add_col:
                st.write("")
                if st.button("➕ New", key="pos_quick_cust_btn", help="Quick register new customer"):
                    quick_add_customer_dialog(current_user)

            # Prescriptions dropdown (filtered by customer if selected)
            prescriptions = PrescriptionService.list_prescriptions(customer_id=selected_cust_id)
            rx_choices = {"None (Over the Counter - OTC)": None}
            for rx in prescriptions:
                rx_choices[f"Rx #{rx['id']} - {rx['patient_name']} (Dr. {rx['doctor_name']})"] = rx["id"]

            rx_sel_col, rx_add_col = st.columns([3, 1])
            with rx_sel_col:
                sel_rx_label = st.selectbox("Attach Doctor Prescription", options=list(rx_choices.keys()), key="pos_rx_select")
                selected_rx_id = rx_choices[sel_rx_label]
            with rx_add_col:
                st.write("")
                if st.button("➕ Rx", key="pos_quick_rx_btn", help="Quick log new prescription"):
                    quick_add_rx_dialog(current_user, selected_cust_id)

        # 2. Product Search & Add to Cart
        with st.container(border=True):
            st.markdown("##### 💊 Product Search & Barcode Scan")

            active_meds = MedicineService.list_medicines(status="active")
            med_dict = {f"{m['name']} ({m['strength']}) - Stock: {m['total_stock']} | ₹{m['selling_price']:.2f}": m for m in active_meds}

            # Barcode quick scan / direct search
            barcode_query = st.text_input("Scan Barcode or Search Product", placeholder="Scan barcode or type name...", key="pos_barcode_input")

            # Auto-match barcode if exact
            selected_med_from_bc = None
            if barcode_query:
                clean_bc = barcode_query.strip().lower()
                for m in active_meds:
                    if (m["barcode"] and m["barcode"].lower() == clean_bc) or (clean_bc in m["name"].lower()):
                        selected_med_from_bc = m
                        break

            sel_product_label = st.selectbox("Select Medicine from Catalog", options=list(med_dict.keys()), key="pos_med_select")
            active_med_item = selected_med_from_bc if selected_med_from_bc else med_dict[sel_product_label]

            # Display Selected Product Info Chip
            st.caption(
                f"Generic: **{active_med_item['generic_name']}** | Category: **{active_med_item['category_name']}** | "
                f"Form: **{active_med_item['dosage_form']}** | Rx Required: **{'YES' if active_med_item['prescription_required'] else 'NO (OTC)'}**"
            )

            p_c1, p_c2 = st.columns(2)
            with p_c1:
                add_qty = st.number_input("Quantity to Dispense *", min_value=1, max_value=max(1, active_med_item["total_stock"]), value=1, step=1)
            with p_c2:
                st.write(f"Unit Price: **₹{active_med_item['selling_price']:.2f}**")
                line_sub = round(add_qty * active_med_item["selling_price"], 2)
                st.write(f"Line Subtotal: **₹{line_sub:.2f}**")

            if st.button("🛒 Add to Counter Cart", type="primary", use_container_width=True):
                if active_med_item["total_stock"] <= 0:
                    st.error(f"Cannot add '{active_med_item['name']}': Total available non-expired stock is 0 units.")
                elif add_qty > active_med_item["total_stock"]:
                    st.error(f"Requested {add_qty} units exceeds available stock ({active_med_item['total_stock']} units).")
                else:
                    existing_item = next((it for it in st.session_state["billing_cart"] if it["medicine_id"] == active_med_item["id"]), None)
                    if existing_item:
                        existing_item["quantity"] += int(add_qty)
                        existing_item["subtotal"] = round(existing_item["quantity"] * existing_item["unit_price"], 2)
                    else:
                        st.session_state["billing_cart"].append({
                            "medicine_id": active_med_item["id"],
                            "medicine_name": f"{active_med_item['name']} ({active_med_item['strength']})",
                            "dosage_form": active_med_item["dosage_form"],
                            "prescription_required": active_med_item["prescription_required"],
                            "quantity": int(add_qty),
                            "unit_price": float(active_med_item["selling_price"]),
                            "subtotal": line_sub,
                        })
                    st.toast(f"Added {active_med_item['name']} to cart!", icon="🛒")
                    st.rerun()

    # --------------------------------------------------------------------------
    # RIGHT PANEL: LIVE CART, TOTALS & CHECKOUT
    # --------------------------------------------------------------------------
    with col_right:
        cart = st.session_state["billing_cart"]

        with st.container(border=True):
            st.markdown("### 🛒 Counter Cart & Invoice Summary")

            if not cart:
                render_empty_state("Cart is Empty", "Add pharmaceutical products from the left panel to begin billing.", icon="🛍️")
            else:
                cart_display = []
                cart_subtotal = 0.0
                rx_in_cart = False

                for idx, it in enumerate(cart):
                    cart_subtotal += it["subtotal"]
                    if it["prescription_required"]:
                        rx_in_cart = True

                    cart_display.append({
                        "#": idx + 1,
                        "Medicine Item": it["medicine_name"],
                        "Qty": f"{it['quantity']} units",
                        "Price": f"₹{it['unit_price']:.2f}",
                        "Subtotal": f"₹{it['subtotal']:,.2f}",
                        "Rx Req": "⚠️ Schedule H" if it["prescription_required"] else "OTC",
                    })

                st.dataframe(pd.DataFrame(cart_display), use_container_width=True, hide_index=True)

                if rx_in_cart and not selected_rx_id:
                    st.error("⚠️ **Schedule H Prescription Required**: Your cart contains prescription-only drugs. Please select an attached doctor prescription in the left panel before completing checkout.")

                col_clr, _ = st.columns([2, 3])
                with col_clr:
                    if st.button("Clear Cart", icon=":material/delete_sweep:", type="secondary"):
                        st.session_state["billing_cart"] = []
                        st.rerun()

                st.markdown("---")

                fc1, fc2 = st.columns(2)
                with fc1:
                    discount_p = st.number_input("Discount %", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
                    pay_method = st.selectbox("Payment Method *", options=["Cash", "UPI", "Card", "Net Banking", "Other"])
                with fc2:
                    tax_p = st.number_input("GST / Tax %", min_value=0.0, max_value=28.0, value=5.0, step=0.5)
                    bill_notes = st.text_input("Invoice Notes (Optional)", placeholder="e.g. Regular monthly refill")

                disc_amount = round(cart_subtotal * (discount_p / 100.0), 2)
                taxable = cart_subtotal - disc_amount
                tax_amount = round(taxable * (tax_p / 100.0), 2)
                grand_total = round(taxable + tax_amount, 2)

                st.markdown(
                    f"""
                    <div style="background: #0F172A; color: #F8FAFC; padding: 1.25rem; border-radius: 12px; margin: 1rem 0;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.35rem; font-size: 0.9rem; color: #94A3B8;">
                            <span>Subtotal:</span>
                            <span>₹{cart_subtotal:,.2f}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.35rem; font-size: 0.9rem; color: #94A3B8;">
                            <span>Discount ({discount_p}%):</span>
                            <span>- ₹{disc_amount:,.2f}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.9rem; color: #94A3B8;">
                            <span>GST Tax ({tax_p}%):</span>
                            <span>+ ₹{tax_amount:,.2f}</span>
                        </div>
                        <hr style="border-color: #334155; margin: 0.5rem 0;" />
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 1.1rem; font-weight: 600;">NET TOTAL PAYABLE:</span>
                            <span style="font-size: 1.75rem; font-weight: 700; color: #2DD4BF;">₹{grand_total:,.2f}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                checkout_disabled = bool(rx_in_cart and not selected_rx_id) or st.session_state.get("is_billing_submitting", False)

                if st.button("💳 Complete Sale & Generate Tax Invoice", type="primary", use_container_width=True, disabled=checkout_disabled):
                    st.session_state["is_billing_submitting"] = True
                    try:
                        sale_result = SaleService.create_sale(
                            current_user=current_user,
                            cart_items=cart,
                            customer_id=selected_cust_id,
                            prescription_id=selected_rx_id,
                            payment_method=pay_method,
                            discount_percent=float(discount_p),
                            tax_percent=float(tax_p),
                            notes=bill_notes,
                        )
                        st.session_state["billing_cart"] = []
                        st.session_state["last_completed_sale"] = sale_result
                        st.toast(f"Sale completed! Invoice #{sale_result['invoice_no']} generated.", icon="🎉")
                        st.rerun()
                    except AppException as e:
                        st.error(e.message)
                    finally:
                        st.session_state["is_billing_submitting"] = False

    completed_sale = st.session_state.get("last_completed_sale")
    if completed_sale:
        st.markdown("---")
        with st.container(border=True):
            st.markdown(f"### 🧾 Latest Completed Invoice: **{completed_sale['invoice_no']}**")
            st.success(f"Sale of **₹{completed_sale['total_amount']:,.2f}** ({completed_sale['payment_method']}) recorded successfully.")

            pdf_bytes = generate_invoice_pdf(completed_sale)

            dl_col1, dl_col2, _ = st.columns([2, 2, 2])
            with dl_col1:
                st.download_button(
                    label="📄 Download Tax Invoice (PDF)",
                    data=pdf_bytes,
                    file_name=f"{completed_sale['invoice_no']}.pdf",
                    mime="application/pdf",
                    icon=":material/download:",
                    type="primary",
                    use_container_width=True,
                )
            with dl_col2:
                if st.button("New Billing Session", icon=":material/refresh:", use_container_width=True):
                    st.session_state["last_completed_sale"] = None
                    st.rerun()

# ==============================================================================
# TAB 2: SALES HISTORY & INVOICE REPRINT
# ==============================================================================
with tab_history:
    all_sales = SaleService.list_sales(limit=500)
    total_invoices = len(all_sales)
    total_revenue = sum(s["total_amount"] for s in all_sales)
    avg_ticket = (total_revenue / total_invoices) if total_invoices > 0 else 0.0

    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Total Completed Invoices", str(total_invoices))
    with k2:
        st.metric("Total Gross Revenue", f"₹{total_revenue:,.2f}")
    with k3:
        st.metric("Average Order Value", f"₹{avg_ticket:,.2f}")

    st.markdown("---")

    f1, f2 = st.columns([3, 2])
    with f1:
        search_term = st.text_input("Search Invoices", placeholder="Search by invoice number, customer name...", key="hist_search_input")
    with f2:
        selected_pm = st.selectbox("Payment Method", options=["All", "Cash", "UPI", "Card", "Net Banking", "Other"], key="hist_pm_select")

    sales_filtered = SaleService.list_sales(
        payment_method=selected_pm,
        search=search_term,
        limit=200,
    )

    if not sales_filtered:
        render_empty_state("No Sales Found", "No billing invoices match the specified criteria.")
    else:
        s_table = []
        for s in sales_filtered:
            s_table.append({
                "Invoice No": s["invoice_no"],
                "Customer": s["customer_name"],
                "Date & Time": s["sale_date"],
                "Items": f"{s['item_count']} items",
                "Subtotal": f"₹{s['subtotal']:,.2f}",
                "Discount": f"- ₹{s['discount']:,.2f}",
                "Tax (GST)": f"+ ₹{s['tax']:,.2f}",
                "Total Amount": f"₹{s['total_amount']:,.2f}",
                "Payment": s["payment_method"],
                "Billed By": s["pharmacist_name"],
            })

        st.dataframe(pd.DataFrame(s_table), use_container_width=True, hide_index=True)

        st.markdown("### Invoice Detailed Breakdown & PDF Reprint")
        inv_choices = {f"{s['invoice_no']} - {s['customer_name']} (₹{s['total_amount']:,.2f})": s["id"] for s in sales_filtered}
        sel_inv_label = st.selectbox("Select invoice to inspect details & download PDF:", options=list(inv_choices.keys()), key="hist_inv_select")
        sel_inv_id = inv_choices[sel_inv_label]

        if sel_inv_id:
            sale_detail = SaleService.get_sale(sel_inv_id)
            with st.container(border=True):
                col_h1, col_h2, col_h3 = st.columns([2, 2, 2])
                with col_h1:
                    st.markdown(f"#### Invoice: **{sale_detail['invoice_no']}**")
                    st.caption(f"Date: **{sale_detail['sale_date']}**")
                    st.write(f"👤 Patient: **{sale_detail['customer_name']}** (Phone: `{sale_detail['customer_phone']}`)")
                with col_h2:
                    st.write(f"💳 Payment Method: **{sale_detail['payment_method']}**")
                    st.write(f"🩺 Prescribing Doctor: **{sale_detail['doctor_name']}**")
                    st.write(f"👨‍⚕️ Dispensing Pharmacist: **{sale_detail['pharmacist_name']}**")
                with col_h3:
                    st.write(f"💰 Grand Total: **₹{sale_detail['total_amount']:,.2f}**")
                    st.write(f"📈 Profit Margin: **₹{sale_detail['profit']:,.2f}**")
                    render_status_badge("paid", "PAID & DISPENSED")

                st.markdown("##### Dispensed Batch Items in this Invoice:")
                items_table = []
                for it in sale_detail["items"]:
                    items_table.append({
                        "Medicine Item": it["medicine_name"],
                        "Dispensed Batch No": it["batch_no"],
                        "Batch Expiry": it["expiry_date"],
                        "Quantity": f"{it['quantity']} units",
                        "Selling Price": f"₹{it['unit_price']:.2f}",
                        "Purchase Cost": f"₹{it['purchase_price']:.2f}",
                        "Subtotal": f"₹{it['subtotal']:,.2f}",
                        "Gross Profit": f"₹{it['profit']:,.2f}",
                    })
                st.dataframe(pd.DataFrame(items_table), use_container_width=True, hide_index=True)

                st.markdown("---")
                pdf_bytes = generate_invoice_pdf(sale_detail)
                st.download_button(
                    label=f"📄 Download Duplicate PDF Invoice ({sale_detail['invoice_no']})",
                    data=pdf_bytes,
                    file_name=f"{sale_detail['invoice_no']}.pdf",
                    mime="application/pdf",
                    icon=":material/download:",
                    type="primary",
                    key="hist_pdf_dl_btn",
                )


# ==============================================================================
# QUICK ADD MODALS (CUSTOMER & PRESCRIPTION)
# ==============================================================================

@st.dialog("Quick Register Customer")
def quick_add_customer_dialog(curr_user):
    """Modal to register customer without leaving billing page."""
    with st.form("quick_cust_form"):
        st.write("Register customer for instant billing:")
        name = st.text_input("Full Name *", placeholder="e.g. Ramesh Sharma")
        phone = st.text_input("Phone Number *", placeholder="e.g. +91 98765 43210")
        email = st.text_input("Email (Optional)")
        addr = st.text_input("Address (Optional)")

        submit = st.form_submit_button("Save Customer", type="primary", use_container_width=True)
        if submit:
            try:
                CustomerService.create_customer(curr_user, {"name": name, "phone": phone, "email": email, "address": addr})
                st.toast("Customer registered!", icon="✅")
                st.rerun()
            except AppException as e:
                st.error(e.message)


@st.dialog("Quick Log Prescription")
def quick_add_rx_dialog(curr_user, cust_id):
    """Modal to log prescription without leaving billing page."""
    with st.form("quick_rx_form"):
        st.write("Log prescription for Schedule H dispensing:")
        p_name = st.text_input("Patient Name *", placeholder="e.g. Rajesh Sharma")
        doc_name = st.text_input("Doctor Name *", placeholder="e.g. Dr. Sneha Roy, MD")
        doc_reg = st.text_input("Doctor Reg No", placeholder="e.g. MCI-88492-A")
        diag = st.text_input("Diagnosis", placeholder="e.g. Acute Bronchitis")

        submit = st.form_submit_button("Save Prescription", type="primary", use_container_width=True)
        if submit:
            try:
                PrescriptionService.create_prescription(
                    curr_user,
                    {
                        "customer_id": cust_id,
                        "patient_name": p_name,
                        "doctor_name": doc_name,
                        "doctor_reg_no": doc_reg,
                        "diagnosis": diag,
                        "prescription_date": date.today(),
                    },
                )
                st.toast("Prescription logged!", icon="✅")
                st.rerun()
            except AppException as e:
                st.error(e.message)
