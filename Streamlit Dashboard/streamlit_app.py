import streamlit as st
import pandas as pd
from helper import process_receipts
import helper
import time


# ------------------------------------------------------------
# Page config
# ------------------------------------------------------------
st.set_page_config(page_title="Costco Receipt Dashboard",
                   layout="wide",
                   initial_sidebar_state="expanded")
helper.load_css()

# ------------------------------------------------------------
# Header + file uploader
# ------------------------------------------------------------
right,left=st.columns([4,1.5])
with right:
    st.title("🧾 Costco Spend Analysis")

    date_range_placeholder = st.markdown(
            "<span style='background:#e5e7eb; padding:2px 10px; border-radius:12px; font-size:0.85rem;'>Waiting for file...</span>",
            unsafe_allow_html=True,
        )

with left:
    file_list = st.file_uploader("Upload Costco receipts", 
                            type=["json"],
                            accept_multiple_files=True)

    if not file_list:
        #st.info("Upload your Costco receipts JSON to begin.")
        st.stop()

    all_receipts = []

    # Load all files
    for f in file_list:
        try:
            df = pd.read_json(f)
            recs = df.to_dict(orient="records")

            if not isinstance(recs, list):
                raise ValueError("Each JSON must contain an array of receipt objects.")

            all_receipts.extend(recs)

        except Exception as e:
            st.error(f"Invalid JSON file {f.name}: {e}")
            st.stop()

    with st.spinner("Processing receipts..."):
        merch, gas, all_locations, date_range = process_receipts(all_receipts)

# Store in session state for other pages
st.session_state["merch"] = merch
st.session_state["gas"] = gas
st.session_state["all_locations"] = all_locations
st.session_state["date_range"] = date_range
# update header date badge
date_range_placeholder.markdown(
    f"<span style='background:#e5e7eb; padding:2px 10px; border-radius:12px; font-size:0.85rem;'>{st.session_state["date_range"]}</span>",
    unsafe_allow_html=True,
)


# st.success("Data loaded! Redirecting to Merchandise page in 10 seconds...")

# time.sleep(10)
# st.switch_page("pages/Merchandise.py")

# Pages at the top — Excel style
tabs = st.tabs(["📦 Merchandise", "⛽ Gas", "📈 Prices"])

