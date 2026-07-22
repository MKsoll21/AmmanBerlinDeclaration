import streamlit as st
import pandas as pd
import plotly.express as px


# ---------------------------------------------------
# Page configuration
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
# Required columns
# ---------------------------------------------------

required_columns = [
    "FLOW_TYPE",
    "MODALITY",
    "SECTOR",
    "DISABILITY",
    "Recipient",
    "Donor"
]


missing = [
    col for col in required_columns
    if col not in df.columns
]


if missing:

    st.error(
        "Missing columns: "
        + ", ".join(missing)
    )

    st.stop()



# ---------------------------------------------------
# Detect sector name column
# ---------------------------------------------------

sector_candidates = [
    "Sector.1",
    "Sector",
    "Sector name"
]


sector_col = None


for col in sector_candidates:

    if col in df.columns:

        sector_col = col
        break



if sector_col is None:

    st.error(
        "No sector column found."
    )

    st.stop()



# ---------------------------------------------------
# CRS filters
# ---------------------------------------------------

data = df.copy()



# Commitments only

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



# Modalities

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


data["MODALITY"] = (
    data["MODALITY"]
    .astype(str)
    .str.upper()
)



data = data[
    data["MODALITY"]
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



# ---------------------------------------------------
# Sector grouping
# ---------------------------------------------------

sector_mapping = {


    "111": "Education",
    "112": "Education",


    "121": "Health",
    "122": "Health",


    "130": "Population Policies / Reproductive Health",


    "140": "Water and Sanitation",


    "151": "Governance and Civil Society",
    "152": "Peace and Security",


    "160": "Other Social Infrastructure",


    "210": "Transport and Storage",
    "220": "Communications",
    "230": "Energy",
    "240": "Banking and Financial Services",


    "311": "Agriculture",
    "312": "Forestry",
    "313": "Fishing",


    "321": "Industry",
    "322": "Mineral Resources",
    "323": "Construction",


    "331": "Trade and Tourism",


    "410": "Environment",
    "430": "Other Multisector",


    "720": "Humanitarian Assistance",
    "730": "Reconstruction and Rehabilitation"

}



def assign_sector_group(value):

    value = str(value)


    for prefix, name in sector_mapping.items():

        if value.startswith(prefix):

            return name


    return "Other"



data["Sector Group"] = (
    data["SECTOR"]
    .apply(assign_sector_group)
)



data["Subsector"] = (
    data[sector_col]
    .fillna(data["SECTOR"])
)
# ---------------------------------------------------
# Disability category
# ---------------------------------------------------

def disability_category(value):

    if pd.isna(value) or str(value).strip() == "":

        return "Not scored"


    try:

        value = int(value)

    except:

        return "Not scored"



    if value == 0:

        return "Scored - not targeted"



    if value in [1, 2]:

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

    "Jordan": "🇯🇴",
    "Lebanon": "🇱🇧",
    "Syrian Arab Republic": "🇸🇾",
    "Syria": "🇸🇾",
    "Iraq": "🇮🇶",
    "Egypt": "🇪🇬",
    "Türkiye": "🇹🇷",
    "Turkey": "🇹🇷",
    "Germany": "🇩🇪",
    "Ukraine": "🇺🇦",
    "Palestinian Adm. Areas": "🇵🇸",
    "West Bank and Gaza Strip": "🇵🇸",
    "Yemen": "🇾🇪",
    "Libya": "🇱🇾",
    "Tunisia": "🇹🇳",
    "Morocco": "🇲🇦",
    "Algeria": "🇩🇿"

}



# ---------------------------------------------------
# Sidebar filters
# ---------------------------------------------------

st.sidebar.header(
    "Filters"
)



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



# Subsector dynamic filter

subsector_source = data.copy()



if sector_group:

    subsector_source = subsector_source[
        subsector_source["Sector Group"]
        .isin(sector_group)
    ]



subsector_options = sorted(
    subsector_source["Subsector"]
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
        filtered["Recipient"].isin(recipient)
    ]


if donor:

    filtered = filtered[
        filtered["Donor"].isin(donor)
    ]


if sector_group:

    filtered = filtered[
        filtered["Sector Group"].isin(sector_group)
    ]


if subsector:

    filtered = filtered[
        filtered["Subsector"].isin(subsector)
    ]




# ---------------------------------------------------
# Country flag display
# ---------------------------------------------------

if len(recipient) == 1:

    selected_country = recipient[0]


    if selected_country in country_flags:

        st.subheader(
            f"{country_flags[selected_country]} "
            f"{selected_country}"
        )



# ---------------------------------------------------
# Metrics
# ---------------------------------------------------

total_records = len(filtered)



targeted_records = (
    filtered["Disability Category"]
    ==
    "Targeted"
).sum()



if total_records > 0:

    targeted_percentage = (
        targeted_records
        /
        total_records
        *
        100
    )

else:

    targeted_percentage = 0



col1, col2, col3 = st.columns(3)



with col1:

    st.metric(
        "CRS commitments analysed",
        total_records
    )



with col2:

    st.metric(
        "Targeted commitments",
        targeted_records
    )



with col3:

    st.metric(
        "Targeted share",
        f"{targeted_percentage:.1f}%"
    )



# ---------------------------------------------------
# Disability marker summary
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



result["Percentage"] = 0.0



if result["Count"].sum() > 0:

    result["Percentage"] = (
        result["Count"]
        /
        result["Count"].sum()
        *
        100
    ).round(1)

# ---------------------------------------------------
# Disability Inclusion Chart
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

            lambda row:
            f'{row["Count"]}<br>{row["Percentage"]}%',

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
