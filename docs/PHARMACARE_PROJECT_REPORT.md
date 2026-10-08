# A PROJECT REPORT ON

# **PHARMACARE**
### **Smart Pharmacy Management & Inventory Monitoring System**
#### **A Web-Based Pharmacy Inventory, POS & Stock Expiry Management Solution**

---

### **Submitted For: B.E. / B.Tech Project Evaluation**
**Subject:** Software Engineering / Database Management / Web Development  
**Academic Year:** 2026–27  

| Parameter | Details |
| :--- | :--- |
| **Submitted By** | [Your Name] |
| **Enrollment Number** | [Your Enrollment Number] |
| **Programme** | B.E. / B.Tech (Computer Engineering / Information Technology / AI & ML) |
| **Semester / Academic Year** | Semester 5 / 2026–27 |
| **College / Institution** | L. D. College of Engineering, Ahmedabad |
| **Department** | Department of Computer Engineering / IT |

---

## **TABLE OF CONTENTS**

| Sr. No. | Chapter / Section | Page No. |
| :---: | :--- | :---: |
| **1** | Introduction | 3 |
| **2** | Problem Statement | 4 |
| **3** | Objectives | 4 |
| **4** | Existing System and Proposed System | 5 |
| **5** | Functional Requirements | 6 |
| **6** | Technology Stack | 7 |
| **7** | System Architecture | 8 |
| **8** | Project Workflow | 9 |
| **9** | Database Design & Entity Schemas | 10 |
| **10** | Backend & Domain Service Implementation | 12 |
| **11** | Frontend Implementation & UI Walkthrough | 14 |
| **12** | Results and Verification | 18 |
| **13** | Advantages and Limitations | 19 |
| **14** | Future Enhancements | 20 |
| **15** | Conclusion and References | 21 |
| **16** | Source Code Appendix | 22 |

---

## **1. INTRODUCTION**

### **1.1 Introduction**
Modern retail pharmacies and dispensary centers handle hundreds of transactions, stock arrivals, prescription validations, and batch expirations daily. Managing medicine inventory, tracking stock batch expiration dates manually, calculating GST taxes, issuing compliant billing receipts, and ensuring Schedule H/X statutory compliance without a centralized digital software system can lead to severe stockouts, financial leakage, and regulatory non-compliance.

Traditional pharmacy workflows rely on paper ledgers, fragmented desktop spreadsheets, or legacy point-of-sale systems that lack real-time stock allocation algorithms (such as FEFO – First-Expiry, First-Out) or automated quarantine management for near-expiry drugs.

To solve these operational challenges, **PharmaCare** was developed as a comprehensive, web-based **Smart Pharmacy Management & Inventory Monitoring System**. PharmaCare provides an end-to-end clinical SaaS platform tailored for retail pharmacies, hospital dispensaries, and wholesale pharmaceutical distributors.

The system provides segregated role-based access control (RBAC) and clinical workflows for:
- **Dispensary Administrators**: Complete system governance, staff RBAC management, pharmacy configuration, hot database snapshot backups, and immutable audit logging.
- **Pharmacists & Dispensary Operators**: Real-time FEFO counter billing, stock receiving, CSV bulk inventory imports, prescription verification, stock quarantine, and financial analytics.

---

### **1.2 Purpose of the System**
The primary purpose of **PharmaCare** is to provide a unified, digital platform that connects inventory management, counter POS billing, wholesale procurement, customer CRM, and statutory compliance into a streamlined operational workflow.

The system aims to eliminate:
- Manual stock ledger bookkeeping and paper-based receipt tracking.
- Stock wastage caused by dispensing newer batches while older batches expire (enforcing strict FEFO).
- Dispensing errors related to Schedule H / Schedule X prescription-only medicines.
- Inventory discrepancies through live CSV bulk import with duplicate detection.
- Financial exposure caused by unmonitored expired medicines sitting in sellable stock.

---

## **2. PROBLEM STATEMENT**

Traditional manual or legacy pharmacy inventory systems suffer from significant operational bottlenecks. The major problems identified in existing pharmacy workflows include:

