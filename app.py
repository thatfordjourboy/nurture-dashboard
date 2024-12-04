import streamlit as st
import pandas as pd
import altair as alt

# Set page configuration to light theme
st.set_page_config(page_title="Sales Analysis Dashboard", layout="wide", initial_sidebar_state="expanded")

# Set the theme to light mode
st.markdown(
    """
    <style>
    .css-1d391kg {
        background-color: #ffffff; /* Light background */
        color: #000000; /* Dark text */
    }
    .card-container {
        display: flex; /* Use flexbox */
        justify-content: space-around; /* Distribute cards evenly */
        flex-wrap: wrap; /* Allow wrapping */
        margin-top: 20px; /* Add space above */
    }
    .card {
        background: linear-gradient(135deg, #36d1dc 0%, #5b86e5 100%);
        color: #ffffff; /* Ensure text color is white */
        border: none; /* Remove border */
        border-radius: 12px; /* Rounded corners */
        padding: 20px;
        margin: 10px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); /* Subtle shadow */
        transition: transform 0.3s, box-shadow 0.3s; /* Smooth hover effect */
        flex: 1; /* Flexible width */
        min-width: 200px; /* Minimum width for responsiveness */
        max-width: 3000px; /* Maximum width for consistent sizing */
        height: 200px; /* Fixed height */
        display: flex;
        flex-direction: column;
        justify-content: space-between; /* Space between elements */
    }
    .card:hover {
        transform: translateY(-5px); /* Hover lift effect */
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2); /* More pronounced shadow on hover */
    }
    .card h3 {
        font-size: 18px; /* Larger font size for labels */
        margin: 0; /* Remove default margin */
        color: #ffffff;
        font-weight: 600;
    }
    .card p {
        font-size: 20px; /* Emphasize values */
        margin: 5px 0 0; /* Spacing */
        font-weight: bold;
        color: #ffffff; /* Ensure value text is white */
    }
    .icon {
        font-size: 35px; /* Icon size */
        margin-bottom: 5px; /* Space below icon */
    }

    </style>
    """,
    unsafe_allow_html=True
)

# Function to load data
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip().str.replace(' ', '_').str.upper()  # Normalize column names
    df.replace('', pd.NA, inplace=True)  # Treat empty strings as NaN
    return df

# Sidebar for file upload
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

