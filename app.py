import streamlit as st
import pandas as pd
import plotly.express as px
import flag

# ---------------------------------------------------
# Page config
# ---------------------------------------------------

st.set_page_config(
    page_title="Amman-Berlin Declaration",
    layout="wide"
)

st.title("Amman-Berlin Declaration")

st.caption(
    "OECD-DAC CRS analysis. Commitments only. "
    "Each CRS record counted individually."
)

# ---------------------------------------------------
# Load data
# ---------------------------------------------------

@st.cache_data
def load_data():
    return pd.read_csv(
        "oecd_data.csv",
        encoding="latin1"
    )

df = load_data()

# ---------------------------------------------------
# Check required columns
# ---------------------------------------------------

required = [
    "FLOW_TYPE",
    "MODALITY",
    "SECTOR",
    "DISABILITY",
    "Recipient",
    "Donor"
]

missing = [c for c in required if c not in df.columns]

if missing:
    st.error(f"Missing columns: {', '.join(missing)}")
    st.stop()

# ---------------------------------------------------
# Detect sector column
# ---------------------------------------------------

possible_sector_columns = [
    "Sector.1",
    "Sector",
    "Sector name"
]

sector_col = next(
    (c for c in possible_sector_columns if c in df.columns),
    None
)

if sector_col is None:
    st.error("No sector column found.")
    st.stop()

# ---------------------------------------------------
# Apply CRS filters
# ---------------------------------------------------

data = df.copy()

# Commitments only

data = data[
    data["FLOW_TYPE"]
    .astype(str)
    .str.upper()
    .isin([
        "C",
        "COMMITMENT"
    ])
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

modality = (
    data["MODALITY"]
    .astype(str)
    .str.upper()
)

data = data[
    modality.isin(allowed_modalities)
    | modality.str.startswith("B03")
]

# Excluded sectors

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

# ---------------------------------------------------
# Sector mapping
# ---------------------------------------------------

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

    # Social
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


def assign_sector_group(code):

    code = str(code)

    for prefix, group in sector_mapping.items():

        if code.startswith(prefix):
            return group

    return "Other"


data["Sector Group"] = (
    data["SECTOR"]
    .apply(assign_sector_group)
)

# Detailed subsector

data["Subsector"] = (
    data[sector_col]
    .fillna(data["SECTOR"])
)

# ---------------------------------------------------
# Disability category
# ---------------------------------------------------

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

# ---------------------------------------------------
# Country flags
# ---------------------------------------------------

country_flags = {

    "Jordan": "JO",
    "Lebanon": "LB",
    "Syrian Arab Republic": "SY",
    "Syria": "SY",
    "Iraq": "IQ",
    "Egypt": "EG",
    "Türkiye": "TR",
    "Turkey": "TR",
    "Germany": "DE",
    "Ukraine": "UA",
    "Palestinian Adm. Areas": "PS",
    "West Bank and Gaza Strip": "PS",
    "Yemen": "YE",
    "Libya": "LY",
    "Tunisia": "TN",
    "Morocco": "MA",
    "Algeria": "DZ"
}

# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------

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

# Dynamic subsectors

# Dynamic subsectors

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

    # ---------------------------------------------------
# Apply filters
# ---------------------------------------------------

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


# ---------------------------------------------------
# Display selected country flag
# ---------------------------------------------------

if len(recipient) == 1:

    selected_country = recipient[0]

    if selected_country in country_flags:

        st.subheader(
            f"{flag.flag(country_flags[selected_country])} "
            f"{selected_country}"
        )


# ---------------------------------------------------
# Metrics
# ---------------------------------------------------

total_commitments = len(filtered)

targeted_commitments = (
    filtered["Disability Category"]
    ==
    "Targeted"
).sum()


col1, col2, col3 = st.columns(3)


col1.metric(
    "CRS commitments analysed",
    total_commitments
)


col2.metric(
    "Targeted commitments",
    targeted_commitments
)


if total_commitments > 0:

    percentage = (
        targeted_commitments
        /
        total_commitments
        *
        100
    )

else:

    percentage = 0


col3.metric(
    "Targeted share",
    f"{percentage:.1f}%"
)


# ---------------------------------------------------
# Disability marker table
# ---------------------------------------------------

result = (
    filtered["Disability Category"]
    .value_counts()
    .reindex(
        [
            "Not scored",
            "Scored - not targeted",
            "Targeted"
        ],
        fill_value=0
    )
    .reset_index()
)


result.columns = [
    "Category",
    "Count"
]


if result["Count"].sum() > 0:

    result["Percentage"] = (
        result["Count"]
        /
        result["Count"].sum()
        *
        100
    ).round(1)

# ---------------------------------------------------
# Disability chart
# ---------------------------------------------------

if result["Count"].sum() > 0:

    fig = px.bar(
        result,
        x="Category",
        y="Count",
        color="Category",

        category_orders={
            "Category": [
                "Not scored",
                "Scored - not targeted",
                "Targeted"
            ]
        },

        text=result.apply(
            lambda r:
            f'{r["Count"]}<br>{r["Percentage"]}%',
            axis=1
        ),

        title="Disability Inclusion Marker",

        color_discrete_map={
            "Not scored": "#BDBDBD",
            "Scored - not targeted": "#4C78A8",
            "Targeted": "#2CA02C"
        }
    )


    fig.update_traces(
        textposition="outside"
    )


    fig.update_layout(

        showlegend=False,

        xaxis_title="",

        yaxis_title="Number of commitments",

        uniformtext_minsize=10,

        uniformtext_mode="hide"

    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # ---------------------------------------------------
    # Table
    # ---------------------------------------------------

    st.subheader(
        "Disability marker breakdown"
    )


    st.dataframe(
        result,
        hide_index=True,
        use_container_width=True
    )


    # ---------------------------------------------------
    # Download
    # ---------------------------------------------------

    st.download_button(

        label="Download filtered CRS data",

        data=filtered.to_csv(
            index=False
        ).encode("utf-8"),

        file_name="filtered_oecd_crs_data.csv",

        mime="text/csv"

    )


else:

    st.warning(
        "No data available for selected filters."
    )

