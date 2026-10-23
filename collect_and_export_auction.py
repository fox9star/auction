import requests
import json
import time
import os
import sys
from datetime import datetime, timedelta
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding='utf-8')

# 1. 법원경매 세션 설정
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8',
    'Referer': 'https://www.courtauction.go.kr/pgj/index.on'
})

# 권역 및 시도 매핑
REGION_MAP = {
    '수도권': [('11', '서울특별시'), ('41', '경기도'), ('28', '인천광역시')],
    '영남권(부울경)': [('26', '부산광역시'), ('31', '울산광역시'), ('48', '경상남도')],
    '영남권(대경권)': [('27', '대구광역시'), ('47', '경상북도')],
    '충청권': [('30', '대전광역시'), ('36', '세종특별자치시'), ('44', '충청남도'), ('43', '충청북도')],
    '호남권': [('29', '광주광역시'), ('46', '전라남도'), ('52', '전북특별자치도')],
    '강원·제주권': [('51', '강원특별자치도'), ('50', '제주특별자치도')]
}

def fetch_page(sd_cd, page_no=1, page_size=40, flbd_min="1", lcl="20000", mcl="20100", scl="20104"):
    payload = {
        "dma_pageInfo": {
            "pageNo": page_no, "pageSize": page_size, "bfPageNo": "", "startRowNo": "",
            "totalCnt": "", "totalYn": "Y" if page_no == 1 else "N", "groupTotalCount": ""
        },
        "dma_srchGdsDtlSrchInfo": {
            "rletDspslSpcCondCd": "", "bidDvsCd": "", "mvprpRletDvsCd": "00031R",
            "cortAuctnSrchCondCd": "0004601", "rprsAdongSdCd": sd_cd,
            "rprsAdongSggCd": "", "rprsAdongEmdCd": "", "rdnmSdCd": "", "rdnmSggCd": "", "rdnmNo": "",
            "mvprpDspslPlcAdongSdCd": "", "mvprpDspslPlcAdongSggCd": "", "mvprpDspslPlcAdongEmdCd": "",
            "rdDspslPlcAdongSdCd": "", "rdDspslPlcAdongSggCd": "", "rdDspslPlcAdongEmdCd": "",
            "cortOfcCd": "", "jdbnCd": "", "execrOfcDvsCd": "",
            "lclDspslGdsLstUsgCd": lcl, "mclDspslGdsLstUsgCd": mcl, "sclDspslGdsLstUsgCd": scl,
            "cortAuctnMbrsId": "", "aeeEvlAmtMin": "", "aeeEvlAmtMax": "",
            "lwsDspslPrcRateMin": "", "lwsDspslPrcRateMax": "",
            "flbdNcntMin": flbd_min, "flbdNcntMax": "",
            "objctArDtsMin": "", "objctArDtsMax": "",
            "mvprpArtclKndCd": "", "mvprpArtclNm": "", "mvprpAtchmPlcTypCd": "",
            "notifyLoc": "on", "lafjOrderBy": "", "pgmId": "PGJ151F01", "csNo": "",
            "cortStDvs": "2", "statNum": 1,
            "bidBgngYmd": datetime.now().strftime("%Y%m%d"),
            "bidEndYmd": (datetime.now() + timedelta(days=45)).strftime("%Y%m%d"),
            "dspslDxdyYmd": "", "fstDspslHm": "", "scdDspslHm": "", "thrdDspslHm": "", "fothDspslHm": "",
            "dspslPlcNm": "", "lwsDspslPrcMin": "", "lwsDspslPrcMax": "",
            "grbxTypCd": "", "gdsVendNm": "", "fuelKndCd": "", "carMdyrMax": "", "carMdyrMin": "", "carMdlNm": ""
        }
    }
    try:
        res = session.post('https://www.courtauction.go.kr/pgj/pgjsearch/searchControllerMain.on', json=payload, timeout=12)
        if res.status_code == 200:
            return res.json().get('data', {})
    except Exception as e:
        print(f"Error fetching sd_cd={sd_cd}, page={page_no}: {e}")
    return {}

print("대법원 경매정보 시스템(courtauction.go.kr) 실시간 데이터 수집 시작...")
all_items = []

