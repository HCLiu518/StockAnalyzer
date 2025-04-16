import time

from dotenv import load_dotenv

from CompanyFinancials import CompanyFinancials
from GoogleSheetsUploader import GoogleSheetsUploader
from Tickers import Tickers

load_dotenv()

tickers = Tickers()
sheets_uploader = GoogleSheetsUploader()

for ticker in tickers.data.keys():
    print(f"Start processing ticker {ticker}")
    if tickers.data[ticker].asset_type != 'Stock' or tickers.data[ticker].status != 'Active':
        continue
    body = [
        ticker,
        tickers.data[ticker].name
    ]
    try:
        companyFinancials = CompanyFinancials(ticker)
        body += [
            companyFinancials.get_latest_stock_price(),
            companyFinancials.get_market_cap(),
            companyFinancials.get_pe_ratio(),
            companyFinancials.get_operating_income_trailing(),
            companyFinancials.get_net_income_trailing(),
            companyFinancials.get_roe_trailing(),
            companyFinancials.get_roa_trailing(),
            companyFinancials.get_revenue_trailing(),
            companyFinancials.get_gross_margin_trailing(),
            companyFinancials.get_book_value_growth_years_last_3(),
            companyFinancials.get_revenue_growth_years_last_3(),
            companyFinancials.get_quarters_revenue_growth_last_4(),
            companyFinancials.get_revenue_growth_percent_last_3(),
            companyFinancials.is_shares_outstanding_less_than_500MM(),
            companyFinancials.get_equity_multiplier(),
            companyFinancials.get_operating_income_growth_rate_1yr(),
            companyFinancials.get_eps_positive_years_last_3(),
            companyFinancials.is_current_roe_highest(),
            companyFinancials.calculate_score()
        ]
        print(f"Updating ticker {ticker} with body {body}")
        sheets_uploader.append_row(body)
        print(f"Finished processing ticker {ticker}")
    except Exception as err:
        print(f"Error processing ticker {ticker}: {err}")

    time.sleep(5)