1. **High Risk of Stock Expiry Losses**: In manual systems, stock batches are stored without automated expiry tracking, leading to expired medicines remaining on shelves and resulting in direct financial loss.
2. **Lack of FEFO (First-Expiry, First-Out) Enforcement**: Pharmacists frequently dispense newly arrived stock while older active batches expire unnoticed.
3. **Complex & Slow Point-of-Sale Billing**: Manual invoice calculation, manual GST application, and lack of real-time stock deduction slow down counter transactions during peak hours.
4. **Statutory Non-Compliance**: Prescribing and dispensing Schedule H / Schedule X drugs without verifying doctor Medical Council registration numbers creates legal non-compliance risks.
5. **Tedious Bulk Stock Entry**: Adding wholesale procurement shipments line-by-line is labor-intensive and prone to typographical errors.
6. **Lack of Audit Trails & Governance**: Traditional ledger systems provide no tamper-evident record of stock adjustments, user authentications, or database modifications.

Therefore, there is an urgent need for a modern, web-based software system that provides real-time stock tracking, automated FEFO allocation, instant POS billing with PDF invoicing, CSV bulk inventory importing, and statutory compliance tracking under a single unified platform.

---

## **3. OBJECTIVES**

The key objectives of the **PharmaCare** project are:

1. To develop a web-based, clinical SaaS pharmacy management system using Python, Streamlit, SQLAlchemy 2.x, and SQLite.
2. To implement a **First-Expiry, First-Out (FEFO)** algorithm for automatic batch selection during billing.
3. To provide an intuitive, high-speed **Counter POS Billing** module with automatic tax calculation and instant ReportLab PDF invoice generation.
4. To enable **CSV Bulk Inventory Import** with real-time preview, data validation, duplicate detection, and stock merge capabilities.
5. To support **Batch-Level Expiry Monitoring**, enabling one-click stock quarantine/disposal with automated audit trail logging.
6. To enforce **Schedule H / Schedule X Statutory Compliance** by requiring valid doctor Medical Council registration numbers before checkout.
7. To provide a comprehensive **Wholesale Procurement & Stock Inward** module linked to supplier directories.
8. To incorporate **Role-Based Access Control (RBAC)** separating Administrator and Pharmacist privileges.
9. To offer **Real-Time Executive Analytics**, including Plotly sales trend charts, profitability margins, live stock valuation, and expiry loss exposure audits.
10. To feature a **Hot Database Snapshot Backup & Restore** engine for seamless data protection.
11. To maintain an **Immutable Security Audit Trail** capturing all user activities, logins, and inventory mutations.
12. To deliver a **Professional Vanilla White UI Design System** with crisp typography, restrained accents, and optimal laptop/desktop responsiveness.

---

## **4. EXISTING SYSTEM AND PROPOSED SYSTEM**

### **4.1 Existing System**
In traditional pharmacy operations:
- Inventory registers are maintained manually in physical logs or standalone spreadsheets.
- Batch numbers, expiry dates, and purchase costs are entered manually during billing.
- Expiry checking requires manual physical auditing of shelf stock.
- Statutory prescription records are stored in paper registers, making search difficult.
- Invoices are hand-written or printed using generic impact printers without automated record locking.

### **4.2 Proposed System (PharmaCare)**
PharmaCare replaces fragmented paper workflows with an integrated web application. The proposed system provides:
- Automated database-backed inventory tracking with multi-batch support per medicine catalog item.
- Automatic FEFO stock allocation during billing to minimize expiry losses.
- One-click CSV bulk inventory import with preview verification and duplicate stock incrementing.
- Automated expiry warning triggers (30-day window) and one-click stock quarantine.
- Digital prescription registry linked to patient records and statutory sales invoices.
- Hot binary database backup export and instant restore.
- Real-time Plotly executive analytics and PDF exportable financial statements.

### **Comparison Matrix**

| Feature | Existing Manual / Spreadsheet System | Proposed PharmaCare System |
| :--- | :--- | :--- |
| **Inventory Tracking** | Manual register / Excel sheet | Centralized database (SQLAlchemy 2.x + SQLite) |
| **Stock Allocation** | Arbitrary / LIFO (Loss-prone) | Automated FEFO (First-Expiry, First-Out) |
| **Billing & POS** | Hand-written or generic receipt | POS counter billing with ReportLab PDF invoices |
| **Bulk Stock Import** | Line-by-line manual entry | CSV Bulk Import with preview & duplicate detection |
| **Expiry Management** | Manual shelf inspection | Automated alerts + 1-click Quarantine & Audit Trail |
| **Statutory Compliance** | Paper prescription checks | Digital Rx registry + Doctor MCI Reg No validation |
| **Wholesale Purchases** | Separate paper vouchers | Integrated Stock Inward entry with vendor profiling |
| **Database Backup** | Manual file copies (Risky) | 1-Click Binary Snapshot Export & Hot Restore |
| **Audit & Governance** | No audit logging | Tamper-evident Audit Trail capturing all operations |
| **UI Aesthetics** | Legacy desktop forms | Modern Clinical Vanilla White SaaS Interface |

