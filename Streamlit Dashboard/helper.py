from datetime import datetime
from collections import defaultdict
import streamlit as st



# ------------------------------------------------------------
# Custom CSS
# ------------------------------------------------------------
def load_css():
    import streamlit as st
    st.markdown("""
    <style>
    :root {
    --bg: #f5f7fb;
    --card-bg: #ffffff;
    --accent: #2563eb;
    --accent-soft: #e0edff;
    --gas-accent: #dc2626;
    --gas-soft: #fee2e2;
    --gold: #d97706;
    --gold-soft: #fef3c7;
    --refund-accent: #7c3aed;
    --refund-soft: #f3e8ff;
    --text-main: #111827;
    --text-muted: #6b7280;
    --border: #e5e7eb;
    --success: #16a34a;
    --danger: #ef4444;
    --radius-lg: 18px;
    --shadow-soft: 0 10px 25px rgba(15, 23, 42, 0.05);
    }

    body {
    background: var(--bg);
    }

    /* Tighten base padding */
    .block-container {
    padding-top: 0.8rem;
    padding-bottom: 1rem;
    padding-left: 1.2rem;
    padding-right: 1.2rem;
    }

    /* Summary cards */
    .summary-card {
    background: var(--card-bg);
    border-radius: var(--radius-lg);
    padding: 14px 16px;
    box-shadow: var(--shadow-soft);
    border: 1px solid var(--border);
    margin-bottom: 8px;
    }
    .summary-card.gold { border-left: 4px solid var(--gold); }
    .summary-card.gas { border-left: 4px solid var(--gas-accent); }
    .summary-card.refund { border-left: 4px solid var(--refund-accent); }

    .summary-card .label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
    font-weight: 600;
    }
    .summary-card .value {
    margin-top: 4px;
    font-size: 1.35rem;
    font-weight: 700;
    }
    .summary-card .sub {
    margin-top: 2px;
    font-size: 0.8rem;
    color: var(--text-muted);
    }

    /* Section headers */
    .section-header {
    font-size: 1.3rem;
    font-weight: 700;
    margin: 1.2rem 0 0.6rem;
    display: flex;
    align-items: center;
    gap: 8px;
    padding-bottom: 0.3rem;
    border-bottom: 2px solid var(--border);
    }

    /* Tables */
    table {
    border-collapse: collapse;
    width: 100%;
    }
    thead { background: var(--accent-soft); }
    th, td {
    padding: 6px 10px !important;
    }
    [data-testid="dataframe"] td {
    padding-top: 4px !important;
    padding-bottom: 4px !important;
    }
    [data-testid="dataframe"] th {
    padding-top: 4px !important;
    padding-bottom: 4px !important;
    }

    /* --- Compact File Uploader --- */

    /* Compact uploader without breaking uploaded-file list */
    div[data-testid="stFileUploader"] {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding: 0 !important;
    }

    /* Only shrink the DROP AREA */
    div[data-testid="stFileUploader"] section {
        padding: 4px 8px !important;
        border-radius: 6px !important;
    }

    /* Shrink icons */
    div[data-testid="stFileUploader"] svg {
        width: 14px !important;
        height: 14px !important;
    }

    /* Shrink text inside drop area */
    div[data-testid="stFileUploader"] section p {
        font-size: 0.80rem !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Metrics */
    div[data-testid="stMetric"] {
    padding-top: 0.1rem;
    padding-bottom: 0.1rem;
    }
    div[data-testid="stMetricValue"] {
    font-size: 1.4rem;
    font-weight: 600;
    }
    div[data-testid="stMetricLabel"] {
    font-size: 0.85rem;
    }

    /* Smaller chart area padding */
    .stAltairChart {
    padding-top: 0.2rem;
    padding-bottom: 0.2rem;
    }
    </style>
    """, unsafe_allow_html=True)



## Identify gas receipts
def is_gas_receipt(rec):
    # Primary identifiers
    if rec.get("receiptType") == "Gas Station":
        return True
    if rec.get("documentType") == "FuelReceipts":
        return True

    # Only true fuel items
    for item in rec.get("itemArray") or []:
        if item.get("itemNumber") in ("800599", "800877"):
            return True

    return False

## New gas grade entry
def new_gas_grade():
    return {"pSpend": 0.0, "pGal": 0.0, "rSpend": 0.0, "rGal": 0.0}

def format_money(v: float) -> str:
    return f"${v:,.2f}"


def format_num(v: float, digits: int = 1) -> str:
    return f"{v:,.{digits}f}"


def month_label_from_key(month_key: str) -> str:
    """month_key is 'YYYY-MM' -> 'Mon 'YY' """
    dt = datetime.strptime(month_key + "-01", "%Y-%m-%d")
    return dt.strftime("%b '%y")


