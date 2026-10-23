import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches

matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

output_dir = r"C:\Users\wood\Desktop\aiwork\auction\images"
os.makedirs(output_dir, exist_ok=True)

# 차트 3: 소멸주의 메커니즘 인포그래픽 다이어그램 (이모지 대신 한글 텍스트 사용으로 폰트 경고 완전 제거)
fig, ax = plt.subplots(figsize=(12, 6.2), dpi=160)
fig.patch.set_facecolor('#F8FAFC')
ax.set_facecolor('#F8FAFC')
ax.axis('off')

# 타임라인 화살표
ax.annotate('', xy=(11.5, 3.2), xytext=(0.5, 3.2),
            arrowprops=dict(arrowstyle="->", color="#A0AEC0", lw=3.5))
ax.text(6.0, 3.4, "등기부등본 접수 일자 순서 (시간 흐름)", ha='center', fontsize=12, weight='bold', color='#718096')

# 1. 선순위 권리
box1 = patches.FancyBboxPatch((0.8, 4.0), 2.2, 1.5, boxstyle="round,pad=0.2", fc="#FFF5F5", ec="#E53E3E", lw=2)
ax.add_patch(box1)
ax.text(1.9, 5.0, "[주의] 선순위 권리", ha='center', fontsize=12, weight='bold', color="#C53030")
ax.text(1.9, 4.35, "• 대항력 임차인\n• 선순위 가처분\n• 유치권(등기외)", ha='center', fontsize=9.5, color="#2D3748")

badge1 = patches.FancyBboxPatch((0.8, 1.9), 2.2, 0.9, boxstyle="round,pad=0.1", fc="#FED7D7", ec="#FEB2B2")
ax.add_patch(badge1)
ax.text(1.9, 2.35, "【인수주의 적용】\n낙찰자 인수 (추가 부담)", ha='center', fontsize=10, weight='bold', color="#9B2C2C")

# 2. 말소기준권리 (핵심)
box2 = patches.FancyBboxPatch((3.8, 3.8), 2.8, 1.9, boxstyle="round,pad=0.2", fc="#EBF8FF", ec="#3182CE", lw=3)
ax.add_patch(box2)
ax.text(5.2, 5.15, "★ 말소기준권리 ★", ha='center', fontsize=13, weight='bold', color="#2B6CB0")
ax.text(5.2, 4.3, "① (근)저당권  ② (가)압류\n③ 담보가등기  ④ 경매개시등기\n⑤ 배당요구한 전세권\n(가장 빠른 접수일자 기준)", ha='center', fontsize=9.5, color="#1A202C")

badge2 = patches.FancyBboxPatch((4.0, 1.8), 2.4, 1.0, boxstyle="round,pad=0.1", fc="#BEE3F8", ec="#90CDF4")
ax.add_patch(badge2)
ax.text(5.2, 2.3, "【권리소멸의 기준선】\n이 권리부터 소멸 시작!", ha='center', fontsize=10, weight='bold', color="#2C5282")

# 3. 후순위 소멸 권리
box3 = patches.FancyBboxPatch((7.4, 4.0), 3.8, 1.5, boxstyle="round,pad=0.2", fc="#F0FFF4", ec="#38A169", lw=2)
ax.add_patch(box3)
ax.text(9.3, 5.0, "[안전] 후순위 모든 채권/권리", ha='center', fontsize=12, weight='bold', color="#276749")
ax.text(9.3, 4.35, "• 2순위·3순위 근저당, 가압류, 일반 압류\n• 후순위 임차인, 후순위 가등기 등 모든 권리", ha='center', fontsize=9.5, color="#2D3748")

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
print("Saved clean:", chart3_path)
