import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURATION & STYLE ---
st.set_page_config(
    page_title="Alpha Dashboard", 
    layout="wide", 
    page_icon="�️"
)

# Custom CSS for Minimalist interactions
st.markdown("""
<style>
    /* Minimalist header */
    .main > div {
        padding-top: 2rem;
    }
    h1 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        color: #FFFFFF;
    }
    h2, h3 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 300;
        color: #E0E0E0;
    }
    /* Metric Card Styling using Streamlit's native metrics but ensuring clean look */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
    }
    /* Remove default burger menu for cleaner look (optional) */
    /* #MainMenu {visibility: hidden;} */
    /* footer {visibility: hidden;} */
</style>
""", unsafe_allow_html=True)

# --- CHARTING THEME ---
def apply_chart_style(fig, title="", height=400):
    fig.update_layout(
        title={
            'text': title,
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20, 'family': "Helvetica Neue", 'color': "white"}
        },
        height=height,
        paper_bgcolor='rgba(0,0,0,0)', # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#B0B0B0"),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#333333', zeroline=False),
        margin=dict(l=40, r=40, t=50, b=40),
        hovermode="x unified"
    )
    return fig

# --- DATA LOADING ---
def load_csv(path):
    if os.path.exists(path):
        return pd.read_csv(path, index_col=0, parse_dates=True)
    return pd.DataFrame()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Navigate up from 'Dashboard' to 'Alpha_Dashboard'
ROOT_DIR = os.path.dirname(BASE_DIR)

P1_PATH = os.path.join(ROOT_DIR, "1_Carry_Trade/carry_trade_data.csv")
P2_PATH = os.path.join(ROOT_DIR, "2_Inflation_Shield/inflation_data.csv")
P3_PATH = os.path.join(ROOT_DIR, "3_Risk_Thermometer/risk_data.csv")
P4_PATH = os.path.join(ROOT_DIR, "4_Real_Economy/economy_data.csv")

# --- MAIN APP ---

st.title("🛡️ Alpha Dashboard")
st.caption("ECONOMIC INTELLIGENCE & MARKET SIGNALS")
st.markdown("---")

# Navigation
page = st.sidebar.radio("Navegación", ["Overview", "Carry Trade (Rates)", "Inflation Shield", "Risk Thermometer", "Real Economy"])

if page == "Overview":
    st.header("Executive Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Load all latest data for summary
    df1 = load_csv(P1_PATH)
    df2 = load_csv(P2_PATH)
    df3 = load_csv(P3_PATH)
    
    with col1:
        if not df1.empty:
            last = df1.iloc[-1]
            st.metric("Tasa 28d", f"{last.get('TIIE 28d', 0):.2f}%", help="Tasa de interés de referencia real")
            spread_status = "⚠️ Stress" if last.get('Liquidity Spread', 0) > 0.5 else "✅ Stable"
            st.caption(f"Liquidity: {spread_status}")
            
    with col2:
        if not df2.empty:
            last = df2.iloc[-1]
            st.metric("Inflación (Breakeven)", f"{last.get('Breakeven Inflation', 0):.2f}%", help="Expectativa a 10 años")
            
    with col3:
        if not df3.empty:
            last = df3.iloc[-1]
            st.metric("USD/MXN", f"${last.get('Tipo de Cambio FIX', 0):.2f}")
            
    with col4:
        st.metric("Status", "Risk ON" if (not df3.empty and df3.iloc[-1].get('Annualized Volatility (30d)', 10) < 15) else "Risk OFF")

    st.markdown("### 📡 Market Pulse")
    if not df3.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df3.index, y=df3['Tipo de Cambio FIX'], mode='lines', name='USD/MXN', line=dict(color='#00CC96', width=2)))
        fig = apply_chart_style(fig, "Tipo de Cambio (Trend)")
        st.plotly_chart(fig, use_container_width=True)

