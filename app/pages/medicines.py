"""Consolidated Medicines, Batches, Expiry Monitor, CSV Import, and Low-Stock Reorders Page."""

from datetime import date, timedelta
from typing import Optional, Dict, Any, List
import io
import streamlit as st
import pandas as pd

from app.utils.session import is_authenticated, get_current_user
from app.components.styles import inject_custom_styles
from app.components.sidebar import render_sidebar
from app.components.status_badge import render_status_badge
from app.components.metric_card import render_metric_card
from app.components.empty_state import render_empty_state
from app.services.medicine_service import MedicineService
from app.services.category_service import CategoryService
from app.services.batch_service import BatchService
from app.services.inventory_service import InventoryService
from app.core.exceptions import AppException, ValidationError, ConflictException

# Enforce authentication guard
if not is_authenticated():
    st.warning("Please log in to access the system.")
    st.stop()

inject_custom_styles()
render_sidebar()

current_user = get_current_user()

st.markdown("## Medicines & Inventory Management")
st.caption("Centralized control for medicine master data, physical batch tracking, expiry quarantine, low-stock reorders, and CSV inventory import")

tab_catalog, tab_expiry, tab_low_stock, tab_import, tab_categories = st.tabs([
    "Medicines & Batches",
    "Expiry & Quarantine",
    "Low Stock & Reorders",
    "Import CSV Inventory",
    "Categories",
])

