class TickerData:
    """
    Class that encapsulates ticker information.
    Expected attributes:
        - symbol: Ticker symbol
        - name: Company name
        - exchange: Exchange where the stock is listed
        - asset_type: Type of asset (usually 'Stock')
        - ipo_date: IPO date of the company
        - delisting_date: Delisting date (if applicable, else may be empty)
        - status: The listing status (e.g., 'Active')
    """
    def __init__(self, symbol, name, exchange, asset_type, ipo_date, delisting_date, status):
        self.symbol = symbol
        self.name = name
        self.exchange = exchange
        self.asset_type = asset_type
        self.ipo_date = ipo_date
        self.delisting_date = delisting_date
        self.status = status

    def __repr__(self):
        return (f"TickerData(symbol={self.symbol}, name={self.name}, exchange={self.exchange}, " 
                f"asset_type={self.asset_type}, ipo_date={self.ipo_date}, "
                f"delisting_date={self.delisting_date}, status={self.status})")