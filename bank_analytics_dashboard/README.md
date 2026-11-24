# BankSight — Banking Analytics Dashboard

A beginner-friendly Streamlit dashboard for transaction monitoring, customer/account analysis, and income/branch performance.

## Dataset (Kaggle)

Use **Banking and Customer Transaction Data** by Yogesh Tekawade:
https://www.kaggle.com/datasets/yogeshtekawade/banking-and-customer-transaction-data

The dataset is described as synthetic and includes customer, transaction/investment, and branch financial-performance data.

## 1. Download the data
1. Open the Kaggle dataset page above and sign in if Kaggle asks.
2. Download the dataset ZIP and extract it.
3. Copy the three CSV files into this project's `data` folder.
4. The app recognizes these common names:
   - `customer_data.csv` or `synthetic_customer_data.csv`
   - `transaction_data.csv` or `synthetic_transaction_data.csv`
   - `bank_data.csv` or `synthetic_bank_data.csv`

If the downloaded filenames differ, rename them to `customer_data.csv`, `transaction_data.csv`, and `bank_data.csv`.

## 2. Install and run (Windows)
Install Python 3.10+ if it is not already installed. Open Command Prompt in this project folder and run:

```bash
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

The dashboard opens in your browser. Keep the Command Prompt window open while using it.

## Dashboard pages
- Overview: KPI cards, monthly transaction count, transaction value by type.
- Transactions: amount distribution, transaction mix, filtered transaction table.
- Customers & accounts: customer types, age/income distribution, customer table.
- Income & branches: revenue, expenses, estimated profit, revenue by city/region.

## Notes
- The app attempts to recognize common variations of column names.
- If a chart is blank, check the CSV header names and compare them with the aliases in `app.py`.
- This dataset is synthetic, not confidential customer data.
- Revenue less expenses is shown as a simple calculated indicator, not audited net income.
