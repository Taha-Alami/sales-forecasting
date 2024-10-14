import pandas as pd
from tbats import BATS, TBATS
from pmdarima.arima import auto_arima
import snowflake.connector
from snowflake.connector import SnowflakeConnection
from settings import settings  # Importing settings for configuration

def snowflake_connection() -> tuple[SnowflakeConnection, snowflake.connector.cursor]:
    """
    Establishes a connection to Snowflake using credentials from the settings module.
    
    Returns:
        tuple: Snowflake connection and cursor objects.
    """
    ctx = snowflake.connector.connect(
        user=settings.SNOWFLAKE_USER,
        password=settings.SNOWFLAKE_PASSWORD,
        account=settings.ACCOUNT,
        role=settings.ROLE,
        warehouse=settings.DATAWAREHOUSE,
        database=settings.DATABASE,
        schema=settings.SCHEMA
    )
    cs = ctx.cursor()
    try:
        cs.execute("SELECT current_version()")
        cs.fetchone()
    finally:
        cs.close()
    return ctx, cs


def read_data(start_date: str, ctx: SnowflakeConnection) -> pd.DataFrame:
    """
    Reads sales data from the Snowflake database, filters, and returns it.
    
    Args:
        start_date (str): Start date for data filtering in 'YYYY-MM-DD' format.
        ctx (SnowflakeConnection): Snowflake connection object.
    
    Returns:
        pd.DataFrame: Processed sales data with dates as index.
    """
    query = """
    SELECT DATE(FK_DATE, 'YYYYMMDD') AS date, "code_marche", "CA" AS sales 
    FROM sales_data 
    WHERE year(FK_DATE) >= 2018 
    ORDER BY date ASC
    """
    data = pd.read_sql(query, ctx)
    data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')
    data = data.groupby("date", as_index=False)['sales'].sum()
    
    data.rename(columns={'sales': 'Sales'}, inplace=True)
    data = data[data['Sales'].notna() & (data['Sales'] != 0)]
    data.set_index('date', inplace=True)
    
    return data[data.index >= start_date]


def bats_model(data: pd.DataFrame) -> BATS:
    """
    Trains and fits a BATS model on the provided sales data.
    
    Args:
        data (pd.DataFrame): Historical sales data.
    
    Returns:
        BATS: Fitted BATS model.
    """
    estimator = BATS(seasonal_periods=[12], use_arma_errors=True, use_box_cox=True)
    return estimator.fit(data)


def arima_model(data: pd.DataFrame) -> auto_arima:
    """
    Trains and fits an ARIMA model on the provided sales data.
    
    Args:
        data (pd.DataFrame): Historical sales data.
    
    Returns:
        auto_arima: Fitted ARIMA model.
    """
    return auto_arima(data, start_p=0, d=1, start_q=0, max_p=5, max_d=10, max_q=10,
                      seasonal=True, m=12, stepwise=False, n_fits=10000)


def tbats_model(data: pd.DataFrame) -> TBATS:
    """
    Trains and fits a TBATS model on the provided sales data.
    
    Args:
        data (pd.DataFrame): Historical sales data.
    
    Returns:
        TBATS: Fitted TBATS model.
    """
    estimator = TBATS(seasonal_periods=[12], use_arma_errors=True, use_box_cox=True)
    return estimator.fit(data)
