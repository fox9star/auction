import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# 16:9 와이드스크린 설정
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

blank_layout = prs.slide_layouts[6]

# 색상 팔레트 정의
COLOR_NAVY = RGBColor(26, 54, 93)      # #1A365D (주요 배경/제목)
COLOR_BLUE = RGBColor(43, 108, 176)    # #2B6CB0 (강조색)
COLOR_TEAL = RGBColor(49, 151, 149)    # #319795 (서브 강조)
COLOR_GRAY_BG = RGBColor(247, 250, 252)# #F7FAFC (슬라이드 배경)
COLOR_CARD_BG = RGBColor(255, 255, 255)# #FFFFFF
COLOR_TEXT_MAIN = RGBColor(45, 55, 72) # #2D3748
COLOR_TEXT_MUTED = RGBColor(113, 128, 150) # #718096
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_RED = RGBColor(197, 48, 48)      # 할인/주의
COLOR_GREEN = RGBColor(47, 133, 90)    # 안전/추천
COLOR_LINE = RGBColor(226, 232, 240)

def set_slide_background(slide, color):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.line.fill.background()
    return bg

def add_header(slide, title_text, category="대한민국 법원경매 종합 분석"):
    # 상단 카테고리 태그
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10), Inches(0.4))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    p_c = tf_c.paragraphs[0]
    p_c.text = category.upper()
    p_c.font.size = Pt(11)
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_TEAL

    # 메인 타이틀
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.5), Inches(0.8))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_NAVY

    # 하단 얇은 라인
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_LINE
    line.line.fill.background()

# ==============================================================================
# SLIDE 1: 표지 (Title Slide)
# ==============================================================================
slide1 = prs.slides.add_slide(blank_layout)
set_slide_background(slide1, COLOR_NAVY)

# 표지 장식용 사각형
accent_bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(0.15), Inches(3.2))
accent_bar.fill.solid()
accent_bar.fill.fore_color.rgb = COLOR_TEAL
accent_bar.line.fill.background()

tb_t = slide1.shapes.add_textbox(Inches(1.2), Inches(1.7), Inches(11), Inches(2.2))
tf = tb_t.text_frame
tf.word_wrap = True

p1 = tf.paragraphs[0]
p1.text = "대한민국 법원 부동산 경매"
p1.font.size = Pt(38)
p1.font.bold = True
p1.font.color.rgb = COLOR_WHITE

p2 = tf.add_paragraph()
p2.text = "종합 가이드 및 실시간 데이터 분석 보고서"
p2.font.size = Pt(34)
p2.font.bold = True
p2.font.color.rgb = COLOR_WHITE
p2.space_before = Pt(8)

p3 = tf.add_paragraph()
p3.text = "법원경매 기초·소멸주의·전국 권역별 추천 및 대전광역시 TOP 50 가치평가 모델"
p3.font.size = Pt(16)
p3.font.color.rgb = RGBColor(203, 213, 225)
p3.space_before = Pt(16)

# 메타 정보 카드
meta_box = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(5.2), Inches(10.9), Inches(1.2))
meta_box.fill.solid()
meta_box.fill.fore_color.rgb = RGBColor(30, 64, 110)
meta_box.line.color.rgb = RGBColor(43, 108, 176)

tb_m = slide1.shapes.add_textbox(Inches(1.5), Inches(5.35), Inches(10.3), Inches(0.9))
tf_m = tb_m.text_frame
p_m = tf_m.paragraphs[0]
p_m.text = "• 데이터 출처: 대한민국 법원경매정보(courtauction.go.kr) 실시간 전수 수집\n• 분석 대상: 전국 17개 시·도 1,287건 유효 물건 및 대전광역시 522건 전수 데이터\n• 산출물: 종합 분석 보고서(MD/HTML/PPTX) 및 엑셀 데이터시트 2종"
p_m.font.size = Pt(12)
p_m.font.color.rgb = RGBColor(226, 232, 240)

# ==============================================================================
# SLIDE 2: 목차 (Table of Contents)
# ==============================================================================
slide2 = prs.slides.add_slide(blank_layout)
set_slide_background(slide2, COLOR_GRAY_BG)
add_header(slide2, "보고서 핵심 구성 및 목차", "Table of Contents")