---

## **5. FUNCTIONAL REQUIREMENTS**

The functional requirements of **PharmaCare** are organized into 11 core operational modules:

### **5.1 User Authentication & Role-Based Access Control (RBAC)**
- Secure password hashing using `bcrypt` and `passlib`.
- Session state management preventing unauthorized page access.
- Role enforcement:
  - **Admin**: Full access to System Admin, Pharmacy Settings, User Accounts, Database Backup, and Audit Logs.
  - **Pharmacist**: Access to Dashboard, Billing/POS, Inventory, Procurement, and Prescriptions.

### **5.2 Medicine Catalog & Therapeutic Categories**
- Category CRUD operations with conflict safeguards.
- Medicine catalog management: Brand name, Generic name, Strength, Dosage Form (Tablet, Capsule, Syrup, Injection, etc.), Reorder Level (`min_stock`), Retail MRP (`selling_price`), and Prescription requirement flag (`prescription_required`).

### **5.3 Batch-Level Inventory & FEFO Stock Allocation**
- Multi-batch registration per medicine (`batch_no`, `expiry_date`, `quantity`, `purchase_price`, `rack_location`).
- Automated FEFO sorting: Billing automatically deducts items from the earliest-expiring non-expired active batch.

### **5.4 Point-of-Sale (POS) Counter Billing**
- Instant medicine search by name, generic composition, or barcode.
- Real-time stock availability and unit cost computation.
- Discount percentage/amount application and GST tax computation.
- One-click checkout with automated stock deduction, customer spend updating, and instant ReportLab PDF invoice compilation.

### **5.5 Schedule H / Rx Statutory Compliance**
- Mandatory prescription verification prompt when billing `prescription_required=True` drugs.
- Option to select registered patient prescription or log prescribing doctor details (Doctor Name, Medical Council Registration Number).

### **5.6 Wholesale Procurement & Stock Inward**
- Multi-item inward invoice entry from registered wholesale suppliers.
- Automatic creation/updating of medicine catalog items and physical batches.
- Supplier procurement profiling and invoice cancellation safeguards.

### **5.7 Expiry Monitoring, Quarantine & Disposal Audit**
- Automated categorization: Active, Approaching Expiry (<30 Days), and Expired stock.
- One-click quarantine transfer and disposal execution with mandatory audit reason logging.

### **5.8 CSV Bulk Inventory Import**
- Template download functionality (`pharmacare_inventory_template.csv`).
- Drag-and-drop CSV file uploader.
- Interactive preview table with duplicate detection.
- Validation summary (Valid rows vs Duplicate stock updates).
- One-click batch transaction import into the SQLite database.

### **5.9 Customer CRM & Prescription Registry**
- Customer contact records, address management, and total expenditure tracking.
- Prescription registry logging clinical diagnosis, dosage regimen, prescribing doctor info, and linked billing invoices.

### **5.10 System Administration & Hot Database Snapshot Backup**
- Configurable pharmacy metadata (Dispensary Name, Address, Drug License No., GSTIN, default tax rate, invoice footer terms).
- One-click SQLite binary snapshot export (`.db`) and hot database restore with safety confirmation checkboxes.

### **5.11 Notification Center & Security Audit Trail**
- Real-time notification queue for low-stock and expiry warnings.
- Broadcast system notice capability for admins.
- Immutable audit log capturing timestamp, user ID, module, action, description, and IP address.

---

## **6. TECHNOLOGY STACK**

| Layer / Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Programming Language** | Python 3.11+ | Primary application language |
| **Frontend UI Framework** | Streamlit 1.37+ | Web interface and interactive layout engine |
| **Design System & Styling** | Vanilla CSS3 | Custom Vanilla White design tokens & CSS injection |
| **Database ORM** | SQLAlchemy 2.x | Object-Relational Mapping & transaction management |
| **Database Engine** | SQLite 3 | Embedded, lightweight relational database engine |
| **Security & Auth** | Passlib & Bcrypt | Password hashing and credential verification |
| **Data Processing** | Pandas 2.2+ | Data manipulation, tabular formatting, CSV processing |
| **Data Visualization** | Plotly 5.18+ | Interactive dual-axis executive sales trend charts |
| **Document Generation** | ReportLab 4.0+ | Dynamic compiled PDF sales receipt & invoice generation |
| **Version Control** | Git & GitHub | Code repository management and cloud deployment |

