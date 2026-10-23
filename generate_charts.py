import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

matplotlib.rcParams['font.family'] = 'Malgun Gothic' # Windows 한글 폰트
matplotlib.rcParams['axes.unicode_minus'] = False

output_dir = r"C:\Users\wood\Desktop\aiwork\auction\images"
os.makedirs(output_dir, exist_ok=True)

# -------------------------------------------------------------------------
# 차트 1: 전국 권역별 경매 물건 분포 및 할인율 통계
# -------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=150)
fig.patch.set_facecolor('#F8FAFC')

# 1-1 도넛 차트
regions = ['수도권', '영남권(부울경·대경)', '충청권', '호남권', '강원·제주권']
counts = [484, 337, 209, 211, 46]
colors = ['#1A365D', '#2B6CB0', '#319795', '#D69E2E', '#E53E3E']

wedges, texts, autotexts = ax1.pie(
    counts, labels=regions, autopct='%1.1f%%', startangle=140,
    colors=colors, pctdistance=0.75,
    textprops={'fontsize': 10, 'weight': 'bold', 'color': '#2D3748'},
    wedgeprops={'width': 0.45, 'edgecolor': '#FFFFFF', 'linewidth': 2}
)
for at in autotexts:
    at.set_color('#FFFFFF')
    at.set_fontsize(11)
    at.set_weight('bold')

ax1.set_title("전국 법원경매 물건 권역별 점유율 (총 1,287건)", fontsize=13, weight='bold', pad=15, color='#1A365D')

# 1-2 권역별 평균 할인율 및 최고 할인율
avg_discounts = [36.5, 42.1, 44.8, 38.2, 41.5]
max_discounts = [65.7, 65.7, 65.7, 65.7, 65.7]
x = np.arange(len(regions))
width = 0.35

rects1 = ax2.bar(x - width/2, avg_discounts, width, label='평균 할인율(%)', color='#3182CE', edgecolor='#CBD5E0')
rects2 = ax2.bar(x + width/2, max_discounts, width, label='최대 유찰 할인율(%)', color='#E53E3E', edgecolor='#CBD5E0')

ax2.set_facecolor('#FFFFFF')
ax2.set_ylabel('할인율 (%)', fontsize=11, weight='bold', color='#4A5568')
ax2.set_title("권역별 경매 할인율 비교", fontsize=13, weight='bold', pad=15, color='#1A365D')
ax2.set_xticks(x)
ax2.set_xticklabels(['수도권', '영남권', '충청권', '호남권', '강원·제주'], fontsize=10, weight='bold')
ax2.legend(loc='upper right', frameon=True, facecolor='#FFFFFF')
ax2.grid(axis='y', linestyle='--', alpha=0.5)
ax2.set_ylim(0, 80)

for r in rects1:
    h = r.get_height()
    ax2.annotate(f'{h:.1f}%', xy=(r.get_x() + r.get_width()/2, h),
                 xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, weight='bold', color='#2B6CB0')

for r in rects2:
    h = r.get_height()
    ax2.annotate(f'{h:.1f}%', xy=(r.get_x() + r.get_width()/2, h),
                 xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, weight='bold', color='#C53030')

plt.tight_layout()
chart1_path = os.path.join(output_dir, "chart_nationwide.png")
plt.savefig(chart1_path, bbox_inches='tight')
plt.close()
print("Saved:", chart1_path)

# -------------------------------------------------------------------------
# 차트 2: 대전광역시 TOP 50 추천 물건 자치구별 분포 및 점수대
# -------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=150)
fig.patch.set_facecolor('#F8FAFC')

# 2-1 대전 TOP 50 자치구별 물건 수
districts = ['유성구', '서구', '중구', '대덕구', '동구']
dist_counts = [22, 17, 5, 4, 2]
dist_colors = ['#2B6CB0', '#319795', '#4FD1C5', '#ED8936', '#A0AEC0']

bars = ax1.bar(districts, dist_counts, color=dist_colors, width=0.55, edgecolor='#CBD5E0')
ax1.set_facecolor('#FFFFFF')
ax1.set_title("대전 TOP 50 추천 물건 자치구별 분포", fontsize=13, weight='bold', pad=15, color='#1A365D')
ax1.set_ylabel("추천 물건 수 (건)", fontsize=11, weight='bold', color='#4A5568')
ax1.set_ylim(0, 26)
ax1.grid(axis='y', linestyle='--', alpha=0.5)

for bar in bars:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.6, f'{yval}건 ({yval*2}%)', ha='center', va='bottom', fontsize=10, weight='bold', color='#2D3748')

# 2-2 대전 TOP 50 감정가 vs 최저가 vs 점수 분포
appraisals = [159, 180, 200, 276, 413, 434, 94, 166, 175, 236, 81.7, 620, 36, 40, 1930] # 백만원 단위
min_prices = [38.2, 30.3, 33.6, 46.4, 99.2, 104.2, 32.2, 56.9, 60.0, 80.9, 1.1, 148.9, 12.3, 13.7, 662.0]
scores = [100, 99, 96, 96, 96, 96, 96, 96, 96, 96, 95, 95, 95, 95, 95]
labels = [f'{i+1}위' for i in range(15)]

