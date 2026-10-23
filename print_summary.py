import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')
wb = openpyxl.load_workbook(r'c:\Users\wood\Desktop\auction\대한민국법원_전국경매물건_정리_및_권역별추천.xlsx', data_only=True)
ws = wb['권역별_추천_베스트물건']

for row in ws.iter_rows(min_row=4, max_row=23, values_only=True):
    # row: rank, region, sido, court, case_no, item_no, usage, address, spec, appraisal, min_price, ratio, discount, yuchal, date, safety, reason
    if row[0] == "추천순위":
        print(f"{'순위':<4} | {'권역':<8} | {'시도':<6} | {'법원':<10} | {'사건번호':<12} | {'감정가':<12} | {'최저가':<12} | {'할인율':<6} | {'소재지'}")
        print("-" * 100)
    else:
        print(f"{row[0]:<4} | {row[1]:<8} | {row[2]:<6} | {row[3]:<10} | {row[4]:<12} | {row[9]:>10,d}원 | {row[10]:>10,d}원 | {row[12]:<6} | {row[7]} ({row[8]})")