# ==============================================================================
# TAB 1: MEDICINES & BATCHES CATALOG
# ==============================================================================
with tab_catalog:
    medicines_all = MedicineService.list_medicines()
    total_meds = len(medicines_all)
    total_units = sum(m["total_stock"] for m in medicines_all)
    low_stock_count = sum(1 for m in medicines_all if m["is_low_stock"])
    rx_count = sum(1 for m in medicines_all if m["prescription_required"])

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_metric_card("Total Products", str(total_meds), "Catalog master items", accent="teal")
    with k2:
        render_metric_card("Total Active Stock", f"{total_units:,}", "Units in physical batches", accent="green")
    with k3:
        render_metric_card("Low Stock Alerts", str(low_stock_count), "Below reorder threshold", accent="amber" if low_stock_count > 0 else "teal")
    with k4:
        render_metric_card("Prescription Only", str(rx_count), "Schedule H / Rx required", accent="blue")

    st.markdown("---")

    c_btn, _, c_search = st.columns([2, 1, 3])
    with c_btn:
        if st.button("Add New Medicine", icon=":material/add_circle:", type="primary", use_container_width=True):
            add_medicine_dialog(current_user)

    with c_search:
        search_kw = st.text_input("Search catalog", placeholder="Search by name, generic, barcode...", label_visibility="collapsed", key="med_search_input")

    f1, f2, f3 = st.columns(3)
    with f1:
        cat_options = {"All Categories": None}
        for c in CategoryService.list_categories():
            cat_options[c["name"]] = c["id"]
        selected_cat_name = st.selectbox("Filter by Category", options=list(cat_options.keys()), key="med_cat_filter")
        selected_cat_id = cat_options[selected_cat_name]

    with f2:
        selected_rx_filter = st.selectbox("Prescription Requirement", options=["All", "Rx Required Only", "OTC Only"], key="med_rx_filter")
        rx_val = True if selected_rx_filter == "Rx Required Only" else (False if selected_rx_filter == "OTC Only" else None)

    with f3:
        selected_status = st.selectbox("Status", options=["All", "Active", "Inactive"], key="med_status_filter")
        status_val = selected_status.lower() if selected_status != "All" else None

    filtered_medicines = MedicineService.list_medicines(
        search=search_kw,
        category_id=selected_cat_id,
        status=status_val,
        prescription_required=rx_val,
    )

    if not filtered_medicines:
        render_empty_state("No Medicines Found", "No medicines match your selected filters. Try clearing search or add a medicine.")
    else:
        st.markdown(f"**Showing {len(filtered_medicines)} medicine(s):**")
        table_rows = []
        for m in filtered_medicines:
            stock_display = f"{m['total_stock']} units"
            if m["is_low_stock"]:
                stock_display += " (Low Stock)"

            table_rows.append({
                "ID": m["id"],
                "Medicine Name": m["name"],
                "Generic Name": m["generic_name"],
                "Category": m["category_name"],
                "Form & Strength": f"{m['dosage_form']} - {m['strength']}",
                "Price": f"₹{m['selling_price']:.2f}",
                "Available Stock": stock_display,
                "Min Stock": m["min_stock"],
                "Rx Req.": "Yes (Rx)" if m["prescription_required"] else "No (OTC)",
                "Status": m["status"].capitalize(),
            })

        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

        st.markdown("### Medicine Details & Batch Inspection")
        med_choices = {f"{m['name']} ({m['strength']}) - Stock: {m['total_stock']}": m["id"] for m in filtered_medicines}
        selected_med_label = st.selectbox("Select medicine to inspect details & batches:", options=list(med_choices.keys()), key="med_detail_select")
        selected_med_id = med_choices[selected_med_label]

        if selected_med_id:
            med_detail = MedicineService.get_medicine(selected_med_id)
            with st.container(border=True):
                col_d1, col_d2, col_d3 = st.columns([2, 2, 2])
                with col_d1:
                    st.markdown(f"#### {med_detail['name']}")
                    st.caption(f"Generic: **{med_detail['generic_name']}**")
                    st.write(f"Category: **{med_detail['category_name']}**")
                    st.write(f"Manufacturer: **{med_detail['manufacturer'] or '-'}**")
                with col_d2:
                    st.write(f"Dosage Form: **{med_detail['dosage_form']}**")
                    st.write(f"Strength: **{med_detail['strength']}**")
                    st.write(f"Selling Price: **₹{med_detail['selling_price']:.2f}**")
                    st.write(f"Barcode: **`{med_detail['barcode'] or 'N/A'}`**")
                with col_d3:
                    st.write(f"Available Stock: **{med_detail['total_stock']} units**")
                    st.write(f"Min Stock Threshold: **{med_detail['min_stock']} units**")
                    st.write(f"Schedule H Rx: **{'Required' if med_detail['prescription_required'] else 'Not Required (OTC)'}**")
                    render_status_badge(med_detail["status"])

                st.markdown("##### Associated Batches:")
                batches = med_detail["batches"]
                if not batches:
                    st.info("No physical batches recorded for this medicine.")
                else:
                    batch_display = []
                    for b in batches:
                        batch_display.append({
                            "Batch No": b["batch_no"],
                            "Expiry Date": b["expiry_date"],
                            "Days Remaining": f"{b['days_remaining']} days" if b['days_remaining'] >= 0 else f"Expired ({abs(b['days_remaining'])}d ago)",
                            "Quantity": f"{b['quantity']} units",
                            "Purchase Price": f"₹{b['purchase_price']:.2f}",
                            "Status": b["status"].replace("_", " ").title(),
                        })
                    st.dataframe(pd.DataFrame(batch_display), use_container_width=True, hide_index=True)

                col_act1, col_act2, col_act3, _ = st.columns([1.5, 1.5, 1.5, 1.5])
                with col_act1:
                    if st.button("Add Batch", icon=":material/add_box:", key=f"add_batch_{selected_med_id}", type="primary"):
                        add_batch_dialog(current_user, preselect_med_id=selected_med_id)
                with col_act2:
                    if st.button("Edit Info", icon=":material/edit:", key=f"edit_btn_{selected_med_id}"):
                        edit_medicine_dialog(current_user, med_detail)
                with col_act3:
                    if st.button("Deactivate", icon=":material/delete:", type="secondary", key=f"del_btn_{selected_med_id}"):
                        delete_medicine_dialog(current_user, med_detail)


