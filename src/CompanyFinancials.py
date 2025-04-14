import os

import requests
import pandas as pd
import time
from dotenv import load_dotenv

# Load variables from .env into the environment
load_dotenv()

API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

if API_KEY is None:
    raise Exception("API key not found. Please set ALPHA_VANTAGE_API_KEY in your .env file.")


class CompanyFinancials:
    def __init__(self, ticker):
        self.ticker = ticker
        self.api_key = API_KEY

        # Fetch data from the different endpoints
        self.daily_data = self._fetch_daily_data()  # TIME_SERIES_DAILY
        self.overview = self._fetch_overview()  # OVERVIEW
        self.income_statement = self._fetch_income_statement()  # INCOME_STATEMENT
        self.balance_sheet = self._fetch_balance_sheet()  # BALANCE_SHEET
        self.earnings = self._fetch_earnings()  # EARNINGS

    def _fetch_daily_data(self):
        url = (
            f"https://www.alphavantage.co/query?"
            f"function=TIME_SERIES_DAILY&symbol={self.ticker}&outputsize=compact&apikey={self.api_key}"
        )
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Error fetching daily data for {self.ticker}")
        data = response.json()
        ts = data.get("Time Series (Daily)")
        if not ts:
            raise Exception(f"No daily time series data returned for {self.ticker}")
        df = pd.DataFrame.from_dict(ts, orient='index')
        df = df.rename(columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. volume": "Volume"
        })
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        # Convert all data to numeric types
        for col in df.columns:
            df[col] = pd.to_numeric(df[col])
        return df

    def _fetch_overview(self):
        url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={self.ticker}&apikey={self.api_key}"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Error fetching overview for {self.ticker}")
        data = response.json()
        if not data:
            raise Exception(f"No overview data returned for {self.ticker}")
        return data

    def _fetch_income_statement(self):
        url = f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={self.ticker}&apikey={self.api_key}"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Error fetching income statement for {self.ticker}")
        data = response.json()
        if not data:
            raise Exception(f"No income statement data returned for {self.ticker}")
        return data

    def _fetch_balance_sheet(self):
        url = f"https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={self.ticker}&apikey={self.api_key}"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Error fetching balance sheet for {self.ticker}")
        data = response.json()
        if not data:
            raise Exception(f"No balance sheet data returned for {self.ticker}")
        return data

    def _fetch_earnings(self):
        url = f"https://www.alphavantage.co/query?function=EARNINGS&symbol={self.ticker}&apikey={self.api_key}"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Error fetching earnings for {self.ticker}")
        data = response.json()
        if not data:
            raise Exception(f"No earnings data returned for {self.ticker}")
        return data

    # 1. Latest daily stock price
    def get_latest_stock_price(self):
        # Assuming the latest date is the last row in the DataFrame.
        latest_date = self.daily_data.index[-1]
        return self.daily_data.loc[latest_date]['Close']

    # 2. Market Cap (from Overview)
    def get_market_cap(self):
        return float(self.overview.get("MarketCapitalization", 0))

    # 3. P/E Ratio (from Overview)
    def get_pe_ratio(self):
        return float(self.overview.get("PERatio", 0))

    # 4. Operating Income (trailing annual, from Income Statement)
    def get_operating_income_trailing(self):
        try:
            quarterly_reports = self.income_statement["quarterlyReports"][:4]
            if len(quarterly_reports) < 4:
                raise Exception("Not enough quarterly data to compute operating income trailing")

            operating_income = sum(float(q.get("operatingIncome", 0)) for q in quarterly_reports)
            return operating_income
        except (IndexError, KeyError):
            return None

    # 5. Net Income Common (trailing annual, from Income Statement)
    def get_net_income_trailing(self):
        try:
            quarterly_reports = self.income_statement["quarterlyReports"][:4]
            if len(quarterly_reports) < 4:
                raise Exception("Not enough quarterly data to compute net income trailing")

            net_income = sum(float(q.get("netIncome", 0)) for q in quarterly_reports)
            return net_income
        except (IndexError, KeyError):
            return None

    # 6. ROE (trailing annual, from Overview)
    def get_roe_trailing(self):
        try:
            # Use the most recent annual shareholder equity as a proxy for average equity.
            latest_bs = self.balance_sheet["quarterlyReports"]
            if not latest_bs:
                raise Exception("No balance sheet data available")

            latest_equity = float(latest_bs[0].get("totalShareholderEquity", 0))
            if latest_equity == 0:
                raise Exception("Latest shareholder equity is zero, cannot compute ROE")

            # Compute ROE as the ratio of TTM net income to the shareholder equity
            ttm_roe = self.get_net_income_trailing() / latest_equity
            return ttm_roe

        except Exception as e:
            print(f"Error calculating TTM ROE from quarterly data: {e}")
            return None

    # 7. ROA (trailing annual, from Overview)
    def get_roa_trailing(self):
        try:
            # Use the most recent annual shareholder equity as a proxy for average equity.
            latest_bs = self.balance_sheet["quarterlyReports"]
            if not latest_bs:
                raise Exception("No balance sheet data available")

            latest_assets  = float(latest_bs[0].get("totalAssets", 0))
            if latest_assets  == 0:
                raise Exception("Latest shareholder equity is zero, cannot compute ROE")

            # Compute ROA as the ratio of TTM net income to total assets
            ttm_roa = self.get_net_income_trailing() / latest_assets
            return ttm_roa

        except Exception as e:
            print(f"Error calculating TTM ROE from quarterly data: {e}")
            return None

    # 8. Revenue (trailing annual, from Income Statement)
    def get_revenue_trailing(self):
        try:
            quarterly_reports = self.income_statement["quarterlyReports"][:4]
            if len(quarterly_reports) < 4:
                raise Exception("Not enough quarterly data to compute revenue trailing")

            revenue = sum(float(q.get("totalRevenue", 0)) for q in quarterly_reports)
            return revenue
        except (IndexError, KeyError):
            return None

    # 9. Gross Margin (trailing annual) = (Gross Profit / Revenue) * 100
    def get_gross_margin_trailing(self):
        try:
            quarterly_reports = self.income_statement["quarterlyReports"][:4]
            if len(quarterly_reports) < 4:
                raise Exception("Not enough quarterly data to compute gross margin trailing")

            gross_profit = sum(float(q.get("grossProfit", 0)) for q in quarterly_reports)
            revenue = self.get_revenue_trailing()
            if revenue > 0:
                return (gross_profit / revenue) * 100
            else:
                return None
        except (IndexError, KeyError):
            return None

    # 10. How many years does book value per share grow in last 3 years?
    def get_book_value_growth_years_last_3(self):
        try:
            quarterly_reports = self.balance_sheet["quarterlyReports"][:16] # last 4 years (most recent first)
            if len(quarterly_reports) < 16:
                raise Exception("Not enough quarterly data to compute book value per share for last 3 years")

            annual_bs = [sum(float(quarterly_reports[i * 4 + j].get("totalShareholderEquity", 0)) for j in range(4)) for i in range(4)]
            shares_outstanding = [float(quarterly_reports[i * 4].get("commonStockSharesOutstanding", 0)) for i in range(4)]
            growth_count = 0
            # Compute book value per share for each year and compare to previous year
            bvps = []
            for i in range(3):
                bvps.append(annual_bs[i] / shares_outstanding[i] if shares_outstanding[i] else 0)
            # Compare each consecutive pair (from older to newer)
            for i in range(len(bvps) - 1):
                # Check if growth from i+1 -> i (since list is most recent first)
                if bvps[i] > bvps[i + 1]:
                    growth_count += 1
            return growth_count
        except (IndexError, KeyError, ValueError):
            return None

    # 11. How many years does revenue grow in last 3 years?
    def get_revenue_growth_years_last_3(self):
        try:
            quarterly_reports = self.income_statement["quarterlyReports"][:16]  # last 4 years (most recent first)
            if len(quarterly_reports) < 16:
                raise Exception("Not enough quarterly data to compute revenue for last 3 years")

            revenues = [sum(float(quarterly_reports[i * 4 + j].get("totalRevenue", 0)) for j in range(4)) for i in range(4)]
            growth_count = 0
            # Compare consecutive annual revenues (list is most recent first)
            for i in range(len(revenues) - 1):
                if revenues[i] > revenues[i + 1]:
                    growth_count += 1
            return growth_count
        except (IndexError, KeyError, ValueError):
            return None

    # 12. How many quarters does revenue grow in last 4 quarters?
    def get_quarters_revenue_growth_last_4(self):
        try:
            quarterly_reports = self.income_statement["quarterlyReports"][:5]
            if len(quarterly_reports) < 5:
                raise Exception("Not enough quarterly data to compute revenue for last 4 quarters")

            growth_count = 0
            revenues = [float(report.get("totalRevenue", 0)) for report in quarterly_reports]
            for i in range(len(revenues) - 1):
                if revenues[i] > revenues[i + 1]:
                    growth_count += 1
            return growth_count
        except (IndexError, KeyError, ValueError):
            return None

    # 13. Last 3 yrs revenue growth in %
    def get_revenue_growth_percent_last_3(self):
        try:
            quarterly_reports = self.income_statement["quarterlyReports"]
            if len(quarterly_reports) < 16:
                raise Exception("Not enough quarterly data to compute revenue growth for last 3 years")
            latest_revenue = sum(float(q.get("totalRevenue", 0)) for q in quarterly_reports[:4])
            forth_year_revenue = sum(float(q.get("totalRevenue", 0)) for q in quarterly_reports[12:16])
            if forth_year_revenue:
                return ((latest_revenue - forth_year_revenue) / forth_year_revenue) * 100
            else:
                return None
        except (IndexError, KeyError, ValueError):
            return None

    # 14. Check if share outstanding < 500MM (500 million)
    def is_shares_outstanding_less_than_500MM(self):
        try:
            shares = float(self.overview.get("SharesOutstanding", 0))
            return shares < 500_000_000
        except ValueError:
            return False

    # 15. Equity multiplier = totalAssets / totalShareholderEquity (from Balance Sheet latest annual report)
    def get_equity_multiplier(self):
        try:
            latest = self.balance_sheet["quarterlyReports"][0]
            total_assets = float(latest.get("totalAssets", 0))
            total_equity = float(latest.get("totalShareholderEquity", 0))
            if total_equity:
                return total_assets / total_equity
            else:
                return None
        except (IndexError, KeyError, ValueError):
            return None

    # 16. Operating income 1yr growing rate in %
    def get_operating_income_growth_rate_1yr(self):
        try:
            quarterly_reports = self.income_statement["quarterlyReports"][:8]
            if len(quarterly_reports) < 8:
                raise Exception("Not enough quarterly data to compute operating income growth rate for last 1 years")
            latest = sum(float(q.get("operatingIncome", 0)) for q in quarterly_reports[:4])
            previous = sum(float(q.get("operatingIncome", 0)) for q in quarterly_reports[4:8])
            if previous:
                return ((latest - previous) / previous) * 100
            else:
                return None
        except (IndexError, KeyError, ValueError):
            return None

    # 17. How many years does EPS > 0 in last 3 years? (from Earnings annual data)
    def get_eps_positive_years_last_3(self):
        try:
            annual_earnings = self.earnings.get("annualEarnings", [])[:3]
            count = 0
            for entry in annual_earnings:
                eps = float(entry.get("reportedEPS", 0))
                if eps > 0:
                    count += 1
            return count
        except (KeyError, ValueError):
            return None

    # 18. If the current ROE is the highest in the trailing years.
    #    Here we compute ROE for each of the available annual periods using: ROE = netIncome / totalShareholderEquity.
    #    We then compare the current (latest) ROE with the previous periods.
    def is_current_roe_highest(self):
        try:
            quarter_is = self.income_statement["quarterlyReports"]
            quarter_bs = self.balance_sheet["quarterlyReports"]
            n_periods = min(len(quarter_is), len(quarter_bs), 4)
            if n_periods == 0:
                return False
            roe_list = []
            for i in range(n_periods):
                net_income = float(quarter_is[i].get("netIncome", 0))
                total_equity = float(quarter_bs[i].get("totalShareholderEquity", 0))
                if total_equity:
                    roe = net_income / total_equity
                    roe_list.append(roe)
            if not roe_list:
                return False
            current_roe = roe_list[0]
            # Check if the current ROE is strictly higher than all trailing periods
            return current_roe == max(roe_list)
        except (IndexError, KeyError, ValueError):
            return False


