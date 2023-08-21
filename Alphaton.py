import os
import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import wikipedia

st.title("Financial Analysis Dashboard")
st.write("This is the work of Nazrin Shamsudin, do enjoy the analysis of stocks prices.🙂")



# FETCHING DATA AND DECLARING VARIABLE OF DATA
def fetch_company_data(tickers, period):
    print(tickers, "str")
    
    try:
         data = yf.download(tickers, period=period, interval="1d", rounding=True, threads=True)
         return data
    except KeyError:
        print(f"No data found for tickers: {tickers}")
        return None

sp500_table = wikipedia.page("List_of_S%26P_500_companies").html().encode("UTF-8")
sp500_tickers = pd.read_html(sp500_table)[0]["Symbol"].tolist()

selected_tickers = ["AAPL", "MSFT", "AMZN", "GOOGL", "NVDA"]
selected_period = '1y'

selected_tickers.append("SPY")
spy_data = fetch_company_data("SPY", f"{selected_period}y")




# spy_data['Return'] = spy_data["Close"] - spy_data["Open"]
# spy_data['Return%'] = (spy_data["Close"] - spy_data["Open"]) / spy_data['Open'] * 100
# dataframes = []


# FETCHING DATA AND DECLARING VARIABLE OF DATA
def fetch_company_data(tickers, period):
    try:
        data = yf.download(tickers, period=period, interval="1d", rounding=True, threads=True)
        return data
    except KeyError:
        print(f"No data found for tickers: {tickers}")
        return None

# Load S&P 500 tickers
sp500_table = wikipedia.page("List_of_S%26P_500_companies").html().encode("UTF-8")
sp500_tickers = pd.read_html(sp500_table)[0]["Symbol"].tolist()



# Sidebar Settings
st.sidebar.header("Settings")
selected_period = st.sidebar.slider("Select Period (Years)", min_value=1, max_value=7, value=5)
selected_tickerlist = st.sidebar.multiselect("Select Tickers", sp500_tickers, ["AAPL", "MSFT", "AMZN", "GOOGL","META", "NVDA", "TSLA"])
selected_start_date = st.sidebar.date_input("Select Start Date", pd.to_datetime('today') - pd.DateOffset(years=selected_period))

# Display selected start date in the sidebar
if selected_start_date:
    st.sidebar.write(f"Selected Start Date: {selected_start_date}")



# Append "SPY" to the selected_tickerlist
if "SPY" not in selected_tickerlist:
    selected_tickerlist.append("SPY")

if selected_tickerlist:
    # Fetch and display SPY data separately
    spy_data = fetch_company_data("SPY", period=f"{selected_period}y")
    # Fetch and display SPY data separately
    # start_date_str = selected_start_date.strftime("%Y-%m-%d")
    # today_str = pd.to_datetime('today').date().strftime("%Y-%m-%d")
    # spy_data = fetch_company_data("SPY", period=f"{start_date_str} - {today_str}")

    if spy_data is not None:
        st.subheader("SPY Stock data")
        spy_data['Return'] = spy_data["Close"] - spy_data["Open"]
        spy_data['Return%'] = (spy_data["Close"] - spy_data["Open"]) / spy_data['Open'] * 100
        st.dataframe(spy_data)


        # Calculate the covariance of SPY
        spy_covariance = spy_data['Return'].cov(spy_data['Return'])


    # Fetch and display selected companies data
    selected_data = fetch_company_data(selected_tickerlist, period=f"{selected_period}y")
    if selected_data is not None:
        st.subheader("Selected Companies data")
        st.dataframe(selected_data)

        print('spy_covariance:', spy_covariance)


# Calculate correlation adn covariance_matrix and other necessary data
if selected_data is not None:
    selected_data_returns = selected_data['Adj Close'].pct_change()
    selected_data_returns.dropna(inplace=True)
    
    # Calculate correlation_matrix and covariance_matrix
    correlation_matrix = selected_data_returns.corr()
    covariance_matrix = selected_data_returns.cov()






# Create a correlation heatmap
st.subheader("Correlation Table")
st.dataframe(correlation_matrix.style.background_gradient(cmap='coolwarm'))

# Create a covariance heatmap
st.subheader("Covariance Table")
st.dataframe(covariance_matrix.style.background_gradient(cmap='coolwarm'))