# ==============================================================================
# TAB 2: EXPIRY DATE & QUARANTINE MONITOR
# ==============================================================================
with tab_expiry:
    col_exp_head, col_window = st.columns([3, 1])
    with col_exp_head:
        st.markdown("### Expiry Date & Quarantine Monitor")
        st.caption("Track drug expiration, prevent expired sales, and log bio-waste disposal")
    with col_window:
        default_days = InventoryService.get_expiry_warning_days()
        window_days = st.selectbox(
            "Warning Window",
            options=[15, 30, 45, 60, 90],
            index=[15, 30, 45, 60, 90].index(default_days) if default_days in [15, 30, 45, 60, 90] else 1,
            key="expiry_window_select",
        )

    expiry_data = InventoryService.get_expiry_overview(warning_days=window_days)

    ek1, ek2, ek3, ek4 = st.columns(4)
    with ek1:
        render_metric_card("Expired Batches", str(expiry_data["expired_batches_count"]), f"{expiry_data['expired_units_total']} units quarantined", accent="red" if expiry_data["expired_batches_count"] > 0 else "teal")
    with ek2:
        render_metric_card("Expired Loss Value", f"₹{expiry_data['expired_loss_value']:,.2f}", "Cost of expired stock", accent="red" if expiry_data["expired_loss_value"] > 0 else "teal")
    with ek3:
        render_metric_card(f"Expiring ≤{window_days}d", str(expiry_data["expiring_soon_batches_count"]), f"{expiry_data['expiring_soon_units_total']} FEFO units", accent="amber" if expiry_data["expiring_soon_batches_count"] > 0 else "teal")
    with ek4:
        render_metric_card("Near-Expiry Value", f"₹{expiry_data['expiring_soon_value']:,.2f}", "Turnover value", accent="amber" if expiry_data["expiring_soon_value"] > 0 else "teal")

    st.markdown("---")

    subtab_exp, subtab_near, subtab_all = st.tabs([
        f"Expired Batches ({expiry_data['expired_batches_count']})",
        f"Expiring Soon ({expiry_data['expiring_soon_batches_count']})",
        f"All Batches ({expiry_data['total_batches_count']})",
    ])

    with subtab_exp:
        expired_list = expiry_data["expired_batches"]
        if not expired_list:
            st.success("No expired batches in stock. All inventory is safe and non-expired.")
        else:
            exp_table = []
            for b in expired_list:
                exp_table.append({
                    "Batch ID": b["batch_id"],
                    "Medicine Name": b["medicine_name"],
                    "Category": b["category"],
                    "Batch Number": b["batch_no"],
                    "Expiry Date": b["expiry_date"],
                    "Days Expired": f"{abs(b['days_remaining'])}d ago",
                    "Quantity": f"{b['quantity']} units",
                    "Purchase Price": f"₹{b['purchase_price']:.2f}",
                    "Loss Value": f"₹{b['total_value']:.2f}",
                })
            st.dataframe(pd.DataFrame(exp_table), use_container_width=True, hide_index=True)

            exp_choices = {f"Batch {b['batch_no']} ({b['medicine_name']}) - Qty: {b['quantity']}": b for b in expired_list if b["quantity"] > 0}
            if exp_choices:
                sel_exp_label = st.selectbox("Select expired batch to dispose:", options=list(exp_choices.keys()), key="exp_discard_select")
                sel_exp_batch = exp_choices[sel_exp_label]
                if st.button("Quarantine & Discard Batch", icon=":material/delete_forever:", type="primary", key="discard_btn"):
                    discard_batch_dialog(current_user, sel_exp_batch)

    with subtab_near:
        near_list = expiry_data["expiring_soon_batches"]
        if not near_list:
            st.info(f"No batches expiring within {window_days} days.")
        else:
            near_table = []
            for b in near_list:
                near_table.append({
                    "Batch ID": b["batch_id"],
                    "Medicine Name": b["medicine_name"],
                    "Category": b["category"],
                    "Batch Number": b["batch_no"],
                    "Expiry Date": b["expiry_date"],
                    "Days Remaining": f"{b['days_remaining']} days",
                    "Available Qty": f"{b['quantity']} units",
                    "Purchase Cost": f"₹{b['purchase_price']:.2f}",
                    "Stock Value": f"₹{b['total_value']:.2f}",
                    "Urgency": b["urgency"],
                })
            st.dataframe(pd.DataFrame(near_table), use_container_width=True, hide_index=True)

    with subtab_all:
        csv_data = InventoryService.export_expiry_report_csv(warning_days=window_days)
        st.download_button(
            label="Download Expiry Report (CSV)",
            data=csv_data,
            file_name=f"pharmacare_expiry_audit_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            icon=":material/download:",
            type="primary",
            key="exp_csv_dl_btn",
        )
        all_table = []
        for b in expiry_data["all_batches"]:
            all_table.append({
                "Medicine": b["medicine_name"],
                "Batch No": b["batch_no"],
                "Category": b["category"],
                "Expiry Date": b["expiry_date"],
                "Days Left": f"{b['days_remaining']}d" if b['days_remaining'] >= 0 else f"EXPIRED ({abs(b['days_remaining'])}d ago)",
                "Quantity": f"{b['quantity']} units",
                "Stock Value": f"₹{b['total_value']:.2f}",
                "Status": b["status"].replace("_", " ").title(),
            })
        st.dataframe(pd.DataFrame(all_table), use_container_width=True, hide_index=True)


