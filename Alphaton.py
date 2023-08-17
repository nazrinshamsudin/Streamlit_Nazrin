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
selected_data = fetch_company_data(selected_tickers, period=selected_period)

spy_data = fetch_company_data("SPY", f"{selected_period}y")
spy_data = spy_data.resample('D').ffill()

# DISPLAY TABLE
st.subheader("SPY Stock data")
spy_data['Return'] = spy_data["Close"] - spy_data["Open"]
spy_data['Return%'] = (spy_data["Close"] - spy_data["Open"]) / spy_data['Open'] * 100
st.dataframe(spy_data)

dataframes = []

st.sidebar.header("Settings")
selected_period = st.sidebar.slider("Select Period (Years)", min_value=3, max_value=7, value=5)
selected_tickerlist = st.sidebar.multiselect("Select Tickers", sp500_tickers, ["AAPL", "MSFT", "AMZN", "GOOGL", "NVDA"])

if selected_tickerlist:
    selected_data = fetch_company_data(selected_tickerlist + ["SPY"], period=f"{selected_period}y")

if selected_data is not None:
    selected_data_returns = selected_data['Adj Close'].pct_change()
    selected_data_returns.dropna(inplace=True)  # Drop rows with NaN values

    correlation_matrix = selected_data_returns.corr()
    covariance_matrix = selected_data_returns.cov()

    benchmark_returns = selected_data_returns["SPY"]
    relative_returns = selected_data_returns.div(benchmark_returns, axis=0)


st.subheader("Selected Companies data")
st.dataframe(selected_data)


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

# Create the scatter plot using Plotly Go
scatter_fig = go.Figure()

# Adding scatter plot for selected companies
for ticker, covariance, correlation in zip(cov_corr_df["Ticker"], cov_corr_df["Covariance with SPY"], cov_corr_df["Correlation with SPY"]):
    scatter_fig.add_trace(go.Scatter(
        x=[correlation],
        y=[covariance],
        mode='markers',
        marker=dict(size=15),
        text=[f"{ticker} (Cov: {covariance:.2f}, Corr: {correlation:.2f})"],
        hoverinfo='text',
        name=ticker
    ))

# Adding a dark green and bigger dot for SPY as a benchmark
scatter_fig.add_trace(go.Scatter(
    x=[1.0],  # SPY correlation is always 1
    y=[covariance_matrix.loc["SPY", "SPY"]],  # SPY covariance with itself
    mode='markers',
    marker=dict(color="red", size=15),  # Dark green and bigger dot
    text=["SPY (Cov: Max, Corr: 1.00)"],
    hoverinfo='text',
    showlegend=False
))

# Update scatter plot layout
scatter_fig.update_layout(
    title="Covariance vs Correlation (Benchmark: SPY)",
    xaxis_title="Correlation with SPY",
    yaxis_title="Covariance with SPY",
    template="plotly_white"
)

# Display the scatter plot
st.plotly_chart(scatter_fig)
#In this version, I've added a loop to iterate through the selected tickers and added scatter plot dots for each ticker. The x-coordinate of each dot represents the correlation with SPY, and the y-coordinate represents the covariance with SPY. This configuration creates a scatter plot with each ticker's dot placed according to its correlation and covariance with SPY. The name parameter is set to the ticker's symbol for labeling each dot.