toc_items = [
    ("01", "부산동경매 정의 및 법원 체계", "부산지방법원 동부지원 관할 구역(해운대·수영·남구·기장) 및 입찰법정 특징"),
    ("02", "전국 60개 법원 입찰법정 및 준비물", "전국 18개 본원 + 42개 지원 현장 응찰 체계 및 필수 준비 서류"),
    ("03", "경매 물건 선별 5대 핵심 지표", "가격 괴리·안전마진·소멸주의·환금성·명도 관리비 5단계 실전 공식"),
    ("04", "소멸주의(消滅主義)와 권리분석", "말소기준권리 5총사, 인수주의와의 비교 및 구매자 3대 제도적 이점"),
    ("05", "전국 권역별 경매 데이터 분석 및 추천", "전국 17개 시도 1,287건 수집 결과 및 권역별(수도권·부울경 등) 가성비 추천"),
    ("06", "대전광역시 경매 전수 수집 & TOP 50", "대전 522건 전수 수집, 100점 만점 정밀 가치평가 모델 및 베스트 매물")
]

for idx, (num, title, desc) in enumerate(toc_items):
    col = idx % 2
    row = idx // 2
    x = Inches(0.8 + col * 5.95)
    y = Inches(1.8 + row * 1.65)
    
    card = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.75), Inches(1.4))
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_CARD_BG
    card.line.color.rgb = COLOR_LINE
    
    num_box = slide2.shapes.add_textbox(x + Inches(0.2), y + Inches(0.2), Inches(0.9), Inches(1.0))
    p_n = num_box.text_frame.paragraphs[0]
    p_n.text = num
    p_n.font.size = Pt(26)
    p_n.font.bold = True
    p_n.font.color.rgb = COLOR_BLUE
    
    txt_box = slide2.shapes.add_textbox(x + Inches(1.1), y + Inches(0.2), Inches(4.4), Inches(1.0))
    tf_txt = txt_box.text_frame
    tf_txt.word_wrap = True
    p_t = tf_txt.paragraphs[0]
    p_t.text = title
    p_t.font.size = Pt(14)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_NAVY
    
    p_d = tf_txt.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = COLOR_TEXT_MUTED
    p_d.space_before = Pt(4)

# ==============================================================================
# SLIDE 3: 부산동경매의 정의 및 특징
# ==============================================================================
slide3 = prs.slides.add_slide(blank_layout)
set_slide_background(slide3, COLOR_GRAY_BG)
add_header(slide3, "부산동경매(부산지방법원 동부지원)의 핵심 특징", "Section 01")

# 카드 1: 관할 및 기본 정보
card1 = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.7), Inches(4.9))
card1.fill.solid()
card1.fill.fore_color.rgb = COLOR_CARD_BG
card1.line.color.rgb = COLOR_LINE

tb1 = slide3.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.1), Inches(4.5))
tf1 = tb1.text_frame
tf1.word_wrap = True

p = tf1.paragraphs[0]
p.text = "🏛 부산지방법원 동부지원 기본 정보"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY

p = tf1.add_paragraph()
p.text = "• 약칭: 부산동 / 부산동부 경매\n• 소재지: 부산광역시 해운대구 재반로112번길 20 (재송동)\n• 관할 구역 (4개 시·구·군):\n   - 해운대구 (센텀시티, 마린시티, 우동, 중동, 좌동)\n   - 수영구 (남천동, 광안동, 민락동, 망미동)\n   - 남구 (대연동, 용호동, 문현동 등 재개발 구역)\n   - 기장군 (정관·일광신도시, 기장읍, 장안읍, 철마면)\n• 입찰 시간:\n   - 입찰서 접수: 오전 10:00 ~ 오전 11:20\n   - 개찰 시작: 오전 11:30 순차 진행"
p.font.size = Pt(12)
p.font.color.rgb = COLOR_TEXT_MAIN
p.space_before = Pt(10)

# 카드 2: 시장 특징 및 주의사항
card2 = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.9))
card2.fill.solid()
card2.fill.fore_color.rgb = COLOR_CARD_BG
card2.line.color.rgb = COLOR_LINE

