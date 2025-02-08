import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import re
import numpy as np
from langchain.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# ---------------------------
# Streamlit UI Setup
# ---------------------------
st.title("📈 Indian Stock Market Chatbot (NSE India)")
st.write("Ask about any NSE-listed stock or the best-performing stock over a specific time period.")

# ---------------------------
# Initialize Chat History
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []  # Stores chat messages

# ---------------------------
# Ollama + LangChain Setup
# ---------------------------
ollama_model = Ollama(model="phi:latest")

prompt_template = PromptTemplate(
    input_variables=["question"],
    template="You are an expert stock market assistant. Answer the following query:\n\n{question}"
)

llm_chain = LLMChain(llm=ollama_model, prompt=prompt_template)

# ---------------------------
# Predefined Stock Symbols
# ---------------------------
STOCK_SYMBOLS = {
    "TATA MOTORS": "TATAMOTORS.NS",
    "RELIANCE": "RELIANCE.NS",
    "INFOSYS": "INFY.NS",
    "TCS": "TCS.NS",
    "HDFC BANK": "HDFCBANK.NS",
    "ICICI BANK": "ICICIBANK.NS",
    "BAJAJ FINANCE": "BAJFINANCE.NS",
    "L&T": "LT.NS",
    "HINDUSTAN UNILEVER": "HINDUNILVR.NS",
    "WIPRO": "WIPRO.NS"
}

# ---------------------------
# Helper Functions
# ---------------------------
def correct_stock_symbol(stock_name):
    """
    Ensure the stock name is in the correct format.
    If a match exists in our dictionary, return it.
    Otherwise, remove spaces and append ".NS" for NSE.
    """
    stock_name = stock_name.upper().strip()
    return STOCK_SYMBOLS.get(stock_name, stock_name.replace(" ", "") + ".NS")

def get_stock_details(stock_name):
    """Fetch stock details from Yahoo Finance."""
    try:
        stock_symbol = correct_stock_symbol(stock_name)
        stock = yf.Ticker(stock_symbol)
        info = stock.info

        if not info or "longName" not in info:
            return {"error": f"Stock '{stock_name}' not found in NSE."}

        return {
            "Symbol": stock_symbol.replace(".NS", ""),
            "Company Name": info.get("longName", "N/A"),
            "Sector": info.get("sector", "N/A"),
            "Market Cap": f"{info.get('marketCap', 'N/A'):,}",
            "Previous Close": f"₹{info.get('previousClose', 'N/A')}",
            "52-Week High": f"₹{info.get('fiftyTwoWeekHigh', 'N/A')}",
            "52-Week Low": f"₹{info.get('fiftyTwoWeekLow', 'N/A')}",
            "Dividend Yield": f"{info.get('dividendYield', 'N/A')}%",
            "P/E Ratio": info.get("trailingPE", "N/A"),
        }
    except Exception as e:
        return {"error": f"Stock not found or API error: {e}"}

def get_stock_chart(stock_name, period="6mo"):
    """Fetch and plot stock price history."""
    try:
        stock_symbol = correct_stock_symbol(stock_name)
        stock = yf.Ticker(stock_symbol)
        hist = stock.history(period=period)

        if hist.empty:
            return f"No data available for {stock_symbol.replace('.NS', '')}."

        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name="Market Data"
        ))
        fig.update_layout(
            title=f"{stock_symbol.replace('.NS', '')} Stock Price - Last {period}",
            xaxis_title="Date",
            yaxis_title="Stock Price (INR)",
            xaxis_rangeslider_visible=False
        )
        return fig
    except Exception as e:
        return f"Error fetching stock chart: {e}"

def get_best_stock(timeframe="1mo"):
    """Identify the best-performing stock based on percentage change."""
    stocks = list(STOCK_SYMBOLS.keys())
    best_stock = None
    best_performance = -np.inf
    try:
        for stock in stocks:
            stock_symbol = correct_stock_symbol(stock)
            stock_data = yf.Ticker(stock_symbol)
            hist = stock_data.history(period=timeframe)
            if hist.empty or len(hist) < 2:
                continue
            performance = (hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]
            if performance > best_performance:
                best_performance = performance
                best_stock = stock
        return best_stock if best_stock else None
    except Exception as e:
        return f"Error fetching best stock: {e}"

def extract_timeframe(user_input):
    """Extract timeframe from user query."""
    match = re.search(r"(\d+)\s*(day|month|year|week)", user_input.lower())
    if match:
        number = int(match.group(1))
        unit = match.group(2)
        return f"{number}{'d' if unit == 'day' else 'mo' if unit == 'month' else 'y' if unit == 'year' else 'd'}"
    return "1mo"

# ---------------------------
# Chat History Display
# ---------------------------
with st.container():
    for message in st.session_state.messages:
        st.text_area(message["role"], message["content"], height=100, disabled=True)

# ---------------------------
# User Input Form
# ---------------------------
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Your question:")
    submit_button = st.form_submit_button("Send")

if submit_button and user_input:
    st.session_state.messages.append({"role": "User", "content": user_input})
    
    words = user_input.lower().split()
    
    if "best" in words and "stock" in words:
        timeframe = extract_timeframe(user_input)
        best_stock = get_best_stock(timeframe)
        if best_stock:
            bot_response = f"The best-performing stock in the last **{timeframe}** is: **{best_stock}**\n\n"
            stock_chart = get_stock_chart(best_stock, timeframe)
            stock_details = get_stock_details(best_stock)
            for key, value in stock_details.items():
                bot_response += f"**{key}:** {value}\n"
        else:
            bot_response = "Could not determine the best stock."
            stock_chart = None
    else:
        # Use LangChain LLM for answering stock-related questions
        ai_response = llm_chain.run(user_input)
        bot_response = f"🤖 **AI Insight:** {ai_response}\n\n"

        stock_name = user_input.split()[-1]
        stock_details = get_stock_details(stock_name)
        if "error" not in stock_details:
            bot_response += f"**Stock Details for {stock_details['Company Name']} ({stock_details['Symbol']})**\n\n"
            for key, value in stock_details.items():
                bot_response += f"**{key}:** {value}\n"
            stock_chart = get_stock_chart(stock_name)
        else:
            bot_response += stock_details["error"]
            stock_chart = None
    
    st.session_state.messages.append({"role": "Bot", "content": bot_response})
    
    with st.container():
        st.text_area("Bot", bot_response, height=150, disabled=True)
        if stock_chart and isinstance(stock_chart, go.Figure):
            st.plotly_chart(stock_chart)