---

## **7. SYSTEM ARCHITECTURE**

PharmaCare follows a decoupled, three-tier web application architecture:

```
+-------------------------------------------------------------------+
|                        CLIENT BROWSER INTERFACE                   |
|          Streamlit Web Frontend (Vanilla White Clinical UI)       |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                     APPLICATION & DOMAIN SERVICES                 |
|   +-------------------+  +-------------------+  +---------------+ |
|   |   AuthService     |  |  MedicineService  |  | SalesService  | |
|   +-------------------+  +-------------------+  +---------------+ |
|   | PurchaseService   |  |   ReportService   |  | AuditService  | |
|   +-------------------+  +-------------------+  +---------------+ |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                       DATA ACCESS LAYER (ORM)                     |
|                 SQLAlchemy 2.x SessionLocal / Models              |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                        DATABASE STORAGE LAYER                     |
|                     SQLite Relational Database                    |
|       (medicines, batches, sales, purchases, audit_logs)          |
+-------------------------------------------------------------------+
```

### **Architecture Explanation**
1. **Frontend Layer**: Streamlit web interface presenting a multi-page app architecture (`main.py`, `dashboard.py`, `billing.py`, `medicines.py`, `purchases.py`, `prescriptions.py`, `reports.py`).
2. **Domain Service Layer**: Pure Python domain services encapsulated in `app/services/` (`AuthService`, `MedicineService`, `SalesService`, `PurchaseService`, `ReportService`, `BackupService`, `AuditService`, `NotificationService`).
3. **Data Access Layer**: SQLAlchemy 2.x Declarative Base models (`app/models/`) with explicit relationships, unique constraints, and foreign key cascades.
4. **Database Storage Layer**: Persistent SQLite binary file (`data/pharmacare.db`) storing structured relational data.

---

## **8. PROJECT WORKFLOW**

The operational execution flow of PharmaCare from procurement to billing and auditing is structured as follows:

```
[Wholesale Supplier Procurement]
               │
               ▼
[Stock Inward Entry / CSV Import] ──► [Medicine & FEFO Batch Creation]
                                                 │
                                                 ▼
                                     [Active Inventory Stock]
                                                 │
                        ┌────────────────────────┴────────────────────────┐
                        ▼                                                 ▼
             [POS Counter Billing]                              [Expiry & Safety Audit]
                        │                                                 │
        ┌───────────────┴───────────────┐                       ┌─────────┴─────────┐
        ▼                               ▼                       ▼                   ▼
[FEFO Stock Deduction]      [Schedule H Rx Validation]   [30-Day Warning]   [Quarantine & Disposal]
        │                               │                       │                   │
        └───────────────┬───────────────┘                       └─────────┬─────────┘
                        ▼                                                 ▼
          [PDF Invoice Compilation]                         [Security Audit Logging]
```

### **Step-by-Step Execution Sequence**
1. **Authentication**: User logs in with username and password. `AuthService` verifies credentials against `bcrypt` password hashes.
2. **Stock Procurement / Import**: Pharmacist receives stock via Stock Inward entry or uploads a CSV file containing catalog items and batch details.
3. **Inventory Update**: `MedicineService` creates or merges medicine records and registers physical batches sorted by `expiry_date`.
4. **Counter POS Checkout**: Pharmacist searches medicines during a sale. `SalesService` validates active stock, selects the earliest expiring non-expired batch (FEFO), verifies Schedule H prescription registration if required, computes tax/discounts, and records the sale.
5. **Invoice Generation**: `ReportService` automatically compiles a printable PDF invoice using ReportLab.
6. **Audit Trail Logging**: Every database mutation automatically triggers `AuditService.log_action()`, recording an immutable log entry.

---

## **9. DATABASE DESIGN & ENTITY SCHEMAS**

PharmaCare contains 14 relational database tables defined using SQLAlchemy 2.x Mapped Column declarations:

```
+-------------------+       +-----------------------+       +-------------------+
|    categories     | 1   * |       medicines       | 1   * |  medicine_batches |
|-------------------|-------|-----------------------|-------|-------------------|
| id (PK)           |       | category_id (FK)      |       | id (PK)           |
| name              |       | name                  |       | medicine_id (FK)  |
| description       |       | generic_name          |       | batch_no          |
+-------------------+       | selling_price         |       | expiry_date       |
                            | min_stock             |       | quantity          |
                            | prescription_required |       | purchase_price    |
                            +-----------------------+       +-------------------+
                                        │
                         ┌──────────────┴──────────────┐
                         ▼                             ▼
              +-------------------+          +-------------------+
              |    sale_items     |          |  purchase_items   |
              |-------------------|          |-------------------|
              | id (PK)           |          | id (PK)           |
              | sale_id (FK)      |          | purchase_id (FK)  |
              | medicine_id (FK)  |          | medicine_id (FK)  |
              | batch_id (FK)     |          | batch_id (FK)     |
              | quantity          |          | quantity          |
              | unit_price        |          | purchase_price    |
              +-------------------+          +-------------------+
```

### **Core Entity Field Specifications**

1. **`users`**: `id`, `username`, `email`, `password_hash`, `full_name`, `role` (`admin` | `pharmacist`), `phone`, `is_active`, `created_at`.
2. **`categories`**: `id`, `name`, `description`, `created_at`.
3. **`medicines`**: `id`, `category_id`, `name`, `generic_name`, `brand`, `dosage_form`, `strength`, `selling_price`, `min_stock`, `prescription_required`, `status`, `barcode`.
4. **`medicine_batches`**: `id`, `medicine_id`, `batch_no`, `expiry_date`, `quantity`, `purchase_price`. (*Unique constraint on `(medicine_id, batch_no)`*).
5. **`suppliers`**: `id`, `name`, `contact_person`, `phone`, `email`, `address`, `gst_number`.
6. **`purchases`**: `id`, `supplier_id`, `user_id`, `invoice_no`, `purchase_date`, `total_amount`, `status` (`received` | `cancelled`), `notes`.
7. **`purchase_items`**: `id`, `purchase_id`, `medicine_id`, `batch_no`, `expiry_date`, `quantity`, `purchase_price`, `subtotal`.
8. **`customers`**: `id`, `name`, `phone`, `email`, `address`, `created_at`.
9. **`prescriptions`**: `id`, `customer_id`, `patient_name`, `patient_age`, `patient_gender`, `prescription_date`, `doctor_name`, `doctor_reg_no`, `diagnosis`, `notes`.
10. **`sales`**: `id`, `invoice_no`, `user_id`, `customer_id`, `prescription_id`, `sale_date`, `subtotal`, `discount_amount`, `tax_amount`, `total_amount`, `payment_method`, `notes`.
11. **`sale_items`**: `id`, `sale_id`, `medicine_id`, `batch_id`, `quantity`, `unit_price`, `subtotal`.
12. **`settings`**: `id`, `key`, `value`, `updated_at`.
13. **`notifications`**: `id`, `title`, `message`, `severity` (`info` | `warning` | `critical`), `is_read`, `created_at`.
14. **`audit_logs`**: `id`, `user_id`, `username`, `module`, `action`, `description`, `ip_address`, `timestamp`.

---

## **10. BACKEND & DOMAIN SERVICE IMPLEMENTATION**

The backend logic is modularized into pure Python domain services in `app/services/`:

### **10.1 FEFO Stock Checkout Logic (`SalesService.create_sale`)**
```python
# FEFO Stock Allocation Snippet
active_batches = session.scalars(
    select(MedicineBatch)
    .where(
        and_(
            MedicineBatch.medicine_id == med_id,
            MedicineBatch.quantity > 0,
            MedicineBatch.expiry_date >= date.today(),
        )
    )
    .order_by(MedicineBatch.expiry_date.asc())
).all()

needed_qty = req_item["quantity"]
for batch in active_batches:
    if needed_qty <= 0:
        break
    deduct_qty = min(batch.quantity, needed_qty)
    batch.quantity -= deduct_qty
    needed_qty -= deduct_qty
    # Record sale_item linked to specific batch_id
```

