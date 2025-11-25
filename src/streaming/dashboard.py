import streamlit as st
import pymongo
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# MongoDB connection
@st.cache_resource
def get_mongo_connection():
    client = pymongo.MongoClient("mongodb://mongodb:27017/")
    db = client["dataco"]
    return db

st.set_page_config(page_title="Supply Chain Dashboard", layout="wide")

st.title("📊 Supply Chain Real-Time Analytics Dashboard")
st.markdown("---")

# Connect to MongoDB
db = get_mongo_connection()
collection = db["predictions"]

# Refresh button
if st.button("🔄 Refresh Data"):
    st.cache_resource.clear()

# Fetch data from MongoDB
@st.cache_data(ttl=10)
def load_data():
    data = list(collection.find().sort("window_start", -1).limit(1000))
    if data:
        df = pd.DataFrame(data)
        if 'window_start' in df.columns:
            df['window_start'] = pd.to_datetime(df['window_start'])
        if 'window_end' in df.columns:
            df['window_end'] = pd.to_datetime(df['window_end'])
        return df
    return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("⚠️ No data available yet. Waiting for streaming data...")
    st.info("Make sure the streaming pipeline is running.")
else:
    st.success(f"✅ Loaded {len(df)} records from MongoDB")
    
    # Key Metrics
    st.header("📈 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_orders = df['total_orders'].sum()
        st.metric("Total Orders", f"{int(total_orders):,}")
    
    with col2:
        total_sales = df['total_sales'].sum()
        st.metric("Total Sales", f"${total_sales:,.2f}")
    
    with col3:
        total_profit = df['total_profit'].sum()
        st.metric("Total Profit", f"${total_profit:,.2f}")
    
    with col4:
        late_deliveries = df['predicted_late_deliveries'].sum()
        st.metric("Predicted Late Deliveries", f"{int(late_deliveries):,}")
    
    st.markdown("---")
    
    # Time series - Sales over time
    st.header("📊 Sales Trends Over Time")
    if 'window_start' in df.columns:
        time_df = df.groupby('window_start').agg({
            'total_sales': 'sum',
            'total_profit': 'sum',
            'total_orders': 'sum'
        }).reset_index()
        
        fig_time = go.Figure()
        fig_time.add_trace(go.Scatter(
            x=time_df['window_start'], 
            y=time_df['total_sales'],
            mode='lines+markers',
            name='Sales',
            line=dict(color='blue', width=2)
        ))
        fig_time.update_layout(
            xaxis_title="Time Window",
            yaxis_title="Total Sales ($)",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig_time, use_container_width=True)
    
    # Region analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("🌍 Sales by Region")
        region_df = df.groupby('Order Region').agg({
            'total_sales': 'sum',
            'total_orders': 'sum'
        }).reset_index()
        
        fig_region = px.bar(
            region_df, 
            x='Order Region', 
            y='total_sales',
            color='total_sales',
            color_continuous_scale='Blues',
            text='total_sales'
        )
        fig_region.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_region.update_layout(height=400)
        st.plotly_chart(fig_region, use_container_width=True)
    
    with col2:
        st.header("📦 Orders by Category")
        category_df = df.groupby('Category Name').agg({
            'total_orders': 'sum'
        }).reset_index()
        
        fig_category = px.pie(
            category_df,
            values='total_orders',
            names='Category Name',
            hole=0.4
        )
        fig_category.update_layout(height=400)
        st.plotly_chart(fig_category, use_container_width=True)
    
    st.markdown("---")
    
    # Profit analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("💰 Profit by Region")
        profit_region = df.groupby('Order Region')['total_profit'].sum().reset_index()
        
        fig_profit = px.bar(
            profit_region,
            x='Order Region',
            y='total_profit',
            color='total_profit',
            color_continuous_scale='Greens'
        )
        fig_profit.update_layout(height=400)
        st.plotly_chart(fig_profit, use_container_width=True)
    
    with col2:
        st.header("⚠️ Late Delivery Predictions")
        late_df = df.groupby('Order Region')['predicted_late_deliveries'].sum().reset_index()
        
        fig_late = px.bar(
            late_df,
            x='Order Region',
            y='predicted_late_deliveries',
            color='predicted_late_deliveries',
            color_continuous_scale='Reds'
        )
        fig_late.update_layout(height=400)
        st.plotly_chart(fig_late, use_container_width=True)
    
    # Shipping performance
    st.header("🚚 Shipping Performance")
    if 'avg_distance' in df.columns:
        shipping_df = df.groupby('Order Region')['avg_distance'].mean().reset_index()
        
        fig_shipping = px.bar(
            shipping_df,
            x='Order Region',
            y='avg_distance',
            color='avg_distance',
            color_continuous_scale='Oranges',
            text='avg_distance'
        )
        fig_shipping.update_traces(texttemplate='%{text:.1f} km', textposition='outside')
        fig_shipping.update_layout(
            yaxis_title="Average Distance (km)",
            height=400
        )
        st.plotly_chart(fig_shipping, use_container_width=True)
    
    # Raw data table
    st.markdown("---")
    st.header("📋 Recent Aggregated Data")
    
    display_df = df.copy()
    if '_id' in display_df.columns:
        display_df = display_df.drop('_id', axis=1)
    
    # Format numeric columns
    numeric_cols = display_df.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_cols:
        if 'sales' in col.lower() or 'profit' in col.lower():
            display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}")
        else:
            display_df[col] = display_df[col].apply(lambda x: f"{x:,.2f}")
    
    st.dataframe(display_df.head(20), use_container_width=True)

# Footer
st.markdown("---")
st.markdown("**Last updated:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
