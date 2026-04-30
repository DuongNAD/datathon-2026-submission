import re
filepath = r'e:\project\datathon-2026-round-1\Nop_bai\Bao_Cao_Chien_Luoc_Toan_Dien_Datathon.md'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all occurrences of width="<number> phần trăm" with width="<number>%"
new_content = re.sub(r'width="(\d+)\s*phần trăm"', r'width="\1%"', content)

# Check if anything changed
if new_content != content:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully replaced HTML width attributes.")
else:
    print("No matches found.")