### **10.2 CSV Bulk Inventory Import (`MedicineService.import_csv_inventory`)**
```python
@staticmethod
def import_csv_inventory(current_user: Dict[str, Any], parsed_rows: List[Dict[str, Any]]) -> Dict[str, int]:
    """Parse CSV rows, create/update catalog items, and allocate batches."""
    imported_meds, imported_batches, updated_batches = 0, 0, 0
    with get_db() as session:
        for row in parsed_rows:
            # Find or create Category
            cat = session.scalar(select(Category).where(Category.name == row["category"]))
            if not cat:
                cat = Category(name=row["category"], description="CSV Auto-Imported")
                session.add(cat)
                session.flush()

            # Find or create Medicine
            med = session.scalar(
                select(Medicine).where(and_(Medicine.name == row["name"], Medicine.strength == row["strength"]))
            )
            if not med:
                med = Medicine(
                    name=row["name"], generic_name=row["generic_name"],
                    category_id=cat.id, strength=row["strength"],
                    selling_price=row["selling_price"], min_stock=row["min_stock"]
                )
                session.add(med)
                session.flush()
                imported_meds += 1

            # Find or create MedicineBatch
            batch = session.scalar(
                select(MedicineBatch).where(and_(MedicineBatch.medicine_id == med.id, MedicineBatch.batch_no == row["batch_no"]))
            )
            if batch:
                batch.quantity += row["quantity"]
                updated_batches += 1
            else:
                new_b = MedicineBatch(medicine_id=med.id, batch_no=row["batch_no"], expiry_date=row["expiry_date"], quantity=row["quantity"], purchase_price=row["purchase_price"])
                session.add(new_b)
                imported_batches += 1

        AuditService.log_action(user_id=current_user["id"], username=current_user["username"], module="INVENTORY", action="CREATE", description=f"CSV Import: {imported_meds} meds, {imported_batches} new batches")
        session.commit()
    return {"imported_medicines": imported_meds, "imported_batches": imported_batches, "updated_batches": updated_batches}
```

---

## **11. FRONTEND IMPLEMENTATION & UI WALKTHROUGH**

PharmaCare features a unified **Professional Vanilla White** clinical design system:
- Canvas background: `#FAF8F5` (Soft warm ivory)
- Sidebar background: `#F3EFEA` (Cream vanilla)
- Containers & Cards: `#FFFFFF` (Elevated crisp white with soft shadow)
- Primary text: `#1C1917` (Deep warm stone charcoal)
- Clinical accent: `#0F766E` (Rich deep teal)

### **Page Module Structure**

1. **`dashboard.py` (Executive Dashboard)**:
   - 4 Top Metrics: Today's Sales, Products in Stock, Batches Approaching Expiry, Replenishment Queue.
   - 4 Quick Shortcuts: `New Sale`, `Receive Stock`, `Find Medicine`, `View Reports`.
   - Actionable Inventory Alerts: FEFO Near-Expiry table & Low-Stock queue with direct quick-action navigation.
   - Dual-axis Plotly Sales Trend Chart (30-day bar & line data with 5 sampled horizontal x-axis tick labels) and Recent Transactions table.

2. **`billing.py` (Counter POS Billing & PDF Invoices)**:
   - Interactive cart builder with live stock validation.
   - Schedule H prescription validation modal.
   - Instant ReportLab PDF compilation and payment method tracking.

3. **`medicines.py` (Inventory Catalog & CSV Bulk Import)**:
   - 5 Main Tabs: `Medicines & Batches`, `Expiry & Quarantine`, `Low Stock & Reorders`, `Import CSV Inventory`, `Categories`.
   - CSV Uploader with interactive preview table and duplicate stock merge step.

4. **`purchases.py` (Stock Inward & Wholesale Procurement)**:
   - Multi-item inward invoice entry from wholesale vendors.
   - Supplier directory and procurement history profile inspection.

5. **`prescriptions.py` (Medical Prescriptions & Compliance)**:
   - Doctor registration number verification and Schedule H statutory linkage.

6. **`reports.py` (Executive Analytics & System Settings)**:
   - Financial Sales Statements, Itemized Profit Margins, Live Inventory Valuation, Expiry Loss Audits.
   - Patient CRM directory, Notification Alert Center, System Settings, Hot Binary Backup/Restore, and Audit Logs.

---

## **12. RESULTS AND VERIFICATION**

The PharmaCare system was fully implemented, integrated, and verified through automated test suites and real-world database scenario testing.

### **Verification Summary**
- **Unit Test Execution**: 16/16 automated test suites passed cleanly (`py -m pytest tests/test_services.py -v`).
- **Database Backup Verification**: Instant binary snapshot created and verified at `data/pharmacare.db.bak`.
- **CSV Bulk Import Test**: Validated using `scratch/test_csv_import.py`, confirming zero errors and clean audit logging.
- **Localhost Deployment**: Operational on `http://localhost:8511`.
- **Cloud Readiness**: Fully configured with `Procfile`, `Dockerfile`, and `render.yaml` for 1-click cloud deployment.

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.6.0
collected 16 items

