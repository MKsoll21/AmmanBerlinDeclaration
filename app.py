import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Amman-Berlin Declaration",
    layout="wide"
)

st.title("Amman-Berlin Declaration")

st.caption(
    "OECD-DAC CRS analysis. Commitments only. "
    "Each CRS record counted individually."
)

# -------------------------
# Load data
# -------------------------

@st.cache_data
def load_data():
    return pd.read_csv(
        "oecd_data.csv",
        encoding="latin1"
    )

df = load_data()

# -------------------------
# Apply filters
# -------------------------

data = df.copy()

# Only commitments
data = data[
    data["FLOW_TYPE"]
    .astype(str)
    .str.upper()
    .isin(["C", "COMMITMENT"])
]

# Allowed modalities
allowed_modalities = [
    "A02",
    "B01",
    "B03",
    "B031",
    "B032",
    "B033",
    "B034",
    "B04",
    "C01",
    "D01",
    "D02",
    "E01"
]

data = data[
    data["MODALITY"]
    .astype(str)
    .str[:3]
    .isin(allowed_modalities)
]

# Exclude sectors
excluded_sectors = [
    "72010",
    "72040",
    "73010"
]

data = data[
    ~data["SECTOR"]
    .astype(str)
    .isin(excluded_sectors)
]

# Disability category
def disability_category(x):
    if pd.isna(x) or x == "":
        return "Not scored"

    try:
        x = int(x)
    except:
        return "Not scored"

    if x == 0:
        return "Scored - not targeted"

    if x in [1, 2]:
        return "Targeted"

    return "Not scored"

data["Disability Category"] = data["DISABILITY"].apply(disability_category)

# -------------------------
# Sidebar
# -------------------------

st.sidebar.header("Filters")

recipient = st.sidebar.selectbox(
    "Recipient",
    ["All"] + sorted(data["Recipient"].dropna().unique())
)

donor = st.sidebar.selectbox(
    "Donor",
    ["All"] + sorted(data["Donor"].dropna().unique())
)

if "Sector.1" in data.columns:
    sector_col = "Sector.1"
elif "Sector" in data.columns:
    sector_col = "Sector"
elif "Sector name" in data.columns:
    sector_col = "Sector name"
else:
    st.error("No sector column found.")
    st.stop()

sector = st.sidebar.selectbox(
    "Sector",
    ["All"] + sorted(data[sector_col].dropna().unique())
)

filtered = data.copy()

if recipient != "All":
    filtered = filtered[filtered["Recipient"] == recipient]

if donor != "All":
    filtered = filtered[filtered["Donor"] == donor]

if sector != "All":
    filtered = filtered[filtered[sector_col] == sector]

# -------------------------
# Results
# -------------------------

st.metric(
    "Total CRS commitments analysed",
    len(filtered)
)

result = (
    filtered["Disability Category"]
    .value_counts()
    .reset_index()
)

result.columns = ["Category", "Count"]

result["Percentage"] = (
    result["Count"] /
    result["Count"].sum() *
    100
).round(1)

fig = px.bar(
    result,
    x="Category",
    y="Count",
    color="Category",
    text=result.apply(
        lambda r: f'{r["Count"]}<br>{r["Percentage"]}%',
        axis=1
    ),
    title="Disability Inclusion Marker"
)

st.plotly_chart(fig, use_container_width=True)

st.dataframe(result, hide_index=True)