for region_name, sidos in REGION_MAP.items():
    print(f"\n[{region_name}] 데이터 수집 중...")
    for sd_cd, sd_name in sidos:
        # 첫 페이지 조회로 전체 건수 확인
        data_first = fetch_page(sd_cd, page_no=1, page_size=40)
        page_info = data_first.get('dma_pageInfo', {})
        total_cnt = int(page_info.get('totalCnt', 0) or 0)
        items = data_first.get('dlt_srchResult', [])
        
        for item in items:
            item['regionGroup'] = region_name
            item['sidoName'] = sd_name
            all_items.append(item)
            
        print(f" - {sd_name}: 총 {total_cnt}건 중 1페이지({len(items)}건) 수집")
        
        # 총 페이지 계산 (최대 5페이지까지 수집하여 권역별 충분한 표본 확보)
        max_pages = min((total_cnt + 39) // 40, 5)
        for p in range(2, max_pages + 1):
            time.sleep(0.15)
            data_next = fetch_page(sd_cd, page_no=p, page_size=40)
            next_items = data_next.get('dlt_srchResult', [])
            for item in next_items:
                item['regionGroup'] = region_name
                item['sidoName'] = sd_name
                all_items.append(item)
            print(f"   * {sd_name} {p}페이지({len(next_items)}건) 추가 완료")

    # 권역별 수집 건수가 120건 미만이면 전체 용도(오피스텔/빌라/상가/단독 등)로 추가 수집하여 TOP 100 보장
    reg_curr_cnt = sum(1 for x in all_items if x.get('regionGroup') == region_name)
    if reg_curr_cnt < 120:
        for sd_cd, sd_name in sidos:
            for p in range(1, 4):
                time.sleep(0.12)
                data_more = fetch_page(sd_cd, page_no=p, page_size=40, flbd_min="", lcl="", mcl="", scl="")
                more_items = data_more.get('dlt_srchResult', [])
                if not more_items:
                    break
                for item in more_items:
                    item['regionGroup'] = region_name
                    item['sidoName'] = sd_name
                    all_items.append(item)
            print(f"   + [{region_name}] {sd_name} 전체용도 보강 수집 완료")

print(f"\n총 {len(all_items)}건의 경매 물건 수집 완료!")

# 2. 데이터 정제 및 권리분석 지표 산출
processed_items = []
seen_keys = set()

# 위험 키워드 (특수권리/주의사항)
RISK_KEYWORDS = ['유치권', '지분', '법정지상권', '분묘', '가등기', '가처분', '재매각', '위반건축물', '맹지']

for it in all_items:
    # 중복 제거 (groupmaemulser 기준)
    unique_key = it.get('groupmaemulser') or f"{it.get('boCd')}_{it.get('saNo')}_{it.get('maemulSer')}"
    if unique_key in seen_keys:
        continue
    seen_keys.add(unique_key)
    
    # 금액 및 비율 계산
    try:
        appraisal_amt = int(it.get('gamevalAmt') or 0)
    except:
        appraisal_amt = 0
        
    try:
        min_price = int(it.get('notifyMinmaePrice1') or 0)
        if min_price == 0:
            min_price = int(it.get('minmaePrice') or 0)
    except:
        min_price = 0
        
    yuchal_cnt = int(it.get('yuchalCnt') or 0)
    
    # 최저가율 (감정가 대비 최저가 비율)
    if appraisal_amt > 0 and min_price > 0:
        ratio = round((min_price / appraisal_amt) * 100, 1)
        discount_rate = round(100 - ratio, 1)
    else:
        ratio = float(it.get('notifyMinmaePriceRate1') or 0)
        discount_rate = 100 - ratio if ratio > 0 else 0
        
    # 날짜 포맷
    mae_date = it.get('maeGiil', '')
    if len(mae_date) == 8:
        mae_date_fmt = f"{mae_date[:4]}-{mae_date[4:6]}-{mae_date[6:8]}"
    else:
        mae_date_fmt = mae_date
        
    # 시간 포맷
    mae_time = it.get('maeHh1', '')
    if len(mae_time) == 4:
        mae_time_fmt = f"{mae_time[:2]}:{mae_time[2:]}"
    else:
        mae_time_fmt = mae_time
        
    # 비고란 리스크 분석
    mul_bigo = it.get('mulBigo') or ''
    has_risk = any(rk in mul_bigo for rk in RISK_KEYWORDS)
    risk_label = "주의물건" if has_risk else "일반(안전)"
    
    # 추천 점수 산출
    # 기본 조건: 아파트/주거용, 특수권리 위험 키워드 없음, 유찰 1~3회 (할인율 20%~50%)
    score = 0
    if not has_risk:
        score += 50
    if 1 <= yuchal_cnt <= 3:
        score += 30
    if discount_rate >= 30:
        score += 20
        
    processed_items.append({
        'region': it.get('regionGroup'),
        'sido': it.get('sidoName'),
        'court': it.get('jiwonNm', ''),
        'dept': it.get('jpDeptNm', ''),
        'tel': it.get('tel', ''),
        'case_no': it.get('srnSaNo', ''),
        'item_no': it.get('maemulSer', '1'),
        'usage': it.get('dspslUsgNm', '아파트'),
        'address': it.get('printSt', ''),
        'spec': it.get('convAddr', ''),
        'appraisal': appraisal_amt,
        'min_price': min_price,
        'ratio': ratio,
        'discount_rate': discount_rate,
        'yuchal': yuchal_cnt,
        'date': mae_date_fmt,
        'time': mae_time_fmt,
        'place': it.get('maePlace', ''),
        'remarks': mul_bigo,
        'risk_label': risk_label,
        'score': score
    })

print(f"데이터 정제 완료: 총 {len(processed_items)}건 유효 물건 분석 완료")

# 3. 엑셀 워크북 생성
wb = openpyxl.Workbook()
wb.remove(wb.active) # 기본 시트 제거

# 스타일 정의
font_title = Font(name='맑은 고딕', size=16, bold=True, color='1A365D')
font_subtitle = Font(name='맑은 고딕', size=10, color='4A5568')
font_header = Font(name='맑은 고딕', size=10, bold=True, color='FFFFFF')
font_body = Font(name='맑은 고딕', size=9)
font_bold = Font(name='맑은 고딕', size=9, bold=True)
font_link = Font(name='맑은 고딕', size=9, color='0000FF', underline='single')

fill_navy = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
fill_teal = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')
fill_highlight = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid')
fill_safe = PatternFill(start_color='E2EFDA', end_color='E2EFDA', fill_type='solid')
fill_warn = PatternFill(start_color='FCE4D6', end_color='FCE4D6', fill_type='solid')

border_thin = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='D9D9D9'),
    bottom=Side(style='thin', color='D9D9D9')
)

