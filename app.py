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
# Identify sector column
# -------------------------

if "Sector.1" in df.columns:
    sector_col = "Sector.1"

elif "Sector" in df.columns:
    sector_col = "Sector"

elif "Sector name" in df.columns:
    sector_col = "Sector name"

else:
    st.error("No sector column found.")
    st.stop()



# -------------------------
# Apply CRS filters
# -------------------------

data = df.copy()


# Only commitments

data = data[
    data["FLOW_TYPE"]
    .astype(str)
    .str.upper()
    .isin(
        [
            "C",
            "COMMITMENT"
        ]
    )
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



# -------------------------
# Sector grouping
# -------------------------

sector_mapping = {

    # Education
    "111": "Education",
    "112": "Education",

    # Health
    "121": "Health",
    "122": "Health",

    # Population
    "130": "Population Policies / Reproductive Health",

    # Water
    "140": "Water and Sanitation",

    # Governance
    "151": "Governance and Civil Society",
    "152": "Peace and Security",

    # Social infrastructure
    "160": "Other Social Infrastructure",


    # Infrastructure
    "210": "Transport and Storage",
    "220": "Communications",
    "230": "Energy",
    "240": "Banking and Financial Services",


    # Production
    "311": "Agriculture",
    "312": "Forestry",
    "313": "Fishing",

    "321": "Industry",
    "322": "Mineral Resources",
    "323": "Construction",

    "331": "Trade and Tourism",


    # Environment
    "410": "Environment",
    "430": "Other Multisector",


    # Humanitarian
    "720": "Humanitarian Assistance",
    "730": "Reconstruction and Rehabilitation"
}



def assign_sector_group(x):

    x = str(x)

    for prefix, group in sector_mapping.items():

        if x.startswith(prefix):
            return group

    return "Other"



data["Sector Group"] = (
    data["SECTOR"]
    .apply(assign_sector_group)
)



# Keep detailed subsector

data["Subsector"] = (
    data[sector_col]
    .fillna(data["SECTOR"])
)



# -------------------------
# Disability category
# -------------------------

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



data["Disability Category"] = (
    data["DISABILITY"]
    .apply(disability_category)
)



# -------------------------
# Sidebar filters
# -------------------------

st.sidebar.header("Filters")



# Recipient

recipient_options = sorted(
    data["Recipient"]
    .dropna()
    .unique()
)


recipient = st.sidebar.multiselect(
    "Recipient",
    recipient_options
)



# Donor

donor_options = sorted(
    data["Donor"]
    .dropna()
    .unique()
)


donor = st.sidebar.multiselect(
    "Donor",
    donor_options
)



# Sector Group

sector_group_options = sorted(
    data["Sector Group"]
    .dropna()
    .unique()
)


sector_group = st.sidebar.multiselect(
    "Sector Group",
    sector_group_options
)



# Dynamic subsector list

subsector_data = data.copy()


if sector_group:

    subsector_data = subsector_data[
        subsector_data["Sector Group"]
        .isin(sector_group)
    ]


subsector_options = sorted(
    subsector_data["Subsector"]
    .dropna()
    .unique()
)



subsector = st.sidebar.multiselect(
    "Subsector",
    subsector_options
)



# -------------------------
# Apply filters
# -------------------------

filtered = data.copy()



if recipient:

    filtered = filtered[
        filtered["Recipient"]
        .isin(recipient)
    ]



if donor:

    filtered = filtered[
        filtered["Donor"]
        .isin(donor)
    ]



if sector_group:

    filtered = filtered[
        filtered["Sector Group"]
        .isin(sector_group)
    ]



if subsector:

    filtered = filtered[
        filtered["Subsector"]
        .isin(subsector)
    ]



# -------------------------
# Results
# -------------------------

st.metric(
    "Total CRS commitments analysed",
    len(filtered)
)



# Disability marker table

result = (
    filtered["Disability Category"]
    .value_counts()
    .reset_index()
)


result.columns = [
    "Category",
    "Count"
]



if len(result) > 0:

    result["Percentage"] = (
        result["Count"]
        /
        result["Count"].sum()
        *
        100
    ).round(1)



    fig = px.bar(
        result,
        x="Category",
        y="Count",
        color="Category",
        text=result.apply(
            lambda r:
            f'{r["Count"]}<br>{r["Percentage"]}%',
            axis=1
        ),
        title="Disability Inclusion Marker"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )



    st.dataframe(
        result,
        hide_index=True
    )


else:

    st.warning(
        "No data available for selected filters."
    )