tests/test_services.py::test_authentication_success_and_failure PASSED   [  6%]
tests/test_services.py::test_user_password_change PASSED                 [ 12%]
tests/test_services.py::test_admin_user_creation_and_status_toggle PASSED [ 18%]
tests/test_services.py::test_category_crud_and_conflict PASSED           [ 25%]
tests/test_services.py::test_medicine_catalog_and_fefo_stock PASSED      [ 31%]
tests/test_services.py::test_supplier_and_purchase_workflow PASSED       [ 37%]
tests/test_services.py::test_customer_and_prescription_management PASSED [ 43%]
tests/test_services.py::test_sales_checkout_fefo_deduction PASSED        [ 50%]
tests/test_services.py::test_sales_schedule_h_prescription_validation PASSED [ 56%]
tests/test_services.py::test_sales_insufficient_stock_rejection PASSED   [ 62%]
tests/test_services.py::test_inventory_expiry_quarantine_overview PASSED [ 68%]
tests/test_services.py::test_inventory_low_stock_detection PASSED        [ 75%]
tests/test_services.py::test_notification_sync_and_resolution PASSED     [ 81%]
tests/test_services.py::test_dashboard_kpis_and_timeline PASSED          [ 87%]
tests/test_services.py::test_report_generation_and_pdf PASSED            [ 93%]
tests/test_services.py::test_settings_and_backup_operations PASSED       [100%]