if __name__ == '__main__':
    # Example usage:
    ticker = 'AAPL'

    try:
        company = CompanyFinancials(ticker)

        print(f"Latest stock price for {ticker}: {company.get_latest_stock_price()}")
        print(f"Market Cap: {company.get_market_cap()}")
        print(f"P/E Ratio: {company.get_pe_ratio()}")
        print(f"Operating Income (Trailing Annual): {company.get_operating_income_trailing()}")
        print(f"Net Income (Trailing Annual): {company.get_net_income_trailing()}")
        print(f"ROE (Trailing Annual): {company.get_roe_trailing()}")
        print(f"ROA (Trailing Annual): {company.get_roa_trailing()}")
        print(f"Revenue (Trailing Annual): {company.get_revenue_trailing()}")
        print(f"Gross Margin (Trailing Annual): {company.get_gross_margin_trailing()}")
        print(f"Book Value per Share Growth Years (last 3 yrs): {company.get_book_value_growth_years_last_3()}")
        print(f"Revenue Growth Years (last 3 yrs): {company.get_revenue_growth_years_last_3()}")
        print(f"Quarters Revenue Growth (last 4 quarters): {company.get_quarters_revenue_growth_last_4()}")
        print(f"Revenue Growth Percent (last 3 yrs): {company.get_revenue_growth_percent_last_3()}")
        print(f"Shares outstanding less than 500MM? {company.is_shares_outstanding_less_than_500MM()}")
        print(f"Equity Multiplier: {company.get_equity_multiplier()}")
        print(f"Operating Income 1yr Growth Rate: {company.get_operating_income_growth_rate_1yr()}")
        print(f"EPS positive years (last 3 yrs): {company.get_eps_positive_years_last_3()}")
        print(f"Is Current ROE the highest? {company.is_current_roe_highest()}")

    except Exception as ex:
        print("An error occurred while fetching financial data:", ex)

    # To respect API rate limits, add delay if making multiple requests.
    time.sleep(12)
