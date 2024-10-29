
This project has been developed to recreate a Web application that calculates the intrinsic P/E and degree of overvaluation for companies listed on NSE/BSE based on financial data scraped from the Screener website.

### Overview

This assignment aimed at developing an interactive web application for scrapping the most important financial figures relative to a user-supplied company symbol, say NESTLEIND, from Screener. These are then used in the computation of relevant metrics such as current P/E ratio, FY23 P/E ratio, compounded growth rates for sales and profit, compute the intrinsic P/E and degree of overvaluation using a growth-RoC DCF model.

### This application was developed with the help of:
- Python
- Streamlit for the user interface
- Pandas for data manipulation
- Plotly Express for visualization
- BeautifulSoup for web scraping
- NumPy for financial calculations

### App Demo
- **Web App Link**: https://internshiptask-ambit.streamlit.app/
- **Code Repository**: https://github.com/shiven06/InternshipTask

### Features

1. **Company Financial Data Scraping**:  
   The application will scrape important financial data like Current P/E, FY23 P/E, and 5 yr med RoCE from the Screener page of a given company. It fetches dynamic data for any given company symbol using the URL format `https://www.screener.in/company/<symbol>/`

2. **Computed Parameters**:
   - **Intrinsic P/E**: Calculated through a DCF-based model based on user inputs - cost of capital, RoCE, growth during high growth, etc.
   - **Degree of Overvaluation**: Calculated as a percentage difference between the lower of the current P/E and FY23 P/E from the calculated intrinsic P/E.

3. **Growth Analysis**:  
   The chart below illustrates the compounded growth of Sales and Profit over the last TTM, 3, 5-, and 10-year period using dynamic data from Screener.

4. **User Inputs**:  
   Cost of Capital, RoCE, High Growth Period, Fade Period, and Terminal Growth Rate can be changed by the user via sliders to make the app interactive and customizable.

### Installing

You can install the required python packages using `requirements.txt`:
```bash
pip install -r requirements.txt
```

The major dependencies include:
- Streamlit 1.12.0
- Requests 2.27.1
- BeautifulSoup4 4.11.1
- Pandas 1.4.0
- Plotly 5.5.0
- NumPy 1.22.0

### How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/shiven06/InternshipTask.git
   ```

3. Enter the project directory and activate your virtual environment:
   ```bash
   cd InternshipTask
   source venv/bin/activate #on mac
   ```

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

7. Run the Streamlit app:
   ```bash
   streamlit run Ambit_IE_Internship_Task.py
   ```

### Challenges Faced

Since this is my first exposure to financial data and terminologies like calculation of intrinsic value and DCF models, I found it difficult to implement correctly the intrinsic P/E and degree of overvaluation. Nevertheless, I certainly put in much effort to understand and exactly replicate the functionality as closely as possible. I would consider myself very happy to get feedback on where improvements might be required and look forward to getting to learn more about financial modeling and applying such knowledge in the time to come.

Thanks for your time.