# ==============================================================================
# TAB 3: LOW STOCK & REORDER MONITOR
# ==============================================================================
with tab_low_stock:
    st.markdown("### Low Stock & Replenishment Reorder Queue")
    st.caption("Identify items below safety threshold (min_stock) and compute reorder quantities")

    low_stock_data = InventoryService.get_low_stock_overview()

    lk1, lk2, lk3, lk4 = st.columns(4)
    with lk1:
        render_metric_card("Out of Stock", str(low_stock_data["out_of_stock_count"]), "Immediate stockout", accent="red" if low_stock_data["out_of_stock_count"] > 0 else "teal")
    with lk2:
        render_metric_card("Below Safety Level", str(low_stock_data["below_threshold_count"]), "Below min threshold", accent="amber" if low_stock_data["below_threshold_count"] > 0 else "teal")
    with lk3:
        render_metric_card("Suggested Reorder", f"{low_stock_data['total_suggested_reorder_units']:,} units", "Recommended replenishment", accent="blue")
    with lk4:
        render_metric_card("Est. Reorder Cost", f"₹{low_stock_data['total_estimated_reorder_cost']:,.2f}", "Wholesale cost", accent="green")

    st.markdown("---")

    subtab_queue, subtab_thresh = st.tabs([
        f"Reorder Queue ({low_stock_data['total_low_stock_items']})",
        "Adjust Safety Stock Thresholds",
    ])

    with subtab_queue:
        if low_stock_data["total_low_stock_items"] > 0:
            reorder_csv = InventoryService.export_low_stock_csv()
            st.download_button(
                label="Download Reorder Sheet (CSV)",
                data=reorder_csv,
                file_name=f"pharmacare_reorder_list_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                icon=":material/download:",
                type="primary",
                key="low_csv_dl_btn",
            )

        items = low_stock_data["items"]
        if not items:
            st.success("All medicines are well above minimum safety stock thresholds!")
        else:
            table_rows = []
            for it in items:
                status_tag = "Out of Stock" if it["current_stock"] == 0 else "Low Stock"
                table_rows.append({
                    "Medicine Name": it["medicine_name"],
                    "Category": it["category"],
                    "Dosage Form": it["dosage_form"],
                    "Current Stock": f"{it['current_stock']} units",
                    "Min Stock Threshold": f"{it['min_stock']} units",
                    "Deficit": f"{it['deficit']} units",
                    "Suggested Reorder": f"{it['suggested_reorder_qty']} units",
                    "Est. Unit Cost": f"₹{it['est_unit_cost']:.2f}",
                    "Est. Total Cost": f"₹{it['est_total_cost']:.2f}",
                    "Urgency": status_tag,
                })
            st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    with subtab_thresh:
        if medicines_all:
            med_thresh_map = {f"{m['name']} ({m['strength']}) - Current Min: {m['min_stock']}": m for m in medicines_all}
            sel_thresh_label = st.selectbox("Select medicine to adjust threshold:", options=list(med_thresh_map.keys()), key="thresh_med_select")
            sel_thresh_med = med_thresh_map[sel_thresh_label]

            with st.form("update_min_stock_form_tab"):
                st.write(f"Adjust safety buffer for **{sel_thresh_med['name']}**:")
                new_min = st.number_input("Minimum Stock Threshold (Units) *", min_value=0, max_value=1000, value=int(sel_thresh_med["min_stock"]), step=5)
                if st.form_submit_button("Update Threshold", type="primary", use_container_width=True):
                    try:
                        InventoryService.update_medicine_min_stock(current_user=current_user, medicine_id=sel_thresh_med["id"], new_min_stock=int(new_min))
                        st.toast("Minimum stock threshold updated!", icon="✅")
                        st.rerun()
                    except AppException as e:
                        st.error(e.message)


