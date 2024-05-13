import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Global Superstores EDA!", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: Global Superstores Exploratory Analysis")
st.markdown("<style>div.block-container{padding-top:1rem;}</style>",unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file",type=(["csv","txt","xls","xlsx"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_excel(filename)
else:
    os.chdir(r"/Users/juanitanelson-addy/OneDrive/VS CODE/CODING PROJECTS")
    df = pd.read_excel("Global Superstore 2018.xls")

col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

#Getting min & max date
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))


#Creating filters
#Region
st.sidebar.header("Filtered Search ")
region = st.sidebar.multiselect("Choose a region: ", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

#Country
country = st.sidebar.multiselect("Choose a country: ", df["Country"].unique())
if not country:
    df3 = df2.copy()
else:
    df3 = df[df["Country"].isin(country)]


#City
city = st.sidebar.multiselect("Choose a city: ", df["City"].unique())
if not city:
    df4 = df3.copy()
else:
    df4 = df[df["City"].isin(city)]


#Filter data based on region, country & city
if not region and not country and not city:
    filtered_df = df
elif not country and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["Country"].isin(country)]
elif not region and country:
    filtered_df = df[df["City"].isin(city)]
elif region and country:
    filtered_df = df3[df3["Region"].isin(region) & df3["Country"].isin(country)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif country and city:
    filtered_df = df3[df["Country"].isin(country) & df3["City"].isin(city)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["Country"].isin(country) & df3["City"].isin(city)]


category_df = filtered_df.groupby(by = ["Category"], as_index=False)["Sales"].sum()

with col1:
    st.subheader("Sales by Category")
    fig = px.bar(category_df, x = "Category", y = "Sales", template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

with col2:
    st.subheader("Sales by Market")
    fig = px.pie(filtered_df, values = "Sales", names = "Market", hole = 0.5)
    fig.update_traces(text = filtered_df["Market"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)
    

cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("View Category Data"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
                            help = "Click here to download the data as a CSV file")
    
with cl2:
    with st.expander("View Market Data"):
        market = filtered_df.groupby(by="Market", as_index=False)["Sales"].sum()
        st.write(category_df.style.background_gradient(cmap="Greens"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Market.csv", mime = "text/csv",
                            help = "Click here to download the data as a CSV file")
    

filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader("Time Series Analysis")

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y = "Sales", labels = {"Sales": "Amount"}, height = 500, width = 1000, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of Time Series"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8)")
    st.download_button("Download Data", data = csv, file_name = "TimeSeries.csv", mime = "text/csv")


#Creating Tree Maps -> market, catgeory & sub-category
st.subheader("Hierarchal View of Sales")
fig3 = px.treemap(filtered_df, path = ["Market", "Category", "Sub-Category"], values = "Sales", hover_data = ["Sales"],
                  color="Sub-Category")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns(2)
with chart1:
    st.subheader("Sales by Segment")
    fig = px.pie(filtered_df, values = "Sales", names = "Segment", template = "plotly_dark")
    fig.update_traces(text = filtered_df["Segment"], textposition = "inside")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader("Sales by Category")
    fig = px.pie(filtered_df, values = "Sales", names = "Category", template = "gridon")
    fig.update_traces(text = filtered_df["Category"], textposition = "inside")
    st.plotly_chart(fig, use_container_width=True)


import plotly.figure_factory as ff
st.subheader(":point_right: Summary of Sub-Category Sales by Month")
with st.expander("Summary Table"):
    df_sample = df[0:5][["Market", "Region", "Country", "Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale="Mint")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month based Sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data=filtered_df, values="Sales", index = ["Sub-Category"], columns="month")
    st.write(sub_category_Year.style.background_gradient(cmap="Purples"))


#Creating a scatter plot
data1 = px.scatter(filtered_df, x = "Sales", y = "Profit", size = "Quantity")
data1["layout"].update(title="Relationship between Sales & Profit", titlefont = dict(size=20), xaxis = dict(title="Sales", titlefont = dict(size=19)),
                       yaxis = dict(title = "Profit", titlefont = dict(size=19)))
st.plotly_chart(data1, use_container_width=True)


with st.expander("View Dataset"):
    st.write(filtered_df.iloc[:500,1:25].style.background_gradient(cmap="Blues"))


#Download OG dataset
csv = df.to_csv(index = False).encode("utf-8")
st.download_button("Download Data", data = csv, file_name = "Data.csv", mime = "text/csv")