align_center = Alignment(horizontal='center', vertical='center', wrap_text=True)
align_left = Alignment(horizontal='left', vertical='center', wrap_text=True)
align_right = Alignment(horizontal='right', vertical='center')

# ----------------------------------------------------
# 시트 1: 권역별 추천 베스트 물건 (Top Picks)
# ----------------------------------------------------
ws_rec = wb.create_sheet(title="권역별_추천_베스트물건")
ws_rec.views.sheetView[0].showGridLines = True

# 타이틀
ws_rec.cell(row=1, column=1, value="🏆 대법원 법원경매 권역별 가성비 최고 추천 물건 (실시간 분석)").font = font_title
ws_rec.cell(row=2, column=1, value=f"기준일자: {datetime.now().strftime('%Y-%m-%d')} | 데이터 출처: 대한민국 법원경매정보(courtauction.go.kr) | 선별기준: 권리분석 안전(특수권리 無), 유찰 1~3회, 높은 할인율").font = font_subtitle
ws_rec.row_dimensions[1].height = 30
ws_rec.row_dimensions[2].height = 20

rec_headers = [
    "추천순위", "권역", "시·도", "관할법원", "사건번호", "물건번호", "용도",
    "소재지 및 아파트명", "면적/내역", "감정평가액(원)", "최저매각가격(원)",
    "최저가율(%)", "할인율(%)", "유찰횟수", "매각기일", "권리분석/안전성", "추천 사유 및 투자 포인트"
]

ws_rec.row_dimensions[4].height = 28
for col_idx, h in enumerate(rec_headers, start=1):
    c = ws_rec.cell(row=4, column=col_idx, value=h)
    c.font = font_header
    c.fill = fill_navy
    c.alignment = align_center
    c.border = border_thin

# 권역별 베스트 물건 선별 (권역당 2~3개씩 총 15개 내외)
top_recommendations = []
for reg in REGION_MAP.keys():
    reg_items = [it for it in processed_items if it['region'] == reg and it['risk_label'] == "일반(안전)"]
    # 점수 높은 순 -> 할인율 높은 순 정렬
    reg_items.sort(key=lambda x: (x['score'], x['discount_rate']), reverse=True)
    # 상위 2~3개 추출
    top_recommendations.extend(reg_items[:3])

row_curr = 5
for idx, r in enumerate(top_recommendations, start=1):
    ws_rec.row_dimensions[row_curr].height = 24
    
    # 추천 사유 생성
    reason = f"감정가 대비 {r['discount_rate']}% 저렴한 최저가. 특수권리 없는 소멸주의 안전 물건으로 실거주 및 시세차익형 접근 유망."
    if r['yuchal'] >= 2:
        reason = f"유찰 {r['yuchal']}회로 가격 메리트 극대화({r['discount_rate']}% 할인). 인근 급매 시세 확인 후 안전마진 확보 가능."
        
    vals = [
        idx, r['region'], r['sido'], r['court'], r['case_no'], r['item_no'], r['usage'],
        r['address'], r['spec'], r['appraisal'], r['min_price'],
        f"{r['ratio']}%", f"{r['discount_rate']}%", f"{r['yuchal']}회", r['date'],
        "✅ 안전 (특수권리 없음)", reason
    ]
    
    for c_idx, val in enumerate(vals, start=1):
        cell = ws_rec.cell(row=row_curr, column=c_idx, value=val)
        cell.font = font_body
        cell.border = border_thin
        
        # 정렬 및 서식
        if c_idx in [1, 2, 3, 5, 6, 7, 12, 13, 14, 15]:
            cell.alignment = align_center
        elif c_idx in [10, 11]:
            cell.alignment = align_right
            cell.number_format = '#,##0'
        elif c_idx in [16]:
            cell.alignment = align_center
            cell.fill = fill_safe
            cell.font = font_bold
        else:
            cell.alignment = align_left
            
    row_curr += 1