tb2 = slide3.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.5))
tf2 = tb2.text_frame
tf2.word_wrap = True

p = tf2.paragraphs[0]
p.text = "📈 시장 특징 및 관할 주의사항"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY

p = tf2.add_paragraph()
p.text = "• 부산 최고의 주거 선호지 밀집:\n   - 해운대·수영·남구는 부산 아파트 경매의 최대 격전지\n   - 낙찰가율 및 입찰 경쟁률이 부산 본원 대비 높음\n\n• 기장군 도농복합·개발 호재지:\n   - 오시리아 관광단지 배후 상가 및 택지지구 아파트\n   - 토지·임야·공장 등 투자용 물건 다양\n\n• ⚠️ 관할 주의: '부산 동구' 지역 물건\n   - 초량동, 범일동, 수정동, 좌천동 등 '부산 동구' 물건은\n     동부지원이 아니라 '부산지방법원 본원'(연제구 거제동) 관할!"
p.font.size = Pt(12)
p.font.color.rgb = COLOR_TEXT_MAIN
p.space_before = Pt(10)

# ==============================================================================
# SLIDE 4: 전국 60개 법원 입찰법정 체계
# ==============================================================================
slide4 = prs.slides.add_slide(blank_layout)
set_slide_background(slide4, COLOR_GRAY_BG)
add_header(slide4, "전국 60개 법원 경매 입찰법정 및 응찰 절차", "Section 02")

# 상단 안내 바
bar = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.733), Inches(0.9))
bar.fill.solid()
bar.fill.fore_color.rgb = RGBColor(235, 248, 255)
bar.line.color.rgb = COLOR_BLUE

tb_b = slide4.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(11.3), Inches(0.8))
tf_b = tb_b.text_frame
tf_b.word_wrap = True
p = tf_b.paragraphs[0]
p.text = "📌 현장 입찰 원칙: 대한민국 법원경매는 온라인 입찰이 불가하며, 물건 관할 법원의 입찰법정에 직접 출석해야 합니다. (전국 18개 본원 + 42개 지원 = 총 60개소)"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY

# 4개 권역 카드
regions_data = [
    ("수도권 (16개소)", "• 서울 5개 본원 (중앙, 동부, 서부, 남부, 북부)\n• 인천 본원, 부천지원\n• 의정부 본원, 고양지원, 남양주지원\n• 수원 본원, 성남, 여주, 평택, 안산, 안양지원"),
    ("영남권 (19개소)", "• 부산 본원, 부산동부지원, 부산서부지원\n• 울산 본원\n• 창원 본원, 마산, 진주, 통영, 밀양, 거창지원\n• 대구 본원, 대구서부, 안동, 경주, 포항, 김천, 상주, 의성, 영덕지원"),
    ("충청·강원권 (15개소)", "• 대전 본원, 홍성, 논산, 천안, 공주, 서산지원\n• 청주 본원, 충주, 제천, 영동지원\n• 춘천 본원, 강릉, 원주, 속초, 영월지원"),
    ("호남·제주권 (10개소)", "• 광주 본원, 목포, 장흥, 순천, 해남지원\n• 전주 본원, 군산, 정읍, 남원지원\n• 제주지방법원 본원")
]

for idx, (r_name, r_desc) in enumerate(regions_data):
    x = Inches(0.8 + idx * 2.98)
    y = Inches(2.9)
    card = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(2.8), Inches(4.0))
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_CARD_BG
    card.line.color.rgb = COLOR_LINE
    
    tb = slide4.shapes.add_textbox(x + Inches(0.15), y + Inches(0.2), Inches(2.5), Inches(3.6))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = r_name
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE
    
    p = tf.add_paragraph()
    p.text = r_desc
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.space_before = Pt(8)

# ==============================================================================
# SLIDE 5: 경매 물건 선별 5대 지표 및 5단계 공식
# ==============================================================================
slide5 = prs.slides.add_slide(blank_layout)
set_slide_background(slide5, COLOR_GRAY_BG)
add_header(slide5, "실전 경매 물건 선별 5대 지표 & 체크리스트", "Section 03")