# ------------------------------------------------------------
# MAIN RECEIPT PROCESSING FUNCTION (Split Gas and Merch)
# ------------------------------------------------------------
def process_receipts(receipts):
    """
    Split records into merchandise vs gas, build item stats, monthly totals, refunds & rewards.
    """

    merch = {
        "receipts": [],
        "item_stats": {},  # itemNumber -> dict
        "monthly": defaultdict(lambda: {"spent": 0.0}),
        "subtotal_by_year": defaultdict(float),
        "total_spent": 0.0,
        "total_units": 0.0,
        "refund_count": 0,
        "refund_total": 0.0,
        "locations": set(),
    }

    gas = {
        "receipts": [],
        "monthly": defaultdict(lambda: {"spent": 0.0}),
        "total_spent": 0.0,
        "total_gallons": 0.0,
        "price_sum": 0.0,  # weighted (price * gallons)
        "count": 0,
        "locations": set(),
        "grades":{}
    }

    all_locations = set()
    all_dates = []

    for rec in receipts:
        trx_date_str = rec.get("transactionDate")
        if not trx_date_str:
            continue

        # transactionDate is ISO-like ("2025-09-01" or "2025-09-01T00:00:00")
        try:
            date = datetime.fromisoformat(trx_date_str)
        except Exception:
            try:
                date = datetime.strptime(trx_date_str, "%Y-%m-%d")
            except Exception:
                continue

        all_dates.append(date)
        month_key = date.strftime("%Y-%m")
        year = date.year

        total = float(rec.get("total") or 0.0)
        loc_name = (rec.get("warehouseName") or "Unknown").strip()
        all_locations.add(loc_name)

        item_array = rec.get("itemArray") or []

        if is_gas_receipt(rec):
            gas["receipts"].append(rec)
            gas["locations"].add(loc_name)
            gas["total_spent"] += total
            gas["count"] += 1
            gas["monthly"][month_key]["spent"] += total

            for item in item_array:
                gals = float(item.get("fuelUnitQuantity") or 0.0)
                price = float(item.get("itemUnitPriceAmount") or 0.0)
                amt = float(item.get("amount") or 0.0)
                item_no = item.get("itemNumber")

                if gals > 0:
                    gas["total_gallons"] += gals
                    gas["price_sum"] += price * gals

                # Build grade breakdown for charts
                if month_key not in gas["grades"]:
                    gas["grades"][month_key] = new_gas_grade()  # triggers default

                g_entry = gas["grades"][month_key]
                if item_no == "800877":  # Premium
                    g_entry["pSpend"] += amt
                    g_entry["pGal"] += gals
                elif item_no == "800599":  # Regular
                    g_entry["rSpend"] += amt
                    g_entry["rGal"] += gals

        else:
            merch["receipts"].append(rec)
            merch["locations"].add(loc_name)
            merch["total_spent"] += total
            merch["monthly"][month_key]["spent"] += total

            # refunds
            if total < 0 or rec.get("transactionType") == "Refund":
                merch["refund_count"] += 1
                merch["refund_total"] += abs(total)

            # executive rewards (pre-tax subtotal)
            subtotal = float(rec.get("subTotal") or 0.0)
            merch["subtotal_by_year"][year] += subtotal

            # item stats
            for item in item_array:
                unit = float(item.get("unit") or 0.0)
                amount = float(item.get("amount") or 0.0)
                item_no = item.get("itemNumber")
                if not item_no or unit <= 0 or amount <= 0:
                    continue

                name = (item.get("itemDescription01") or "").strip()
                unit_price = amount / unit

                if item_no not in merch["item_stats"]:
                    merch["item_stats"][item_no] = {
                        "itemNumber": item_no,
                        "name": name,
                        "total_spent": 0.0,
                        "total_units": 0.0,
                        "purchases": 0,
                        "price_history": [],  # list of dicts {date, price}
                    }

                stat = merch["item_stats"][item_no]
                stat["total_spent"] += amount
                stat["total_units"] += unit
                stat["purchases"] += 1
                stat["price_history"].append({"date": date, "price": unit_price})
                merch["total_units"] += unit

    # item stats post-processing
    for stat in merch["item_stats"].values():
        hist = sorted(stat["price_history"], key=lambda x: x["date"])
        stat["price_history"] = hist
        prices = [p["price"] for p in hist]
        if prices:
            stat["first_price"] = prices[0]
            stat["last_price"] = prices[-1]
            stat["max_price"] = max(prices)
            stat["min_price"] = min(prices)
        else:
            stat["first_price"] = stat["last_price"] = stat["max_price"] = stat["min_price"] = 0.0

    # date range string for header
    if all_dates:
        min_d, max_d = min(all_dates), max(all_dates)
        if min_d.year == max_d.year:
            date_range_str = str(min_d.year)
        else:
            date_range_str = f"{min_d.year} – {max_d.year}"
    else:
        date_range_str = "Waiting for file..."

    # Store in session state for other pages
    st.session_state["merch"] = merch
    st.session_state["gas"] = gas
    st.session_state["all_locations"] = all_locations
    st.session_state["date_range"] = date_range_str

    return merch, gas, all_locations, date_range_str