# ----------------------------------------------------
# 시트 2: 전국 수집 물건 전체 목록
# ----------------------------------------------------
ws_all = wb.create_sheet(title="전국_경매물건_전체목록")
ws_all.views.sheetView[0].showGridLines = True

ws_all.cell(row=1, column=1, value="📋 대한민국 법원경매 전국 아파트/주거용 물건 현황").font = font_title
ws_all.cell(row=2, column=1, value=f"총 {len(processed_items)}개 물건 정리 완료 (정렬: 권역별 > 시도별 > 유찰횟수 높은 순)").font = font_subtitle
ws_all.row_dimensions[1].height = 30
ws_all.row_dimensions[2].height = 20

all_headers = [
    "번호", "권역", "시·도", "관할법원", "담당계", "사건번호", "물건번호", "용도",
    "소재지(주소)", "건물 및 면적 내역", "감정평가액(원)", "최저매각가격(원)",
    "최저가율(%)", "할인율(%)", "유찰횟수", "매각기일", "매각시간", "매각장소",
    "권리구분", "비고(특이사항)"
]

ws_all.row_dimensions[4].height = 28
for col_idx, h in enumerate(all_headers, start=1):
    c = ws_all.cell(row=4, column=col_idx, value=h)
    c.font = font_header
    c.fill = fill_teal
    c.alignment = align_center
    c.border = border_thin

# 정렬: 권역 -> 할인율 높은 순
processed_items.sort(key=lambda x: (x['region'], -x['discount_rate']))

row_curr = 5
for idx, it in enumerate(processed_items, start=1):
    ws_all.row_dimensions[row_curr].height = 22
    vals = [
        idx, it['region'], it['sido'], it['court'], it['dept'], it['case_no'], it['item_no'], it['usage'],
        it['address'], it['spec'], it['appraisal'], it['min_price'],
        f"{it['ratio']}%", f"{it['discount_rate']}%", f"{it['yuchal']}회", it['date'], it['time'], it['place'],
        it['risk_label'], it['remarks']
    ]
    for c_idx, val in enumerate(vals, start=1):
        cell = ws_all.cell(row=row_curr, column=c_idx, value=val)
        cell.font = font_body
        cell.border = border_thin
        
        if c_idx in [1, 2, 3, 5, 7, 8, 13, 14, 15, 16, 17]:
            cell.alignment = align_center
        elif c_idx in [11, 12]:
            cell.alignment = align_right
            cell.number_format = '#,##0'
        elif c_idx == 19:
            cell.alignment = align_center
            if it['risk_label'] == '주의물건':
                cell.fill = fill_warn
                cell.font = font_bold
            else:
                cell.fill = fill_safe
        else:
            cell.alignment = align_left
            
    row_curr += 1

# 열 너비 자동 조정
for ws in [ws_rec, ws_all]:
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            # 헤더/타이틀 제외 본문 위주 계산
            if cell.row > 3 and cell.value:
                val_str = str(cell.value)
                # 한글 고려 대략적 폭 계산
                length = sum(2 if ord(ch) > 127 else 1 for ch in val_str)
                if length > max_len:
                    max_len = length
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 11), 55)

# 특정 중요 열 수동 조정
ws_rec.column_dimensions['A'].width = 10
ws_rec.column_dimensions['D'].width = 18
ws_rec.column_dimensions['E'].width = 15
ws_rec.column_dimensions['H'].width = 45
ws_rec.column_dimensions['I'].width = 30
ws_rec.column_dimensions['Q'].width = 50

ws_all.column_dimensions['A'].width = 8
ws_all.column_dimensions['D'].width = 18
ws_all.column_dimensions['F'].width = 15
ws_all.column_dimensions['I'].width = 45
ws_all.column_dimensions['J'].width = 30
ws_all.column_dimensions['T'].width = 35

output_filename = "대한민국법원_전국경매물건_정리_및_권역별추천.xlsx"
output_path_aiwork = os.path.join(r"C:\Users\wood\Desktop\aiwork\auction", output_filename)
output_path = os.path.join(r"c:\Users\wood\Desktop\auction", output_filename)
wb.save(output_path_aiwork)
try:
    wb.save(output_path)
except Exception:
    pass
print(f"\n✅ 엑셀 파일 저장 완료: {output_path_aiwork} (총 {len(processed_items)}건)")