steps_data = [
    ("1단계", "가격 및 수익성", "감정평가액 맹신 금지\n현재 급매가 대비 안전마진 확인\n유찰 저감률(20~30%) 분석"),
    ("2단계", "권리분석 안전성", "말소기준권리 이후 소멸 여부\n선순위 대항력 임차인 인수액 0원\n특수권리(유치권/지분) 필터링"),
    ("3단계", "시장 경쟁도·환금성", "최근 3~6개월 매매/전세 실거래량\n평균 입찰 경쟁자 수 확인\n낙찰 후 빠른 엑시트 가능성"),
    ("4단계", "명도 및 숨은 비용", "점유자 성향 및 전액 배당 여부\n인도명령 및 강제집행 비용 고려\n공용부분 미납 관리비 사전 확인"),
    ("5단계", "최종 입찰가 결정", "급매 시세 - 총 취득원가\n(취득세+명도비+수리비+대출이자)\n= 나의 목표 입찰가 도출")
]

for idx, (st_num, st_title, st_desc) in enumerate(steps_data):
    x = Inches(0.8 + idx * 2.38)
    y = Inches(1.8)
    card = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(2.25), Inches(5.0))
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_CARD_BG
    card.line.color.rgb = COLOR_LINE
    
    # 상단 스텝 라벨
    st_box = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.2), y + Inches(0.2), Inches(1.85), Inches(0.45))
    st_box.fill.solid()
    st_box.fill.fore_color.rgb = COLOR_BLUE
    st_box.line.fill.background()
    p = st_box.text_frame.paragraphs[0]
    p.text = st_num
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.alignment = PP_ALIGN.CENTER
    
    tb = slide5.shapes.add_textbox(x + Inches(0.15), y + Inches(0.8), Inches(1.95), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = st_title
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.alignment = PP_ALIGN.CENTER
    
    p = tf.add_paragraph()
    p.text = st_desc
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.space_before = Pt(10)

# ==============================================================================
# SLIDE 6: 소멸주의(消滅主義) 심층 분석
# ==============================================================================
slide6 = prs.slides.add_slide(blank_layout)
set_slide_background(slide6, COLOR_GRAY_BG)
add_header(slide6, "경매의 핵심 엔진: 소멸주의(消滅主義)의 이해", "Section 04")

# 왼쪽: 소멸주의 정의 및 비교
card_l = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0))
card_l.fill.solid()
card_l.fill.fore_color.rgb = COLOR_CARD_BG
card_l.line.color.rgb = COLOR_LINE

tb_l = slide6.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.1), Inches(4.6))
tf_l = tb_l.text_frame
tf_l.word_wrap = True

p = tf_l.paragraphs[0]
p.text = "⚖️ 소멸주의 vs 인수주의 비교"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY

p = tf_l.add_paragraph()
p.text = "• 소멸주의 (대원칙 - 민사집행법 제91조 제2항)\n   - 매각대금을 완납하면 등기부상 모든 저당권, 가압류 등\n     복잡한 권리는 낙찰자가 갚을 필요 없이 법원이 모두 직권 말소!\n   - 구매자에게 '완전히 깨끗한 새 도화지'를 제공함\n\n• 인수주의 (예외)\n   - 권리가 지워지지 않고 낙찰자가 그대로 승계해야 하는 경우\n\n• 말소기준권리 5총사 (이 중 가장 빠른 접수일자 기준):\n   ① (근)저당권  ② (가)압류  ③ 담보가등기\n   ④ 경매기입등기  ⑤ 배당요구한 전세권"
p.font.size = Pt(11)
p.font.color.rgb = COLOR_TEXT_MAIN
p.space_before = Pt(8)

# 오른쪽: 구매자 혜택 및 인수 예외
card_r = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0))
card_r.fill.solid()
card_r.fill.fore_color.rgb = COLOR_CARD_BG
card_r.line.color.rgb = COLOR_LINE

tb_r = slide6.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.6))
tf_r = tb_r.text_frame
tf_r.word_wrap = True

p = tf_r.paragraphs[0]
p.text = "🛡️ 구매자 입장에서의 3대 이점 & 주의사항"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY

p = tf_r.add_paragraph()
p.text = "• 구매자 3대 이점:\n   1. 사기 위험 원천 차단: 법원이 공권력으로 권리 정리\n   2. 확실한 안전마진: 복잡한 부실채권을 합법적으로 정리하여\n      시세 대비 30~50% 저렴하게 매수 가능\n   3. 예측 가능성: 낙찰가 외에 숨은 빚을 갚을 위험 소멸\n\n• ⚠️ 낙찰자가 인수하는 3대 예외 (주의!):\n   1. 대항력 있는 선순위 임차인의 미배당 보증금\n   2. 선순위 가처분 / 선순위 가등기\n   3. 등기부 외 특수권리 (유치권, 법정지상권)"
p.font.size = Pt(11)
p.font.color.rgb = COLOR_TEXT_MAIN
p.space_before = Pt(8)

# ==============================================================================
# SLIDE 7: 전국 권역별 경매 데이터 분석 및 추천
# ==============================================================================
slide7 = prs.slides.add_slide(blank_layout)
set_slide_background(slide7, COLOR_GRAY_BG)
add_header(slide7, "전국 권역별 경매 데이터 분석 및 베스트 추천", "Section 05")

# 테이블 생성
table_shape = slide7.shapes.add_table(7, 7, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.8))
table = table_shape.table

# 열 너비 설정
table.columns[0].width = Inches(1.4)
table.columns[1].width = Inches(1.4)
table.columns[2].width = Inches(1.6)
table.columns[3].width = Inches(3.5)
table.columns[4].width = Inches(1.3)
table.columns[5].width = Inches(1.3)
table.columns[6].width = Inches(1.2)

headers = ["권역", "관할법원", "사건번호", "소재지 및 아파트명", "감정평가액", "최저매각가격", "할인율"]
for col_idx, h in enumerate(headers):
    cell = table.cell(0, col_idx)
    cell.text = h
    cell.fill.solid()
    cell.fill.fore_color.rgb = COLOR_BLUE
    p = cell.text_frame.paragraphs[0]
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.alignment = PP_ALIGN.CENTER

rec_data = [
    ("수도권", "부천지원", "2024타경5702", "경기 부천시 소사본동 삼신아파트 1동 3층", "2억 6,700만", "9,158만 원", "-65.7% (3회)"),
    ("영남(부울경)", "부산동부", "2025타경462", "부산 수영구 광안동 성우이린타워 9층", "2억 2,800만", "7,820만 원", "-65.7% (3회)"),
    ("영남(부울경)", "부산동부", "2025타경634", "부산 수영구 망미동 망미한신 103동 2층", "5억 7,500만", "1억 9,722만 원", "-65.7% (3회)"),
    ("영남(대경권)", "대구지법", "2025타경10173", "대구 동구 신서동 명가클래식 11층", "1억 9,100만", "6,551만 원", "-65.7% (3회)"),
    ("충청권", "대전지법", "2025타경503447", "대전 대덕구 대화동 세원풍남 5동 5층", "1억 6,600만", "5,693만 원", "-65.7% (3회)"),
    ("강원권", "속초지원", "2025타경10411", "강원 양양군 양양읍 양양서문주공 102동", "1억 5,000만", "5,145만 원", "-65.7% (3회)")
]

for row_idx, r in enumerate(rec_data, start=1):
    for col_idx, val in enumerate(r):
        cell = table.cell(row_idx, col_idx)
        cell.text = val
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_CARD_BG if row_idx % 2 == 1 else RGBColor(241, 245, 249)
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(10)
        p.font.color.rgb = COLOR_TEXT_MAIN
        if col_idx in [0, 1, 2, 6]:
            p.alignment = PP_ALIGN.CENTER
        elif col_idx in [4, 5]:
            p.alignment = PP_ALIGN.RIGHT
            if col_idx == 5:
                p.font.bold = True

# ==============================================================================
# SLIDE 8: 대전광역시 경매 전수 수집 및 평가 모델
# ==============================================================================
slide8 = prs.slides.add_slide(blank_layout)
set_slide_background(slide8, COLOR_GRAY_BG)
add_header(slide8, "대전광역시 경매 전수 수집 및 100점 만점 평가 모델", "Section 06")

