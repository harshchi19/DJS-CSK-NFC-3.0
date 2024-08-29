# Import necessary libraries
import yfinance as yf
from transformers import pipeline
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF

# Function to get stock data using yfinance
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    # Fetch financial data
    financials = stock.financials
    balance_sheet = stock.balance_sheet

    # Get net income, revenue, and average equity
    try:
        net_income = financials.loc['Net Income'].values[0]
        revenue = financials.loc['Total Revenue'].values[0]
        avg_equity = (balance_sheet.loc['Total Stockholder Equity'].values[0] + balance_sheet.loc['Total Stockholder Equity'].values[1]) / 2
    except KeyError:
        st.error("Failed to fetch financial data. Please check if the ticker is correct.")
        return None, None, None

    return net_income, revenue, avg_equity

# Function to perform DuPont analysis
def calculate_dupont_analysis(net_income, revenue, avg_equity):
    # Calculate the three components of DuPont Analysis
    profit_margin = net_income / revenue
    asset_turnover = revenue / avg_equity
    equity_multiplier = avg_equity / (avg_equity - net_income)  # A simplified assumption for illustration purposes

    # Calculate ROE
    roe = profit_margin * asset_turnover * equity_multiplier

    # Create a summary dictionary
    summary = {
        "Net Income": net_income,
        "Revenue": revenue,
        "Average Equity": avg_equity,
        "Profit Margin": profit_margin,
        "Asset Turnover": asset_turnover,
        "Equity Multiplier": equity_multiplier,
        "Return on Equity (ROE)": roe
    }
    return summary

# Function to scrape web data using HuggingFace model
def scrape_data(ticker):
    # Use a summarization pipeline from HuggingFace to scrape and summarize web data
    summarizer = pipeline("summarization")
    # Assume `scrape_web_for_stock_info` is a function that fetches web data based on the stock ticker
    web_data = f"News and insights related to {ticker} stock..."
    summary = summarizer(web_data, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
    return summary

# Function to create PDF report
def create_pdf_report(summary, ticker, web_summary):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"DuPont Analysis Report for {ticker}", ln=True, align='C')

    pdf.set_font("Arial", size=12)
    for key, value in summary.items():
        pdf.cell(200, 10, f"{key}: {value:.2f}", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "Web Insights:", ln=True)
    
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, web_summary)
    
    pdf_file_name = f"{ticker}_dupont_report.pdf"
    pdf.output(pdf_file_name)
    return pdf_file_name

# Streamlit interface
st.title("DuPont Analysis for Stock Ticker")
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, MSFT):")

if ticker:
    net_income, revenue, avg_equity = get_stock_data(ticker)
    
    if net_income and revenue and avg_equity:
        dupont_summary = calculate_dupont_analysis(net_income, revenue, avg_equity)
        web_summary = scrape_data(ticker)
        
        st.write("### DuPont Analysis Summary")
        st.write(pd.DataFrame(dupont_summary.items(), columns=["Metric", "Value"]))

        # Create and download the PDF report
        if st.button("Generate PDF Report"):
            pdf_file = create_pdf_report(dupont_summary, ticker, web_summary)
            with open(pdf_file, "rb") as file:
                btn = st.download_button(label="Download PDF Report", data=file, file_name=pdf_file, mime="application/pdf")

        st.write("### Web Insights")
        st.write(web_summary)
    else:
        st.error("Failed to retrieve financial data. Please check the ticker symbol.")
