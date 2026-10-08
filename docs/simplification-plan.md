# PharmaCare — Simplification & Usability Architecture Plan

## Phase 1: Audit & Navigation Consolidation Plan

This document outlines the architectural plan for simplifying the PharmaCare Smart Pharmacy Management System.

### 1. Primary Navigation Structure (6 Core Sections)

The application navigation is consolidated into six primary sections using Streamlit multi-page routing, with administrator-only tabs cleanly embedded within **Reports & Settings**.

| Primary Section | Included Capabilities & Consolidated Pages | Role Access |
|---|---|---|
| **1. Dashboard** | Executive metrics, sales timeline, category distribution, actionable alert badges, quick action buttons (`pages/dashboard.py`). | All Users |
| **2. Billing / POS** | Single-screen counter POS (`pages/billing.py`), FEFO batch deduction, customer lookup, Rx validation, GST calculation, PDF invoice generation, and Sales History tab (`pages/sales_history.py`). | All Users |
| **3. Medicines & Inventory** | Consolidated inventory management (`pages/medicines.py`), Expiry & Quarantine tab (`pages/expiry_monitor.py`), Low-Stock & Reorder queue (`pages/low_stock.py`), and Categories manager. | All Users |
| **4. Stock Inward** | Multi-item intake receiving form (`pages/purchases.py`), Inward purchase history, and Suppliers directory (`pages/suppliers.py`). | All Users |
| **5. Prescriptions** | Doctor prescription registry (`pages/prescriptions.py`), patient mapping, Schedule H compliance status, and prescription verification. | All Users |
| **6. Reports & Settings** | Sales reports & financial valuation (`pages/reports.py`), Customer directory (`pages/customers.py`), Notification center (`pages/notifications.py`), plus **Admin-Only** System Administration (`pages/admin.py`) and Audit Logs (`pages/audit_logs.py`). | All Users (Admin tabs restricted) |

---

### 2. Feature Mapping Matrix (Keep, Simplify, Defer)

#### ✅ Keep (Essential Core Business Rules)
- **First-Expiry-First-Out (FEFO)** batch allocation for sales.
- **Schedule H prescription validation** prior to dispensing controlled medicines.
- **Automatic expired stock quarantine** and bio-waste disposal logging.
- **ReportLab PDF invoice** rendering with breakdown of items, tax, and discount.
- **SQLAlchemy 2.x ORM models** with SQLite `PRAGMA foreign_keys=ON`.
- **Role-Based Access Control (RBAC)** (`Admin` vs. `Pharmacist`).
- **Immutable audit logging** for security actions.
- **SQLite hot backup snapshot & restoration**.

#### ⚡ Simplify (Workflow & Navigation UX Enhancements)
- **Navigation Menu**: Reduced from 14 standalone sidebar menu items to **6 intuitive sections**.
- **POS Checkout**: Consolidated into a single screen with quick customer selection, instant cart updates, FEFO allocation summary, and built-in PDF download.
- **Inventory Management**: Unified view housing medicines, batches, expiry alerts, low stock queue, and categories in clean tabs.
- **Procurement Workflow**: Single location for receiving stock purchases and managing supplier contacts.
- **Visual Design**: Standardized clinical teal & slate aesthetic with clean typography, metric cards, status badges, and empty states.

#### ⏸️ Defer (Out of Scope / Non-Essential Complexity)
- **External SMS/Email Gateways**: Deferred to maintain standalone pure-Python zero-dependency operations.
- **Camera/Hardware Barcode Webhooks**: Kept as instant barcode/SKU text input.
- **Multi-Branch Multi-Store Sync**: Deferred for single-location pharmacy operation simplicity.

---

### 3. Implementation Order
1. **Phase 1**: Project Audit & Documentation (Completed).
2. **Phase 2**: Navigation & Layout Structure (`app/main.py` + routing).
3. **Phase 3**: Dashboard & Workflow Optimization (`app/pages/`).
4. **Phase 4**: Verification of Business Rules & FEFO Integrity.
5. **Phase 5**: Styling & Visual Consistency (`app/components/styles.py` & sidebar).
6. **Phase 6**: Comprehensive Testing & Safety Check.
