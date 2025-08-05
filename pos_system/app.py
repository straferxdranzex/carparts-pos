import streamlit as st
import pandas as pd
import uuid
from utils import (
    load_inventory,
    save_inventory,
    calculate_profit,
    calculate_selling_price,
    mark_as_sold,
)

st.set_page_config(page_title="Car Parts POS", layout="wide")
st.title("🚗 Car Parts POS System")

# Load inventory
df = load_inventory()

# Tabs
tab1, tab2, tab3 = st.tabs(
    ["📦 Add New Part", "🧾 Inventory & Sales", "📊 Partner Profit Summary"]
)

# 1. Add New Part
with tab1:
    st.subheader("Add a New Car Part to Inventory")
    with st.form("add_part_form"):
        name = st.text_input("Part Name")
        description = st.text_area("Description")
        buying_price = st.number_input("Buying Price (USD)", min_value=0.0)
        shipping_price = st.number_input("Shipping Price (USD)", min_value=0.0)
        conversion_rate = st.number_input("USD to PKR Rate", min_value=0.0, value=280.0)
        profit_margin = st.number_input("Profit Margin (%)", min_value=0.0, value=20.0)
        quantity = st.number_input("Quantity", min_value=1, value=1)

        submitted = st.form_submit_button("➕ Add Part")
        if submitted:
            new_part = {
                "id": str(uuid.uuid4())[:8],
                "name": name,
                "description": description,
                "buying_price_usd": buying_price,
                "shipping_price_usd": shipping_price,
                "conversion_rate": conversion_rate,
                "profit_margin": profit_margin,
                "quantity": quantity,
                "sold": 0,
                "total_profit_pkr": 0.0,
            }
            df = pd.concat([df, pd.DataFrame([new_part])], ignore_index=True)
            save_inventory(df)
            st.success(f"Added {name} to inventory!")

# 2. Inventory and Sales
with tab2:
    st.subheader("Inventory and Sales Dashboard")
    if df.empty:
        st.info("No parts in inventory yet.")
    else:
        st.write("### Current Inventory")
        st.dataframe(df.drop(columns=["id"]), use_container_width=True)

        st.write("### Sell a Unit")
        part_options = df[df["quantity"] > 0][["id", "name"]]
        if not part_options.empty:
            part_selection = st.selectbox(
                "Select Part to Mark as Sold",
                options=part_options["id"],
                format_func=lambda x: f"{part_options[part_options['id'] == x]['name'].values[0]}",
            )

            if st.button("✅ Mark as Sold"):
                df = mark_as_sold(df, part_selection)
                save_inventory(df)
                st.success("Marked as sold and updated profit!")

# 3. Partner Profit Split
with tab3:
    st.subheader("Partner Profit Summary (PKR)")
    total_profit = df["total_profit_pkr"].sum()
    partner_1 = total_profit * 0.6
    partner_2 = total_profit * 0.4

    st.metric("Total Profit (PKR)", f"{total_profit:,.2f}")
    st.metric("Partner A (60%)", f"{partner_1:,.2f}")
    st.metric("Partner B (40%)", f"{partner_2:,.2f}")

    st.write("### Sales Summary by Part")
    profit_df = df[["name", "sold", "total_profit_pkr"]].copy()
    profit_df["Partner A (60%)"] = profit_df["total_profit_pkr"] * 0.6
    profit_df["Partner B (40%)"] = profit_df["total_profit_pkr"] * 0.4
    st.dataframe(profit_df, use_container_width=True)