============================= 16 passed in 2.45s ==============================
```

---

## **13. ADVANTAGES AND LIMITATIONS**

### **13.1 Advantages**
1. **Automated FEFO Stock Protection**: Prevents expiry loss by prioritizing older active batches during billing.
2. **High-Speed Counter POS Billing**: Streamlines checkout with automatic tax, discount, and instant PDF invoice generation.
3. **CSV Bulk Stock Ingest**: Reduces stock entry time from hours to seconds with duplicate detection.
4. **Statutory Compliance Safeguards**: Enforces Schedule H doctor Medical Council registration number validation.
5. **Data Protection & Disaster Recovery**: Provides 1-click hot SQLite snapshot backup export and restore.
6. **Immutable Audit Governance**: Maintains a complete record of user activities and stock modifications.
7. **Modern Vanilla White Design System**: Delivers a warm, professional clinical UI readable on any screen.

### **13.2 Limitations**
1. **Embedded SQLite Database**: SQLite is optimized for local/single-server deployments; high-concurrency enterprise multi-branch setups would benefit from PostgreSQL migration.
2. **Hardware Integration**: Barcode scanner integration relies on standard keyboard-emulation input; native hardware SDK integration can be added.
3. **SMS Gateway**: Notification alerts are displayed in-app; direct SMS/WhatsApp gateway integration requires third-party API credentials.

---

## **14. FUTURE ENHANCEMENTS**

The system design allows for easy expansion in future versions:

1. **Real-Time WebSocket Notifications**: Instant push notifications for low-stock triggers across multi-terminal counters.
2. **SMS & WhatsApp Invoice Dispatch**: Automatic SMS/WhatsApp receipt sending to patients upon counter checkout.
3. **Multi-Branch Centralized Cloud Synchronization**: Migrating from SQLite to cloud PostgreSQL for real-time inventory sync across multiple pharmacy branches.
4. **Integrated Payment Gateway**: UPI QR code generation and credit card terminal integration during POS checkout.
5. **AI Demand Forecasting**: Machine learning models predicting seasonal medicine demand and automated purchase order generation.

---

## **15. CONCLUSION AND REFERENCES**

### **15.1 Conclusion**
**PharmaCare** successfully demonstrates a modern, clinical SaaS web application for pharmacy inventory management, FEFO stock allocation, POS counter billing, statutory compliance verification, and executive reporting.

The system replaces manual ledgers and outdated spreadsheets with a modular architecture built using Python, Streamlit, SQLAlchemy 2.x, and SQLite. The implementation of FEFO stock deduction, CSV bulk import, hot database snapshot backups, and immutable audit logging significantly enhances operational efficiency, reduces stock expiry financial loss, and ensures regulatory compliance.

---

### **15.2 References**
1. **Streamlit Documentation**: [https://docs.streamlit.io/](https://docs.streamlit.io/)
2. **SQLAlchemy 2.x Documentation**: [https://docs.sqlalchemy.org/](https://docs.sqlalchemy.org/)
3. **Python Documentation**: [https://docs.python.org/3/](https://docs.python.org/3/)
4. **ReportLab PDF Library**: [https://www.reportlab.com/documentation/](https://www.reportlab.com/documentation/)
5. **Plotly Python Graphing Library**: [https://plotly.com/python/](https://plotly.com/python/)
6. **Pharmacy Council of India Statutory Guidelines**: Good Pharmacy Practice & Schedule H/X Statutory Standards.
7. **Project GitHub Repository**: [https://github.com/Lkkkira/biscuit-](https://github.com/Lkkkira/biscuit-)

---

## **16. SOURCE CODE APPENDIX**

The complete source code of **PharmaCare** is organized under `app/`:

```
PharmaCare/
├── app/
│   ├── main.py                  # Streamlit entrypoint & page routing
│   ├── components/
│   │   ├── styles.py            # Global Vanilla White CSS design tokens
│   │   ├── sidebar.py           # Clinical sidebar & session controls
│   │   ├── metric_card.py       # Top-accent KPI metric card layout
│   │   ├── status_badge.py      # Clinical status badges
│   │   └── empty_state.py       # Standardized empty state banner
│   ├── core/
│   │   ├── database.py          # SQLAlchemy 2.x engine & SessionLocal
│   │   ├── config.py            # Application settings & environment vars
│   │   ├── exceptions.py        # Custom exception handlers
│   │   └── logging.py           # Structured logger configuration
│   ├── models/                  # SQLAlchemy ORM Data Models
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── medicine.py
│   │   ├── supplier.py
│   │   ├── purchase.py
│   │   ├── customer.py
│   │   ├── prescription.py
│   │   ├── sale.py
│   │   ├── setting.py
│   │   ├── notification.py
│   │   └── audit_log.py
│   ├── services/                # Pure Python Domain Services
│   │   ├── auth_service.py
│   │   ├── category_service.py
│   │   ├── medicine_service.py
│   │   ├── purchase_service.py
│   │   ├── customer_service.py
│   │   ├── prescription_service.py
│   │   ├── sales_service.py
│   │   ├── report_service.py
│   │   ├── dashboard_service.py
│   │   ├── setting_service.py
│   │   ├── notification_service.py
│   │   ├── backup_service.py
│   │   └── audit_service.py
│   └── pages/                   # Consolidated Application Page Views
│       ├── dashboard.py         # Executive Dashboard & 5-date sales chart
│       ├── billing.py           # POS Counter Billing & PDF receipts
│       ├── medicines.py         # Inventory Catalog & CSV Import
│       ├── purchases.py         # Stock Inward & Wholesale Procurement
│       ├── prescriptions.py     # Prescriptions Registry & Schedule H checks
│       └── reports.py           # Reports, CRM, Admin & Audit Logs
├── tests/
│   └── test_services.py         # 16 Automated Pytest Unit Tests
├── .streamlit/
│   └── config.toml              # Streamlit Theme Configuration
├── Dockerfile                   # Container deployment manifest
├── Procfile                     # Cloud web process manifest
├── render.yaml                  # Render deployment manifest
└── requirements.txt             # Python dependencies
```

### **16.1 Main Application Entrypoint (`app/main.py`)**
```python
"""PharmaCare main entrypoint and multi-page routing configuration."""

import streamlit as st
from app.core.database import init_db
from app.utils.session import init_session_state, is_authenticated

st.set_page_config(
    page_title="PharmaCare - Pharmacy Management",
    page_icon="✚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database schema
init_db()

# Initialize session state variables
init_session_state()

# Navigation setup
if not is_authenticated():
    # Show Login View
    from app.pages.login import render_login_page
    render_login_page()
else:
    # Render main navigation pages
    pg = st.navigation(
        [
            st.Page("pages/dashboard.py", title="Dashboard", icon=":material/dashboard:"),
            st.Page("pages/billing.py", title="Billing / POS", icon=":material/point_of_sale:"),
            st.Page("pages/medicines.py", title="Medicines & Inventory", icon=":material/medication:"),
            st.Page("pages/purchases.py", title="Stock Inward", icon=":material/inventory_2:"),
            st.Page("pages/prescriptions.py", title="Prescriptions", icon=":material/prescriptions:"),
            st.Page("pages/reports.py", title="Reports & Settings", icon=":material/analytics:"),
        ]
    )
    pg.run()
```
