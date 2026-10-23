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

def fetch_daejeon_page(page_no=1, page_size=40):
    payload = {
        "dma_pageInfo": {
            "pageNo": page_no, "pageSize": page_size, "bfPageNo": "", "startRowNo": "",
            "totalCnt": "", "totalYn": "Y" if page_no == 1 else "N", "groupTotalCount": ""
        },
        "dma_srchGdsDtlSrchInfo": {
            "rletDspslSpcCondCd": "", "bidDvsCd": "", "mvprpRletDvsCd": "00031R",
            "cortAuctnSrchCondCd": "0004601", "rprsAdongSdCd": "30", # 대전광역시
            "rprsAdongSggCd": "", "rprsAdongEmdCd": "", "rdnmSdCd": "", "rdnmSggCd": "", "rdnmNo": "",
            "mvprpDspslPlcAdongSdCd": "", "mvprpDspslPlcAdongSggCd": "", "mvprpDspslPlcAdongEmdCd": "",
            "rdDspslPlcAdongSdCd": "", "rdDspslPlcAdongSggCd": "", "rdDspslPlcAdongEmdCd": "",
            "cortOfcCd": "", "jdbnCd": "", "execrOfcDvsCd": "",
            "lclDspslGdsLstUsgCd": "", "mclDspslGdsLstUsgCd": "", "sclDspslGdsLstUsgCd": "",
            "cortAuctnMbrsId": "", "aeeEvlAmtMin": "", "aeeEvlAmtMax": "",
            "lwsDspslPrcRateMin": "", "lwsDspslPrcRateMax": "",
            "flbdNcntMin": "", "flbdNcntMax": "",
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
        print(f"Error fetching page {page_no}: {e}")
    return {}

print("대전광역시 전체 경매 물건 데이터 수집 시작...")
data_first = fetch_daejeon_page(page_no=1, page_size=40)
total_count = int(data_first.get('dma_pageInfo', {}).get('totalCnt', 0) or 0)
all_items = list(data_first.get('dlt_srchResult', []))
print(f"대전광역시 전체 경매 물건 수: {total_count}건 (1페이지 {len(all_items)}건 수집 완료)")

max_pages = (total_count + 39) // 40
for p in range(2, max_pages + 1):
    time.sleep(0.12)
    data = fetch_daejeon_page(page_no=p, page_size=40)
    items = data.get('dlt_srchResult', [])
    all_items.extend(items)
    print(f" -> {p}/{max_pages} 페이지 수집 완료 ({len(items)}건 추가)")

print(f"전체 수집 완료: 총 {len(all_items)}건")

# 중복 제거 및 데이터 정제
seen_keys = set()
cleaned_items = []

RISK_KEYWORDS = ['유치권', '지분', '법정지상권', '분묘', '가등기', '가처분', '재매각', '위반건축물', '맹지', '토지만매각', '건물만매각']

for it in all_items:
    unique_key = it.get('groupmaemulser') or f"{it.get('boCd')}_{it.get('saNo')}_{it.get('maemulSer')}_{it.get('mokmulSer')}"
    if unique_key in seen_keys:
        continue
    seen_keys.add(unique_key)
    
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
    
    if appraisal_amt > 0 and min_price > 0:
        ratio = round((min_price / appraisal_amt) * 100, 1)
        discount_rate = round(100 - ratio, 1)
    else:
        ratio = float(it.get('notifyMinmaePriceRate1') or 0)
        discount_rate = round(100 - ratio, 1) if ratio > 0 else 0
        
    mae_date = it.get('maeGiil', '')
    mae_date_fmt = f"{mae_date[:4]}-{mae_date[4:6]}-{mae_date[6:8]}" if len(mae_date) == 8 else mae_date
    
    mae_time = it.get('maeHh1', '')
    mae_time_fmt = f"{mae_time[:2]}:{mae_time[2:]}" if len(mae_time) == 4 else mae_time
    
    mul_bigo = it.get('mulBigo') or ''
    matched_risks = [rk for rk in RISK_KEYWORDS if rk in mul_bigo]
    has_risk = len(matched_risks) > 0
    risk_label = f"주의({','.join(matched_risks)})" if has_risk else "안전(소멸주의)"
    
    # ----------------------------------------------------
    # 다차원 가치 평가 점수 산정 모델 (100점 만점)
    # ----------------------------------------------------
    # 1. 가격 메리트 점수 (40점)
    if discount_rate >= 60:
        score_price = 40
    elif discount_rate >= 45:
        score_price = 32
    elif discount_rate >= 30:
        score_price = 25
    elif discount_rate >= 15:
        score_price = 18
    else:
        score_price = 10
        
    # 2. 권리 안전성 점수 (30점)
    if not has_risk:
        score_risk = 30
    else:
        # 지분이나 유치권 등 고위험은 큰 감점
        score_risk = -15
        
    # 3. 용도 및 환금성 점수 (20점)
    usg = it.get('dspslUsgNm', '')
    if any(k in usg for k in ['아파트', '주상복합']):
        score_usg = 20
    elif any(k in usg for k in ['오피스텔', '다세대', '연립', '빌라']):
        score_usg = 16
    elif any(k in usg for k in ['단독', '다가구', '상가주택']):
        score_usg = 14
    elif any(k in usg for k in ['근린생활', '상가', '점포', '업무']):
        score_usg = 12
    elif any(k in usg for k in ['대지', '주택용지']):
        score_usg = 10
    else:
        score_usg = 7
        
    # 4. 대전 자치구별 입지 점수 (10점)
    sigu = it.get('hjguSigu', '')
    addr = it.get('printSt', '')
    if '유성구' in sigu or '유성구' in addr:
        score_loc = 10
    elif '서구' in sigu or '서구' in addr:
        score_loc = 9
    elif '중구' in sigu or '중구' in addr:
        score_loc = 7
    elif '동구' in sigu or '동구' in addr:
        score_loc = 6
    elif '대덕구' in sigu or '대덕구' in addr:
        score_loc = 6
    else:
        score_loc = 5
        
    total_score = max(0, score_price + score_risk + score_usg + score_loc)
    
    # 종합 추천 사유 작성
    comments = []
    if not has_risk:
        comments.append("권리분석 안전(특수권리 없음)")
    else:
        comments.append(f"권리상 주의 요망({','.join(matched_risks)})")
        
    if discount_rate >= 50:
        comments.append(f"감정가 대비 {discount_rate}% 폭넓은 할인(유찰 {yuchal_cnt}회)")
    elif discount_rate >= 20:
        comments.append(f"감정가 대비 {discount_rate}% 저감(유찰 {yuchal_cnt}회)")
    else:
        comments.append("신건(1회차 진행)")
        
    if score_usg >= 16:
        comments.append("환금성·임대수요 우수 주거용")
    elif score_usg >= 12:
        comments.append("월세수익형 상업·근린시설")
        
    cleaned_items.append({
        'sido': '대전광역시',
        'sigu': sigu or '대전',
        'court': it.get('jiwonNm', '대전지방법원'),
        'dept': it.get('jpDeptNm', ''),
        'tel': it.get('tel', ''),
        'case_no': it.get('srnSaNo', ''),
        'item_no': it.get('maemulSer', '1'),
        'usage': usg,
        'address': addr,
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
        'score_price': score_price,
        'score_risk': score_risk,
        'score_usg': score_usg,
        'score_loc': score_loc,
        'total_score': total_score,
        'comment': " | ".join(comments)
    })

print(f"데이터 정제 완료: 총 {len(cleaned_items)}건")

# 높은 점수부터 낮은 점수 순으로 정렬
cleaned_items.sort(key=lambda x: (x['total_score'], x['discount_rate'], -x['appraisal']), reverse=True)

# TOP 100 선정
top_50 = cleaned_items[:100]
print(f"TOP 100 선정 완료! 최고 점수: {top_50[0]['total_score']}점, {len(top_50)}위 점수: {top_50[-1]['total_score']}점")

# 엑셀 워크북 생성
wb = openpyxl.Workbook()
wb.remove(wb.active)

font_title = Font(name='맑은 고딕', size=16, bold=True, color='1A365D')
font_subtitle = Font(name='맑은 고딕', size=10, color='4A5568')
font_header = Font(name='맑은 고딕', size=10, bold=True, color='FFFFFF')
font_body = Font(name='맑은 고딕', size=9)
font_bold = Font(name='맑은 고딕', size=9, bold=True)
font_rank = Font(name='맑은 고딕', size=10, bold=True, color='1F4E78')
font_score = Font(name='맑은 고딕', size=10, bold=True, color='C00000')

fill_navy = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
fill_blue = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')
fill_safe = PatternFill(start_color='E2EFDA', end_color='E2EFDA', fill_type='solid')
fill_warn = PatternFill(start_color='FCE4D6', end_color='FCE4D6', fill_type='solid')
fill_gold = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid')

border_thin = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='D9D9D9'),
    bottom=Side(style='thin', color='D9D9D9')
)

