import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime
import numpy as np

# set the session state for the date range
if "expenses" not in st.session_state:
  st.session_state.expenses = pd.DataFrame(columns=["Date", "Category","Amount","Note"])

# initialize the budget if not exists
if "monthly_budget" not in st.session_state:
   st.session_state.monthly_budget = 1000.00  # default budget

# initialize the categories if not exists
if "custom_categories" not in st.session_state:
   st.session_state.custom_categories = ["Food", "Transport", "Entertainment", "Other"]

############################################################  sidebar ############################################################ 

#Sidebar for setting and filtering
st.sidebar.header("Settings & Filters")

# Budget managements
st.sidebar.subheader("Budget Management")
new_budget = st.sidebar.number_input("Monthly Budget", value=st.session_state.monthly_budget, min_value=0.0, format="%.2f")
if st.sidebar.button(" Update Budget"):
   st.session_state.monthly_budget = new_budget
   st.sidebar.success("Budget updated")

# Categories managements
st.sidebar.subheader("Categories Management")
new_category=st.sidebar.text_input("Add new Category")
if st.sidebar.button("Add category"):
    if new_category not in st.session_state.custom_categories:
      st.session_state.custom_categories.append(new_category)
    else:
       st.sidebar.warning("Category already exists")

# Categories selection
st.sidebar.subheader("Filter by Category")
selected_categories = st.sidebar.multiselect(
   "Filter by Category",
   options=st.session_state.custom_categories,
   default=st.session_state.custom_categories 
)

# Date range filter
st.sidebar.subheader("Date Range Filter")
if not st.session_state.expenses.empty:
    min_date = st.session_state.expenses["Date"].min()
    max_date = st.session_state.expenses["Date"].max()
else:
    min_date = date.today().replace(day=1)  # default to the first day of the current month
    max_date = date.today()
date_range= st.sidebar.date_input(
    "Select Date Range",
    value=(min_date,max_date),
    min_value=min_date,
    max_value=max_date
)

############################################################ expenses ############################################################ 

st.title("Expense Tracker")
# filter expenses based on selected categories and date range
filtered_expenses=st.session_state.expenses.copy()
if not filtered_expenses.empty:
  filtered_expenses["Date"] = pd.to_datetime(filtered_expenses["Date"])

  if len(date_range) ==2:
    start_date, end_date = date_range
    filtered_expenses = filtered_expenses[
            (filtered_expenses['Date'].dt.date >= start_date) & 
            (filtered_expenses['Date'].dt.date <= end_date)
        ]
            
# Apply category filter
filtered_expenses = filtered_expenses[filtered_expenses['Category'].isin(selected_categories)]

# # display expenses version 1
# st.subheader("Expenses")
# st.dataframe(st.session_state.expenses)

# Display metrics and expenses version 2
if not filtered_expenses.empty:
    col_metrics = st.columns(4)
    total_spent = filtered_expenses['Amount'].sum()
    avg_expense = filtered_expenses['Amount'].mean()
    transaction_count = len(filtered_expenses)
    current_month_spent = filtered_expenses[
        filtered_expenses['Date'].dt.month == datetime.now().month
    ]['Amount'].sum() if not filtered_expenses.empty else 0
    
    with col_metrics[0]:
        st.metric("Total Spent", f"${total_spent:.2f}")
    with col_metrics[1]:
        st.metric("Average Expense", f"${avg_expense:.2f}")
    with col_metrics[2]:
        st.metric("Transactions", transaction_count)
    with col_metrics[3]:
        budget_remaining = st.session_state.monthly_budget - current_month_spent
        st.metric("Budget Remaining", f"${budget_remaining:.2f}", 
                 delta=f"${-current_month_spent:.2f}")
st.dataframe(filtered_expenses, use_container_width=True)

# add expenses
st.subheader("Add Expense")