# Create a DataFrame for covariance and correlation data
cov_corr_data = []
for ticker in selected_tickerlist:
    correlation = correlation_matrix.loc[ticker, "SPY"]
    covariance = covariance_matrix.loc[ticker, "SPY"]
    cov_corr_data.append({"Ticker": ticker, "Covariance with SPY": covariance, "Correlation with SPY": correlation})

cov_corr_df = pd.DataFrame(cov_corr_data)





# Sort the DataFrame in ascending order of Covariance with SPY
sorted_cov_corr_df = cov_corr_df.sort_values(by='Covariance with SPY', ascending=True)
sorted_cov_cor_df = cov_corr_df.sort_values(by='Correlation with SPY', ascending=True)



# Display the sorted DataFrame in a table with numbered index
#sorted_cov_corr_df['New data'] = sorted_cov_corr_df['Covariance with SPY'] / 0.000182

# sorted_cov_corr_df['New data2'] = sorted_cov_corr_df['Correlation with SPY'] /0.000182
# print(sorted_cov_corr_df)
# #New_data = 



sorted_cov_corr_df.reset_index(drop=True, inplace=True)
sorted_cov_corr_df.index = sorted_cov_corr_df.index + 1
st.subheader("Top 10 Tickers with Correlation and Covariance")
st.table(sorted_cov_corr_df[['Ticker', 'Correlation with SPY', 'Covariance with SPY']].head(10))




#SPY only data
sorted_cov_corr_df['Scaled Covariance'] = sorted_cov_cor_df['Covariance with SPY'] / 0.000182

#Calculate the new scale value of covariance
# sorted_cov_corr_df['Scaled Covariance'] = sorted_cov_corr_df['Covariance with SPY'] / 0.000182
# print(sorted_cov_corr_df)



# Create the scatter plot using Plotly Go
scatter_fig = go.Figure()



# Adding scatter plot for selected companies
for ticker, scaled_covariance, correlation in zip(cov_corr_df["Ticker"], sorted_cov_corr_df["Scaled Covariance"], cov_corr_df["Correlation with SPY"]):
    scatter_fig.add_trace(go.Scatter(
        x=[correlation],
        y=[scaled_covariance],
        mode='markers',
        marker=dict(size=15),
        text=[f"{ticker} (Cov: {scaled_covariance:.2f}, Corr: {correlation:.2f})"],
        hoverinfo='text',
        name=ticker
    ))

   # Add annotation to display ticker name
    scatter_fig.add_annotation(
        x=correlation,
        y=scaled_covariance,
        xshift=-24,  # Shift the text to the left
        text=ticker,
        showarrow=False
    )

# Add a text annotation to display the selected start date
if isinstance(selected_start_date, pd.Timestamp):
    scatter_fig.add_annotation(
        x=0.1,  # Adjust the x-coordinate to position the text
        y=0.9,  # Adjust the y-coordinate to position the text
        text=f"Selected Start Date: {selected_start_date.date()}",
        showarrow=False
    )

# Adding a green and bigger dot for SPY as a benchmark
# scatter_fig.add_trace(go.Scatter(
#     x=[1.0],  # SPY correlation is always 1
#     y=[scaled_covariance_matrix.loc["SPY", "SPY"]],  # SPY covariance with itself
#     mode='markers',
#     marker=dict(color="lightgreen", size=21),  # Dark green and bigger dot
#     text=["SPY (Cov: Max, Corr: 1.00)"],
#     hoverinfo='text',
#     showlegend=False
# ))

# Update scatter plot layout
scatter_fig.update_layout(
    title="Covariance vs Correlation (SPY as a Benchmark)",
    xaxis_title="Correlation",
    yaxis_title="Covariance",
    template="plotly_white",
    # width = 700, # set widdth and height accord to specifics pixels
    # height=600

)



# Display the scatter plot
st.plotly_chart(scatter_fig)
#In this version, I've added a loop to iterate through the selected tickers and added scatter plot dots for each ticker. The x-coordinate of each dot represents the correlation with SPY, and the y-coordinate represents the covariance with SPY. This configuration creates a scatter plot with each ticker's dot placed according to its correlation and covariance with SPY. The name parameter is set to the ticker's symbol for labeling each dot.