align_center = Alignment(horizontal='center', vertical='center', wrap_text=True)
align_left = Alignment(horizontal='left', vertical='center', wrap_text=True)
align_right = Alignment(horizontal='right', vertical='center')

# -------------------------------------------------------------------------
# 시트 1: 대전광역시 경매 TOP 50 추천 물건 (점수순)
# -------------------------------------------------------------------------
ws_top = wb.create_sheet(title="대전_경매_TOP50_추천")
ws_top.views.sheetView[0].showGridLines = True

ws_top.cell(row=1, column=1, value="🏆 대전광역시 법원경매 베스트 TOP 50 추천 물건 (가치·가격 정밀평가 순)").font = font_title
ws_top.cell(row=2, column=1, value=f"기준일자: {datetime.now().strftime('%Y-%m-%d')} | 데이터 출처: 대한민국 법원경매정보(courtauction.go.kr) | 평가모델: 가격할인율(40점)+권리안전성(30점)+용도환금성(20점)+입지선호도(10점)").font = font_subtitle
ws_top.row_dimensions[1].height = 32
ws_top.row_dimensions[2].height = 20

headers_top = [
    "추천순위", "종합점수", "자치구", "사건번호", "물건번호", "용도",
    "소재지(주소)", "건물/면적 내역", "감정평가액(원)", "최저매각가격(원)",
    "최저가율", "할인율", "유찰횟수", "매각기일", "담당계", "권리구분", "투자분석 및 추천코멘트"
]