with tabs[0]:
    import streamlit as st
    import pandas as pd
    import helper

    helper.load_css()

    #st.title("📦 Merchandise Dashboard")



    if "merch" not in st.session_state:
        st.error("No data loaded. Upload JSON on the Home page.")
        st.stop()

    merch = st.session_state["merch"]
    all_locations = st.session_state["all_locations"]

    # ------------------------------------------------------------
    # MERCHANDISE SECTION
    # ------------------------------------------------------------



    st.markdown("<div class='section-header'>🛒 Warehouse Shopping</div>", unsafe_allow_html=True)

    summary_cols = st.columns(6)

    with summary_cols[0]:
        st.markdown(
            f"""
            <div class="summary-card">
            <div class="label">Net Spent (Merch)</div>
            <div class="value">{helper.format_money(merch['total_spent'])}</div>
            <div class="sub">Purchases - refunds</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with summary_cols[1]:
        st.markdown(
            f"""
            <div class="summary-card">
            <div class="label">Net Items</div>
            <div class="value">{helper.format_num(merch['total_units'],0)}</div>
            <div class="sub">Unique codes: {len(merch['item_stats'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with summary_cols[2]:
        avg_per_receipt = merch["total_spent"] / len(merch["receipts"]) if merch["receipts"] else 0
        st.markdown(
            f"""
            <div class="summary-card">
            <div class="label">Merch Visits</div>
            <div class="value">{len(merch['receipts'])}</div>
            <div class="sub">Avg {helper.format_money(avg_per_receipt)} / trip</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with summary_cols[3]:
        st.markdown(
            f"""
            <div class="summary-card refund">
            <div class="label" style="color:#7c3aed;">Total Refunded</div>
            <div class="value" style="color:#7c3aed;">{helper.format_money(merch['refund_total'])}</div>
            <div class="sub">Returns count: {merch['refund_count']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with summary_cols[4]:
        st.markdown(
            f"""
            <div class="summary-card">
            <div class="label">Merch Locations</div>
            <div class="value">{len(merch['locations'])}</div>
            <div class="sub">Unique warehouses</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    # Executive rewards
    years = sorted(merch["subtotal_by_year"].keys(), reverse=True)
    rewards_rows = []
    total_rewards = 0.0
    for y in years:
        sub = merch["subtotal_by_year"][y]
        rew = sub * 0.02
        total_rewards += rew
        rewards_rows.append({"Year": y, "Qualifying Spend": sub, "2% Cashback": rew})

    with summary_cols[5]:
        st.markdown(
            f"""
            <div class="summary-card gold">
            <div class="label" style="color:#b45309;">Est. Executive Reward</div>
            <div class="value" style="color:#b45309;">{helper.format_money(total_rewards)}</div>
            <div class="sub">2% of annual subtotals</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")
    # ------------------------------------------------------------
    # Merch item tables
    # ------------------------------------------------------------

    item_values = list(merch["item_stats"].values())

    def df_most_expensive():
        rows = []
        for s in item_values:
            if s["max_price"] <= 0:
                continue

            avg_price = s["total_spent"] / s["total_units"]
            rows.append(
                {
                    "Item": s["name"],
                    "Item #": s["itemNumber"],
                    "Max Price (num)": s["max_price"],         # numeric
                    "Avg Price (num)": avg_price,              # numeric
                }
            )

        # If no rows, return empty table with proper columns
        if not rows:
            return pd.DataFrame(columns=["Item", "Item #", "Max Price", "Avg Price"])

        # Sort numerically
        df = pd.DataFrame(rows).sort_values(
            by="Max Price (num)", ascending=False
        ).head(10)

        # Convert to formatted strings for display
        df["Max Price"] = df["Max Price (num)"].map(helper.format_money)
        df["Avg Price"] = df["Avg Price (num)"].map(helper.format_money)

        return df[["Item", "Item #", "Max Price", "Avg Price"]]

    def df_most_total_spent():
        rows = []
        for s in item_values:
            total_spent = s["total_spent"]
            units = s["total_units"]

            if units <= 0 or total_spent <= 0:
                continue

            avg_price = total_spent / units

            rows.append(
                {
                    "Item": s["name"],
                    "Item #": s["itemNumber"],
                    "Total (num)": total_spent,      # numeric
                    "Units": units,                  # numeric
                    "Avg Price (num)": avg_price,    # numeric
                }
            )

        # No items → return empty frame with proper columns
        if not rows:
            return pd.DataFrame(
                columns=["#", "Item", "Item #", "Total", "Units", "Avg Price"]
            )

        # Sort numerically (not formatted)
        df = pd.DataFrame(rows).sort_values(
            by="Total (num)", ascending=False
        ).head(10)

        # Format for display
        df["#"] = range(1, len(df) + 1)
        df["Total"] = df["Total (num)"].map(helper.format_money)
        df["Avg Price"] = df["Avg Price (num)"].map(helper.format_money)

        return df[["#", "Item", "Item #", "Total", "Units", "Avg Price"]]

    def df_most_purchased():
        rows = []
        for s in item_values:

            units = s["total_units"]
            total_spent = s["total_spent"]

            # Skip invalid items
            if units <= 0 or total_spent <= 0:
                continue

            avg_price = total_spent / units

            # Price change (optional)
            change = s["max_price"] - s["min_price"]

            rows.append(
                {
                    "Item": s["name"],
                    "Item #": s["itemNumber"],
                    "Units (num)": units,           # numeric for sorting
                    "Avg Price (num)": avg_price,   # numeric
                    "Change (num)": change,         # numeric change
                }
            )

        # If no rows → return an empty DataFrame with correct columns
        if not rows:
            return pd.DataFrame(
                columns=["#", "Item", "Item #", "Units", "Avg Price", "Change"]
            )

        # Sort by numeric units
        df = pd.DataFrame(rows).sort_values(
            by="Units (num)", ascending=False
        ).head(10)

        # Add rank
        df["#"] = range(1, len(df) + 1)

        # Human-friendly formatting
        df["Units"] = df["Units (num)"].map(lambda x: f"{x:,.0f}")
        df["Avg Price"] = df["Avg Price (num)"].map(helper.format_money)
        df["Change"] = df["Change (num)"].apply(
            lambda v: f"+{helper.format_money(v)}" if v > 0.01 else "-"
        )

        return df[["#", "Item", "Item #", "Units", "Avg Price", "Change"]]

    top_row_left, top_row_mid, top_row_right = st.columns(3)

    with top_row_left:
        st.subheader("💎 Most Expensive")
        df_exp = df_most_expensive()
        if not df_exp.empty:
            st.dataframe(df_exp, hide_index=True, use_container_width=True)
        else:
            st.info("Not enough price history.")

    with top_row_mid:
        st.subheader("💰 Most Total Spent")
        df_spent = df_most_total_spent()
        st.dataframe(df_spent, hide_index=True, use_container_width=True)
        
    with top_row_right:
        st.subheader("🔥 Most Frequently Bought")
        df_freq = df_most_purchased()
        st.dataframe(df_freq, hide_index=True, use_container_width=True)

    # ------------------------------------------------------------
    # Merch: Rewards table + monthly trend
    # ------------------------------------------------------------
    left_merch, right_merch = st.columns(2)

    with left_merch:
        st.subheader("🏆 2% Reward Tracker")
        if rewards_rows:
            rewards_df = pd.DataFrame(rewards_rows)
            rewards_df["Qualifying Spend"] = rewards_df["Qualifying Spend"].map(helper.format_money)
            rewards_df["2% Cashback"] = rewards_df["2% Cashback"].map(helper.format_money)
            st.dataframe(rewards_df, hide_index=True, use_container_width=True)
        else:
            st.info("No subtotal data available for rewards.")

    with right_merch:
        st.subheader("📊 Merchandise Spending Trend")
        if merch["monthly"]:
            merch_month_df = (
                pd.DataFrame(
                    [
                        {"month_key": k, "month": helper.month_label_from_key(k), "total": v["spent"]}
                        for k, v in merch["monthly"].items()
                    ]
                )
                .sort_values("month_key")
            )

            import altair as alt

            chart = (
                alt.Chart(merch_month_df)
                .mark_bar()
                .encode(
                    x=alt.X("month:N", title="Month", sort=None),
                    y=alt.Y("total:Q", title="Amount Spent ($)"),
                    tooltip=["month", "total"],
                )
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No monthly merchandise data.")

    # Combined locations
    st.markdown("")
    st.markdown(
        f"""
        <div class="summary-card" style="max-width:280px; margin-top:0.6rem;">
        <div class="label">Total Unique Locations</div>
        <div class="value">{len(all_locations)}</div>
        <div class="sub">Gas + merchandise combined</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with tabs[1]:
    import streamlit as st
    import pandas as pd
    import helper

    helper.load_css()

    #st.title("⛽ Gas Dashboard")


    if "gas" not in st.session_state:
        st.error("No data loaded. Upload JSON on the Home page.")
        st.stop()

    gas = st.session_state["gas"]

    # ------------------------------------------------------------
    # GAS SECTION
    # ------------------------------------------------------------
    st.markdown(
        "<div class='section-header' style='color:#b91c1c; border-color:#fecaca;'>⛽ Gas Station Stats</div>",
        unsafe_allow_html=True,
    )

    gas_cols = st.columns(5)

    weighted_avg_price = (
        gas["price_sum"] / gas["total_gallons"] if gas["total_gallons"] > 0 else 0.0
    )

    with gas_cols[0]:
        st.markdown(
            f"""
            <div class="summary-card gas">
            <div class="label">Total Gas Spent</div>
            <div class="value">{helper.format_money(gas['total_spent'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with gas_cols[1]:
        st.markdown(
            f"""
            <div class="summary-card">
            <div class="label">Total Gallons</div>
            <div class="value">{helper.format_num(gas['total_gallons'],1)} gal</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with gas_cols[2]:
        st.markdown(
            f"""
            <div class="summary-card">
            <div class="label">Avg Price / Gal</div>
            <div class="value">{helper.format_money(weighted_avg_price)}</div>
            <div class="sub">Weighted average</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with gas_cols[3]:
        st.markdown(
            f"""
            <div class="summary-card">
            <div class="label">Gas Visits</div>
            <div class="value">{gas['count']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with gas_cols[4]:
        st.markdown(
            f"""
            <div class="summary-card">
            <div class="label">Gas Locations</div>
            <div class="value">{len(gas['locations'])}</div>
            <div class="sub">Unique stations</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")

    gas_top_left, gas_top_right = st.columns(2)

    # Gas price history (premium vs regular)
    with gas_top_left:
        st.subheader("📉 Price Per Gallon History")
        if gas["grades"]:
            import altair as alt

            rows = []
            for month_key, g in gas["grades"].items():
                rows.append(
                    {
                        "month_key": month_key,
                        "month": helper.month_label_from_key(month_key),
                        "grade": "Premium",
                        "price": g["pSpend"] / g["pGal"] if g["pGal"] > 0 else None,
                    }
                )
                rows.append(
                    {
                        "month_key": month_key,
                        "month": helper.month_label_from_key(month_key),
                        "grade": "Regular",
                        "price": g["rSpend"] / g["rGal"] if g["rGal"] > 0 else None,
                    }
                )
            gas_price_df = pd.DataFrame(rows).dropna()
            gas_price_df = gas_price_df.sort_values("month_key")
            chart = (
                alt.Chart(gas_price_df)
                .mark_line(point=True)
                .encode(
                    x=alt.X("month:N", title="Month", sort=None),
                    y=alt.Y("price:Q", title="Price ($/gal)"),
                    color="grade:N",
                    tooltip=["grade", "month", "price"],
                )
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No gas grade data.")

    # Gas spend breakdown (premium vs regular)
    with gas_top_right:
        st.subheader("💳 Gas Spend by Grade")
        if gas["grades"]:
            rows = []
            for month_key, g in gas["grades"].items():
                rows.append(
                    {
                        "month_key": month_key,
                        "month": helper.month_label_from_key(month_key),
                        "Premium Spend": g["pSpend"],
                        "Regular Spend": g["rSpend"],
                    }
                )
            gas_spend_df = pd.DataFrame(rows).sort_values("month_key")
            gas_spend_df_melt = gas_spend_df.melt(
                id_vars=["month_key", "month"], var_name="grade", value_name="spend"
            )
            import altair as alt

            chart = (
                alt.Chart(gas_spend_df_melt)
                .mark_bar()
                .encode(
                    x=alt.X("month:N", title="Month", sort=None),
                    y=alt.Y("spend:Q", title="Spend ($)"),
                    color="grade:N",
                    tooltip=["month", "grade", "spend"],
                )
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No gas spend breakdown data.")

    # Total monthly gas spend
    st.subheader("📊 Total Monthly Gas Spending")
    if gas["monthly"]:
        gas_month_df = (
            pd.DataFrame(
                [
                    {"month_key": k, "month": helper.month_label_from_key(k), "total": v["spent"]}
                    for k, v in gas["monthly"].items()
                ]
            )
            .sort_values("month_key")
        )
        import altair as alt

        chart = (
            alt.Chart(gas_month_df)
            .mark_bar()
            .encode(
                x=alt.X("month:N", title="Month", sort=None),
                y=alt.Y("total:Q", title="Amount Spent ($)"),
                tooltip=["month", "total"],
            )
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No gas receipts detected.")



    st.divider()

with tabs[2]:
    import streamlit as st
    import pandas as pd
    import helper

    helper.load_css()

    #st.title("📈 Price Trends & Item Lookup")

    if "merch" not in st.session_state:
        st.error("No data loaded. Upload JSON on the Home page.")
        st.stop()

    merch = st.session_state["merch"]



    # ------------------------------------------------------------
    # Searchable Item Lookup
    # ------------------------------------------------------------
    st.markdown("<div class='section-header'>📈 Price Trends & Item Lookup", unsafe_allow_html=True)
    item_values = list(merch["item_stats"].values())
    def df_price_increase():
        rows = []
        for s in item_values:
            if s["last_price"] > s["first_price"]:
                diff = s["last_price"] - s["first_price"]
                rows.append(
                    {
                        "Item": s["name"],
                        "Item #": s["itemNumber"],
                        "Old → New": f"{helper.format_money(s['first_price'])} → {helper.format_money(s['last_price'])}",
                        "Diff (num)": diff,   # numeric
                    }
                )

        # If no rows → return empty table with correct columns
        if not rows:
            return pd.DataFrame(columns=["Item", "Item #", "Old → New", "Diff"])

        # Build DataFrame and sort N U M E R I C A L L Y
        df = pd.DataFrame(rows).sort_values(
            by="Diff (num)", ascending=False
        ).head(50)

        # Human-friendly column
        df["Diff"] = df["Diff (num)"].map(helper.format_money)

        return df[["Item", "Item #", "Old → New", "Diff"]]


    def df_price_decrease():
        rows = []
        for s in item_values:
            if s["last_price"] < s["first_price"]:
                diff = s["last_price"] - s["first_price"]
                rows.append(
                    {
                        "Item": s["name"],
                        "Item #": s["itemNumber"],
                        "Old → New": f"{helper.format_money(s['first_price'])} → {helper.format_money(s['last_price'])}",
                        "Diff (num)": diff,   # numeric
                    }
                )

        # If no rows → return an empty table with correct columns
        if not rows:
            return pd.DataFrame(columns=["Item", "Item #", "Old → New", "Diff"])

        # Build DataFrame and sort N U M E R I C A L L Y
        df = pd.DataFrame(rows).sort_values(
            by="Diff (num)",
            ascending=True   # lower first
        ).head(50)

        # Human-readable formatted column
        df["Diff"] = df["Diff (num)"].map(helper.format_money)

        return df[["Item", "Item #", "Old → New", "Diff"]]


    

    bottom_row_left, bottom_row_right = st.columns(2)

    with bottom_row_left:
        st.subheader("📈 Price Increases")
        df_inc = df_price_increase()
        if not df_inc.empty:
            st.dataframe(df_inc, hide_index=True, use_container_width=True)
        else:
            st.info("No items with price increases.")
        

    with bottom_row_right:
        st.subheader("📉 Price Drops")
        df_dec = df_price_decrease()
        if not df_dec.empty:
            st.dataframe(df_dec, hide_index=True, use_container_width=True)
        else:
            st.info("No items with price decreases.")
        
    st.markdown("<div class='section-header'>🔍 Item Lookup</div>", unsafe_allow_html=True)

    if merch["item_stats"]:
        item_label_to_key = {
            f"{v['name']} (#{v['itemNumber']})": k for k, v in merch["item_stats"].items()
        }
        choices = [""] + sorted(item_label_to_key.keys())
        choice = st.selectbox("Search for an item", options=choices, index=0)

        if choice:
            key = item_label_to_key[choice]
            stat = merch["item_stats"][key]

            st.markdown(f"### 🛒 {stat['name']}  (#{stat['itemNumber']})")

            #with summary_cols[0]:
            # st.markdown(
            #     f"""
            #     <div class="summary-card">
            #     <div class="label">Times Bought</div>
            #     <div class="value">{stat["purchases"]}</div>
            #     /<div class="sub"></div>
            #     </div>
            #     """,
            #     unsafe_allow_html=True,
            # )

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                #st.metric("Times Bought", stat["purchases"])
                st.markdown(
                    f"""
                    <div class="summary-card">
                    <div class="label">Times Bought</div>
                    <div class="value">{stat["purchases"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
            with m2:
                #st.metric("Total Spent", helper.format_money(stat["total_spent"]))
                st.markdown(
                    f"""
                    <div class="summary-card">
                    <div class="label">Total Spent</div>
                    <div class="value">{stat["total_spent"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with m3:
                avg_price = stat["total_spent"] / stat["total_units"]
                #st.metric("Avg Price", helper.format_money(avg_price))
                st.markdown(
                    f"""
                    <div class="summary-card">
                    <div class="label">Avg Price</div>
                    <div class="value">{helper.format_money(avg_price)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with m4:
                # st.metric(
                #     "Min → Max Price",
                #     f"{helper.format_money(stat['min_price'])} → {helper.format_money(stat['max_price'])}",
                # )
                st.markdown(
                    f"""
                    <div class="summary-card">
                    <div class="label">Min → Max Price</div>
                    <div class="value">{helper.format_money(stat['min_price'])} → {helper.format_money(stat['max_price'])}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Price history table + chart
            hist_df = pd.DataFrame(stat["price_history"])
            hist_df = hist_df.sort_values("date")
            hist_df["date"] = hist_df["date"].dt.date

            st.markdown("#### 🗂️ Price History")
            st.dataframe(hist_df.rename(columns={"date": "Purchase Date", "price": "Price"}),
                        hide_index=True,
                        use_container_width=True)

            if not hist_df.empty:
                import altair as alt

                chart = (
                    alt.Chart(hist_df)
                    .mark_line(point=True)
                    .encode(
                        x=alt.X("date:T", title="Date"),
                        y=alt.Y("price:Q", title="Price ($)"),
                        tooltip=["date", "price"],
                    )
                )
                st.markdown("#### 📈 Price Trend Over Time")
                st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No merchandise items to search.")