with st.form(key="expense_form"): 
  
  col1,col2 = st.columns(2)
  expense_date = col1.date_input("Date",value=date.today())
  category=col2.selectbox("Category",st.session_state.custom_categories)

  col3,col4 = st.columns(2)
  amount = col3.number_input("Amount",min_value=0.01, format="%.2f")
  note = col4.text_input("Note")
  submit_button=st.form_submit_button("Add Expense")

  if submit_button:
    new_data= pd.DataFrame({
      "Date": [expense_date],
      "Category": [category],
      "Amount": [amount],
      "Note": [note]
    })
    st.balloons()
    st.session_state.expenses=pd.concat([st.session_state.expenses, new_data],ignore_index=True)
    st.success("Expense added successfully!")

# visualize expenses version 1
# if not st.session_state.expenses.empty:
#   st.subheader("Expense breakdown by category")
#   fig=px.pie(st.session_state.expenses, names="Category", values="Amount", title="Expenses Distribution", hole=0.4)
#   st.plotly_chart(fig, use_container_width=True)
# else:
#     st.info("No data to display. Add an expense or upload a CSV.")

# visualize expenses version 2
if not filtered_expenses.empty:
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Category Breakdown", "📈 Trends", "📅 Monthly Analysis", "🎯 Budget Tracking"])
    
    with tab1:
        st.subheader("Expense breakdown by category")
        fig_pie = px.pie(filtered_expenses, names="Category", values="Amount", 
                        title="Expenses Distribution", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Category summary table
        category_summary = filtered_expenses.groupby('Category')['Amount'].agg(['sum', 'mean', 'count']).round(2)
        category_summary.columns = ['Total', 'Average', 'Count']
        st.subheader("Category Summary")
        st.dataframe(category_summary)
    
    with tab2:
        st.subheader("Spending Trends")
        # Daily spending trend
        daily_spending = filtered_expenses.groupby('Date')['Amount'].sum().reset_index()
        fig_line = px.line(daily_spending, x='Date', y='Amount', 
                          title="Daily Spending Trend", markers=True)
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Weekly spending
        filtered_expenses['Week'] = filtered_expenses['Date'].dt.isocalendar().week
        weekly_spending = filtered_expenses.groupby('Week')['Amount'].sum().reset_index()
        fig_bar = px.bar(weekly_spending, x='Week', y='Amount', 
                        title="Weekly Spending")
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab3:
        st.subheader("Monthly Analysis")
        # Monthly breakdown
        filtered_expenses['Month'] = filtered_expenses['Date'].dt.to_period('M')
        monthly_spending = filtered_expenses.groupby(['Month', 'Category'])['Amount'].sum().reset_index()
        monthly_spending['Month'] = monthly_spending['Month'].astype(str)
        
        fig_monthly = px.bar(monthly_spending, x='Month', y='Amount', color='Category',
                           title="Monthly Spending by Category")
        st.plotly_chart(fig_monthly, use_container_width=True)
        
        # Monthly statistics
        monthly_stats = filtered_expenses.groupby('Month')['Amount'].agg(['sum', 'mean', 'count']).round(2)
        monthly_stats.columns = ['Total', 'Average per Transaction', 'Transaction Count']
        st.dataframe(monthly_stats)
    
    with tab4:
        st.subheader("Budget Tracking")
        
        # Current month progress
        current_month = datetime.now().month
        current_year = datetime.now().year
        current_month_expenses = filtered_expenses[
            (filtered_expenses['Date'].dt.month == current_month) & 
            (filtered_expenses['Date'].dt.year == current_year)
        ]
        
        if not current_month_expenses.empty:
            current_spent = current_month_expenses['Amount'].sum()
            budget_percentage = (current_spent / st.session_state.monthly_budget) * 100
            
            # Budget progress bar
            st.metric("Current Month Spending", f"${current_spent:.2f}", 
                     f"{budget_percentage:.1f}% of budget")
            
            progress_bar = st.progress(min(budget_percentage / 100, 1.0))
            
            if budget_percentage > 100:
                st.error(f"⚠️ Budget exceeded by ${current_spent - st.session_state.monthly_budget:.2f}")
            elif budget_percentage > 80:
                st.warning(f"⚠️ You've used {budget_percentage:.1f}% of your budget")
            else:
                st.success(f"✅ You're within budget ({budget_percentage:.1f}% used)")
            
            # Budget by category
            category_budget = current_month_expenses.groupby('Category')['Amount'].sum().reset_index()
            fig_budget = px.bar(category_budget, x='Category', y='Amount',
                              title="Current Month Spending by Category")
            st.plotly_chart(fig_budget, use_container_width=True)
        else:
            st.info("No expenses recorded for current month")

# save expenses to CSV

# Advanced Data Management

st.subheader("Data Management")
col5,col6, col7=st.columns(3)

with col5:
  if not st.session_state.expenses.empty:
    csv_data = st.session_state.expenses.to_csv(index=False)
    st.download_button(
      label="📥 Download CSV",
      data=csv_data,
      file_name=f"expenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", 
      mime="text/csv"
    )
  else:
    st.info("No data to download")

with col6:
  uploaded_file = st.file_uploader("📤 Upload CSV", type=["csv"])
  if uploaded_file is not None:
    try:
        new_expenses = pd.read_csv(uploaded_file)
        # Validate columns
        required_columns = ["Date", "Category", "Amount", "Note"]
        if all(col in new_expenses.columns for col in required_columns):
            st.session_state.expenses = new_expenses
            st.success("✅ Data loaded from CSV!")
            st.rerun()
        else:
            st.error(f"❌ CSV must contain columns: {required_columns}")
    except Exception as e:
        st.error(f"❌ Error loading CSV: {e}")

with col7:
    if st.button("🗑️ Clear All Data"):
        st.session_state.expenses = pd.DataFrame(columns=["Date", "Category","Amount","Note"])
        st.success("All data cleared!")
        st.rerun()

# Advanced Analytics Section
if not st.session_state.expenses.empty:
    st.subheader("📊 Advanced Analytics")
    
    analytics_col1, analytics_col2 = st.columns(2)
    
    with analytics_col1:
        st.write("**Top Spending Categories**")
        top_categories = st.session_state.expenses.groupby('Category')['Amount'].sum().sort_values(ascending=False).head(5)
        for category, amount in top_categories.items():
            st.write(f"• {category}: ${amount:.2f}")
    
    with analytics_col2:
        st.write("**Spending Statistics**")
        expenses_stats = st.session_state.expenses['Amount'].describe()
        st.write(f"• Highest expense: ${expenses_stats['max']:.2f}")
        st.write(f"• Lowest expense: ${expenses_stats['min']:.2f}")
        st.write(f"• Standard deviation: ${expenses_stats['std']:.2f}")
        st.write(f"• Median: ${expenses_stats['50%']:.2f}")

# Expense Search and Edit
st.subheader("🔍 Search & Edit Expenses")
search_col1, search_col2 = st.columns(2)

with search_col1:
    search_term = st.text_input("Search in notes")
    if search_term:
        search_results = st.session_state.expenses[
            st.session_state.expenses['Note'].str.contains(search_term, case=False, na=False)
        ]
        st.dataframe(search_results)

with search_col2:
    if not st.session_state.expenses.empty:
        expense_to_delete = st.selectbox(
            "Select expense to delete",
            options=range(len(st.session_state.expenses)),
            format_func=lambda x: f"{st.session_state.expenses.iloc[x]['Date']} - {st.session_state.expenses.iloc[x]['Category']} - ${st.session_state.expenses.iloc[x]['Amount']:.2f}"
        )
        
        if st.button("🗑️ Delete Selected Expense"):
            st.session_state.expenses = st.session_state.expenses.drop(expense_to_delete).reset_index(drop=True)
            st.success("Expense deleted!")
            st.rerun()
