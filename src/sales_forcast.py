import numpy as np
import pandas as pd
from pmdarima.arima import auto_arima
from tbats import BATS, TBATS
from dateutil.relativedelta import relativedelta
from snowflake.connector.pandas_tools import write_pandas 
import argparse
import warnings

# Utility imports (these functions should be generic in your portfolio)
from src.utils import read_data, bats_model, snowflake_connection

warnings.filterwarnings("ignore")

def prepare_prediction():
    """
    Function to forecast sales for the next 2 years (24 months) using a BATS model.
    Generates predictions and confidence intervals, and stores them in a data store.
    """

    # Argument parser for prediction file path
    parser = argparse.ArgumentParser()
    parser.add_argument("--prediction_total_file_path", type=str, help="Path to save the prediction data")
    args = parser.parse_args()

    # Step 1: Load historical sales data
    ctx, _ = snowflake_connection()
    data = read_data('2016', ctx)  # Read historical sales data starting from 2016

    # Step 2: Prepare time steps for future sales prediction (2 years)
    date_max = data.index.max().date()
    steps = 24 - date_max.month  # Predict for 24 months ahead (2 years)
    future_dates = [date_max + relativedelta(months=idx) for idx in range(1, steps + 1)]

    # Step 3: Train BATS model and make sales predictions
    fitted_model = bats_model(data)
    prediction = pd.DataFrame(fitted_model.forecast(steps=steps), index=future_dates)
    prediction.columns = ['predicted_sales']  # Sales-specific terminology
    prediction['prediction_date'] = date_max

    # Step 4: Update historical data with predictions
    data_updated = data.copy()
    data_updated.loc[prediction.index[0]] = [prediction['predicted_sales'].iloc[0]]
    data_updated.index.name = 'Date'
    data_updated['prediction_date'] = date_max
    data_updated.index = pd.to_datetime(data_updated.index)
    data_updated = data_updated[data_updated.index.year >= date_max.year]  # Filter recent data
    prediction.index.name = 'Date'
    data_prediction = pd.concat([data_updated, prediction])

    # Step 5: Save the prediction data locally
    data_prediction.to_pickle(args.prediction_total_file_path)

    # Step 6: Prepare confidence intervals for the sales predictions
    confidence_levels = [0.85, 0.9, 0.95]  # Confidence intervals (85%, 90%, 95%)
    prediction_conf_total = pd.DataFrame()

    for confidence in confidence_levels:
        _, confidence_interval = fitted_model.forecast(steps=steps, confidence_level=confidence)
        prediction_conf = pd.DataFrame({'DATE': future_dates})
        prediction_conf['LOWER_BOUND'] = confidence_interval['lower_bound']
        prediction_conf['UPPER_BOUND'] = confidence_interval['upper_bound']
        prediction_conf['CONFIDENCE_LEVEL'] = [confidence] * prediction_conf.shape[0]
        prediction_conf_total = pd.concat([prediction_conf_total, prediction_conf])

    # Step 7: Save confidence intervals to the database (Snowflake)
    ctx, cs = snowflake_connection()  # Reusing connection
    write_pandas(conn=ctx, df=prediction_conf_total, table_name='SALES_CONFIDENCE_INTERVALS')

if __name__ == "__main__":
    prepare_prediction()