# --- PILLAR 1 ---
elif page == "Carry Trade (Rates)":
    st.markdown("## 💵 The Carry Trade Engine")
    df = load_csv(P1_PATH)
    
    if not df.empty:
        # Metrics Row
        col1, col2, col3 = st.columns(3)
        last = df.iloc[-1]
        
        col1.metric("Liquidity Spread", f"{last.get('Liquidity Spread', 0):.4f}", delta="vs Avg")
        col2.metric("Yield Curve Slope", f"{last.get('Yield Curve Slope', 0):.4f}", delta="Recession Signal" if last.get('Yield Curve Slope', 0) < 0 else "Normal")
        col3.metric("Carry Spread (vs FED)", f"{last.get('Carry Spread (bp)', 0):.0f} bp", help="Target > 400bp")

        # Charts
        tab_a, tab_b = st.tabs(["Spreads & Rates", "Yield Curve"])
        
        with tab_a:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['TIIE 28d'], name='TIIE 28d', line=dict(color='#636EFA')))
            if 'FED Rate (Proxy 13W)' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['FED Rate (Proxy 13W)'], name='FED Rate (Proxy)', line=dict(color='#EF553B', dash='dot')))
            fig = apply_chart_style(fig, "TIIE vs FED Rates")
            st.plotly_chart(fig, use_container_width=True)
            
            if 'Liquidity Spread' in df.columns:
                fig_spread = px.area(df, x=df.index, y='Liquidity Spread', title="Liquidity Stress")
                fig_spread.update_traces(line_color='#AB63FA', fillcolor='rgba(171,99,250,0.2)')
                fig_spread = apply_chart_style(fig_spread, "Liquidity Spread (TIIE - Fondeo)")
                fig_spread.add_hline(y=0.5, line_dash="drive", line_color="red")
                st.plotly_chart(fig_spread, use_container_width=True)

        with tab_b:
             if 'Yield Curve Slope' in df.columns:
                fig_curve = go.Figure()
                fig_curve.add_trace(go.Scatter(x=df.index, y=df['Yield Curve Slope'], fill='tozeroy', line=dict(color='#FFA15A')))
                fig_curve.add_hline(y=0, line_color="red", line_dash="dot")
                fig_curve = apply_chart_style(fig_curve, "Yield Curve Slope (364d - 28d)")
                st.plotly_chart(fig_curve, use_container_width=True)

# --- PILLAR 2 ---
elif page == "Inflation Shield":
    st.markdown("## 🔥 Inflation Shield (Real Rates)")
    df = load_csv(P2_PATH)
    
    if not df.empty:
        col1, col2 = st.columns(2)
        last = df.iloc[-1]
        
        col1.metric("UDI Value", f"{last.get('UDI', 0):.4f}")
        col2.metric("Breakeven Inflation (10y)", f"{last.get('Breakeven Inflation', 0):.2f}%")
        
        fig = go.Figure()
        if 'Breakeven Inflation' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['Breakeven Inflation'], name='Breakeven 10y', line=dict(color='#FF6692', width=2)))
            fig.add_hline(y=3.0, line_color="green", annotation_text="Banxico Target")
            fig = apply_chart_style(fig, "Inflation Expectations")
            st.plotly_chart(fig, use_container_width=True)
            
        if 'UDI Velocity (%)' in df.columns:
            st.subheader("UDI Velocity")
            df['Rolling Vel'] = df['UDI Velocity (%)'].rolling(7).mean()
            fig_vel = go.Figure()
            fig_vel.add_trace(go.Bar(x=df.index, y=df['UDI Velocity (%)'], name='Daily Change', marker_color='#19D3F3', opacity=0.3))
            fig_vel.add_trace(go.Scatter(x=df.index, y=df['Rolling Vel'], name='7d Avg', line=dict(color='#FFFFFF')))
            fig_vel = apply_chart_style(fig_vel, "UDI Velocity (Daily %)")
            st.plotly_chart(fig_vel, use_container_width=True)

# --- PILLAR 3 ---
elif page == "Risk Thermometer":
    st.markdown("## 🌡️ Risk Thermometer")
    df = load_csv(P3_PATH)
    
    if not df.empty:
        col1, col2 = st.columns(2)
        last = df.iloc[-1]
        
        col1.metric("USD/MXN", f"{last.get('Tipo de Cambio FIX', 0):.4f}")
        vol = last.get('Annualized Volatility (30d)', 0)
        col2.metric("Volatility (30d)", f"{vol:.2f}%", delta="Squeeze" if vol < 5 else "Normal")
        
        # Dual Axis Chart? Or two stacked
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Tipo de Cambio FIX'], name='USD/MXN', line=dict(color='#00CC96')))
        fig = apply_chart_style(fig, "Exchange Rate History")
        st.plotly_chart(fig, use_container_width=True)
        
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(x=df.index, y=df['Annualized Volatility (30d)'], name='Volatility', line=dict(color='#FECB52')))
        fig_vol.add_hline(y=5, line_color="green", line_dash="dash", annotation_text="Calma Chicha")
        fig_vol.add_hline(y=15, line_color="red", line_dash="dash", annotation_text="Stress")
        fig_vol = apply_chart_style(fig_vol, "Volatility Thermometer")
        st.plotly_chart(fig_vol, use_container_width=True)

# --- PILLAR 4 ---
elif page == "Real Economy":
    st.markdown("## 🏭 Real Economy Pulse")
    df = load_csv(P4_PATH)
    
    if not df.empty:
        last = df.iloc[-1]
        st.metric("Divergence (M1 - IPC)", f"{last.get('Divergence', 0):.2f}", help="Positive = Money Supply > Stocks Growth")
        
        fig = go.Figure()
        if 'M1 Normalized' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['M1 Normalized'], name='Liquidity (Base Monetaria)', line=dict(color='#636EFA')))

        if 'IPC Normalized' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['IPC Normalized'], name='IPC (Stocks)', line=dict(color='#00CC96')))
            
        fig = apply_chart_style(fig, "Money Supply vs Stock Market (Normalized Base 100)")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("Alpha Dashboard v2.0 | Automated Banxico & Market Data Pipeline")

