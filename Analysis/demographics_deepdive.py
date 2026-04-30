import pandas as pd
import json

orders = pd.read_csv('orders.csv')

# 1. Device behavior (if exists)
if 'device' in orders.columns:
    device_stats = orders.groupby('device').size() / len(orders) * 100
    print("--- Device Stats ---")
    print(device_stats)

# 2. Payment methods
if 'payment_method' in orders.columns:
    payment_stats = orders.groupby('payment_method').size() / len(orders) * 100
    print("\n--- Payment Methods ---")
    print(payment_stats)

# 3. Installments
if 'payment_installments' in orders.columns:
    inst_stats = orders.groupby('payment_installments').size() / len(orders) * 100
    print("\n--- Installments ---")
    print(inst_stats)