ws_top.row_dimensions[4].height = 28
for col_idx, h in enumerate(headers_top, start=1):
    c = ws_top.cell(row=4, column=col_idx, value=h)
    c.font = font_header
    c.fill = fill_navy
    c.alignment = align_center
    c.border = border_thin

row_curr = 5
for rank, it in enumerate(top_50, start=1):
    ws_top.row_dimensions[row_curr].height = 24
    vals = [
        rank, it['total_score'], it['sigu'], it['case_no'], it['item_no'], it['usage'],
        it['address'], it['spec'], it['appraisal'], it['min_price'],
        f"{it['ratio']}%", f"{it['discount_rate']}%", f"{it['yuchal']}회", it['date'], it['dept'],
        it['risk_label'], it['comment']
    ]
    for c_idx, val in enumerate(vals, start=1):
        cell = ws_top.cell(row=row_curr, column=c_idx, value=val)
        cell.font = font_body
        cell.border = border_thin
        
        if c_idx == 1:
            cell.alignment = align_center
            cell.font = font_rank
            if rank <= 3:
                cell.fill = fill_gold
        elif c_idx == 2:
            cell.alignment = align_center
            cell.font = font_score
        elif c_idx in [3, 4, 5, 6, 11, 12, 13, 14, 15]:
            cell.alignment = align_center
        elif c_idx in [9, 10]:
            cell.alignment = align_right
            cell.number_format = '#,##0'
        elif c_idx == 16:
            cell.alignment = align_center
            if '주의' in it['risk_label']:
                cell.fill = fill_warn
            else:
                cell.fill = fill_safe
        else:
            cell.alignment = align_left
            
    row_curr += 1

# -------------------------------------------------------------------------
# 시트 2: 대전광역시 전체 경매 물건 목록
# -------------------------------------------------------------------------
ws_all = wb.create_sheet(title="대전_전체물건_전수목록")
ws_all.views.sheetView[0].showGridLines = True

ws_all.cell(row=1, column=1, value="📋 대전광역시 법원경매 진행 물건 전수 목록 (전체)").font = font_title
ws_all.cell(row=2, column=1, value=f"총 {len(cleaned_items)}건 수집 및 정렬 완료 (정렬: 종합점수 높은 순)").font = font_subtitle
ws_all.row_dimensions[1].height = 32
ws_all.row_dimensions[2].height = 20