ax2.set_facecolor('#FFFFFF')
scatter = ax2.scatter(appraisals, min_prices, s=[s*2.5 for s in scores], c=scores, cmap='viridis', edgecolors='#1A365D', alpha=0.85, linewidth=1.5)
cbar = plt.colorbar(scatter, ax=ax2)
cbar.set_label('종합 평가 점수 (100점 만점)', fontsize=10, weight='bold')

for i, txt in enumerate(labels[:8]):
    ax2.annotate(txt, (appraisals[i], min_prices[i]), xytext=(7, 5), textcoords='offset points', fontsize=9, weight='bold', color='#1A365D')

ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.set_xlabel("감정평가액 (백만 원, 로그 스케일)", fontsize=11, weight='bold', color='#4A5568')
ax2.set_ylabel("최저매각가격 (백만 원, 로그 스케일)", fontsize=11, weight='bold', color='#4A5568')
ax2.set_title("대전 TOP 매물 감정가 대비 최저가 & 점수 분포", fontsize=13, weight='bold', pad=15, color='#1A365D')
ax2.grid(True, which="both", ls="--", alpha=0.4)

plt.tight_layout()
chart2_path = os.path.join(output_dir, "chart_daejeon_top50.png")
plt.savefig(chart2_path, bbox_inches='tight')
plt.close()
print("Saved:", chart2_path)

# -------------------------------------------------------------------------
# 차트 3: 소멸주의 메커니즘 인포그래픽 다이어그램
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
fig.patch.set_facecolor('#F8FAFC')
ax.set_facecolor('#F8FAFC')
ax.axis('off')

# 타임라인 화살표
ax.annotate('', xy=(11.5, 3.2), xytext=(0.5, 3.2),
            arrowprops=dict(arrowstyle="->", color="#A0AEC0", lw=3.5))
ax.text(6.0, 3.4, "등기부등본 접수 일자 순서 (시간 흐름)", ha='center', fontsize=12, weight='bold', color='#718096')

# 1. 선순위 권리
box1 = patches.FancyBboxPatch((0.8, 4.0), 2.2, 1.4, boxstyle="round,pad=0.2", fc="#FFF5F5", ec="#E53E3E", lw=2)
ax.add_patch(box1)
ax.text(1.9, 4.9, "⚠️ 선순위 권리", ha='center', fontsize=12, weight='bold', color="#C53030")
ax.text(1.9, 4.35, "• 대항력 임차인\n• 선순위 가처분\n• 유치권(등기외)", ha='center', fontsize=9.5, color="#2D3748")

badge1 = patches.FancyBboxPatch((0.8, 2.0), 2.2, 0.8, boxstyle="round,pad=0.1", fc="#FED7D7", ec="#FEB2B2")
ax.add_patch(badge1)
ax.text(1.9, 2.4, "【인수주의 적용】\n낙찰자가 인수(추가부담)", ha='center', fontsize=10, weight='bold', color="#9B2C2C")

# 2. 말소기준권리 (핵심)
box2 = patches.FancyBboxPatch((3.8, 3.8), 2.8, 1.8, boxstyle="round,pad=0.2", fc="#EBF8FF", ec="#3182CE", lw=3)
ax.add_patch(box2)
ax.text(5.2, 5.0, "★ 말소기준권리 ★", ha='center', fontsize=13, weight='bold', color="#2B6CB0")
ax.text(5.2, 4.3, "① (근)저당권  ② (가)압류\n③ 담보가등기  ④ 경매개시등기\n⑤ 배당요구한 전세권\n(가장 빠른 접수일자 기준)", ha='center', fontsize=9.5, color="#1A202C")

badge2 = patches.FancyBboxPatch((4.0, 1.9), 2.4, 0.9, boxstyle="round,pad=0.1", fc="#BEE3F8", ec="#90CDF4")
ax.add_patch(badge2)
ax.text(5.2, 2.35, "【권리소멸의 기준선】\n이 권리부터 소멸 시작!", ha='center', fontsize=10, weight='bold', color="#2C5282")

# 3. 후순위 소멸 권리
box3 = patches.FancyBboxPatch((7.4, 4.0), 3.8, 1.4, boxstyle="round,pad=0.2", fc="#F0FFF4", ec="#38A169", lw=2)
ax.add_patch(box3)
ax.text(9.3, 4.9, "✅ 후순위 모든 채권/권리", ha='center', fontsize=12, weight='bold', color="#276749")
ax.text(9.3, 4.35, "• 2순위·3순위 근저당, 가압류, 압류\n• 후순위 임차인, 후순위 가등기 등 모든 권리", ha='center', fontsize=9.5, color="#2D3748")

badge3 = patches.FancyBboxPatch((7.6, 1.9), 3.4, 0.9, boxstyle="round,pad=0.1", fc="#C6F6D5", ec="#9AE6B4")
ax.add_patch(badge3)
ax.text(9.3, 2.35, "【소멸주의 100% 적용】\n낙찰자 부담 0원! 법원이 전부 직권 말소!", ha='center', fontsize=10, weight='bold', color="#22543D")

ax.set_xlim(0, 12)
ax.set_ylim(1.2, 6.2)
plt.title("대한민국 법원경매 소멸주의(消滅主義) 권리 소멸 메커니즘", fontsize=15, weight='bold', pad=20, color="#1A365D")

plt.tight_layout()
chart3_path = os.path.join(output_dir, "infographic_extinction.png")
plt.savefig(chart3_path, bbox_inches='tight')
plt.close()
print("Saved:", chart3_path)
