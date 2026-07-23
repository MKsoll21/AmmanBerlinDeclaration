import streamlit as st
import pandas as pd


# ---------------------------------------------------
# Page configuration
# ---------------------------------------------------

st.set_page_config(
    page_title="Data Explorer - Amman Berlin Declaration",
    layout="wide"
)


st.title("📊 Amman-Berlin Declaration - Data Explorer")

st.caption(
    "Top rankings based on filtered OECD-DAC CRS commitments. "
    "Each CRS record counted individually."
)


# ---------------------------------------------------
# Load data
# ---------------------------------------------------

@st.cache_data
def load_data():

    return pd.read_csv(
        "oecd_data.csv",
        encoding="utf-8-sig"
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
# Sector name column
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
# Clean data
# ---------------------------------------------------

data = df.copy()


for col in ["Recipient", "Donor"]:

    data[col] = (
        data[col]
        .astype(str)
        .str.strip()
        .str.replace(
            "Ã¼",
            "ü",
            regex=False
        )
    )


name_mapping = {

    "TÃ¼rkiye": "Türkiye",
    "Turkey": "Türkiye",

    "Palestinian Authority or West Bank and Gaza Strip": "Palestine",
    "West Bank and Gaza Strip": "Palestine",
    "Palestinian Territories": "Palestine",
    "Palestinian Adm. Areas": "Palestine"

}


data["Recipient"] = (
    data["Recipient"]
    .replace(name_mapping)
)


data["Donor"] = (
    data["Donor"]
    .replace(name_mapping)
)



# ---------------------------------------------------
# Commitments only
# ---------------------------------------------------

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


# ---------------------------------------------------
# Modalities
# ---------------------------------------------------

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


# ---------------------------------------------------
# Sector groups
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
# Sidebar filters
# ---------------------------------------------------

st.sidebar.header(
    "Filters"
)


# ---------------------------------------------------
# Amman-Berlin Declaration quick filters
# ---------------------------------------------------

amman_berlin_recipient_endorsers = [

    "Algeria",
    "Egypt",
    "Germany",
    "Iraq",
    "Jordan",
    "Lebanon",
    "Morocco",
    "Palestine",
    "Türkiye",
    "Ukraine",
    "United Kingdom"

]


amman_berlin_donor_endorsers = [

    "Australia",
    "Canada",
    "Denmark",
    "France",
    "Germany",
    "Japan",
    "Netherlands",
    "Norway",
    "Qatar",
    "Sweden",
    "Türkiye",
    "United Kingdom",
    "United States",

    "EU Institutions",

    "United Nations Development Programme [UNDP]",

    "United Nations Children's Fund [UNICEF]",

    "United Nations High Commissioner for Refugees [UNHCR]",

    "World Health Organisation [WHO]"

]



endorsing_recipients = st.sidebar.checkbox(
    "Only Amman-Berlin Declaration Recipients"
)


endorsing_donors = st.sidebar.checkbox(
    "Only Amman-Berlin Declaration Donors"
)



# ---------------------------------------------------
# Recipient filter
# ---------------------------------------------------

recipient_options = sorted(
    data["Recipient"]
    .dropna()
    .unique()
)


if endorsing_recipients:

    recipient_default = [

        x for x in recipient_options

        if x in amman_berlin_recipient_endorsers

    ]

else:

    recipient_default = []



recipient = st.sidebar.multiselect(
    "Recipient",
    recipient_options,
    default=recipient_default
)



# ---------------------------------------------------
# Donor filter
# ---------------------------------------------------

donor_options = sorted(
    data["Donor"]
    .dropna()
    .unique()
)



if endorsing_donors:

    donor_default = [

        x for x in donor_options

        if x in amman_berlin_donor_endorsers

    ]

else:

    donor_default = []



donor = st.sidebar.multiselect(
    "Donor",
    donor_options,
    default=donor_default
)



# ---------------------------------------------------
# Sector Group filter
# ---------------------------------------------------

sector_options = sorted(
    data["Sector Group"]
    .dropna()
    .unique()
)


sector_group = st.sidebar.multiselect(
    "Sector Group",
    sector_options
)



# ---------------------------------------------------
# Dynamic subsector filter
# ---------------------------------------------------

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
# Filter summary
# ---------------------------------------------------

st.sidebar.divider()

st.sidebar.metric(
    "Filtered commitments",
    len(filtered)
)

# ---------------------------------------------------
# Ranking functions
# ---------------------------------------------------

def create_ranking(df, group_column):

    table = (
        df
        .groupby(group_column)
        .agg(
            Commitments=(group_column, "size"),
            Targeted=(
                "Disability Category",
                lambda x: (
                    x == "Targeted"
                ).sum()
            )
        )
    )


    table["Targeted %"] = (
        table["Targeted"]
        /
        table["Commitments"]
        *
        100
    ).round(1)


    table = (
        table
        .sort_values(
            "Commitments",
            ascending=False
        )
        .head(15)
        .reset_index()
    )


    return table



def create_pair_ranking(
    df,
    columns
):

    table = (
        df
        .groupby(columns)
        .size()
        .reset_index(
            name="Commitments"
        )
        .sort_values(
            "Commitments",
            ascending=False
        )
        .head(15)
    )


    return table



# ---------------------------------------------------
# Create tables
# ---------------------------------------------------

donor_table = create_ranking(
    filtered,
    "Donor"
)



recipient_table = create_ranking(
    filtered,
    "Recipient"
)



sector_table = create_ranking(
    filtered,
    "Sector Group"
)



subsector_table = create_ranking(
    filtered,
    "Subsector"
)



donor_recipient_table = create_pair_ranking(
    filtered,
    [
        "Donor",
        "Recipient"
    ]
)



donor_sector_table = create_pair_ranking(
    filtered,
    [
        "Donor",
        "Sector Group"
    ]
)



recipient_sector_table = create_pair_ranking(
    filtered,
    [
        "Recipient",
        "Sector Group"
    ]
)



# ---------------------------------------------------
# Formatting helper
# ---------------------------------------------------

def style_table(df):

    return df

# ---------------------------------------------------
# Display tables
# ---------------------------------------------------

st.divider()

st.subheader(
    "📊 Rankings"
)


tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🌍 Donors",
        "🏛 Recipients",
        "📚 Sectors",
        "🔗 Networks"
    ]
)