headers_all = [
    "번호", "종합점수", "자치구", "사건번호", "물건번호", "용도",
    "소재지(주소)", "건물/면적 내역", "감정평가액(원)", "최저매각가격(원)",
    "최저가율", "할인율", "유찰횟수", "매각기일", "매각시간", "매각장소",
    "담당계", "연락처", "권리구분", "비고(특이사항)", "세부점수(가격/권리/용도/입지)"
]

ws_all.row_dimensions[4].height = 28
for col_idx, h in enumerate(headers_all, start=1):
    c = ws_all.cell(row=4, column=col_idx, value=h)
    c.font = font_header
    c.fill = fill_blue
    c.alignment = align_center
    c.border = border_thin

row_curr = 5
for idx, it in enumerate(cleaned_items, start=1):
    ws_all.row_dimensions[row_curr].height = 22
    sub_scores = f"{it['score_price']}/{it['score_risk']}/{it['score_usg']}/{it['score_loc']}"
    vals = [
        idx, it['total_score'], it['sigu'], it['case_no'], it['item_no'], it['usage'],
        it['address'], it['spec'], it['appraisal'], it['min_price'],
        f"{it['ratio']}%", f"{it['discount_rate']}%", f"{it['yuchal']}회", it['date'], it['time'], it['place'],
        it['dept'], it['tel'], it['risk_label'], it['remarks'], sub_scores
    ]
    for c_idx, val in enumerate(vals, start=1):
        cell = ws_all.cell(row=row_curr, column=c_idx, value=val)
        cell.font = font_body
        cell.border = border_thin
        
        if c_idx in [1, 2, 3, 4, 5, 6, 11, 12, 13, 14, 15, 17, 21]:
            cell.alignment = align_center
        elif c_idx in [9, 10]:
            cell.alignment = align_right
            cell.number_format = '#,##0'
        elif c_idx == 19:
            cell.alignment = align_center
            if '주의' in it['risk_label']:
                cell.fill = fill_warn
            else:
                cell.fill = fill_safe
        else:
            cell.alignment = align_left
            
    row_curr += 1

# 열 너비 수동 최적화
ws_top.column_dimensions['A'].width = 10
ws_top.column_dimensions['B'].width = 11
ws_top.column_dimensions['C'].width = 12
ws_top.column_dimensions['D'].width = 15
ws_top.column_dimensions['E'].width = 9
ws_top.column_dimensions['F'].width = 15
ws_top.column_dimensions['G'].width = 46
ws_top.column_dimensions['H'].width = 28
ws_top.column_dimensions['I'].width = 15
ws_top.column_dimensions['J'].width = 15
ws_top.column_dimensions['K'].width = 10
ws_top.column_dimensions['L'].width = 10
ws_top.column_dimensions['M'].width = 10
ws_top.column_dimensions['N'].width = 13
ws_top.column_dimensions['O'].width = 11
ws_top.column_dimensions['P'].width = 15
ws_top.column_dimensions['Q'].width = 45

ws_all.column_dimensions['A'].width = 8
ws_all.column_dimensions['B'].width = 10
ws_all.column_dimensions['C'].width = 12
ws_all.column_dimensions['D'].width = 15
ws_all.column_dimensions['E'].width = 9
ws_all.column_dimensions['F'].width = 15
ws_all.column_dimensions['G'].width = 46
ws_all.column_dimensions['H'].width = 28
ws_all.column_dimensions['I'].width = 15
ws_all.column_dimensions['J'].width = 15
ws_all.column_dimensions['K'].width = 10
ws_all.column_dimensions['L'].width = 10
ws_all.column_dimensions['M'].width = 10
ws_all.column_dimensions['N'].width = 13
ws_all.column_dimensions['O'].width = 10
ws_all.column_dimensions['P'].width = 18
ws_all.column_dimensions['Q'].width = 11
ws_all.column_dimensions['R'].width = 18
ws_all.column_dimensions['S'].width = 18
ws_all.column_dimensions['T'].width = 32
ws_all.column_dimensions['U'].width = 22

output_filename = "대전광역시_경매물건_TOP50_추천.xlsx"
output_path_aiwork = os.path.join(r"C:\Users\wood\Desktop\aiwork\auction", output_filename)
output_path = os.path.join(r"c:\Users\wood\Desktop\auction", output_filename)
wb.save(output_path_aiwork)
try:
    wb.save(output_path)
except Exception:
    pass
print(f"\n✅ 엑셀 파일 저장 완료: {output_path_aiwork} (대전 전수 {len(cleaned_items)}건)")