# ==============================================================================
# TAB 4: IMPORT CSV INVENTORY (PREVIEW, VALIDATION & CONFIRMATION STEP)
# ==============================================================================
with tab_import:
    st.markdown("### CSV Inventory Bulk Import")
    st.caption("Upload a structured CSV file to import medicines, categories, and initial batch stock with duplicate detection and preview validation.")

    # Template Download Box
    sample_csv_content = (
        "name,generic_name,category,dosage_form,strength,selling_price,min_stock,batch_no,expiry_date,quantity,purchase_price,barcode,prescription_required\n"
        "Amoxicillin 500mg,Amoxicillin,Antibiotics,Capsule,500mg,45.0,15,AMX-2026-B1,2027-06-30,100,28.0,890100100200,True\n"
        "Metformin 500mg,Metformin Hydrochloride,Antidiabetic,Tablet,500mg,18.0,20,MET-2026-B1,2027-12-31,200,10.5,890100100201,False\n"
        "Pantoprazole 40mg,Pantoprazole Sodium,Gastrointestinal,Tablet,40mg,60.0,10,PAN-2026-B1,2027-08-15,150,38.0,890100100202,False\n"
    )

    col_template, col_upload = st.columns([1.2, 2.5])
    with col_template:
        with st.container(border=True):
            st.markdown("##### 📄 Standard CSV Template")
            st.caption("Download template format with expected header columns.")
            st.download_button(
                label="Download Sample CSV Template",
                data=sample_csv_content,
                file_name="pharmacare_inventory_template.csv",
                mime="text/csv",
                icon=":material/download:",
                use_container_width=True,
            )

    with col_upload:
        uploaded_csv = st.file_uploader("Upload Inventory CSV File", type=["csv"], help="Select a CSV file containing inventory rows.")

    if uploaded_csv:
        try:
            df_preview = pd.read_csv(uploaded_csv)
            st.markdown("---")
            st.markdown("#### 1. CSV Data Preview & Pre-Validation")

            # Check required columns
            required_cols = ["name", "category", "dosage_form", "strength"]
            missing_cols = [c for c in required_cols if c not in df_preview.columns]

            if missing_cols:
                st.error(f"Missing required header columns in CSV: `{', '.join(missing_cols)}`")
            else:
                # Pre-scan existing database records for duplicate detection
                existing_meds = MedicineService.list_medicines()
                existing_med_keys = {f"{m['name'].strip().lower()}_{m['strength'].strip().lower()}" for m in existing_meds}

                parsed_rows = []
                valid_count = 0
                duplicate_count = 0

                for idx, row in df_preview.iterrows():
                    med_name = str(row.get("name") or "").strip()
                    strength = str(row.get("strength") or "500mg").strip()
                    key = f"{med_name.lower()}_{strength.lower()}"

                    is_duplicate = key in existing_med_keys
                    if is_duplicate:
                        duplicate_count += 1
                        status_str = "Existing Medicine (Stock Incremented)"
                    else:
                        status_str = "New Medicine"

                    if med_name:
                        valid_count += 1
                        parsed_rows.append({
                            "name": med_name,
                            "generic_name": str(row.get("generic_name") or med_name).strip(),
                            "category": str(row.get("category") or "General").strip(),
                            "dosage_form": str(row.get("dosage_form") or "Tablet").strip(),
                            "strength": strength,
                            "selling_price": float(row.get("selling_price") or 0.0),
                            "min_stock": int(row.get("min_stock") or 15),
                            "batch_no": str(row.get("batch_no") or "").strip().upper(),
                            "expiry_date": str(row.get("expiry_date") or date.today() + timedelta(days=365)),
                            "quantity": int(row.get("quantity") or 0),
                            "purchase_price": float(row.get("purchase_price") or 0.0),
                            "barcode": str(row.get("barcode") or "").strip(),
                            "prescription_required": bool(str(row.get("prescription_required")).lower() in ["true", "1", "yes"]),
                            "import_status": status_str,
                        })

                # Show Summary KPI Cards
                ic1, ic2, ic3 = st.columns(3)
                with ic1:
                    render_metric_card("Total Parsed Rows", str(len(df_preview)), "Rows in CSV file", accent="teal")
                with ic2:
                    render_metric_card("Valid Import Items", str(valid_count), "Ready for database insert", accent="green")
                with ic3:
                    render_metric_card("Duplicate Matches", str(duplicate_count), "Will update existing stock", accent="amber" if duplicate_count > 0 else "blue")

                st.markdown("##### Parsed Records Verification Table:")
                df_parsed_display = pd.DataFrame(parsed_rows)
                st.dataframe(df_parsed_display, use_container_width=True, hide_index=True)

                st.markdown("---")
                st.markdown("#### 2. Confirm & Save to Database")

                if st.button("Confirm & Import Valid Records into Database", type="primary", use_container_width=True, icon=":material/check_circle:"):
                    try:
                        res = MedicineService.import_csv_inventory(current_user, parsed_rows)
                        st.success(
                            f"CSV Import Successful! "
                            f"Added **{res['imported_medicines']}** new medicines, "
                            f"**{res['imported_batches']}** new batches, and updated **{res['updated_batches']}** existing batches."
                        )
                        st.toast("Inventory CSV imported successfully!", icon="🎉")
                    except Exception as e:
                        st.error(f"Import failed: {str(e)}")

        except Exception as e:
            st.error(f"Failed to read CSV file: {str(e)}")


