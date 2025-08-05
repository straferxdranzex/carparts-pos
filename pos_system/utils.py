import pandas as pd
import os

INVENTORY_FILE = "data/inventory.csv"


def load_inventory():
    """Loads inventory from CSV, creates file and folder if not exists."""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(INVENTORY_FILE), exist_ok=True)

    if not os.path.exists(INVENTORY_FILE):
        df = pd.DataFrame(columns=[
            "id", "name", "description", "buying_price_usd",
            "shipping_price_usd", "conversion_rate", "profit_margin",
            "quantity", "sold", "total_profit_pkr"
        ])
        df.to_csv(INVENTORY_FILE, index=False)
    else:
        df = pd.read_csv(INVENTORY_FILE)
    return df



def save_inventory(df):
    """Saves inventory back to CSV."""
    df.to_csv(INVENTORY_FILE, index=False)


def calculate_selling_price(buying_price, shipping_price, rate, margin):
    """Returns final selling price in PKR."""
    base_cost = (buying_price + shipping_price) * rate
    return base_cost * (1 + margin / 100)


def calculate_profit(buying_price, shipping_price, rate, margin):
    """Returns profit in PKR per unit."""
    base_cost = (buying_price + shipping_price) * rate
    selling_price = base_cost * (1 + margin / 100)
    return selling_price - base_cost


def mark_as_sold(df, part_id):
    """Marks one unit of a part as sold, updates profit and quantity."""
    index = df[df["id"] == part_id].index

    if not index.empty and df.loc[index[0], "quantity"] > 0:
        i = index[0]
        df.at[i, "quantity"] -= 1
        df.at[i, "sold"] += 1

        profit = calculate_profit(
            df.at[i, "buying_price_usd"],
            df.at[i, "shipping_price_usd"],
            df.at[i, "conversion_rate"],
            df.at[i, "profit_margin"],
        )
        df.at[i, "total_profit_pkr"] += profit

    return df