# Load data only if a file is uploaded
if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Check if the dataframe is empty
    if df.empty:
        st.error("The uploaded file is empty. Please upload a valid CSV file.")
    else:
        # Convert MONTH to a categorical type with a specific order
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        df['MONTH'] = pd.Categorical(df['MONTH'], categories=month_order, ordered=True)

        # Executive Summary
        st.title("Sales Analysis Dashboard - Nurtureholiks")

        # Key Metrics
        st.subheader("Key Insights")

        # Calculate total sales
        total_sales = df['SALES'].sum()

        # Calculate total units sold
        total_units_sold = df['QTY_SOLD'].sum()

        # Calculate total number of unique products
        total_products = df['PRODUCT'].nunique()

        # Calculate top performing product
        top_product = df.groupby('PRODUCT')['SALES'].sum().idxmax()  
        top_product_sales = df.groupby('PRODUCT')['SALES'].sum().max()

        # Calculate top month
        top_month = df.groupby('MONTH')['SALES'].sum().idxmax()  # Get the month with the highest sales
        top_month_sales = df.groupby('MONTH')['SALES'].sum().max()  # Get the sales amount for the top month

        # Create columns for the cards
        col1, col2, col3, col4, col5 = st.columns(5)

        # Add icons and display metrics in cards
        with col1:
            st.markdown(
                f"""
                <div class="card">
                    <div class="icon">💰</div>
                    <h3>Total Sales</h3>
                    <p>GHS {total_sales:,.2f}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div class="card">
                    <div class="icon">📦</div>
                    <h3>Total Units Sold</h3>
                    <p>{total_units_sold:,}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""
                <div class="card">
                    <div class="icon">🛒</div>
                    <h3>Total Products</h3>
                    <p>{total_products:,}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col4:
            st.markdown(
                f"""
                <div class="card">
                    <div class="icon">🏆</div>
                    <h3>Top Product</h3>
                    <p>{top_product}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col5:
            st.markdown(
                f"""
                <div class="card">
                    <div class="icon">📅</div>
                    <h3>Top Month</h3>
                    <p>{top_month}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Total Sales Over Time
        st.subheader("Total Sales Over Time")
        total_sales_over_time = df.groupby('MONTH', observed=False)['SALES'].sum().reset_index()
        chart_sales_over_time = alt.Chart(total_sales_over_time).mark_line(point=True).encode(
            x=alt.X('MONTH:O', title='Month', sort=month_order),
            y=alt.Y('SALES:Q', title='Total Sales'),
            tooltip=['MONTH', 'SALES']
        ).properties(title="Total Sales Over Time")
        st.altair_chart(chart_sales_over_time, use_container_width=True)

        # Monthly Sales Trends
        st.subheader("Monthly Sales Trends")
        monthly_sales_trends = df.groupby(['MONTH', 'PRODUCT'], observed=False)['SALES'].sum().reset_index()

        # Get unique products for filtering
        unique_products = monthly_sales_trends['PRODUCT'].unique()

        # Create a multiselect widget for product selection
        selected_products = st.multiselect(
            "Select Products to Display",
            options=unique_products,
            default=unique_products[:2]  # Default to the first two products
        )

        # Filter the data based on selected products
        filtered_monthly_sales_trends = monthly_sales_trends[monthly_sales_trends['PRODUCT'].isin(selected_products)]

        # Create the chart
        chart_monthly_trends = alt.Chart(filtered_monthly_sales_trends).mark_line(point=True).encode(
            x=alt.X('MONTH:O', title='Month', sort=month_order),
            y=alt.Y('SALES:Q', title='Sales'),
            color='PRODUCT:N',
            tooltip=['MONTH', 'PRODUCT', 'SALES']
        ).properties(title="Monthly Sales Trends")

        # Display the chart
        st.altair_chart(chart_monthly_trends, use_container_width=True)

        # Sales by Product
        st.subheader("Sales by Product")
        sales_by_product = df.groupby('PRODUCT')['SALES'].sum().reset_index()
        chart_sales_by_product = alt.Chart(sales_by_product).mark_bar().encode(
            x=alt.X('PRODUCT:O', title='Product', sort='-y'),
            y=alt.Y('SALES:Q', title='Sales'),
            tooltip=['PRODUCT', 'SALES']
        ).properties(title="Sales by Product")
        st.altair_chart(chart_sales_by_product, use_container_width=True)

        # -------------------------
        # Sales Contribution by Product Category
        # -------------------------

        st.markdown("---")  # Dash to separate sections
        st.subheader("Sales Contribution by Product Category")

        # Ensure the DataFrame is not empty
        if df.empty:
            st.error("The data frame is empty. Please upload valid sales data.")
        else:
            # Calculate total sales by product
            sales_contribution = df.groupby('PRODUCT')['SALES'].sum().reset_index()

            # Sort by sales in descending order and get the top 20 products
            top_sales_contribution = sales_contribution.sort_values(by='SALES', ascending=False).head(20)

            # Create a pie chart for the top 20 products
            pie_chart = alt.Chart(top_sales_contribution).mark_arc().encode(
                theta=alt.Theta('SALES:Q', title='Sales'),
                color=alt.Color('PRODUCT:N', title='Product'),
                tooltip=['PRODUCT', 'SALES']
            ).properties(
                title="Sales Contribution by Top 20 Products",
                width=400,
                height=400
            )

            st.altair_chart(pie_chart, use_container_width=True)

        # -------------------------
        # Stock Analysis Logic
        # -------------------------

        st.markdown("---")  # Dash to separate sections
        st.subheader("Stock Analysis")

        # Ensure the DataFrame is not empty
        if df.empty:
            st.error("The data frame is empty. Please upload valid sales data.")
        else:
            # Perform stock analysis
            stock_analysis = df.groupby('PRODUCT').agg({'TOTAL_STOCK': 'sum', 'ACTUAL_STOCK': 'sum', 'SALES': 'sum'}).reset_index()

            # Sort the stock analysis by TOTAL_STOCK in descending order
            stock_analysis = stock_analysis.sort_values(by='TOTAL_STOCK', ascending=False)

            # Optional: Create a bar chart for stock analysis
            stock_chart = alt.Chart(stock_analysis).mark_bar().encode(
                x=alt.X('PRODUCT:N', title='Product', sort='-y'),
                y=alt.Y('TOTAL_STOCK:Q', title='Total Stock'),
                tooltip=['PRODUCT', 'TOTAL_STOCK', 'ACTUAL_STOCK', 'SALES']
            ).properties(
                title="Total Stock Analysis",
                width=800,
                height=400
            )

            st.altair_chart(stock_chart, use_container_width=True)

        # Price vs. Sales Correlation
        st.subheader("Price vs. Sales Correlation")

        # Create price bins and labels
        price_bins = pd.cut(df['PRICE_(GHS)'], bins=10)  # Create 10 price bins
        price_sales_agg = df.groupby(price_bins).agg({'SALES': 'mean'}).reset_index()

        # Create descriptive labels for the bins
        price_sales_agg['PRICE_LABEL'] = price_sales_agg['PRICE_(GHS)'].apply(lambda x: f"{x.left:.2f} - {x.right:.2f}")

        # Create a scatter plot with a trend line
        scatter_chart = alt.Chart(price_sales_agg).mark_circle(size=60).encode(
            x=alt.X('PRICE_LABEL:O', title='Price Range (GHS)', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('SALES:Q', title='Average Sales'),
            tooltip=['PRICE_LABEL', 'SALES']
        ).properties(title="Price vs. Average Sales")

        # Add a trend line
        trend_line = scatter_chart.transform_regression('PRICE_LABEL', 'SALES').mark_line(color='red')

        # Combine scatter plot and trend line
        final_chart = scatter_chart + trend_line

        # Display the chart
        st.altair_chart(final_chart, use_container_width=True)

        # Monthly Performance Comparison
        st.subheader("Monthly Performance Comparison")

        # Get unique products for filtering
        unique_products_performance = df['PRODUCT'].unique()

        # Create a multiselect widget for product selection with a unique key
        selected_products_performance = st.multiselect(
            "Select Products to Display",
            options=unique_products_performance,
            default=unique_products_performance[:2]  # Default to the first two products
        )

        # Filter the data based on selected products
        filtered_monthly_performance = df[df['PRODUCT'].isin(selected_products_performance)]

        # Create the chart for quantity sold
        chart_heatmap = alt.Chart(filtered_monthly_performance).mark_line(point=True).encode(
            x=alt.X('MONTH:O', title='Month', sort=month_order),
            y=alt.Y('QTY_SOLD:Q', title='Quantity Sold'),  # Change to quantity sold
            color='PRODUCT:N',
            tooltip=['MONTH', 'PRODUCT', 'QTY_SOLD']  # Update tooltip
        ).properties(title="Monthly Performance Comparison (Quantity Sold)")

        # Display the chart
        st.altair_chart(chart_heatmap, use_container_width=True)

        # -------------------------
        # ABC Classification Logic
        # -------------------------

        st.markdown("---")  # Dash to separate charts from ABC insights
        st.subheader("ABC Classification")

        # Ensure the DataFrame is not empty
        if df.empty:
            st.error("The data frame is empty. Please upload valid sales data.")
        else:
            # Define the correct order of months
            month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                           'July', 'August', 'September', 'October', 'November', 'December']

            # Create a list of unique months from the data and convert to categorical
            unique_months = df['MONTH'].unique().tolist()
            unique_months = sorted(unique_months, key=lambda x: month_order.index(x))  # Sort based on month order

            # Add a filter for month selection
            selected_months = st.multiselect("Select Month(s) to Filter", options=unique_months, default=unique_months)

            # Filter the DataFrame based on selected months
            filtered_df = df[df['MONTH'].isin(selected_months)]

            # Calculate cumulative sales percentage for the filtered data
            abc_data = filtered_df.groupby('PRODUCT')['SALES'].sum().reset_index()
            abc_data = abc_data.sort_values(by='SALES', ascending=False)
            abc_data['CUMULATIVE_SALES'] = abc_data['SALES'].cumsum()
            abc_data['CUMULATIVE_PERCENTAGE'] = 100 * abc_data['CUMULATIVE_SALES'] / abc_data['SALES'].sum()

            # Assign ABC categories based on dynamic thresholds
            def assign_abc_category(cum_percentage, a_threshold=20, b_threshold=50):
                if cum_percentage <= a_threshold:
                    return 'A'
                elif cum_percentage <= b_threshold:
                    return 'B'
                else:
                    return 'C'

            # Apply the classification function
            abc_data['CATEGORY'] = abc_data['CUMULATIVE_PERCENTAGE'].apply(assign_abc_category)

            # Visualization of ABC Categories
            abc_chart = alt.Chart(abc_data).mark_bar().encode(
                x=alt.X('PRODUCT:N', title='Product', sort='-y'),
                y=alt.Y('SALES:Q', title='Sales'),
                color=alt.Color('CATEGORY:N', title='ABC Category', scale=alt.Scale(domain=['A', 'B', 'C'], range=['#6a11cb', '#2575fc', '#ffcc00'])),  # C color changed to yellow
                tooltip=['PRODUCT', 'SALES', 'CATEGORY', 'CUMULATIVE_PERCENTAGE']
            ).properties(
                title="ABC Classification by Product",
                width=800,
                height=400
            ).configure_mark(
                opacity=0.8
            )

            st.altair_chart(abc_chart, use_container_width=True)

            # Display ABC summary
            abc_summary = abc_data.groupby('CATEGORY')['SALES'].sum().reset_index()
            abc_summary['PERCENTAGE'] = 100 * abc_summary['SALES'] / abc_summary['SALES'].sum()
            
            # Create columns for side-by-side display
            col1, col2 = st.columns(2)

            with col1:
                st.write("### Summary by Category")
                st.dataframe(abc_summary)

            with col2:
                st.write("### Top 5 Products in Category C")
                
                # Filter for Category C products
                category_c_products = abc_data[abc_data['CATEGORY'] == 'C']

                # Get the top 5 products in Category C based on sales
                top_c_products = category_c_products.nlargest(5, 'SALES')

                # Create a bar chart for the top 5 products in Category C
                top_c_chart = alt.Chart(top_c_products).mark_bar().encode(
                    y=alt.Y('PRODUCT:N', title='Product', sort='-y'),
                    x=alt.X('SALES:Q', title='Sales'),
                    color=alt.value('#ffcc00'),  # Use a distinct color for visibility
                    tooltip=['PRODUCT', 'SALES']
                ).properties(
                    title="Top 5 Products in Category C",
                    width=400,
                    height=400
                )

                # Display the chart
                st.altair_chart(top_c_chart, use_container_width=True)

            # Add a dash to separate sections
            st.markdown("---")  # Dash to separate sections

            # Display Product-Level Classification
            st.write("### Product-Level ABC Classification")
            st.dataframe(abc_data)

            # General Tips
            st.markdown("---")  # Dash to separate tips
            st.subheader("General Tips for ABC Classification")
            st.write("""
            - **Focus on A Items**: These products contribute the most to your revenue. Ensure they are always in stock and consider strategies to promote them further.
            - **Monitor B Items**: These items are important but not as critical as A items. Regularly review their performance and adjust inventory levels accordingly.
            - **Manage C Items Efficiently**: While these items contribute less to overall sales, they can take up valuable inventory space. Consider reducing stock levels or using just-in-time inventory practices.
            - **Review Regularly**: ABC classifications can change over time. Regularly review your classifications to ensure they reflect current sales trends.
            - **Use Data for Decision Making**: Leverage the insights gained from ABC classification to inform purchasing, marketing, and sales strategies.
            """)

else:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
                    padding: 30px;
                    border-radius: 12px;
                    color: white;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
                    text-align: center;">
            <h1 style="margin-bottom: 15px;">Welcome to the Nurtureholiks Sales Analysis Dashboard</h1>
            <p style="font-size: 16px;">This dashboard allows you to analyze and visualize the company's sales data effectively. 
            Upload a CSV file to get started.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### How to Use the Dashboard")
    st.write("""
    1. **Upload Your Data**:
       - Use the file uploader in the sidebar to upload your sales data as a CSV file.
       - Ensure your file includes columns the following columns (in the order provided): PRODUCT, MONTH, PRICE, QTY SOLD, SALES, TOTAL STOCK, STOCK LEFT(EXCEL), ACTUAL STOCK, SYSTEM STOCK, SURPLUS & SHORTAGE.
    
    2. **Analyze Key Metrics**:
       - View metrics like total sales, top-performing products, and peak sales months through interactive cards and visualizations.

    3. **Explore Visualizations**:
       - Examine trends with line charts, bar charts, and pie charts.
       - Filter data dynamically to focus on specific products or months.

    4. **ABC Classification**:
       - Categorize products into `A`, `B`, and `C` categories based on their contribution to total sales for better inventory management.
    
    5. **FAQ**:
    """)

    st.markdown("""
        <div style="margin-left: 20px;">
        <ul>
            <li><strong>What data format is required?</strong> Ensure your file is in CSV format with clear headers.</li>
            <li><strong>What insights can I gain?</strong> Key insights include product performance, sales trends, and inventory efficiency.</li>
            <li><strong>Can I filter data?</strong> Yes, you can filter by products, months, or other attributes dynamically on selected charts.</li>
            <li><strong>What is ABC classification?</strong> It segments products into three categories (`A`, `B`, and `C`) based on their contribution to total sales.</li>
        </ul>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin-top: 20px; text-align: center; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);">
            <p style="font-size: 14px; color: #333;">Tip: If you're new to this dashboard, start by uploading a sample CSV file to explore its capabilities.</p>
        </div>
    """, unsafe_allow_html=True)

    # FAQ Section

    st.markdown("---")  # Dash to separate sections
    st.subheader("Frequently Asked Questions (FAQ)")

    # Define FAQ content
    faq_data = [
        {
            "question": "What types of data can I upload?",
            "answer": "You can upload sales data in CSV format, which should include columns for product names, sales figures, and any relevant dates."
        },
        {
            "question": "How often should I update my data?",
            "answer": "It's recommended to update your data regularly, ideally on a quarterly basis, to ensure you have the most accurate insights."
        },
        {
            "question": "What insights can I gain from this dashboard?",
            "answer": "The dashboard provides insights into sales performance, product categorization (ABC classification), stock analysis, and sales contributions by product category."
        },
        {
            "question": "Can I filter the data by month?",
            "answer": "Yes, you can filter the data by month to analyze sales performance for specific periods."
        },
        {
            "question": "Who can I contact for support?",
            "answer": "For support, please contact our customer service team at info@nurtureholiks.com."
        }
    ]

    # Create a collapsible FAQ section
    for faq in faq_data:
        with st.expander(faq["question"], expanded=False):
            st.write(faq["answer"])
