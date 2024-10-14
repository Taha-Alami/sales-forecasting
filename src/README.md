# Sales Forecasting Project

## Project Overview

This project focuses on **sales forecasting** using time series models such as BATS, TBATS, and ARIMA. The model predicts future sales based on historical sales data. The project includes connection to a Snowflake database for data retrieval and model storage.

The project is structured in a modular way, making it easy to adjust and extend for different datasets or forecasting methods.

## Key Features

- **Snowflake Integration**: Fetch historical sales data from Snowflake.
- **Time Series Models**: BATS, TBATS, and ARIMA models for forecasting.
- **Confidence Intervals**: Generate forecasted values with confidence intervals.
- **Modular Design**: Easily swap models and data sources.

## Project Structure
sales-forecasting/
├── src/
│   ├── main.py               # Main script for sales forecasting
│   ├── utils.py              # Utility functions for Snowflake connection, data reading, and model training
│   ├── settings.py           # Settings configuration for Snowflake and logging
├── .env                      # Environment variables (credentials)
├── README.md                 # Project documentation
├── requirements.txt  requirements.txt          # Python dependencies

## Setup and Installation

### Prerequisites

- Python 3.8+
- Snowflake account credentials
- Azure Key Vault for storing sensitive credentials

### Step-by-Step Installation

1. Clone the repository:
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables in a `.env` file:
    ```
    SNOWFLAKE_USER=<your_snowflake_user>
    SNOWFLAKE_PASSWORD=<your_snowflake_password>
    SNOWFLAKE_ACCOUNT=<your_snowflake_account>
    SNOWFLAKE_DATABASE=<your_database>
    SNOWFLAKE_SCHEMA=<your_schema>
    ```

4. Run the sales forecasting script:
    ```bash
    python src/main.py --prediction_total_file_path <output_path>
    ```

## Usage

- The main forecasting script can be run via command line using the `main.py` script. Make sure to provide the appropriate file paths and ensure Snowflake credentials are available either in the environment or Azure Key Vault.
  
- Forecasted results will be saved in a pickle file specified by the argument `--prediction_total_file_path`.

## Models Used

- **BATS**: Suitable for seasonal time series with Box-Cox transformation.
- **TBATS**: Similar to BATS but adds additional flexibility for complex seasonal data.
- **ARIMA**: A popular time series model for forecasting with autoregressive properties.

## License

This project is licensed under the MIT License.
