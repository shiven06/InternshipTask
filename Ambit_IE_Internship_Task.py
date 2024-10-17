import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import numpy as np

# define the url structure and headers for http requests
BASE_URL = "https://www.screener.in/company/{symbol}/"


# function to download and parse html content
def download_and_parse(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

# function to pivot and prepare dataframe for display
def prepare_growth_display(df, metric_prefix):
    # filter dataframe for relevant metrics
    growth_df = df[df['Metric'].str.contains(metric_prefix)]
    # pivot dataframe to get periods as columns
    growth_df = growth_df.pivot(index='Metric', columns='Period', values='Value').reset_index()
    # clean up the dataframe for better display
    growth_df.set_index('Metric', inplace=True)  # set 'Metric' as the new index
    return growth_df

# to find specific roce% value from table
def find_specific_roce(df, metric_name):
    try:
        # find the row that contains the metric name (e.g., "ROCE %")
        metric_row = df[df['Metric'].str.contains(metric_name, case=False, na=False)]
        if not metric_row.empty:
            # get the fifth last column's name
            # assuming that the last few columns are always the dates we are interested in
            period = metric_row.columns[-5]  # change the index as needed (-5 for fifth from the last)
            return metric_row[period].values[0]
    except Exception as e:
        return f"Error fetching data: {str(e)}"
    return "Data not available"

def get_table(parsed, table_id):
    results = parsed.find('section', {'id': table_id})
    table = results.find('table', class_='data-table')
    headers = [header.text.strip() for header in table.find_all('th')[1:]]
    df_rows=[]
    for row in table.find_all('tr')[1:]:
        df_row=[]
        for cell in row.find_all('td'):
            df_row.append(cell.text.strip())
        df_rows.append(df_row)
    return pd.DataFrame(df_rows, columns=['Metric'] + headers)


def get_profit_loss_additional(parsed):
    # find the section containing the profit & loss statement
    profit_loss_section = parsed.find('section', {'id': 'profit-loss'})

    tables = profit_loss_section.find_all('table', class_='ranges-table')
    # initialize list to store all data
    data = []

    # iterate through each table and extract data
    for table in tables:
        # fet the header (growth type)
        header = table.find('th').text.strip()
        
        # find all rows within the table
        rows = table.find_all('tr')[1:]  # skip the first header row
        
        for row in rows:
            # get the period and the percentage values
            period = row.find_all('td')[0].text.strip()
            value = row.find_all('td')[1].text.strip()
            data.append([header, period, value])

    # convert to a pandas dataframe
    df = pd.DataFrame(data, columns=['Metric', 'Period', 'Value'])

    return df
    
# function to find specific financial metrics from parsed html
def find_metric(parsed, html_tag, attribute_type, attribute_value):
    metric_tag = parsed.find(html_tag, {attribute_type: attribute_value})
    return metric_tag.text.strip() if metric_tag else 'Data not available'


# to find 'EPS in Rs'
def find_specific_eps(df, date):
    eps_row = df[df['Metric'].str.contains('EPS')]
    if not eps_row.empty and date in eps_row.columns:
        return eps_row[date].values[0]
    return None

def plot_growth_chart(df, title):
    # ensure periods are in the desired order
    period_order = ['TTM:', '3 Years:', '5 Years:', '10 Years:']
    df['Period'] = pd.Categorical(df['Period'], categories=period_order, ordered=True)

    # convert percentage strings to numbers for plotting
    df['Value'] = df['Value'].str.rstrip('%').astype(float)

    # create the horizontal bar chart
    fig = px.bar(df, y='Period', x='Value', orientation='h', title=title, text='Value')
    fig.update_layout(xaxis_title='Growth (%)', yaxis_title='', yaxis=dict(categoryorder='total ascending'))
    fig.update_traces(textposition='outside')
    return fig

TAX_RATE = 0.25

# function to calculate the intrinsic P/E ratio based on DCF analysis
def dcf_intrinsic_pe(eps, growth_rate, high_growth_period, fade_period, terminal_growth_rate, coc):
    eps = float(eps)
    growth_rate = float(growth_rate) / 100
    terminal_growth_rate = float(terminal_growth_rate) / 100
    coc = float(coc) / 100

    # time array for the high growth and fade periods
    high_growth_years = np.arange(1, high_growth_period + 1)
    fade_years = np.arange(1, fade_period + 1)

    # high growth value calculation
    high_growth_values = eps * (1 + growth_rate) ** high_growth_years / (1 + coc) ** high_growth_years
    high_growth_value = np.sum(high_growth_values)

    # fade period value calculation
    fade_growth_rates = growth_rate - (fade_years / fade_period) * (growth_rate - terminal_growth_rate)
    fade_values = eps * (1 + fade_growth_rates) ** (high_growth_years[-1] + fade_years) / (1 + coc) ** (high_growth_years[-1] + fade_years)
    fade_value = np.sum(fade_values)

    # terminal value calculation
    terminal_value = (eps * (1 + terminal_growth_rate) ** (high_growth_period + fade_period + 1)) / (coc - terminal_growth_rate)
    terminal_value_discounted = terminal_value / (1 + coc) ** (high_growth_period + fade_period)

    # intrinsic value calculation
    intrinsic_value = (high_growth_value + fade_value + terminal_value_discounted) * (1 - TAX_RATE)
    intrinsic_pe = intrinsic_value / eps

    return intrinsic_pe

def calculate_overvaluation(current_pe, fy23_pe, intrinsic_pe):
    lower_pe = min(float(current_pe), float(fy23_pe))
    overvaluation = (lower_pe / intrinsic_pe - 1) * 100
    return overvaluation

# streamlit UI setup
st.title('Valuing Consistent Compounders')

# main input fields
symbol_input = st.text_input("Enter Company Symbol", "NESTLEIND")

# sliders for DCF calculation parameters
coc = st.slider('Cost of Capital (CoC) (%)',8,16,step=1,value=12)  # default set to 12%
roce_input = st.slider('Return on Capital Employed (RoCE) (%)',10,100,step=10,value=50)  # default set to 50%
growth_during_high_growth = st.slider('Growth during high growth period ($)',8,20,step=2,value=12)  # default set to 12%
high_growth_period = st.slider('High growth period (years)',10,25,step=2,value=14)  # default set to 14 years
fade_period = st.select_slider('Fade period (years)', options=[5,10,15,20], value=10)  # default set to 10 years  # default set to 10 years
terminal_growth_rate = st.select_slider('Terminal growth rate (%)', options=[0,1,2,3,4,5,6,7,7.5], value=5)  # default set to 2%

# main function to handle data fetching and processing
def main():
    url = BASE_URL.format(symbol=symbol_input)
    parsed_html = download_and_parse(url)

    quarters_df = get_table(parsed_html, 'quarters')
    profit_loss_df =  get_table(parsed_html, 'profit-loss')
    profit_loss_additional_df = get_profit_loss_additional(parsed_html)
    balance_sheet_df = get_table(parsed_html, 'balance-sheet')
    cash_flow_df = get_table(parsed_html, 'cash-flow')
    ratios_df = get_table(parsed_html, 'ratios')
    shareholding_df = get_table(parsed_html, 'shareholding')
    
    # fetch key metrics
    stock_symbol = find_metric(parsed_html, 'h1', 'class', 'h2 shrink-text')  # fetch the stock symbol
    current_pe = None
    pe_elements = parsed_html.find_all('li', class_='flex flex-space-between')  # find all 'li' elements once
    for li in pe_elements:
        if 'Stock P/E' in li.text:  # check if 'Stock P/E' is in the text of the 'li' element
            number_span = li.find('span', class_='number')
            if number_span:
                current_pe = number_span.text.strip()  # store the value if found
                break

    current_price = None
    price_elements = parsed_html.find_all('li', class_='flex flex-space-between')  # find all 'li' elements once
    for li in price_elements:
        if 'Current Price' in li.text:  
            number_span = li.find('span', class_='number')
            if number_span:
                current_price = number_span.text.strip()  # store the value if found
                break

    epsvalue=find_specific_eps(profit_loss_df, 'Mar 2024')
    rocevalue=find_specific_roce(ratios_df, 'ROCE %')

    if current_price and epsvalue and epsvalue != 'EPS value not found':
        try:
            fy23_pe = float(current_price.replace(',', '')) / float(epsvalue)
            fy23_pe_calc = f"{fy23_pe:.2f}"  # format to 2 decimal places
        except ValueError:
            fy23_pe_calc = "Error in calculation"
    else:
        fy23_pe_calc = "Data not available for calculation"
    
    
    sales_growth_df = profit_loss_additional_df[profit_loss_additional_df['Metric'].str.contains('Compounded Sales Growth')].reset_index(drop=True)
    sales_growth_df.index=sales_growth_df.index+1
    profit_growth_df = profit_loss_additional_df[profit_loss_additional_df['Metric'].str.contains('Compounded Profit Growth')].reset_index(drop=True)
    profit_growth_df.index=profit_growth_df.index+1
    
    # preparing dataframes for display
    prepared_sales_growth = prepare_growth_display(profit_loss_additional_df, 'Compounded Sales Growth')
    prepared_profit_growth = prepare_growth_display(profit_loss_additional_df, 'Compounded Profit Growth')
    sales_growth_chart = plot_growth_chart(sales_growth_df, "Compounded Sales Growth")
    profit_growth_chart = plot_growth_chart(profit_growth_df, "Compounded Profit Growth")


    if epsvalue and current_price:
        epsvalue = float(epsvalue.replace(',', ''))
        current_price = float(current_price.replace(',', ''))
        fy23_pe = current_price / epsvalue
        intrinsic_pe = dcf_intrinsic_pe(epsvalue, 12, high_growth_period, fade_period, terminal_growth_rate, coc)
        overvaluation = calculate_overvaluation(current_price, fy23_pe, intrinsic_pe)
        
    else:
        st.error("Financial data is incomplete or missing.")

    # display the fetched data
    st.write(f"Stock Symbol: {stock_symbol}")
    st.write(f"Current P/E Ratio: {current_pe}")
    st.write(f"Current Price: {current_price}")
    st.write(f"EPS: {epsvalue}")
    st.write(f"FY23 PE: {fy23_pe_calc}")
    st.write(f"5 Year Median Pre-Tax RoCE %: {rocevalue}")
    st.table(prepared_sales_growth)
    st.table(prepared_profit_growth)
    st.plotly_chart(sales_growth_chart, use_container_width=True)
    st.plotly_chart(profit_growth_chart, use_container_width=True)
    st.write(f"Intrinsic P/E calculated: {intrinsic_pe:.2f}")
    st.write(f"Degree of Overvaluation: {overvaluation:.2f}%")

# trigger the main function with a button
if st.button('Fetch and Display Data'):
    main()