# ---------------------------------------------------
# Donors
# ---------------------------------------------------

with tab1:

    st.markdown(
        "### Top 15 Donors"
    )

    st.caption(
        "Ranked by number of CRS commitments"
    )


    st.dataframe(
        style_table(donor_table),
        use_container_width=True,
        hide_index=True
    )


    st.download_button(

        label="⬇️ Download Donor Ranking",

        data=donor_table.to_csv(
            index=False
        ).encode("utf-8"),

        file_name=
        "top15_donors.csv",

        mime="text/csv"

    )



# ---------------------------------------------------
# Recipients
# ---------------------------------------------------

with tab2:

    st.markdown(
        "### Top 15 Recipients"
    )


    st.dataframe(

        style_table(recipient_table),

        use_container_width=True,

        hide_index=True

    )


    st.download_button(

        label="⬇️ Download Recipient Ranking",

        data=recipient_table.to_csv(
            index=False
        ).encode("utf-8"),

        file_name=
        "top15_recipients.csv",

        mime="text/csv"

    )



# ---------------------------------------------------
# Sectors
# ---------------------------------------------------

with tab3:

    st.markdown(
        "### Top 15 Sector Groups"
    )


    st.dataframe(

        style_table(sector_table),

        use_container_width=True,

        hide_index=True

    )


    st.markdown(
        "### Top 15 Subsectors"
    )


    st.dataframe(

        style_table(subsector_table),

        use_container_width=True,

        hide_index=True

    )


    col1, col2 = st.columns(2)


    with col1:

        st.download_button(

            label="⬇️ Download Sector Ranking",

            data=sector_table.to_csv(
                index=False
            ).encode("utf-8"),

            file_name=
            "top15_sector_groups.csv",

            mime="text/csv"

        )


    with col2:

        st.download_button(

            label="⬇️ Download Subsector Ranking",

            data=subsector_table.to_csv(
                index=False
            ).encode("utf-8"),

            file_name=
            "top15_subsectors.csv",

            mime="text/csv"

        )



# ---------------------------------------------------
# Networks
# ---------------------------------------------------

with tab4:

    st.markdown(
        "### Top 15 Donor - Recipient Relationships"
    )


    st.dataframe(

        donor_recipient_table,

        use_container_width=True,

        hide_index=True

    )


    st.markdown(
        "### Top 15 Donor - Sector Relationships"
    )


    st.dataframe(

        donor_sector_table,

        use_container_width=True,

        hide_index=True

    )


    st.markdown(
        "### Top 15 Recipient - Sector Relationships"
    )


    st.dataframe(

        recipient_sector_table,

        use_container_width=True,

        hide_index=True

    )


    st.download_button(

        label="⬇️ Download Network Tables",

        data=donor_recipient_table.to_csv(
            index=False
        ).encode("utf-8"),

        file_name=
        "top15_networks.csv",

        mime="text/csv"

    )


