import pandas as pd
import os

target_dates = ['2013-01-01', '2013-01-02', '2013-01-03', '2013-01-04']

# Process orders.csv
print("Processing orders.csv...")
df_orders = pd.read_csv('orders.csv')
for date in target_dates:
    df_filtered = df_orders[df_orders['order_date'] == date]
    df_filtered.to_csv(f'Data_Analysis/orders_{date}.csv', index=False)

# Process web_traffic.csv
print("Processing web_traffic.csv...")
df_wt = pd.read_csv('web_traffic.csv')
for date in target_dates:
    df_filtered = df_wt[df_wt['date'] == date]
    df_filtered.to_csv(f'Data_Analysis/web_traffic_{date}.csv', index=False)

print("Extraction completed!")
