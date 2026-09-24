import openpyxl
import pandas as pd

excel_path = "reports/vehicle_selection_44A_manual_review.xlsx"
csv_path = "reports/vehicle_selection_44A_case_ledger.csv"

print("--- EXCEL FILE SHEET NAMES ---")
wb = openpyxl.load_workbook(excel_path, read_only=True)
print(wb.sheetnames)

# Look at columns from the first sheet
sheet = wb.active
print("Active Sheet Title:", sheet.title)
for r in range(1, 5):
    row_vals = [sheet.cell(row=r, column=c).value for c in range(1, 20)]
    print(f"Row {r}:", row_vals)

print("\n--- CSV FILE HEAD ---")
df_csv = pd.read_csv(csv_path)
print("CSV columns:", df_csv.columns.tolist())
print(df_csv.head(2))

# Count Fixed-Wing cases in CSV
v_counts = df_csv["Selected Vehicle Family"].value_counts()
print("\nCSV Family counts:")
print(v_counts)

# Let's count in the Excel active sheet
row_count = 0
fw_excel_count = 0
# Read with pandas
df_excel = pd.read_excel(excel_path, sheet_name="MANUAL_REVIEW")
print("\nExcel MANUAL_REVIEW columns:", df_excel.columns.tolist())
print("Excel MANUAL_REVIEW head:")
print(df_excel.head(2))

# Value counts of Selected Vehicle in Excel
# Check column names:
v_col = None
for col in df_excel.columns:
    if "selected" in col.lower() or "vehicle" in col.lower() or "family" in col.lower():
        print(f"Potential column: {col}")
        v_col = col

if v_col:
    print(df_excel[v_col].value_counts())