# ==============================================================================
# TAB 5: CATEGORIES MANAGEMENT
# ==============================================================================
with tab_categories:
    st.markdown("### Therapeutic Category Management")
    st.caption("Organize products by medical classifications")

    c_c_btn, _ = st.columns([2, 4])
    with c_c_btn:
        if st.button("Add New Category", icon=":material/add:", type="primary", use_container_width=True, key="tab_add_cat_btn"):
            add_category_dialog(current_user)

    categories_list = CategoryService.list_categories()
    if not categories_list:
        render_empty_state("No Categories", "No categories defined yet.")
    else:
        c_df = pd.DataFrame([
            {
                "Category ID": c["id"],
                "Category Name": c["name"],
                "Description": c["description"],
                "Linked Medicines": f"{c['medicine_count']} products",
                "Created Date": c["created_at"],
            }
            for c in categories_list
        ])
        st.dataframe(c_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        cat_choices = {f"{c['name']} ({c['medicine_count']} items)": c for c in categories_list}
        selected_cat_label = st.selectbox("Select category to edit or delete:", options=list(cat_choices.keys()), key="cat_action_select_tab")
        sel_cat_obj = cat_choices[selected_cat_label]

        ca1, ca2, _ = st.columns([1.5, 1.5, 3])
        with ca1:
            if st.button("Edit Category", icon=":material/edit:", key="edit_cat_btn_tab"):
                edit_category_dialog(current_user, sel_cat_obj)
        with ca2:
            if st.button("Delete Category", icon=":material/delete:", type="secondary", key="del_cat_btn_tab"):
                delete_category_dialog(current_user, sel_cat_obj)


# ==============================================================================
# MODAL DIALOGS
# ==============================================================================

@st.dialog("Add New Medicine")
def add_medicine_dialog(curr_user):
    cats = CategoryService.list_categories()
    if not cats:
        st.error("Please create at least one Category before adding medicines.")
        return
    cat_map = {c["name"]: c["id"] for c in cats}

    with st.form("add_med_form_dlg"):
        name = st.text_input("Medicine Brand Name *", placeholder="e.g. Paracetamol 500mg")
        generic = st.text_input("Generic Chemical Name *", placeholder="e.g. Acetaminophen")
        c1, c2 = st.columns(2)
        with c1:
            cat_name = st.selectbox("Therapeutic Category *", options=list(cat_map.keys()))
            dosage = st.selectbox("Dosage Form *", options=["Tablet", "Capsule", "Syrup", "Injection", "Ointment", "Drops", "Inhaler"])
            selling_p = st.number_input("Selling Price (₹) *", min_value=0.0, value=25.0, step=1.0)
        with c2:
            strength = st.text_input("Strength *", placeholder="e.g. 500mg, 10mg/ml")
            min_stk = st.number_input("Min Reorder Stock *", min_value=0, value=15, step=5)
            barcode = st.text_input("Barcode (optional)", placeholder="e.g. 890103000101")

        mfr = st.text_input("Manufacturer", placeholder="e.g. Abbott Healthcare")
        brand = st.text_input("Brand", placeholder="e.g. Calpol")
        rx_req = st.checkbox("Requires Doctor Prescription (Schedule H / X)")

        if st.form_submit_button("Save Medicine", type="primary", use_container_width=True):
            try:
                MedicineService.create_medicine(
                    current_user=curr_user,
                    data={
                        "name": name,
                        "generic_name": generic,
                        "category_id": cat_map[cat_name],
                        "dosage_form": dosage,
                        "strength": strength,
                        "selling_price": selling_p,
                        "min_stock": min_stk,
                        "barcode": barcode,
                        "manufacturer": mfr,
                        "brand": brand,
                        "prescription_required": rx_req,
                    },
                )
                st.toast(f"Medicine '{name}' created!", icon="✅")
                st.rerun()
            except AppException as e:
                st.error(e.message)


@st.dialog("Edit Medicine")
def edit_medicine_dialog(curr_user, med_data):
    cats = CategoryService.list_categories()
    cat_map = {c["name"]: c["id"] for c in cats}
    cat_names = list(cat_map.keys())

    curr_cat_idx = 0
    for idx, cname in enumerate(cat_names):
        if cat_map[cname] == med_data["category_id"]:
            curr_cat_idx = idx
            break

    dosage_forms = ["Tablet", "Capsule", "Syrup", "Injection", "Ointment", "Drops", "Inhaler"]
    dosage_idx = dosage_forms.index(med_data["dosage_form"]) if med_data["dosage_form"] in dosage_forms else 0

    with st.form("edit_med_form_dlg"):
        name = st.text_input("Medicine Name *", value=med_data["name"])
        generic = st.text_input("Generic Chemical Name *", value=med_data["generic_name"])
        c1, c2 = st.columns(2)
        with c1:
            cat_name = st.selectbox("Category *", options=cat_names, index=curr_cat_idx)
            dosage = st.selectbox("Dosage Form *", options=dosage_forms, index=dosage_idx)
            selling_p = st.number_input("Selling Price (₹) *", min_value=0.0, value=float(med_data["selling_price"]), step=1.0)
        with c2:
            strength = st.text_input("Strength *", value=med_data["strength"])
            min_stk = st.number_input("Min Reorder Stock *", min_value=0, value=int(med_data["min_stock"]), step=5)
            barcode = st.text_input("Barcode", value=med_data["barcode"] or "")

        mfr = st.text_input("Manufacturer", value=med_data["manufacturer"] or "")
        brand = st.text_input("Brand", value=med_data["brand"] or "")
        status = st.selectbox("Status", options=["active", "inactive"], index=0 if med_data["status"] == "active" else 1)
        rx_req = st.checkbox("Requires Doctor Prescription (Schedule H)", value=bool(med_data["prescription_required"]))

        if st.form_submit_button("Update Medicine", type="primary", use_container_width=True):
            try:
                MedicineService.update_medicine(
                    current_user=curr_user,
                    medicine_id=med_data["id"],
                    data={
                        "name": name,
                        "generic_name": generic,
                        "category_id": cat_map[cat_name],
                        "dosage_form": dosage,
                        "strength": strength,
                        "selling_price": selling_p,
                        "min_stock": min_stk,
                        "barcode": barcode,
                        "manufacturer": mfr,
                        "brand": brand,
                        "prescription_required": rx_req,
                        "status": status,
                    },
                )
                st.toast("Medicine updated!", icon="✅")
                st.rerun()
            except AppException as e:
                st.error(e.message)


@st.dialog("Delete / Deactivate Medicine")
def delete_medicine_dialog(curr_user, med_data):
    st.warning(f"Deactivate or remove **{med_data['name']}**?")
    if st.button("Confirm Removal", type="primary", use_container_width=True):
        try:
            MedicineService.delete_medicine(curr_user, med_data["id"])
            st.toast(f"Medicine '{med_data['name']}' processed.", icon="✅")
            st.rerun()
        except AppException as e:
            st.error(e.message)


@st.dialog("Add Category")
def add_category_dialog(curr_user):
    with st.form("add_cat_form_dlg"):
        name = st.text_input("Category Name *", placeholder="e.g. Antibiotics, Painkillers")
        desc = st.text_area("Description", placeholder="Medical classification details...")
        if st.form_submit_button("Save Category", type="primary", use_container_width=True):
            try:
                CategoryService.create_category(curr_user, name, desc)
                st.toast("Category created!", icon="✅")
                st.rerun()
            except AppException as e:
                st.error(e.message)


@st.dialog("Edit Category")
def edit_category_dialog(curr_user, cat_obj):
    with st.form("edit_cat_form_dlg"):
        name = st.text_input("Category Name *", value=cat_obj["name"])
        desc = st.text_area("Description", value=cat_obj["description"])
        if st.form_submit_button("Update Category", type="primary", use_container_width=True):
            try:
                CategoryService.update_category(curr_user, cat_obj["id"], name, desc)
                st.toast("Category updated!", icon="✅")
                st.rerun()
            except AppException as e:
                st.error(e.message)


@st.dialog("Delete Category")
def delete_category_dialog(curr_user, cat_obj):
    st.write(f"Delete category **{cat_obj['name']}**?")
    if st.button("Confirm Delete", type="primary", use_container_width=True):
        try:
            CategoryService.delete_category(curr_user, cat_obj["id"])
            st.toast("Category deleted!", icon="✅")
            st.rerun()
        except Exception as e:
            st.error(str(e))


@st.dialog("Add Physical Batch")
def add_batch_dialog(curr_user, preselect_med_id: Optional[int] = None):
    meds = MedicineService.list_medicines()
    if not meds:
        st.error("Please add medicines first.")
        return

    med_map = {f"{m['name']} ({m['strength']})": m["id"] for m in meds}
    default_idx = 0
    if preselect_med_id:
        for idx, (label, mid) in enumerate(med_map.items()):
            if mid == preselect_med_id:
                default_idx = idx
                break

    with st.form("add_batch_form_dlg"):
        med_label = st.selectbox("Medicine *", options=list(med_map.keys()), index=default_idx)
        batch_no = st.text_input("Batch Number *", placeholder="e.g. BATCH-2026-01").upper()
        c1, c2 = st.columns(2)
        with c1:
            expiry_d = st.date_input("Expiry Date *", value=date.today() + timedelta(days=365))
            qty = st.number_input("Quantity *", min_value=1, value=50, step=10)
        with c2:
            p_price = st.number_input("Purchase Price Per Unit (₹) *", min_value=0.0, value=15.0, step=1.0)

        if st.form_submit_button("Save Batch to Inventory", type="primary", use_container_width=True):
            try:
                BatchService.create_batch(
                    current_user=curr_user,
                    medicine_id=med_map[med_label],
                    batch_no=batch_no,
                    expiry_date_val=expiry_d,
                    quantity=int(qty),
                    purchase_price=float(p_price),
                )
                st.toast(f"Batch '{batch_no}' created!", icon="✅")
                st.rerun()
            except AppException as e:
                st.error(e.message)


@st.dialog("Record Batch Disposal / Quarantine")
def discard_batch_dialog(curr_user, batch_obj):
    st.write(f"Dispose Expired Stock for **{batch_obj['medicine_name']}** (Batch: {batch_obj['batch_no']})")
    with st.form("discard_batch_form_dlg"):
        reason = st.selectbox(
            "Disposal Protocol Reason *",
            options=[
                "Standard statutory quarantine and incinerate",
                "Manufacturer return / credit note claim",
                "Quarantined in hazardous waste storage",
                "State drug inspector witnessed disposal",
            ],
        )
        inspector_notes = st.text_input("Notes", placeholder="e.g. Cleared under disposal protocol #D-2026")
        if st.form_submit_button("Confirm Discard & Zero Stock", type="primary", use_container_width=True):
            try:
                full_reason = f"{reason} - {inspector_notes}" if inspector_notes else reason
                res = InventoryService.quarantine_and_discard_batch(
                    current_user=curr_user,
                    batch_id=batch_obj["batch_id"],
                    reason=full_reason,
                )
                st.toast(f"Disposed batch ({res['discarded_quantity']} units zeroed).", icon="✅")
                st.rerun()
            except AppException as e:
                st.error(e.message)
