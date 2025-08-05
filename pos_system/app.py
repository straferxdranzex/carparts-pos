import streamlit as st
import pandas as pd
import uuid
from utils import (
    load_inventory, save_inventory,
    calculate_profit, calculate_selling_price,
    mark_as_sold, delete_item, reset_inventory  
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

        st.write("### Sell Part Units")
        part_options = df[df["quantity"] > 0][["id", "name", "quantity"]]
        if not part_options.empty:
            part_selection = st.selectbox(
                "Select Part to Sell",
                options=part_options["id"],
                format_func=lambda x: f"{part_options[part_options['id'] == x]['name'].values[0]}"
            )

            selected_part = part_options[part_options["id"] == part_selection]
            max_qty = int(selected_part["quantity"].values[0])
            quantity_to_sell = st.number_input("Quantity to Sell", min_value=1, max_value=max_qty, step=1)

            if st.button("✅ Mark as Sold"):
                try:
                    df = mark_as_sold(df, part_selection, quantity_to_sell)
                    save_inventory(df)
                    st.success(f"Marked {quantity_to_sell} unit(s) as sold.")
                except ValueError as e:
                    st.error(str(e))

        st.write("### 🔴 Delete an Item")
        part_to_delete = st.selectbox(
            "Select part to delete",
            options=df["id"],
            format_func=lambda x: f"{df[df['id'] == x]['name'].values[0]}"
        )
        if st.button("🗑️ Delete Selected Item"):
            df = delete_item(df, part_to_delete)
            save_inventory(df)
            st.warning("Item deleted from inventory.")



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

    st.write("### 🔁 Reset Application")
    with st.expander("⚠️ Reset All Data (Danger Zone)"):
        st.warning("This will permanently delete ALL inventory, sales, and profit data.")
        if st.button("❌ Reset Everything"):
            reset_inventory()
            st.success("Application has been reset.")
            st.rerun()

