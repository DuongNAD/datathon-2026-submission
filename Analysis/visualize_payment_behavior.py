import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.patches import Patch

# Setup paths
data_dir = r"e:\project\datathon-2026-round-1"
nop_bai_dir = os.path.join(data_dir, "Nop_bai", "Images")
if not os.path.exists(nop_bai_dir):
    os.makedirs(nop_bai_dir)

print("Reading data...")
orders = pd.read_csv(os.path.join(data_dir, "orders.csv"))
payments = pd.read_csv(os.path.join(data_dir, "payments.csv"))

# Calculate proportions
device_stats = orders['device_type'].value_counts(normalize=True) * 100
payment_stats = payments['payment_method'].value_counts(normalize=True) * 100

# Group installments as requested by the PDF: 1 time, 3 months, 6+12 months (Other)
installments = payments['installments'].value_counts(normalize=True) * 100
inst_1 = installments.get(1, 0)
inst_3 = installments.get(3, 0)
inst_6_12 = installments.get(6, 0) + installments.get(12, 0)
inst_other = 100 - (inst_1 + inst_3 + inst_6_12)

installments_stats = pd.Series({
    'Thanh toán 1 lần': inst_1,
    'Trả góp 3 tháng': inst_3,
    'Trả góp 6 & 12 tháng': inst_6_12
})

# ==========================================
# VISUALIZATION 1: DEVICE TYPES (DONUT CHART)
# ==========================================
sns.set_theme(style="whitegrid")
plt.figure(figsize=(8, 8))

device_colors = ['#4A90E2', '#50E3C2', '#F5A623']
wedges, texts, autotexts = plt.pie(device_stats, labels=device_stats.index.str.title(), 
                                   autopct='%1.1f%%', startangle=90, colors=device_colors, 
                                   pctdistance=0.8,
                                   wedgeprops=dict(width=0.4, edgecolor='w'))
plt.title("THIẾT BỊ ĐẶT HÀNG", fontsize=16, fontweight='bold', pad=15)
plt.setp(autotexts, size=14, weight="bold", color="white")
plt.setp(texts, size=14)

legend_elements_a = [Patch(facecolor=device_colors[i], label=device_stats.index.str.title()[i]) for i in range(len(device_stats))]
plt.legend(handles=legend_elements_a, loc='upper right', bbox_to_anchor=(1.3, 1.0), frameon=False, fontsize=12)

plt.tight_layout()
chart1_path = os.path.join(nop_bai_dir, "5a_Device_Behavior.png")
plt.savefig(chart1_path, dpi=300, bbox_inches='tight')
print(f"Chart 1 saved to {chart1_path}")
plt.close()

# ==========================================
# VISUALIZATION 2: PAYMENT METHODS (BAR CHART)
# ==========================================
plt.figure(figsize=(10, 6))

payment_labels = payment_stats.index.str.replace('_', ' ').str.title()
ax2 = sns.barplot(x=payment_labels, y=payment_stats.values, 
                  hue=payment_labels, palette='viridis', legend=False)
plt.title("PHƯƠNG THỨC THANH TOÁN", fontsize=14, fontweight='bold', pad=15)
plt.ylabel("Tỷ lệ (%)", fontsize=12)
plt.xlabel("")

# Annotate bars
for p in ax2.patches:
    height = p.get_height()
    if height > 0:
        plt.text(p.get_x() + p.get_width()/2., height + 1, f'{height:.1f}%', ha="center", fontsize=11, fontweight='bold')
plt.ylim(0, 65)

plt.tight_layout()
chart2_path = os.path.join(nop_bai_dir, "5b_Payment_Methods.png")
plt.savefig(chart2_path, dpi=300, bbox_inches='tight')
print(f"Chart 2 saved to {chart2_path}")
plt.close()

# ==========================================
# VISUALIZATION 3: INSTALLMENTS (BAR CHART)
# ==========================================
plt.figure(figsize=(8, 6))

colors_inst = ['#8E44AD', '#E74C3C', '#F39C12']
ax3 = sns.barplot(x=installments_stats.index, y=installments_stats.values, 
                  hue=installments_stats.index, palette=colors_inst, legend=False)
plt.title("HÀNH VI TRẢ GÓP", fontsize=14, fontweight='bold', pad=50)
plt.ylabel("Tỷ lệ (%)", fontsize=12)
plt.xlabel("")
plt.ylim(0, 50)

# Annotate bars
for p in ax3.patches:
    height = p.get_height()
    if height > 0:
        plt.text(p.get_x() + p.get_width()/2., height + 1, f'{height:.1f}%', ha="center", fontsize=11, fontweight='bold')

labels_inst = installments_stats.index
legend_elements_c = [Patch(facecolor=colors_inst[i], label=labels_inst[i]) for i in range(len(labels_inst))]
plt.legend(handles=legend_elements_c, loc='lower center', bbox_to_anchor=(0.5, 1.02), ncol=3, frameon=False, fontsize=11)

plt.tight_layout()
chart3_path = os.path.join(nop_bai_dir, "5c_Installment_Behavior.png")
plt.savefig(chart3_path, dpi=300, bbox_inches='tight')
print(f"Chart 3 saved to {chart3_path}")
plt.close()