# 4개 지표 카드
scores = [
    ("40점", "가격 할인율 (Price)", "• 60% 이상 할인 (3회+): 40점\n• 45~59% 할인 (2회): 32점\n• 30~44% 할인 (1~2회): 25점\n• 15~29% 할인: 18점\n• 신건 (0%): 10점"),
    ("30점", "권리 안전성 (Safety)", "• 특수권리 없는 완전 소멸주의: 30점\n• 경미한 주의 (단순재매각 등): 18점\n• 위험 권리 (유치권/지분/법정지상권):\n  -15점 대폭 감점 (위험 필터링)"),
    ("20점", "용도·환금성 (Liquidity)", "• 아파트/주상복합: 20점 만점\n• 오피스텔/다세대/빌라: 16점\n• 단독/다가구/상가주택: 14점\n• 근린상가/업무시설: 12점\n• 대지/주택용지: 10점"),
    ("10점", "입지 선호도 (Location)", "• 유성구 (도안/노은/연구단지): 10점\n• 서구 (둔산동 학원가/행정타운): 9점\n• 중구 (원도심 재개발/서대전역): 7점\n• 동구 (대전역 역세권 개발): 6점\n• 대덕구 (산단 배후 주거단지): 6점")
]

for idx, (pts, title, desc) in enumerate(scores):
    x = Inches(0.8 + idx * 2.98)
    y = Inches(1.8)
    card = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(2.8), Inches(4.9))
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_CARD_BG
    card.line.color.rgb = COLOR_LINE
    
    # 점수 배지
    badge = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.2), y + Inches(0.2), Inches(2.4), Inches(0.6))
    badge.fill.solid()
    badge.fill.fore_color.rgb = COLOR_NAVY
    badge.line.fill.background()
    p = badge.text_frame.paragraphs[0]
    p.text = pts
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.alignment = PP_ALIGN.CENTER
    
    tb = slide8.shapes.add_textbox(x + Inches(0.15), y + Inches(0.9), Inches(2.5), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE
    
    p = tf.add_paragraph()
    p.text = desc
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.space_before = Pt(8)

# ==============================================================================
# SLIDE 9: 대전광역시 TOP 10 추천 물건
# ==============================================================================
slide9 = prs.slides.add_slide(blank_layout)
set_slide_background(slide9, COLOR_GRAY_BG)
add_header(slide9, "대전광역시 경매 베스트 TOP 10 물건", "Section 07")

# 테이블 생성
table_shape9 = slide9.shapes.add_table(11, 7, Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.1))
t9 = table_shape9.table

t9.columns[0].width = Inches(0.8)
t9.columns[1].width = Inches(1.0)
t9.columns[2].width = Inches(1.0)
t9.columns[3].width = Inches(1.6)
t9.columns[4].width = Inches(4.3)
t9.columns[5].width = Inches(1.5)
t9.columns[6].width = Inches(1.533)

headers9 = ["순위", "점수", "자치구", "사건번호", "소재지 및 단지명", "감정평가액", "최저매각가격"]
for col_idx, h in enumerate(headers9):
    cell = t9.cell(0, col_idx)
    cell.text = h
    cell.fill.solid()
    cell.fill.fore_color.rgb = COLOR_NAVY
    p = cell.text_frame.paragraphs[0]
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.alignment = PP_ALIGN.CENTER

top10_data = [
    ("1위", "100점", "유성구", "2025타경503878", "송강동 청솔아파트 102동 7층", "1억 5,900만", "3,817만 (-76%)"),
    ("2위", "99점", "서구", "2025타경502021", "월평동 에코리움 5층", "1억 8,000만", "3,025만 (-83%)"),
    ("3위", "96점", "유성구", "2025타경503678", "봉명동 사이언스타운 6층 (오피스텔)", "2억", "3,361만 (-83%)"),
    ("4위", "96점", "유성구", "2024타경109647", "봉명동 유성자이 1층 133호 (상가)", "2억 7,600만", "4,638만 (-83%)"),
    ("5위", "96점", "유성구", "2024타경8362", "덕명동 베네디또빌 1층 102호 (다세대)", "4억 1,300만", "9,916만 (-76%)"),
    ("6위", "96점", "유성구", "2024타경8362", "덕명동 베네디또빌 1층 101호 (다세대)", "4억 3,400만", "1억 420만 (-76%)"),
    ("7위", "96점", "유성구", "2025타경3894", "봉명동 다세대 5층 511호", "9,400만", "3,224만 (-66%)"),
    ("8위", "96점", "대덕구", "2025타경503447", "대화동 세원풍남 5동 5층 (아파트)", "1억 6,600만", "5,693만 (-66%)"),
    ("9위", "96점", "유성구", "2026타경45", "용산동 세안프라자 3층 (근린상가)", "1억 7,500만", "6,002만 (-66%)"),
    ("10위", "96점", "유성구", "2025타경3906", "문지동 효성해링턴 배후 상가 3층", "2억 3,600만", "8,094만 (-66%)")
]

