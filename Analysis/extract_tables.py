import pdfplumber
import pandas as pd
import re

pdf_path = 'Bao_Cao_Supply_Chain_Hoan_Chinh.pdf'

def clean_value(val, is_no_format=False):
    if val is None:
        return val
    # Remove newlines
    val = val.replace('\n', ' ').strip()
    
    # Check if it looks like a formatted number from the PDF
    if re.match(r'^-?\d{1,3}(,\d{3})*(\.\d+)?$', val) or re.match(r'^-?\d+(\.\d+)?$', val):
        # Remove '.0' at the end
        if val.endswith('.0'):
            val = val[:-2]
            
        if is_no_format:
            # For year or ID, remove commas (e.g. 2,012 -> 2012)
            val = val.replace(',', '')
        else:
            # Convert to VN format: dot for thousand separator, comma for decimal
            if '.' in val:
                val = val.replace(',', 'X').replace('.', ',').replace('X', '.')
            else:
                val = val.replace(',', '.')
    return val

with pdfplumber.open(pdf_path) as pdf:
    table_index = 1
    tracking_data = []
    tracking_columns = []
    
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if not table or not table[0]:
                continue
            
            cleaned_table = []
            for row_idx, row in enumerate(table):
                cleaned_row = []
                for col_idx, cell in enumerate(row):
                    # Table 1: index 1, col 0 is year
                    # Table 2: index 2, col 0 is year
                    # Table 5: index 5, col 0 is ID
                    is_no_format = (table_index in [1, 2, 5] and col_idx == 0)
                    cleaned_row.append(clean_value(cell, is_no_format=is_no_format))
                cleaned_table.append(cleaned_row)
                
            if table_index == 1:
                tracking_columns = cleaned_table[0]
                tracking_data.extend(cleaned_table[1:])
            elif table_index == 2:
                tracking_data.extend(cleaned_table)
                df = pd.DataFrame(tracking_data, columns=tracking_columns)
                df.to_csv('clean_table_tracking.csv', index=False, encoding='utf-8-sig')
            else:
                df = pd.DataFrame(cleaned_table[1:], columns=cleaned_table[0])
                if table_index == 3:
                    name = 'clean_table_profit.csv'
                elif table_index == 4:
                    name = 'clean_table_risk.csv'
                elif table_index == 5:
                    name = 'clean_table_stop_selling.csv'
                else:
                    name = f'clean_table_{table_index}.csv'
                
                df.to_csv(name, index=False, encoding='utf-8-sig')
                
            table_index += 1

import os
# Dọn dẹp các file cũ không dùng
for i in range(1, 6):
    old_file = f'clean_table_{i}.csv'
    if os.path.exists(old_file):
        os.remove(old_file)

print("Hoan tat trich xuat, chuan hoa va don dep cac file cu!")
