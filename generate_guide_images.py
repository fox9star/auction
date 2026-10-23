import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches

matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

output_dir = r"C:\Users\wood\Desktop\aiwork\auction\images"
os.makedirs(output_dir, exist_ok=True)


# ==============================================================================
# 이미지 1: 실전 법원경매 7단계 마스터 로드맵 (guide_7steps_roadmap.png)
# ==============================================================================
def make_7steps_roadmap():
    fig, ax = plt.subplots(figsize=(13, 6.8), dpi=160)
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')
    ax.axis('off')
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7.2)

    ax.text(6.5, 6.72, "대한민국 법원경매 실전 7단계 마스터 로드맵 (D-14일 ~ 입주·수익실현)",
            ha='center', va='center', fontsize=15.5, weight='bold', color='#1A365D')
    ax.text(6.5, 6.32, "입찰 준비(STEP 1~4)  ▶  법원 실전 입찰(STEP 5)  ▶  잔금·소유권·명도 완료(STEP 6~7)",
            ha='center', va='center', fontsize=10.5, weight='bold', color='#475569')

    # 상단 4단계 (STEP 1 ~ STEP 4)
    top_steps = [
        ("STEP 1", "D-14일", "물건 탐색·후보 선정", "• 아파트·주거용 오피스텔\n• 1~3회 유찰(30~65%↓)\n• 특수권리 물건 제외", "#1E40AF", "#EFF6FF", "#93C5FD"),
        ("STEP 2", "D-10일", "3대 공적서류 권리분석", "• 등기부: 말소기준권리\n• 매각물건명세서: 선순위\n• 현황조사서: 점유확인", "#1E40AF", "#EFF6FF", "#93C5FD"),
        ("STEP 3", "D-5일", "현장 임장·시세·관리비", "• 국토부 실거래·급매호가\n• 중개소 2~3곳 시세탐문\n• 관리실 미납공용관리비", "#0F766E", "#F0FDFA", "#5EEAD4"),
        ("STEP 4", "D-2일", "입찰가 산정·대출가심사", "• 급매가-마진-부대비용\n• 경락잔금대출(70~80%)\n• 필요 실투자금 확정", "#0F766E", "#F0FDFA", "#5EEAD4"),
    ]

    x_positions_top = [0.55, 3.65, 6.75, 9.85]
    box_w = 2.6
    box_h = 2.35
    y_top = 3.55

    for i, (st, dday, title, desc, c_main, c_bg, c_ec) in enumerate(top_steps):
        x = x_positions_top[i]
        card = patches.FancyBboxPatch((x, y_top), box_w, box_h, boxstyle="round,pad=0.14", fc=c_bg, ec=c_ec, lw=2)
        ax.add_patch(card)

        pill = patches.FancyBboxPatch((x + 0.12, y_top + box_h - 0.42), 0.95, 0.34, boxstyle="round,pad=0.06", fc=c_main, ec="none")
        ax.add_patch(pill)
        ax.text(x + 0.59, y_top + box_h - 0.25, st, ha='center', va='center', fontsize=9, weight='bold', color='#FFFFFF')
        ax.text(x + box_w - 0.15, y_top + box_h - 0.25, dday, ha='right', va='center', fontsize=9, weight='bold', color=c_main)

        ax.text(x + box_w / 2, y_top + 1.48, title, ha='center', va='center', fontsize=11, weight='bold', color='#0F172A')
        ax.text(x + 0.15, y_top + 0.72, desc, ha='left', va='center', fontsize=8.8, color='#334155', linespacing=1.45)

        if i < 3:
            ax.annotate('', xy=(x_positions_top[i+1] - 0.12, y_top + box_h/2), xytext=(x + box_w + 0.12, y_top + box_h/2),
                        arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.35", color="#64748B", lw=2.5))

    # 하단 3단계 (STEP 5 ~ STEP 7)
    bot_steps = [
        ("STEP 5 [핵심]", "D-Day 10:00", "법원 출석 · 입찰표 투입 · 개찰",
         "• 신분증 + 도장 + 최저가의 10% 자기앞수표 1장 지참\n• 기일입찰표·보증금봉투·입찰봉투 작성 후 입찰함 투입\n• 11:30 개찰: 최고가 낙찰자 결정 (패찰 시 수표 즉시 반환)",
         "#B91C1C", "#FEF2F2", "#FCA5A5"),
        ("STEP 6", "낙찰 후 7~45일", "매각허가확정 및 잔금 완납",
         "• 낙찰 7일 후 매각허가결정 → 14일 후 매각허가확정\n• 확정 후 약 30일 내 대금지급기한까지 잔금(90%) 납부\n• 잔금 완납 즉시 법적 소유권 100% 취득 + 말소촉탁등기",
         "#1D4ED8", "#EFF6FF", "#93C5FD"),
        ("STEP 7 [완성]", "잔금 후 1~6주", "인도명령 신청 · 명도 · 입주/임대",
         "• 잔금 납부 당일 법원에 [부동산 인도명령 신청서] 접수\n• 점유자와 이사 일정 및 적정 이사비(50~150만원) 협의\n• 공실 상태·관리비 완납 영수증·비밀번호 인계 후 이사비 지급",
         "#15803D", "#F0FDF4", "#86EFAC"),
    ]

    x_positions_bot = [0.55, 4.75, 8.95]
    box_w_bot = 3.5
    box_h_bot = 2.45
    y_bot = 0.45

    for i, (st, dday, title, desc, c_main, c_bg, c_ec) in enumerate(bot_steps):
        x = x_positions_bot[i]
        card = patches.FancyBboxPatch((x, y_bot), box_w_bot, box_h_bot, boxstyle="round,pad=0.14", fc=c_bg, ec=c_ec, lw=2.2)
        ax.add_patch(card)

        pill = patches.FancyBboxPatch((x + 0.12, y_bot + box_h_bot - 0.44), 1.35, 0.35, boxstyle="round,pad=0.06", fc=c_main, ec="none")
        ax.add_patch(pill)
        ax.text(x + 0.79, y_bot + box_h_bot - 0.26, st, ha='center', va='center', fontsize=8.8, weight='bold', color='#FFFFFF')
        ax.text(x + box_w_bot - 0.15, y_bot + box_h_bot - 0.26, dday, ha='right', va='center', fontsize=9, weight='bold', color=c_main)

        ax.text(x + box_w_bot / 2, y_bot + 1.56, title, ha='center', va='center', fontsize=11, weight='bold', color='#0F172A')
        ax.text(x + 0.16, y_bot + 0.76, desc, ha='left', va='center', fontsize=8.6, color='#334155', linespacing=1.45)

        if i < 2:
            ax.annotate('', xy=(x_positions_bot[i+1] - 0.12, y_bot + box_h_bot/2), xytext=(x + box_w_bot + 0.12, y_bot + box_h_bot/2),
                        arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.35", color="#64748B", lw=2.5))

    # STEP 4 -> STEP 5 연결 경로 (상단과 하단 사이의 빈 공간 y=3.23을 따라 깔끔하게 이동)
    ax.plot([11.15, 11.15, 2.3, 2.3], [y_top - 0.14, 3.23, 3.23, y_bot + box_h_bot + 0.22],
            color="#DC2626", lw=2.2, linestyle="-")
    ax.annotate('', xy=(2.3, y_bot + box_h_bot + 0.12), xytext=(2.3, 3.23),
                arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.35", color="#DC2626", lw=2.2))

    plt.tight_layout()
    p = os.path.join(output_dir, "guide_7steps_roadmap.png")
    plt.savefig(p, bbox_inches='tight')
    plt.close()
    print("Saved:", p)


# ==============================================================================
# 이미지 2: 상한 입찰가 산정 공식 & 유찰 저감 구조 (guide_bid_price_formula.png)
# ==============================================================================
def make_bid_price_formula():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.6), dpi=160)
    fig.patch.set_facecolor('#F8FAFC')

    # 좌측: 상한 입찰가 산정 워터폴 다이어그램 (예: 급매 시세 3억 원 아파트 기준)
    ax1.set_facecolor('#FFFFFF')
    categories = ['① 현재 급매 시세\n(기준점)', '② 목표 안전마진\n(-15%)', '③ 미납공용관리비\n·명도이사비', '④ 취득세·등기비\n·기본수리비', '★ 최대 입찰가 ★\n(내 입찰 상한선)']
    values = [30000, -4500, -500, -1000, 24000]
    bottoms = [0, 25500, 25000, 24000, 0]
    colors = ['#2563EB', '#F59E0B', '#EF4444', '#EC4899', '#0D9488']

    bars = ax1.bar(categories, [abs(v) for v in values], bottom=bottoms, color=colors, width=0.52, edgecolor='#1E293B', linewidth=1)
    ax1.set_ylim(0, 35000)
    ax1.set_ylabel("금액 (만 원, 3억 급매 아파트 예시)", fontsize=10, weight='bold', color='#334155')
    ax1.set_title("① 초보자 필승 [최대 입찰가] 산정 워터폴 공식", fontsize=12.5, weight='bold', color='#1A365D', pad=14)
    ax1.grid(axis='y', linestyle='--', alpha=0.4)
    ax1.tick_params(axis='x', labelsize=8.8)

    labels_txt = ["3억 0,000만\n(100%)", "-4,500만\n(안전마진)", "-500만\n(관리비·명도)", "-1,000만\n(세금·수리)", "2억 4,000만\n(상한선 80%)"]
    for i, bar in enumerate(bars):
        top_y = bottoms[i] + abs(values[i])
        ax1.text(bar.get_x() + bar.get_width()/2, top_y + 700, labels_txt[i],
                 ha='center', va='bottom', fontsize=8.8, weight='bold', color='#0F172A')

    # 우측: 유찰 회차별 최저매각가격 저감 곡선 (30% 저감 법원 vs 20% 저감 법원)
    ax2.set_facecolor('#FFFFFF')
    rounds = ['신건\n(1회차)', '1회 유찰\n(2회차)', '2회 유찰\n(3회차)', '3회 유찰\n(4회차)', '4회 유찰\n(5회차)']
    rate_30 = [100, 70, 49, 34.3, 24.0]  # 대전·충청 등 30% 저감 법원
    rate_20 = [100, 80, 64, 51.2, 41.0]  # 수도권 일부 20% 저감 법원

    ax2.plot(rounds, rate_30, marker='o', linewidth=3, markersize=8, color='#DC2626', label='30% 저감 법원 (대전·충청 등)')
    ax2.plot(rounds, rate_20, marker='s', linewidth=2.5, markersize=7, color='#2563EB', linestyle='--', label='20% 저감 법원 (서울·수도권 일부)')

    # 초보자 골든크로스 추천 구간 음영
    ax2.axhspan(34, 70, color='#FEF3C7', alpha=0.55, label='초보자 추천 입찰 구간 (1~3회 유찰)')
    for i, r30 in enumerate(rate_30):
        ax2.text(i, r30 - 6.5, f"{r30}%", ha='center', va='top', fontsize=8.8, weight='bold', color='#B91C1C')
    for i, r20 in enumerate(rate_20):
        if i > 0:
            ax2.text(i, r20 + 3.5, f"{r20}%", ha='center', va='bottom', fontsize=8.5, weight='bold', color='#1D4ED8')

    ax2.set_ylim(10, 115)
    ax2.set_ylabel("감정평가액 대비 최저매각가격 비율 (%)", fontsize=10, weight='bold', color='#334155')
    ax2.set_title("② 유찰 회차별 최저매각가격 저감률 & 추천 진입 구간", fontsize=12.5, weight='bold', color='#1A365D', pad=14)
    ax2.grid(True, linestyle='--', alpha=0.4)
    ax2.legend(loc='upper right', fontsize=8.5, frameon=True)

    plt.suptitle("법원경매 안전마진 확보를 위한 입찰가 산정 공식 & 유찰 저감 시뮬레이션", fontsize=14.5, weight='bold', color='#0F172A', y=1.02)
    plt.tight_layout()
    p = os.path.join(output_dir, "guide_bid_price_formula.png")
    plt.savefig(p, bbox_inches='tight')
    plt.close()
    print("Saved:", p)


# ==============================================================================
# 이미지 3: 법원 입찰 당일 필수 준비물 & 서류 3종 제출 구조도 (guide_court_bidding_kit.png)
# ==============================================================================
def make_court_bidding_kit():
    fig, ax = plt.subplots(figsize=(12.5, 5.8), dpi=160)
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')
    ax.axis('off')
    ax.set_xlim(0, 12.5)
    ax.set_ylim(0, 6.0)

    ax.text(6.25, 5.58, "법원 입찰 당일(D-Day) 필수 지참물 & 입찰서류 3종 제출 구조도",
            ha='center', va='center', fontsize=15, weight='bold', color='#1A365D')
    ax.text(6.25, 5.18, "오전 09:40 입찰법정 도착 권장  |  10:00 입찰 개시  |  11:10~11:30 입찰 마감 및 개찰",
            ha='center', va='center', fontsize=10, weight='bold', color='#DC2626')

    # 좌측 박스: 필수 준비물 3총사
    b_left = patches.FancyBboxPatch((0.4, 0.55), 3.6, 4.2, boxstyle="round,pad=0.16", fc="#FFFFFF", ec="#2563EB", lw=2.2)
    ax.add_patch(b_left)
    ax.text(2.2, 4.42, "【1】 본인 입찰 3대 필수 준비물", ha='center', va='center', fontsize=11.5, weight='bold', color="#1E40AF")

    items_left = [
        ("① 본인 신분증", "주민등록증 · 운전면허증 · 여권"),
        ("② 본인 도장", "막도장 가능 (서명/지장 불가)"),
        ("③ 입찰보증금 (수표 1장)", "최저매각가격의 10% 이상\n(입찰가의 10%가 아님! 재매각 20~30%)"),
        ("※ 대리입찰 추가서류", "본인 인감증명서 + 인감날인 위임장\n+ 대리인 신분증·도장"),
    ]
    y_curr = 3.78
    for t_head, t_sub in items_left:
        sub_b = patches.FancyBboxPatch((0.6, y_curr - 0.55), 3.2, 0.72, boxstyle="round,pad=0.08", fc="#EFF6FF", ec="#BFDBFE", lw=1.2)
        ax.add_patch(sub_b)
        ax.text(0.75, y_curr - 0.06, t_head, ha='left', va='center', fontsize=9.5, weight='bold', color='#1E3A8A')
        ax.text(0.75, y_curr - 0.34, t_sub, ha='left', va='center', fontsize=8.2, color='#334155')
        y_curr -= 0.92

    # 중앙 박스: 법원 서류 3종 결합 프로세스
    b_mid = patches.FancyBboxPatch((4.45, 0.55), 4.1, 4.2, boxstyle="round,pad=0.16", fc="#FFFFFF", ec="#0D9488", lw=2.2)
    ax.add_patch(b_mid)
    ax.text(6.5, 4.42, "【2】 법정 입찰서류 3중 봉투 작성·결합", ha='center', va='center', fontsize=11.5, weight='bold', color="#0F766E")

    mid_cards = [
        ("A. 기일입찰표 (백색/황색 용지)", "사건번호 · 물건번호 · 입찰자 인적사항\n입찰가격(숫자 정자 기재) · 보증금액 기재 후 날인", "#F0FDFA", "#5EEAD4"),
        ("B. 입찰보증금 봉투 (소봉투)", "자기앞수표(최저가 10%↑)를 넣고\n봉투 앞면 사건번호·성명 기재 및 뒷면 연결부 도장 날인", "#F0FDFA", "#5EEAD4"),
        ("C. 입찰봉투 (대봉투) 최종 투입!", "[A. 기일입찰표] + [B. 보증금 소봉투]를 대봉투에 동봉\n집행관에게 신분증 제시·확인 후 입찰함에 투입!", "#FEF3C7", "#F59E0B"),
    ]
    y_m = 3.55
    for title_m, desc_m, fc_m, ec_m in mid_cards:
        cm = patches.FancyBboxPatch((4.68, y_m - 0.62), 3.64, 0.95, boxstyle="round,pad=0.08", fc=fc_m, ec=ec_m, lw=1.5)
        ax.add_patch(cm)
        ax.text(6.5, y_m + 0.12, title_m, ha='center', va='center', fontsize=9.5, weight='bold', color='#0F172A')
        ax.text(6.5, y_m - 0.28, desc_m, ha='center', va='center', fontsize=8.2, color='#334155')
        y_m -= 1.22

    # 우측 박스: 초보자 3대 실수 주의보
    b_right = patches.FancyBboxPatch((8.95, 0.55), 3.15, 4.2, boxstyle="round,pad=0.16", fc="#FFF5F5", ec="#E53E3E", lw=2.2)
    ax.add_patch(b_right)
    ax.text(10.52, 4.42, "【3】 초보자 단골 실수 TOP 3", ha='center', va='center', fontsize=11.5, weight='bold', color="#B91C1C")

    warns = [
        ("실수 1. 숫자 '0' 하나 더 쓰기", "3억을 30억으로 오기재 시 취소 불가!\n보증금 10% 전액 몰수 위험\n→ 투입 전 만·억 단위 3번 검산!"),
        ("실수 2. 보증금 단 10원 부족", "입찰보증금이 최저가의 10%보다\n10원이라도 적으면 즉시 입찰 무효!\n→ 십만원 단위 올림 수표 권장"),
        ("실수 3. 물건번호 누락·오기", "한 사건에 물건이 여러 개일 때\n물건번호(1번, 2번) 미기재 시 무효!"),
    ]
    y_w = 3.55
    for w_head, w_desc in warns:
        cw = patches.FancyBboxPatch((9.15, y_w - 0.65), 2.75, 0.98, boxstyle="round,pad=0.08", fc="#FFFFFF", ec="#FCA5A5", lw=1.3)
        ax.add_patch(cw)
        ax.text(10.52, y_w + 0.12, w_head, ha='center', va='center', fontsize=9.2, weight='bold', color='#991B1B')
        ax.text(10.52, y_w - 0.30, w_desc, ha='center', va='center', fontsize=8.0, color='#334155')
        y_w -= 1.22

    plt.tight_layout()
    p = os.path.join(output_dir, "guide_court_bidding_kit.png")
    plt.savefig(p, bbox_inches='tight')
    plt.close()
    print("Saved:", p)


# ==============================================================================
# 이미지 4: 임차인 대항력 3초 판별 & 명도 프로세스 (guide_tenant_and_eviction.png)
# ==============================================================================
def make_tenant_and_eviction():
    fig, ax = plt.subplots(figsize=(12.5, 5.6), dpi=160)
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')
    ax.axis('off')
    ax.set_xlim(0, 12.5)
    ax.set_ylim(0, 5.8)

    ax.text(6.25, 5.4, "임차인(세입자) 보증금 인수 3초 판별법 & 낙찰 후 명도(인도) 표준 절차",
            ha='center', va='center', fontsize=15, weight='bold', color='#1A365D')

    # 상단: 임차인 대항력 판별 3분류
    ax.text(6.25, 4.92, "▼ 매각물건명세서 [최선순위 설정일자(말소기준권리)] vs 임차인 [전입신고일] 비교",
            ha='center', va='center', fontsize=10.5, weight='bold', color='#334155')

    cases = [
        ("CASE A. 후순위 임차인 (대항력 없음)",
         "전입신고일  >  최선순위 설정일자 (말소기준보다 늦음)",
         "[안전] 낙찰자 보증금 인수 0원! (100% 안전)\n• 배당 결과와 무관하게 낙찰자 인수 책임 전혀 없음\n• 잔금 납부 후 [부동산 인도명령]으로 신속 명도 가능",
         "#F0FDF4", "#16A34A", "#15803D"),
        ("CASE B. 선순위 임차인 + 배당요구 O",
         "전입신고일  <  최선순위 설정일자 (종기 내 배당요구 신청)",
         "[조건부] 전액 배당 시 인수 0원 / 미배당 차액만 인수\n• 낙찰대금에서 보증금 전액 배당되면 인수금 0원(안전)\n• 일부 미배당 시 그 차액만 입찰가에서 낮춰 쓰면 공략 가능",
         "#FFFBEB", "#D97706", "#B45309"),
        ("CASE C. 선순위 임차인 + 배당요구 X",
         "전입신고일  <  최선순위 설정일자 (배당요구 미신청)",
         "[위험] 보증금 전액 낙찰자 인수! (초보자 절대 제외)\n• 낙찰대금 외에 임차인 보증금 전액을 별도로 물어줘야 함\n• 초보자 입찰 대상에서 1순위로 제외해야 할 대표 유형",
         "#FEF2F2", "#DC2626", "#B91C1C"),
    ]

    xs = [0.4, 4.4, 8.4]
    for i, (c_title, c_cond, c_body, bg_c, bd_c, tx_c) in enumerate(cases):
        x = xs[i]
        box = patches.FancyBboxPatch((x, 2.55), 3.7, 2.05, boxstyle="round,pad=0.12", fc=bg_c, ec=bd_c, lw=2)
        ax.add_patch(box)
        ax.text(x + 1.85, 4.32, c_title, ha='center', va='center', fontsize=10, weight='bold', color=tx_c)
        ax.text(x + 1.85, 3.96, c_cond, ha='center', va='center', fontsize=8.3, weight='bold', color='#1E293B')
        ax.text(x + 0.15, 3.18, c_body, ha='left', va='center', fontsize=8.2, color='#334155', linespacing=1.42)

    # 하단: 잔금 납부 후 명도(인도) 4단계 타임라인
    bot_panel = patches.FancyBboxPatch((0.4, 0.35), 11.7, 1.85, boxstyle="round,pad=0.14", fc="#FFFFFF", ec="#CBD5E1", lw=1.8)
    ax.add_patch(bot_panel)
    ax.text(6.25, 1.92, "★ 잔금 완납 후 점유자 명도(인도) 4단계 표준 프로세스 (평균 2~6주 소요)",
            ha='center', va='center', fontsize=11, weight='bold', color='#1E3A8A')

    ev_steps = [
        ("1단계 [잔금 당일]", "잔금 완납 + 인도명령 신청", "소유권 즉시 취득과 동시에\n법원에 인도명령 신청서 접수"),
        ("2단계 [잔금 후 3일 내]", "점유자 첫 접촉 · 안내문", "정중한 방문/연락으로\n이사 일정 조율 개시"),
        ("3단계 [잔금 후 2~3주]", "인도명령 결정 · 이사비 합의", "법원 인도명령 결정문 송달\n적정 이사비(50~150만) 합의"),
        ("4단계 [이사 당일]", "공실 확인 · 열쇠 인수", "짐 반출·관리비 정산 영수증·\n비번 인계 현장에서 이사비 지급"),
    ]
    ex_s = [0.65, 3.55, 6.45, 9.35]
    for i, (es_t, es_m, es_d) in enumerate(ev_steps):
        bx = ex_s[i]
        sb = patches.FancyBboxPatch((bx, 0.52), 2.5, 1.12, boxstyle="round,pad=0.08", fc="#F1F5F9", ec="#94A3B8", lw=1.2)
        ax.add_patch(sb)
        ax.text(bx + 1.25, 1.44, es_t, ha='center', va='center', fontsize=8.5, weight='bold', color='#0F766E')
        ax.text(bx + 1.25, 1.16, es_m, ha='center', va='center', fontsize=9.2, weight='bold', color='#0F172A')
        ax.text(bx + 1.25, 0.78, es_d, ha='center', va='center', fontsize=7.9, color='#475569')
        if i < 3:
            ax.annotate('', xy=(ex_s[i+1] - 0.06, 1.08), xytext=(bx + 2.56, 1.08),
                        arrowprops=dict(arrowstyle="->,head_width=0.28,head_length=0.28", color="#2563EB", lw=2))

    plt.tight_layout()
    p = os.path.join(output_dir, "guide_tenant_and_eviction.png")
    plt.savefig(p, bbox_inches='tight')
    plt.close()
    print("Saved:", p)


if __name__ == "__main__":
    make_7steps_roadmap()
    make_bid_price_formula()
    make_court_bidding_kit()
    make_tenant_and_eviction()
    print("All 4 beginner guide infographics generated successfully!")