for row_idx, r in enumerate(top10_data, start=1):
    for col_idx, val in enumerate(r):
        cell = t9.cell(row_idx, col_idx)
        cell.text = val
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_CARD_BG if row_idx % 2 == 1 else RGBColor(241, 245, 249)
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_MAIN
        if col_idx in [0, 1, 2, 3]:
            p.alignment = PP_ALIGN.CENTER
            if col_idx == 0 and row_idx <= 3:
                p.font.bold = True
        elif col_idx in [5, 6]:
            p.alignment = PP_ALIGN.RIGHT
            if col_idx == 6:
                p.font.bold = True
                p.font.color.rgb = COLOR_RED

# ==============================================================================
# SLIDE 10: 프로젝트 산출물 및 향후 활용 가이드
# ==============================================================================
slide10 = prs.slides.add_slide(blank_layout)
set_slide_background(slide10, COLOR_GRAY_BG)
add_header(slide10, "프로젝트 산출물 및 실무 활용 가이드", "Project Outputs")

outputs = [
    ("📊 데이터 분석 엑셀 파일 (2종)", "• 대전광역시_경매물건_TOP50_추천.xlsx\n   - 대전 522건 전수 수집 및 100점 만점 TOP 50 정렬\n• 대한민국법원_전국경매물건_정리_및_권역별추천.xlsx\n   - 전국 17개 시·도 1,287건 수집 및 권역별 추천 리스트"),
    ("📄 문서 및 보고서 산출물", "• 부동산_경매_종합_분석_보고서.html\n   - 반응형 웹 스타일, 목차(TOC) 및 인쇄 최적화\n• 부동산_경매_종합_분석_보고서.md\n   - GitHub 표준 마크다운 보고서\n• 부동산_경매_종합_분석_보고서.pptx\n   - 16:9 와이드스크린 프레젠테이션 (본 파일)"),
    ("⚙️ 자동화 데이터 파이프라인 스크립트", "• process_daejeon_top50.py (대전 전수 수집 및 가치평가)\n• collect_and_export_auction.py (전국 17개 시도 크롤러)\n• check_daejeon.py & print_summary.py (검증 툴)"),
    ("💡 실전 입찰 최종 체크리스트", "• 매각기일 1주일 전 매각물건명세서 변경 여부 재확인\n• 해당 아파트/상가 관리사무소 방문해 공용 관리비 확인\n• 네이버 부동산 및 현장 공인중개사를 통한 급매 호가 크로스체크")
]

for idx, (title, desc) in enumerate(outputs):
    col = idx % 2
    row = idx // 2
    x = Inches(0.8 + col * 5.95)
    y = Inches(1.8 + row * 2.5)
    
    card = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.75), Inches(2.25))
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_CARD_BG
    card.line.color.rgb = COLOR_LINE
    
    tb = slide10.shapes.add_textbox(x + Inches(0.2), y + Inches(0.2), Inches(5.35), Inches(1.9))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE
    
    p = tf.add_paragraph()
    p.text = desc
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.space_before = Pt(8)

# 저장 실행
output_path1 = r"C:\Users\wood\Desktop\aiwork\auction\부동산_경매_종합_분석_보고서.pptx"
output_path2 = r"C:\Users\wood\Desktop\auction\부동산_경매_종합_분석_보고서.pptx"

prs.save(output_path1)
print(f"✅ 저장 완료: {output_path1}")

try:
    prs.save(output_path2)
    print(f"✅ 백업 저장 완료: {output_path2}")
except Exception as e:
    print(f"백업 저장 스킵: {e}")
