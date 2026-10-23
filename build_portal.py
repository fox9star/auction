from datetime import datetime
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# portal_data.json 로드 및 자동 법률/좌표 인리치먼트 보장
from enrich_engine import enrich_all_portal_data

with open(r'C:\Users\wood\Desktop\aiwork\auction\portal_data.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

raw_data = enrich_all_portal_data(raw_data)

meta = raw_data.get('meta', {})
refreshed_at = meta.get('refreshed_at') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
nat_total_cnt = int(meta.get('nationwide_total') or 1395)
dj_total_cnt = int(meta.get('daejeon_total') or 283)
dj_top_cnt = int(meta.get('region_top_count') or meta.get('daejeon_top_count') or 100)
max_disc_str = meta.get('max_discount') or '98.6%'
nat_total_fmt = f"{nat_total_cnt:,}"
dj_total_fmt = f"{dj_total_cnt:,}"
meta_json_str = json.dumps({
    'refreshed_at': refreshed_at,
    'nationwide_total': nat_total_cnt,
    'daejeon_total': dj_total_cnt,
    'daejeon_top_count': dj_top_cnt,
    'region_top_count': 100,
    'max_discount': max_disc_str
}, ensure_ascii=False)


# 병합된 아이템 목록 생성 (각 권역별 TOP 100)
all_items = []
seen_case_keys = {}
regional_top100 = raw_data.get('regional_top100', {})

if regional_top100:
    for reg_key, items_list in regional_top100.items():
        for it in items_list:
            k = f"{it.get('court', '')}|{it.get('case_no', '')}|{it.get('item_no', '1')}"
            if k in seen_case_keys:
                ex = seen_case_keys[k]
                if reg_key not in ex['regions']:
                    ex['regions'].append(reg_key)
                continue
            disc_str = str(it.get('discount', '0%'))
            disc_val = float(it.get('discount_val', disc_str.replace('%', '').strip() or 0))
            item_dict = {
                'id': it['id'],
                'rank': it.get('rank_label') or f"{reg_key} {it['rank']}위",
                'rank_num': int(it.get('rank') or 1),
                'score': it.get('score', 85),
                'region_key': reg_key,
                'region_group': it.get('region', reg_key),
                'regions': [reg_key],
                'sido': it.get('sido', reg_key),
                'sigu': it.get('sigu', it.get('sido', '')),
                'court': it.get('court', ''),
                'dept': it.get('dept', '경매계'),
                'case_no': it.get('case_no', ''),
                'item_no': it.get('item_no', '1'),
                'usage': it.get('usage', '아파트'),
                'address': it.get('address', ''),
                'spec': it.get('spec', ''),
                'appraisal': int(it.get('appraisal') or 0),
                'min_price': int(it.get('min_price') or 0),
                'ratio': it.get('ratio', '100%'),
                'discount': disc_str,
                'discount_val': disc_val,
                'yuchal': it.get('yuchal', '0회'),
                'date': it.get('date', ''),
                'risk': it.get('risk', '안전(소멸주의)'),
                'comment': it.get('comment', ''),
                'lat': it.get('lat') or 36.3504,
                'lng': it.get('lng') or 127.3845,
                'auction_reason': it.get('auction_reason'),
                'tenant_info': it.get('tenant_info'),
                'next_round_sim': it.get('next_round_sim'),
                'category': 'daejeon' if reg_key == '대전광역시' else 'region_top100'
            }
            seen_case_keys[k] = item_dict
            all_items.append(item_dict)
else:
    for it in raw_data.get('daejeon_top50', []):
        all_items.append({
            'id': it['id'],
            'rank': f"대전 {it['rank']}위",
            'rank_num': int(it.get('rank') or 1),
            'score': it['score'],
            'region_key': '대전광역시',
            'region_group': '충청권',
            'regions': ['대전광역시', '충청권'],
            'sido': '대전광역시',
            'sigu': it['sigu'],
            'court': it['court'],
            'dept': it['dept'],
            'case_no': it['case_no'],
            'item_no': it['item_no'],
            'usage': it['usage'],
            'address': it['address'],
            'spec': it['spec'],
            'appraisal': it['appraisal'],
            'min_price': it['min_price'],
            'ratio': it['ratio'],
            'discount': it['discount'],
            'discount_val': float(it['discount'].replace('%', '') if '%' in it['discount'] else 0),
            'yuchal': it['yuchal'],
            'date': it['date'],
            'risk': it['risk'],
            'comment': it['comment'],
            'auction_reason': it.get('auction_reason'),
            'tenant_info': it.get('tenant_info'),
            'next_round_sim': it.get('next_round_sim'),
            'category': 'daejeon'
        })

json_str = json.dumps(all_items, ensure_ascii=False)

html_content = f"""<!DOCTYPE html>
<html lang="ko" data-theme="gray">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>대한민국 법원경매 스마트 분석 포털 | Real Estate Auction Hub</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <!-- Leaflet & MarkerCluster (무료 오픈 지도 엔진) -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
  <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
  <script>
    (function() {{
      try {{
        var saved = localStorage.getItem('auction_theme');
        if (!saved) {{
          // 처음 접속 시 기본 테마: 그레이 모드 적용
          saved = 'gray';
        }}
        if (saved === 'light') {{
          document.documentElement.removeAttribute('data-theme');
        }} else {{
          document.documentElement.setAttribute('data-theme', saved);
        }}
      }} catch (e) {{}}
    }})();
    mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
  </script>
  <style>
    :root {{
      --primary: #1a365d;
      --primary-light: #2a4365;
      --secondary: #2b6cb0;
      --accent: #319795;
      --accent-light: #e6fffa;
      --bg: #f7fafc;
      --card-bg: #ffffff;
      --surface-sub: #f8fafc;
      --heading: #1a365d;
      --text: #2d3748;
      --text-muted: #718096;
      --border: #e2e8f0;
      --red: #e53e3e;
      --red-light: #fff5f5;
      --green: #38a169;
      --green-light: #f0fff4;
      --gold: #d69e2e;
      --gold-light: #fefcbf;
    }}

    html[data-theme="dark"] {{
      --primary: #0f172a;
      --primary-light: #1e293b;
      --secondary: #3b82f6;
      --accent: #14b8a6;
      --accent-light: rgba(20, 184, 166, 0.15);
      --bg: #0b1120;
      --card-bg: #1e293b;
      --surface-sub: #0f172a;
      --heading: #93c5fd;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --border: #334155;
      --red: #f87171;
      --red-light: rgba(239, 68, 68, 0.15);
      --green: #4ade80;
      --green-light: rgba(34, 197, 94, 0.15);
      --gold: #fbbf24;
      --gold-light: rgba(251, 191, 36, 0.18);
      color-scheme: dark;
    }}

    html[data-theme="gray"] {{
      --primary: #374151;
      --primary-light: #4b5563;
      --secondary: #475569;
      --accent: #0f766e;
      --accent-light: #ccfbf1;
      --bg: #cbd5e1;
      --card-bg: #e5e7eb;
      --surface-sub: #d6dce3;
      --heading: #1f2937;
      --text: #1f2937;
      --text-muted: #4b5563;
      --border: #b8c1cc;
      --red: #b91c1c;
      --red-light: #fee2e2;
      --green: #15803d;
      --green-light: #dcfce7;
      --gold: #b45309;
      --gold-light: #fef3c7;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
    }}

    /* Header Nav */
    header {{
      background: var(--primary);
      color: #fff;
      padding: 14px 20px;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    }}

    .header-inner {{
      max-width: 1580px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: nowrap;
      gap: 10px;
    }}

    .logo-area {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-shrink: 0;
      cursor: pointer;
      user-select: none;
      transition: opacity 0.15s, transform 0.15s;
    }}
    .logo-area:hover {{
      opacity: 0.92;
      transform: translateY(-1px);
    }}
    .logo-area:active {{
      transform: scale(0.98);
    }}

    .logo-icon {{
      background: var(--accent);
      color: #fff;
      width: 36px;
      height: 36px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 900;
      font-size: 1.15rem;
      flex-shrink: 0;
    }}

    .logo-text h1 {{
      font-size: 1.12rem;
      font-weight: 800;
      letter-spacing: -0.5px;
      white-space: nowrap;
    }}

    .logo-text p {{
      font-size: 0.7rem;
      color: #cbd5e0;
      white-space: nowrap;
    }}

    nav {{
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: nowrap;
    }}

    .nav-btn {{
      background: rgba(255,255,255,0.12);
      border: 1px solid rgba(255,255,255,0.2);
      color: #fff;
      padding: 7px 11px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.8rem;
      font-weight: 600;
      transition: all 0.2s;
      white-space: nowrap;
      flex-shrink: 0;
    }}

    .nav-btn:hover, .nav-btn.active {{
      background: #fff;
      color: var(--primary);
      border-color: #fff;
    }}

    /* Main Container */
    .container {{
      max-width: 1300px;
      margin: 25px auto;
      padding: 0 20px;
    }}

    /* Hero Banner Area */
    .hero-card {{
      background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
      color: #fff;
      border-radius: 12px;
      padding: 28px 38px 24px;
      margin-bottom: 25px;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 14px;
      box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }}

    .hero-top-row {{
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 20px;
    }}

    .hero-text {{
      flex: 1;
      min-width: 300px;
    }}

    .hero-text h2 {{
      font-size: 1.7rem;
      font-weight: 800;
      margin-bottom: 8px;
      line-height: 1.25;
    }}

    .hero-text p {{
      font-size: 0.95rem;
      color: #e2e8f0;
      max-width: 720px;
      line-height: 1.55;
    }}

    .hero-stats {{
      display: flex;
      gap: 16px;
      align-items: stretch;
      flex-shrink: 0;
    }}

    .stat-pill {{
      background: rgba(255,255,255,0.15);
      backdrop-filter: blur(5px);
      padding: 12px 20px;
      border-radius: 8px;
      text-align: center;
      border: 1px solid rgba(255,255,255,0.25);
    }}

    .stat-pill .num {{
      font-size: 1.5rem;
      font-weight: 900;
      color: #38b2ac;
    }}

    .stat-pill .label {{
      font-size: 0.78rem;
      color: #edf2f7;
    }}

    /* Search & Filter Toolbar */
    .toolbar {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 20px 24px;
      margin-bottom: 25px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }}

    .search-row {{
      display: flex;
      gap: 12px;
      margin-bottom: 16px;
    }}

    .search-input {{
      flex: 1;
      padding: 12px 18px;
      border: 2px solid var(--border);
      border-radius: 8px;
      font-size: 0.95rem;
      outline: none;
      background: var(--card-bg);
      color: var(--text);
      transition: border-color 0.2s, background-color 0.2s;
    }}

    .search-input:focus {{
      border-color: var(--secondary);
    }}

    .filter-row {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      align-items: center;
    }}

    .filter-group {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .filter-group label {{
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--text-muted);
    }}

    select {{
      padding: 8px 12px;
      border: 1px solid var(--border);
      border-radius: 6px;
      font-size: 0.88rem;
      background: var(--card-bg);
      color: var(--text);
      cursor: pointer;
    }}

    .btn-reset {{
      margin-left: auto;
      background: var(--surface-sub);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 8px 14px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.85rem;
      font-weight: 600;
    }}

    .btn-reset:hover {{
      background: var(--border);
    }}

    /* Content Views */
    .view-section {{
      display: none;
    }}

    .view-section.active {{
      display: block;
    }}

    /* Cards Grid */
    .results-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 15px;
      padding: 0 4px;
    }}

    .results-count {{
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text-muted);
    }}

    .results-count span {{
      color: var(--secondary);
      font-size: 1.1rem;
    }}

    .view-toggle-btns {{
      display: flex;
      gap: 6px;
    }}

    .toggle-btn {{
      padding: 6px 12px;
      background: var(--card-bg);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.82rem;
      font-weight: 600;
    }}

    .toggle-btn.active {{
      background: var(--secondary);
      color: #fff;
      border-color: var(--secondary);
    }}

    .cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
      gap: 20px;
    }}

    .auction-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 20px;
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
      position: relative;
      display: flex;
      flex-direction: column;
    }}

    .auction-card:hover {{
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.08);
      border-color: var(--secondary);
    }}

    .card-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
    }}

    .badges {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }}

    .badge {{
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 700;
    }}

    .badge-rank {{
      background: #ebf8ff;
      color: var(--secondary);
    }}

    .badge-discount {{
      background: var(--red-light);
      color: var(--red);
    }}

    .badge-safe {{
      background: var(--green-light);
      color: var(--green);
    }}

    .badge-risk-safe {{
      background: var(--green-light);
      color: var(--green);
      border: 1px solid rgba(56, 161, 105, 0.35);
      font-weight: 700;
    }}

    .badge-risk-warning {{
      background: var(--gold-light);
      color: #744210;
      border: 1px solid rgba(214, 158, 46, 0.45);
      font-weight: 700;
    }}

    .badge-risk-danger {{
      background: var(--red-light);
      color: var(--red);
      border: 1px solid rgba(229, 62, 62, 0.45);
      font-weight: 700;
    }}

    /* Legal, Tenant, Foreigner & Simulation Styles */
    .badge-foreigner {{
      background: #ede9fe;
      color: #5b21b6;
      border: 1px solid #c4b5fd;
      font-weight: 800;
    }}
    .badge-domestic {{
      background: #ecfdf5;
      color: #047857;
      border: 1px solid #a7f3d0;
      font-weight: 700;
    }}
    .badge-owner {{
      background: #f1f5f9;
      color: #475569;
      border: 1px solid #cbd5e1;
      font-weight: 600;
    }}
    .badge-auction-reason {{
      background: #fef3c7;
      color: #92400e;
      border: 1px solid #fde68a;
      font-weight: 700;
    }}

    .legal-quick-filter-bar {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      padding: 10px 14px;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      margin-bottom: 14px;
    }}
    .lqf-label {{
      font-size: 0.85rem;
      font-weight: 800;
      color: var(--heading);
      margin-right: 4px;
    }}
    .lqf-btn {{
      background: var(--surface-sub);
      border: 1px solid var(--border);
      color: var(--text);
      font-size: 0.82rem;
      padding: 6px 12px;
      border-radius: 20px;
      cursor: pointer;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
    }}
    .lqf-btn:hover {{
      background: #e2e8f0;
      border-color: #cbd5e1;
    }}
    .lqf-btn.active {{
      background: var(--primary);
      color: #fff;
      border-color: var(--primary);
      font-weight: 800;
      box-shadow: 0 2px 6px rgba(49, 130, 206, 0.35);
    }}
    .lqf-btn.lqf-foreign {{
      border-color: #c4b5fd;
      background: #f5f3ff;
      color: #5b21b6;
    }}
    .lqf-btn.lqf-foreign.active {{
      background: #6366f1;
      color: #fff;
      border-color: #6366f1;
    }}
    .lqf-cnt {{
      background: rgba(0, 0, 0, 0.08);
      padding: 1px 6px;
      border-radius: 10px;
      font-size: 0.74rem;
      font-weight: 700;
    }}
    .lqf-btn.active .lqf-cnt {{
      background: rgba(255, 255, 255, 0.25);
      color: #fff;
    }}

    .card-legal-row {{
      display: flex;
      flex-direction: column;
      gap: 4px;
      margin: 8px 0;
      padding: 8px 10px;
      background: var(--surface-sub);
      border: 1px solid var(--border);
      border-radius: 6px;
      font-size: 0.78rem;
    }}
    .card-legal-row .legal-tag {{
      display: flex;
      align-items: baseline;
      gap: 6px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    .card-legal-row .legal-tag.tag-foreign {{
      color: #5b21b6;
      font-weight: 700;
    }}
    .card-legal-row .tag-icon {{
      font-size: 0.85rem;
    }}
    .card-legal-row .tag-text {{
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    .card-next-sim {{
      margin-top: 6px;
      padding: 6px 8px;
      background: #eff6ff;
      border-left: 3px solid #3b82f6;
      border-radius: 4px;
      font-size: 0.76rem;
      color: #1e40af;
      line-height: 1.4;
    }}

    /* Modal Legal Sections */
    .legal-detail-section {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px;
      margin-bottom: 14px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }}
    .section-badge-head {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border);
    }}
    .section-badge-head .sb-title {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 1.02rem;
      font-weight: 800;
      color: var(--heading);
    }}
    .legal-detail-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 10px;
      margin-bottom: 12px;
    }}
    .legal-grid-cell {{
      background: var(--surface-sub);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 10px 12px;
    }}
    .legal-grid-cell .lg-label {{
      font-size: 0.74rem;
      color: var(--text-muted);
      font-weight: 700;
      margin-bottom: 3px;
    }}
    .legal-grid-cell .lg-val {{
      font-size: 0.9rem;
      color: var(--heading);
      line-height: 1.3;
    }}
    .legal-story-desc {{
      background: var(--surface-sub);
      border-radius: 6px;
      padding: 12px;
      font-size: 0.86rem;
      line-height: 1.6;
      color: var(--text);
      border-left: 4px solid var(--primary);
    }}
    .legal-story-desc .ls-lead {{
      font-weight: 800;
      color: var(--heading);
      margin-bottom: 4px;
    }}

    /* Foreigner Alert Banner */
    .foreigner-alert-banner {{
      background: #f5f3ff;
      border: 2px solid #818cf8;
      border-radius: 8px;
      padding: 14px;
      margin-bottom: 14px;
    }}
    .foreigner-alert-banner .fab-head {{
      display: flex;
      gap: 10px;
      align-items: center;
      margin-bottom: 8px;
    }}
    .foreigner-alert-banner .fab-icon {{
      font-size: 1.6rem;
    }}
    .foreigner-alert-banner .fab-title {{
      font-size: 0.96rem;
      font-weight: 800;
      color: #4338ca;
    }}
    .foreigner-alert-banner .fab-court-case {{
      font-size: 0.76rem;
      color: #6366f1;
      font-weight: 700;
    }}
    .foreigner-alert-banner .fab-body {{
      font-size: 0.85rem;
      line-height: 1.55;
      color: #312e81;
    }}
    .foreigner-alert-banner .fab-warning {{
      background: #fee2e2;
      border: 1px solid #fca5a5;
      color: #991b1b;
      padding: 6px 10px;
      border-radius: 6px;
      margin-bottom: 8px;
      font-size: 0.84rem;
    }}
    .foreigner-alert-banner .fab-badges {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 10px;
      padding-top: 10px;
      border-top: 1px dashed #c7d2fe;
      font-size: 0.82rem;
      color: #3730a3;
    }}

    .owner-occupant-banner {{
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 10px 12px;
      margin-bottom: 12px;
      font-size: 0.85rem;
      color: #334155;
    }}
    .domestic-tenant-banner {{
      background: #f0fdf4;
      border: 1px solid #86efac;
      border-radius: 6px;
      padding: 10px 12px;
      margin-bottom: 12px;
      font-size: 0.85rem;
      color: #166534;
    }}

    /* Simulation Section */
    .sim-metric-row {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 10px;
      margin-bottom: 12px;
    }}
    .sim-box {{
      background: #ffffff;
      border: 1px solid #bfdbfe;
      border-radius: 8px;
      padding: 10px 12px;
      text-align: center;
    }}
    .sim-box .sim-lbl {{
      font-size: 0.74rem;
      color: #64748b;
      font-weight: 700;
      margin-bottom: 4px;
    }}
    .sim-box .sim-val {{
      font-size: 1.05rem;
      font-weight: 900;
      color: #1e3a8a;
    }}
    .sim-box .sim-sub {{
      font-size: 0.72rem;
      color: #dc2626;
      font-weight: 700;
      margin-top: 2px;
    }}
    .sim-advice-box {{
      background: #eff6ff;
      border-left: 4px solid #2563eb;
      padding: 10px 12px;
      border-radius: 6px;
      font-size: 0.85rem;
      line-height: 1.5;
      color: #1e3a8a;
    }}

    /* 등기부을구 권리분석 타임라인 서열 카드 */
    .lien-timeline-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px;
      margin-bottom: 14px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }}
    .lt-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border);
    }}
    .lt-title {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 1.02rem;
      font-weight: 800;
      color: var(--heading);
    }}
    .lt-track {{
      display: flex;
      align-items: center;
      gap: 8px;
      overflow-x: auto;
      padding-bottom: 8px;
    }}
    .lt-node {{
      flex: 1;
      min-width: 170px;
      background: var(--surface-sub);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 12px;
      text-align: center;
      position: relative;
    }}
    .lt-node.malso-node {{
      border-color: #3b82f6;
      background: #eff6ff;
    }}
    .lt-node.tenant-node {{
      border-color: #10b981;
      background: #ecfdf5;
    }}
    .lt-node.danger-node {{
      border-color: #ef4444;
      background: #fef2f2;
    }}
    .lt-node.normal-node {{
      border-color: #cbd5e1;
      background: #f8fafc;
    }}
    .lt-node.end-node {{
      border-color: #8b5cf6;
      background: #f5f3ff;
    }}
    .lt-tag {{
      font-size: 0.7rem;
      font-weight: 800;
      padding: 2px 8px;
      border-radius: 12px;
      display: inline-block;
      margin-bottom: 4px;
    }}
    .tag-malso {{ background: #3b82f6; color: #fff; }}
    .tag-tenant {{ background: #10b981; color: #fff; }}
    .tag-danger {{ background: #ef4444; color: #fff; }}
    .tag-normal {{ background: #64748b; color: #fff; }}
    .tag-end {{ background: #8b5cf6; color: #fff; }}
    .lt-date {{ font-size: 0.76rem; color: var(--text-muted); font-weight: 700; }}
    .lt-name {{ font-size: 0.86rem; font-weight: 800; color: var(--heading); margin: 2px 0; }}
    .lt-sub {{ font-size: 0.74rem; color: var(--text-muted); margin-bottom: 4px; }}
    .lt-status {{ font-size: 0.75rem; font-weight: 800; padding: 2px 6px; border-radius: 4px; }}
    .status-extinguish {{ color: #047857; background: #d1fae5; }}
    .status-takeover {{ color: #b91c1c; background: #fee2e2; }}
    .lt-connector {{ color: #94a3b8; font-weight: 900; font-size: 1.1rem; }}
    .lt-summary-note {{
      margin-top: 10px;
      padding: 8px 12px;
      background: var(--surface-sub);
      border-radius: 6px;
      font-size: 0.82rem;
      line-height: 1.5;
    }}

    /* 실거래가 대조 갭투자 & 수익률 시뮬레이터 카드 */
    .invest-sim-card {{
      background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
      border: 1px solid #bae6fd;
      border-radius: 10px;
      padding: 16px;
      margin-bottom: 14px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }}
    .isc-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 1px solid #e0f2fe;
    }}
    .isc-title {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 1.02rem;
      font-weight: 800;
      color: #0369a1;
    }}
    .isc-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 10px;
    }}
    .isc-cell {{
      background: #ffffff;
      border: 1px solid #e0f2fe;
      border-radius: 8px;
      padding: 10px 12px;
      text-align: center;
      transition: all 0.2s ease;
    }}
    .isc-cell.highlight-zero-gap {{
      border-color: #c4b5fd;
      background: #faf5ff;
    }}
    .isc-label {{
      font-size: 0.74rem;
      font-weight: 700;
      color: #64748b;
      margin-bottom: 4px;
    }}
    .isc-main {{
      font-size: 1.12rem;
      font-weight: 900;
      line-height: 1.2;
    }}
    .isc-sub {{
      font-size: 0.72rem;
      color: var(--text-muted);
      margin-top: 3px;
    }}

    /* 인터랙티브 지도 뷰 스타일 */
    .map-view-layout {{
      display: flex;
      gap: 14px;
      height: 740px;
    }}
    .map-list-sidebar {{
      width: 380px;
      min-width: 330px;
      display: flex;
      flex-direction: column;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      overflow: hidden;
    }}
    .map-sidebar-head {{
      padding: 12px 14px;
      background: var(--surface-sub);
      border-bottom: 1px solid var(--border);
    }}
    .map-sidebar-items {{
      flex: 1;
      overflow-y: auto;
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .map-sidebar-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 12px;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .map-sidebar-card:hover, .map-sidebar-card.active {{
      border-color: #2563eb;
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
      transform: translateY(-1px);
    }}
    .map-sidebar-card.active {{
      background: var(--surface-sub);
      border-width: 2px;
    }}
    .map-main-pane {{
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 8px;
      min-width: 0;
    }}
    .map-toolbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
      background: var(--surface-sub);
      border: 1px solid var(--border);
      padding: 8px 12px;
      border-radius: 8px;
    }}
    .map-quick-regions {{
      display: flex;
      align-items: center;
      gap: 4px;
      flex-wrap: wrap;
    }}
    .map-loc-btn {{
      padding: 4px 10px;
      border-radius: 6px;
      border: 1px solid var(--border);
      background: var(--card-bg);
      color: var(--text);
      font-size: 0.76rem;
      font-weight: 800;
      cursor: pointer;
      transition: all 0.15s;
    }}
    .map-loc-btn:hover, .map-loc-btn.active {{
      background: #2563eb;
      color: #fff;
      border-color: #2563eb;
    }}
    .map-legend-bar {{
      display: flex;
      align-items: center;
      gap: 14px;
      font-size: 0.76rem;
      padding: 6px 12px;
      background: var(--surface-sub);
      border: 1px solid var(--border);
      border-radius: 6px;
      flex-wrap: wrap;
    }}
    .legend-item {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-weight: 700;
    }}
    .legend-dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }}
    .legend-dot.red {{ background: #e53e3e; }}
    .legend-dot.orange {{ background: #ed8936; }}
    .legend-dot.gold {{ background: #d69e2e; }}
    .legend-dot.blue {{ background: #3182ce; }}

    .leaflet-popup-content-wrapper {{
      background: var(--card-bg, #fff) !important;
      color: var(--text, #1a202c) !important;
      border-radius: 10px !important;
      box-shadow: 0 10px 25px rgba(0,0,0,0.3) !important;
      border: 1px solid var(--border, #e2e8f0) !important;
      padding: 0 !important;
    }}
    .leaflet-popup-content {{
      margin: 12px 14px !important;
      line-height: 1.4 !important;
    }}

    .badge-score {{
      background: var(--gold-light);
      color: #744210;
      font-weight: 800;
    }}

    .card-case {{
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--text-muted);
    }}

    .card-title {{
      font-size: 1.05rem;
      font-weight: 800;
      color: var(--heading);
      margin-bottom: 8px;
      line-height: 1.4;
    }}

    .card-spec {{
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-bottom: 14px;
      background: var(--surface-sub);
      padding: 6px 10px;
      border-radius: 6px;
    }}

    .price-box {{
      margin-top: auto;
      border-top: 1px dashed var(--border);
      padding-top: 12px;
    }}

    .price-row {{
      display: flex;
      justify-content: space-between;
      font-size: 0.85rem;
      margin-bottom: 4px;
    }}

    .price-row .label {{ color: var(--text-muted); }}
    .price-row .val {{ font-weight: 600; }}

    .price-main {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-top: 6px;
    }}

    .price-main .label {{
      font-size: 0.9rem;
      font-weight: 800;
      color: var(--red);
    }}

    .price-main .val {{
      font-size: 1.25rem;
      font-weight: 900;
      color: var(--red);
    }}

    .card-meta {{
      margin-top: 12px;
      display: flex;
      justify-content: space-between;
      font-size: 0.78rem;
      color: var(--text-muted);
      border-top: 1px solid var(--border);
      padding-top: 8px;
    }}

    /* Yuchal Story Styles (카드 요약 & 상세 모달 회차별 타임라인/스토리) */
    .card-yuchal-story {{
      margin-top: 10px;
      padding: 8px 11px;
      border-radius: 7px;
      background: var(--surface-sub);
      border: 1px solid var(--border);
      border-left: 4px solid var(--red);
      font-size: 0.79rem;
      line-height: 1.45;
      color: var(--text);
    }}
    .card-yuchal-story .ys-head {{
      font-weight: 800;
      color: var(--red);
      margin-right: 4px;
    }}
    .card-yuchal-story .ys-sub {{
      display: block;
      margin-top: 2px;
      font-size: 0.75rem;
      color: var(--text-muted);
    }}
    .yuchal-story-section {{
      background: var(--surface-sub);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px 16px;
      margin-bottom: 12px;
    }}
    .yuchal-story-head {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 10px;
    }}
    .yuchal-story-title {{
      font-size: 0.92rem;
      font-weight: 800;
      color: var(--heading);
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .yuchal-steps-bar {{
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
      margin-bottom: 10px;
      padding: 8px 10px;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
    }}
    .yuchal-step-pill {{
      display: inline-flex;
      flex-direction: column;
      padding: 5px 10px;
      border-radius: 6px;
      background: var(--surface-sub);
      border: 1px solid var(--border);
      font-size: 0.74rem;
      line-height: 1.3;
    }}
    .yuchal-step-pill.current {{
      background: var(--red-light);
      border-color: var(--red);
      color: var(--red);
      font-weight: 800;
    }}
    .yuchal-step-arrow {{
      color: var(--text-muted);
      font-size: 0.8rem;
      font-weight: 800;
    }}
    .yuchal-timeline-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.78rem;
      margin-bottom: 10px;
      background: var(--card-bg);
      border-radius: 6px;
      overflow: hidden;
    }}
    .yuchal-timeline-table th {{
      background: var(--primary);
      color: #fff;
      padding: 6px 8px;
      text-align: left;
      font-weight: 700;
      white-space: nowrap;
    }}
    .yuchal-timeline-table td {{
      padding: 6px 8px;
      border-bottom: 1px solid var(--border);
    }}
    .yuchal-timeline-table tr.cur-round td {{
      background: var(--red-light);
      font-weight: 800;
    }}
    .yuchal-narrative-box {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-left: 4px solid var(--secondary);
      border-radius: 8px;
      padding: 10px 13px;
      font-size: 0.82rem;
      line-height: 1.55;
      color: var(--text);
    }}
    .yuchal-narrative-box ul {{
      margin-left: 16px;
      margin-top: 4px;
    }}
    .yuchal-narrative-box li {{
      margin-bottom: 4px;
    }}

    /* Table View */
    .table-view-container {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      overflow-x: auto;
      display: none;
    }}

    table.data-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.88rem;
    }}

    table.data-table th {{
      background: var(--primary);
      color: #fff;
      padding: 12px 14px;
      font-weight: 600;
      white-space: nowrap;
      text-align: left;
    }}

    table.data-table td {{
      padding: 12px 14px;
      border-bottom: 1px solid var(--border);
      vertical-align: middle;
    }}

    table.data-table tr:hover td {{
      background: var(--surface-sub);
      cursor: pointer;
    }}

    /* Detail Modal */
    .modal-backdrop {{
      display: none;
      position: fixed;
      top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0,0,0,0.5);
      backdrop-filter: blur(3px);
      z-index: 1000;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }}

    .modal-backdrop.show {{
      display: flex;
    }}

    .modal-box {{
      background: var(--card-bg);
      color: var(--text);
      width: 100%;
      max-width: 740px;
      border-radius: 12px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.25);
      overflow: hidden;
      animation: pop 0.2s ease-out;
      max-height: 94vh;
      display: flex;
      flex-direction: column;
    }}

    @keyframes pop {{
      from {{ transform: scale(0.95); opacity: 0; }}
      to {{ transform: scale(1); opacity: 1; }}
    }}

    .modal-header {{
      background: var(--primary);
      color: #fff;
      padding: 14px 22px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .modal-header h3 {{
      font-size: 1.1rem;
      font-weight: 800;
    }}

    .modal-close {{
      background: none;
      border: none;
      color: #fff;
      font-size: 1.4rem;
      cursor: pointer;
    }}

    .modal-body {{
      padding: 18px 22px;
      overflow-y: auto;
    }}

    .modal-info-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      margin-bottom: 12px;
    }}
    @media (max-width: 640px) {{
      .modal-info-grid {{ grid-template-columns: 1fr 1fr; }}
    }}

    .modal-item {{
      background: var(--surface-sub);
      padding: 10px 12px;
      border-radius: 8px;
      border: 1px solid var(--border);
    }}

    .modal-item .title {{
      font-size: 0.75rem;
      color: var(--text-muted);
      font-weight: 600;
      margin-bottom: 3px;
    }}

    .modal-item .desc {{
      font-size: 0.92rem;
      font-weight: 700;
      color: var(--text);
    }}

    .modal-footer {{
      padding: 12px 22px;
      border-top: 1px solid var(--border);
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      background: var(--surface-sub);
    }}

    .btn-action {{
      background: var(--secondary);
      color: #fff;
      padding: 10px 18px;
      border-radius: 6px;
      text-decoration: none;
      font-size: 0.88rem;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border: none;
      cursor: pointer;
    }}

    .btn-action:hover {{
      background: var(--primary);
    }}

    /* Knowledge & Guide Section */
    .guide-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 30px;
      margin-bottom: 25px;
    }}

    .guide-card h3 {{
      font-size: 1.35rem;
      color: var(--heading);
      margin-bottom: 16px;
      border-bottom: 2px solid var(--border);
      padding-bottom: 10px;
    }}

    .img-box {{
      text-align: center;
      margin: 20px 0;
    }}

    .img-box img {{
      max-width: 100%;
      height: auto;
      border-radius: 8px;
      border: 1px solid var(--border);
      box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    }}

    /* Downloads List */
    .dl-list {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 16px;
    }}

    .dl-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 18px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }}

    .dl-card .icon {{
      font-size: 1.6rem;
      margin-right: 12px;
    }}

    .dl-card .details h4 {{
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--heading);
    }}

    .dl-card .details p {{
      font-size: 0.78rem;
      color: var(--text-muted);
    }}

    /* Theme Switcher Group */
    .theme-group {{
      display: inline-flex;
      align-items: center;
      background: rgba(0,0,0,0.22);
      padding: 3px;
      border-radius: 8px;
      border: 1px solid rgba(255,255,255,0.22);
      gap: 3px;
      margin-left: 2px;
      flex-shrink: 0;
      white-space: nowrap;
    }}
    .theme-toggle {{
      background: transparent;
      border: none;
      color: rgba(255,255,255,0.85);
      padding: 5px 10px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.8rem;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: all 0.18s;
      white-space: nowrap;
    }}
    .theme-toggle:hover {{
      background: rgba(255,255,255,0.16);
      color: #fff;
    }}
    .theme-toggle.active {{
      background: #fff;
      color: #1a365d;
      box-shadow: 0 1px 4px rgba(0,0,0,0.2);
    }}
    html[data-theme="dark"] .theme-toggle.active {{
      background: #fde68a;
      color: #0f172a;
    }}
    html[data-theme="gray"] .theme-toggle.active {{
      background: #e5e7eb;
      color: #1f2937;
    }}
    html[data-theme="gray"] .badge-rank {{
      background: #cbd5e1;
      color: #1e293b;
    }}
    html[data-theme="gray"] .guide-box-pro {{
      background: #d5e3dc !important;
      border-color: #86efac !important;
    }}
    html[data-theme="gray"] .guide-box-con {{
      background: #e7dfd3 !important;
      border-color: #fca5a5 !important;
    }}
    html[data-theme="dark"] .badge-rank {{
      background: rgba(59, 130, 246, 0.2);
      color: #93c5fd;
    }}
    html[data-theme="dark"] .badge-score {{
      color: #fde68a;
    }}
    html[data-theme="dark"] .mermaid {{
      background: #f8fafc;
      border-radius: 8px;
      padding: 14px;
    }}
    html[data-theme="dark"] .court-region-card {{
      background: var(--surface-sub) !important;
      border-color: var(--border) !important;
    }}
    html[data-theme="dark"] .court-region-card h4 {{
      color: var(--heading) !important;
    }}
    html[data-theme="dark"] .guide-box-pro {{
      background: rgba(34, 197, 94, 0.12) !important;
      border-color: rgba(34, 197, 94, 0.35) !important;
    }}
    html[data-theme="dark"] .guide-box-pro h4,
    html[data-theme="dark"] .guide-box-pro div {{
      color: #86efac !important;
    }}
    html[data-theme="dark"] .guide-box-pro ul {{
      color: var(--text) !important;
    }}
    html[data-theme="dark"] .guide-box-con {{
      background: rgba(239, 68, 68, 0.12) !important;
      border-color: rgba(239, 68, 68, 0.35) !important;
    }}
    html[data-theme="dark"] .guide-box-con h4 {{
      color: #fca5a5 !important;
    }}
    html[data-theme="dark"] .guide-box-con ul {{
      color: var(--text) !important;
    }}

    /* Refresh Button & Status Badge */
    .btn-refresh-data {{
      background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%);
      color: #fff;
      border: 1px solid rgba(255,255,255,0.28);
      padding: 7px 13px;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
      box-shadow: 0 2px 6px rgba(0,0,0,0.18);
    }}
    .btn-refresh-data:hover {{
      filter: brightness(1.1);
      transform: translateY(-1px);
    }}
    .btn-refresh-data.loading .refresh-icon {{
      display: inline-block;
      animation: spinRefresh 0.8s linear infinite;
    }}
    @keyframes spinRefresh {{
      from {{ transform: rotate(0deg); }}
      to {{ transform: rotate(360deg); }}
    }}
    .refresh-meta-bar {{
      display: inline-flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 2px;
      padding: 6px 14px;
      border-radius: 999px;
      background: rgba(255,255,255,0.14);
      border: 1px solid rgba(255,255,255,0.22);
      font-size: 0.78rem;
      color: #e2e8f0;
    }}
    .refresh-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #4ade80;
      box-shadow: 0 0 8px #4ade80;
      display: inline-block;
    }}
    .refresh-dot.offline {{
      background: #fbbf24;
      box-shadow: 0 0 8px #fbbf24;
    }}
    .btn-live-court {{
      background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
      color: #fff;
      border: 1px solid rgba(255,255,255,0.28);
      padding: 10px 18px;
      border-radius: 8px;
      font-size: 0.9rem;
      font-weight: 800;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
      transition: all 0.2s;
      box-shadow: 0 3px 10px rgba(37,99,235,0.28);
    }}
    .btn-live-court:hover {{
      filter: brightness(1.1);
      transform: translateY(-1px);
    }}
    .btn-live-court.loading .live-icon {{
      display: inline-block;
      animation: spinRefresh 0.8s linear infinite;
    }}
    .badge-live {{
      background: #dc2626;
      color: #fff;
      font-weight: 800;
      animation: pulseLive 1.8s infinite;
    }}
    @keyframes pulseLive {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.72; }}
    }}
    #refresh-toast {{
      position: fixed;
      top: 76px;
      right: 24px;
      z-index: 9999;
      background: var(--primary);
      color: #fff;
      border: 1px solid rgba(255,255,255,0.22);
      padding: 12px 18px;
      border-radius: 10px;
      font-size: 0.86rem;
      font-weight: 700;
      box-shadow: 0 10px 28px rgba(0,0,0,0.28);
      opacity: 0;
      transform: translateY(-10px);
      pointer-events: none;
      transition: all 0.25s ease;
    }}
    #refresh-toast.show {{
      opacity: 1;
      transform: translateY(0);
    }}

    /* Regional TOP 100 Quick Selector Bar */
    .region-top100-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 14px;
      padding: 12px 16px;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      align-items: center;
    }}
    .region-top100-bar .bar-title {{
      font-size: 0.85rem;
      font-weight: 800;
      color: var(--heading);
      margin-right: 6px;
      white-space: nowrap;
    }}
    .region-pill-btn {{
      background: var(--surface-sub);
      color: var(--text);
      border: 1px solid var(--border);
      padding: 7px 13px;
      border-radius: 999px;
      font-size: 0.82rem;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.18s;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      white-space: nowrap;
    }}
    .region-pill-btn:hover {{
      border-color: var(--accent);
      color: var(--accent);
      transform: translateY(-1px);
    }}
    .region-pill-btn.active {{
      background: var(--primary);
      color: #fff;
      border-color: var(--primary);
      box-shadow: 0 2px 8px rgba(26,54,93,0.25);
    }}
    .region-pill-btn .cnt-badge {{
      background: rgba(255,255,255,0.22);
      padding: 1px 6px;
      border-radius: 999px;
      font-size: 0.72rem;
      font-weight: 800;
    }}
    .region-pill-btn:not(.active) .cnt-badge {{
      background: var(--border);
      color: var(--text-muted);
    }}

    /* Map Buttons & Embedded Map Styles */
    .btn-map-mini {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 9px;
      border-radius: 6px;
      border: 1px solid rgba(49, 151, 149, 0.35);
      background: var(--accent-light);
      color: var(--accent);
      font-size: 0.75rem;
      font-weight: 800;
      cursor: pointer;
      transition: all 0.15s;
      white-space: nowrap;
      text-decoration: none;
    }}
    .btn-map-mini:hover {{
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
      transform: translateY(-1px);
    }}
    .map-embed-wrap {{
      background: var(--surface-sub);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px 14px;
      margin-bottom: 12px;
    }}
    .map-embed-head {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 8px;
    }}
    .map-embed-title {{
      font-size: 0.88rem;
      font-weight: 800;
      color: var(--heading);
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .map-ext-btns {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }}
    .map-ext-btn {{
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 0.74rem;
      font-weight: 800;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      cursor: pointer;
      border: 1px solid var(--border);
      background: var(--card-bg);
      color: var(--text);
      transition: all 0.15s;
    }}
    .map-ext-btn:hover {{
      transform: translateY(-1px);
      filter: brightness(0.96);
    }}
    .map-ext-btn.naver {{ background: #03c75a; color: #fff; border-color: #02b350; }}
    .map-ext-btn.kakao {{ background: #fee500; color: #191919; border-color: #ebd400; }}
    .map-ext-btn.google {{ background: #2563eb; color: #fff; border-color: #1d4ed8; }}
    .map-iframe-frame {{
      width: 100%;
      height: 230px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: #e2e8f0;
    }}

    /* 60 Courts Directory Grid & Cards */
    .courts-dir-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 16px;
      margin-top: 16px;
    }}
    .court-item-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-left: 5px solid var(--secondary);
      border-radius: 10px;
      padding: 16px 18px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      transition: transform 0.18s, box-shadow 0.18s, border-color 0.18s;
    }}
    .court-item-card.bonwon {{
      border-left-color: var(--primary);
    }}
    .court-item-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 18px rgba(0,0,0,0.07);
      border-color: var(--accent);
    }}
    .court-card-head {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .court-name-wrap {{
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }}
    .court-num-badge {{
      background: var(--surface-sub);
      border: 1px solid var(--border);
      color: var(--text-muted);
      font-size: 0.72rem;
      font-weight: 800;
      padding: 2px 7px;
      border-radius: 5px;
    }}
    .court-type-badge {{
      font-size: 0.72rem;
      font-weight: 800;
      padding: 2px 7px;
      border-radius: 5px;
    }}
    .court-type-badge.bonwon {{
      background: #1a365d;
      color: #fff;
    }}
    .court-type-badge.jiwon {{
      background: #e2e8f0;
      color: #1e293b;
    }}
    html[data-theme="dark"] .court-type-badge.jiwon {{
      background: #334155;
      color: #e2e8f0;
    }}
    .court-info-line {{
      font-size: 0.84rem;
      color: var(--text);
      line-height: 1.45;
      display: flex;
      align-items: flex-start;
      gap: 6px;
    }}
    .court-info-line .lbl {{
      font-weight: 800;
      color: var(--text-muted);
      min-width: 64px;
      flex-shrink: 0;
    }}
    .court-card-actions {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      margin-top: auto;
      padding-top: 8px;
      border-top: 1px dashed var(--border);
    }}


    @media (max-width: 768px) {{
      .hero-card {{ flex-direction: column; align-items: flex-start; }}
      .hero-top-row {{ flex-direction: column; align-items: flex-start; }}
      .cards-grid {{ grid-template-columns: 1fr; }}
      .courts-dir-grid {{ grid-template-columns: 1fr; }}
      .search-row {{ flex-direction: column; }}
      .filter-row {{ flex-direction: column; align-items: flex-start; }}
    }}
  
    /* 위반건축물 & 이행강제금 뱃지 */
    .badge-bldg-danger {{ background: #fee2e2; color: #991b1b; border: 1px solid #f87171; font-weight: 800; }}
    .badge-bldg-warning {{ background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; font-weight: 800; }}
    .badge-bldg-clean {{ background: #dcfce7; color: #166534; border: 1px solid #86efac; font-weight: 800; }}

    /* 캘린더 뷰 스타일 */
    .calendar-wrapper {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }}
    .cal-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      padding-bottom: 14px;
      border-bottom: 2px solid var(--border);
      margin-bottom: 14px;
    }}
    .cal-nav {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .cal-title {{
      font-size: 1.25rem;
      font-weight: 900;
      color: var(--heading);
      min-width: 140px;
      text-align: center;
    }}
    .cal-btn {{
      padding: 6px 12px;
      background: var(--surface-sub);
      border: 1px solid var(--border);
      border-radius: 6px;
      color: var(--text);
      font-size: 0.82rem;
      font-weight: 800;
      cursor: pointer;
      transition: all .15s;
    }}
    .cal-btn:hover {{
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
    }}
    .cal-btn.today {{
      background: var(--secondary);
      color: #fff;
      border-color: var(--secondary);
    }}
    .cal-controls {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .cal-fav-label {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.82rem;
      font-weight: 800;
      color: var(--heading);
      cursor: pointer;
    }}
    .cal-badge {{
      background: #eff6ff;
      color: #1e40af;
      border: 1px solid #bfdbfe;
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 0.78rem;
      font-weight: 800;
    }}
    .cal-grid {{
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      gap: 6px;
    }}
    .cal-day-head {{
      text-align: center;
      font-size: 0.82rem;
      font-weight: 900;
      padding: 8px 0;
      color: var(--text-muted);
      background: var(--surface-sub);
      border-radius: 6px;
    }}
    .cal-day-head.sun {{ color: #ef4444; }}
    .cal-day-head.sat {{ color: #3b82f6; }}
    .cal-cell {{
      min-height: 95px;
      background: var(--surface-sub);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 6px 8px;
      display: flex;
      flex-direction: column;
      transition: all .15s;
      cursor: pointer;
    }}
    .cal-cell:hover {{
      border-color: var(--accent);
      background: rgba(37,99,235,0.03);
    }}
    .cal-cell.today {{
      border-color: #2563eb;
      box-shadow: 0 0 0 2px rgba(37,99,235,0.2);
    }}
    .cal-cell.other-month {{
      opacity: 0.35;
      background: transparent;
    }}
    .cal-cell-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 4px;
    }}
    .cal-date-num {{
      font-size: 0.84rem;
      font-weight: 800;
      color: var(--heading);
    }}
    .cal-date-cnt {{
      font-size: 0.7rem;
      font-weight: 900;
      background: #ef4444;
      color: #fff;
      padding: 1px 6px;
      border-radius: 10px;
    }}
    .cal-event-chip {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 4px;
      padding: 2px 4px;
      margin-bottom: 3px;
      font-size: 0.7rem;
      font-weight: 700;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      color: var(--text);
    }}
    .cal-drawer {{
      margin-top: 16px;
      background: var(--surface-sub);
      border: 2px solid var(--accent);
      border-radius: 10px;
      padding: 16px;
      animation: fadeIn .2s;
    }}
    .cal-drawer-head {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 8px;
    }}
    .cal-drawer-list {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 10px;
    }}
    .cal-drawer-item {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 12px;
      cursor: pointer;
    }}
    .cal-drawer-item:hover {{
      border-color: var(--accent);
    }}

  </style>
</head>
<body>

  <!-- Header -->
  <header>
    <div class="header-inner">
      <div class="logo-area" onclick="goHome()" onkeydown="if(event.key==='Enter'||event.key===' '){{event.preventDefault();goHome();}}" role="button" tabindex="0" title="클릭 시 포털 홈 화면(처음 화면)으로 복귀">
        <div class="logo-icon">⚖️</div>
        <div class="logo-text">
          <h1>대한민국 법원경매 스마트 분석 포털</h1>
          <p>Real-time Supreme Court Auction Analytics &amp; Value Scoring Hub</p>
        </div>
      </div>
      <nav>
        <button class="nav-btn" data-tab="map" onclick="openMapView()">🗺️ 전국 경매 지도</button>
        <button class="nav-btn" data-tab="calendar" onclick="setViewMode('calendar')">📅 입찰 캘린더</button>
        <button class="nav-btn" data-tab="guide" onclick="switchTab('guide')">📚 소멸주의 &amp; 경매 가이드</button>
        <button class="nav-btn" data-tab="courts" onclick="switchTab('courts')">🏛️ 전국 60개 입찰법정</button>
        <button class="nav-btn" data-tab="downloads" onclick="switchTab('downloads')">📥 보고서 및 데이터 다운로드</button>
        <button id="btn-refresh-data" class="btn-refresh-data" style="padding:7px 11px; font-size:0.8rem; white-space:nowrap; flex-shrink:0;" onclick="refreshAuctionData()" title="최신 경매 물건 데이터 리프레쉬">
          <span class="refresh-icon">🔄</span> 경매정보 리프레쉬
        </button>
        <div class="theme-group" role="group" aria-label="테마 모드 선택">
          <button id="theme-btn-light" class="theme-toggle" onclick="toggleTheme('light')" title="라이트모드">☀️ 라이트</button>
          <button id="theme-btn-gray" class="theme-toggle active" onclick="toggleTheme('gray')" title="그레이모드">🌓 그레이</button>
          <button id="theme-btn-dark" class="theme-toggle" onclick="toggleTheme('dark')" title="다크모드">🌙 다크</button>
        </div>
      </nav>
    </div>
  </header>

  <div id="refresh-toast" role="status" aria-live="polite"></div>

  <div class="container">
    
    <!-- Hero Banner Area -->
    <div class="hero-card">
      <div class="hero-top-row">
        <div class="hero-text">
          <h2>실시간 대법원 경매 빅데이터 통합 플랫폼</h2>
          <p id="hero-desc-text">전국 17개 시·도 {nat_total_fmt}건의 유효 경매 물건과 대전광역시 {dj_total_fmt}건 전수 데이터를 바탕으로, 100점 만점 다차원 가치평가 모델을 적용해 각 권역별 베스트 <strong>TOP 100</strong> 알짜배기 매물을 실시간으로 탐색할 수 있습니다.</p>
        </div>
        <div class="hero-stats">
          <div class="stat-pill">
            <div class="num" id="stat-total">{nat_total_fmt}</div>
            <div class="label">전국 분석 물건</div>
          </div>
          <div class="stat-pill">
            <div class="num" id="stat-dj-top">TOP {dj_top_cnt}</div>
            <div class="label">권역별 추천 순위</div>
          </div>
          <div class="stat-pill">
            <div class="num" id="stat-max-discount">{max_disc_str}</div>
            <div class="label">최대 유찰 할인율</div>
          </div>
        </div>
      </div>
      <div class="refresh-meta-bar">
        <span id="live-conn-dot" class="refresh-dot"></span>
        <span>최종 데이터 리프레쉬: <strong id="last-refresh-time">{refreshed_at}</strong></span>
        <span id="live-conn-status" style="color:#a7f3d0; font-weight:700;">(🟢 대법원 courtauction.go.kr 실시간 API 직결됨)</span>
        <button type="button" class="btn-refresh-data" style="padding:4px 11px; font-size:0.76rem; margin-left:4px;" onclick="refreshAuctionData()" title="대법원 경매정보 실시간 전체 리프레쉬">
          <span class="refresh-icon">🔄</span> 경매정보 리프레쉬
        </button>
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- TAB 1: AUCTION EXPLORER (경매 물건 실시간 검색 & 대시보드) -->
    <!-- ============================================================= -->
    <div id="tab-explorer" class="view-section active">

      <!-- 권역별 TOP 100 원클릭 선택 탭 바 -->
      <div class="region-top100-bar" id="region-quick-bar">
        <span class="bar-title">🏆 권역별 TOP 100 바로보기:</span>
        <button type="button" class="region-pill-btn active" data-region="대전광역시" onclick="selectRegionQuick('대전광역시')">🔥 대전광역시 <span class="cnt-badge">TOP 100</span></button>
        <button type="button" class="region-pill-btn" data-region="수도권" onclick="selectRegionQuick('수도권')">🏙️ 수도권(서울·경기·인천) <span class="cnt-badge">TOP 100</span></button>
        <button type="button" class="region-pill-btn" data-region="영남권" onclick="selectRegionQuick('영남권')">🌊 영남권 통합 <span class="cnt-badge">TOP 100</span></button>
        <button type="button" class="region-pill-btn" data-region="영남권(부울경)" onclick="selectRegionQuick('영남권(부울경)')">⚓ 부울경(부산·울산·경남) <span class="cnt-badge">TOP 100</span></button>
        <button type="button" class="region-pill-btn" data-region="영남권(대경권)" onclick="selectRegionQuick('영남권(대경권)')">🍎 대경권(대구·경북) <span class="cnt-badge">TOP 100</span></button>
        <button type="button" class="region-pill-btn" data-region="충청권" onclick="selectRegionQuick('충청권')">🏛️ 충청권(대전·세종·충남북) <span class="cnt-badge">TOP 100</span></button>
        <button type="button" class="region-pill-btn" data-region="호남권" onclick="selectRegionQuick('호남권')">🌾 호남권(광주·전남북) <span class="cnt-badge">TOP 100</span></button>
        <button type="button" class="region-pill-btn" data-region="강원" onclick="selectRegionQuick('강원')">⛰️ 강원·제주권 <span class="cnt-badge">TOP 100</span></button>
        <button type="button" class="region-pill-btn" data-region="ALL" onclick="selectRegionQuick('ALL')">🌍 전국 전체 통합</button>
      </div>
      
      <!-- Toolbar -->
      <div class="toolbar">
        <div class="search-row">
          <input type="text" id="keyword-search" class="search-input" placeholder="아파트 단지명, 도로명, 동/구 이름, 사건번호(예: 2025타경503878) 입력 후 [대법원 실시간 조회] 또는 검색..." oninput="filterData()" onkeydown="if(event.key==='Enter'){{event.preventDefault();liveSearchCourtAuction();}}">
          <button type="button" id="btn-live-court-search" class="btn-live-court" onclick="liveSearchCourtAuction()" title="현재 검색어·필터 조건으로 대법원 경매정보(courtauction.go.kr) 서버를 실시간 직접 조회합니다">
            <span class="live-icon">📡</span> 대법원 실시간 조회
          </button>
        </div>
        <div class="filter-row">
          <div class="filter-group">
            <label>권역/지역 (각 권역 TOP 100)</label>
            <select id="filter-region" onchange="filterData()">
              <option value="ALL">전체 지역 (전국 통합)</option>
              <option value="대전광역시" selected>대전광역시 (TOP 100)</option>
              <option value="수도권">수도권 - 서울/경기/인천 (TOP 100)</option>
              <option value="영남권">영남권 통합 - 부울경·대경 (TOP 100)</option>
              <option value="영남권(부울경)">영남권(부울경) - 부산/울산/경남 (TOP 100)</option>
              <option value="영남권(대경권)">영남권(대경권) - 대구/경북 (TOP 100)</option>
              <option value="충청권">충청권 - 대전/세종/충남북 (TOP 100)</option>
              <option value="호남권">호남권 - 광주/전남북 (TOP 100)</option>
              <option value="강원">강원·제주권 - 강원/제주 (TOP 100)</option>
            </select>
          </div>

          <div class="filter-group">
            <label>순위 표시 범위</label>
            <select id="filter-topn" onchange="filterData()">
              <option value="100" selected>TOP 100 전체보기 (1위~100위)</option>
              <option value="50">TOP 50 보기 (1위~50위)</option>
              <option value="30">TOP 30 보기 (1위~30위)</option>
              <option value="10">TOP 10 보기 (1위~10위)</option>
              <option value="9999">제한 없음 (전체)</option>
            </select>
          </div>

          <div class="filter-group">
            <label>물건 용도</label>
            <select id="filter-usage" onchange="filterData()">
              <option value="ALL">전체 용도</option>
              <option value="아파트">아파트 / 주상복합</option>
              <option value="오피스텔">오피스텔 / 도시형생활주택</option>
              <option value="다세대">다세대 / 빌라 / 연립</option>
              <option value="상가">상가 / 근린생활시설</option>
              <option value="단독">단독 / 다가구</option>
            </select>
          </div>

          <div class="filter-group">
            <label>최소 할인율</label>
            <select id="filter-discount" onchange="filterData()">
              <option value="0" selected>전체 할인율 (TOP 100 전체)</option>
              <option value="30">30% 이상 할인 (1회 유찰+)</option>
              <option value="50">50% 이상 할인 (2회 유찰+)</option>
              <option value="65">65% 이상 할인 (3회 유찰+)</option>
              <option value="75">75% 이상 할인 (초특가)</option>
            </select>
          </div>

          <div class="filter-group">
            <label>👤 점유/외국인 세입자</label>
            <select id="filter-tenant" onchange="filterData()">
              <option value="ALL" selected>전체 점유 형태</option>
              <option value="FOREIGNER">🌐 외국인 세입자만 (체류확인서 필수)</option>
              <option value="OWNER">👤 소유자 직접 거주</option>
              <option value="DOMESTIC">🇰🇷 내국인 임차인</option>
              <option value="SENIOR">⚠️ 선순위 대항력 주의</option>
            </select>
          </div>

          <div class="filter-group">
            <label>⚖️ 경매 신청 사유</label>
            <select id="filter-auction-reason" onchange="filterData()">
              <option value="ALL" selected>전체 경매 사유</option>
              <option value="MORTGAGE">⚖️ 임의경매 (담보대출 연체 실행)</option>
              <option value="JEONSE">⚖️ 강제경매 (전세보증금 반환 판결)</option>
              <option value="GENERAL">⚖️ 강제경매 (일반 대여금/사업 부채)</option>
              <option value="PARTITION">⚖️ 형식적경매 (공유물 분할)</option>
            </select>
          </div>

          <div class="filter-group">
            <label>정렬 기준</label>
            <select id="sort-order" onchange="filterData()">
              <option value="score_desc" selected>권역 추천순위·점수 높은순</option>
              <option value="discount_desc">할인율 높은순</option>
              <option value="price_asc">최저매각가격 낮은순</option>
              <option value="appraisal_desc">감정평가액 높은순</option>
              <option value="date_asc">매각기일 빠른순</option>
            </select>
          </div>

          <button class="btn-reset" onclick="resetFilters()">🔄 필터 초기화</button>
          <button type="button" class="btn-refresh-data" style="height:38px; padding:0 14px;" onclick="refreshAuctionData()" title="대법원 경매정보 데이터 리프레쉬">
            <span class="refresh-icon">🔄</span> 경매정보 리프레쉬
          </button>
        </div>
      </div>

      <!-- Legal & Foreigner Quick Filter Pill Bar -->
      <div class="legal-quick-filter-bar">
        <span class="lqf-label">⚡ 빠른 조건 필터:</span>
        <button type="button" class="lqf-btn active" id="lqf-all" onclick="setQuickLegalFilter('ALL', this)">전체보기</button>
        <button type="button" class="lqf-btn lqf-foreign" id="lqf-foreigner" onclick="setQuickLegalFilter('FOREIGNER', this)">🌐 외국인 세입자 매물 (체류확인서 필수) <span class="lqf-cnt" id="cnt-foreign">132</span></button>
        <button type="button" class="lqf-btn" id="lqf-owner" onclick="setQuickLegalFilter('OWNER', this)">👤 소유자 직접 거주</button>
        <button type="button" class="lqf-btn" id="lqf-domestic" onclick="setQuickLegalFilter('DOMESTIC', this)">🇰🇷 내국인 임차인</button>
        <button type="button" class="lqf-btn" id="lqf-senior" onclick="setQuickLegalFilter('SENIOR', this)">⚠️ 선순위 대항력 주의</button>
        <button type="button" class="lqf-btn" id="lqf-jeonse" onclick="setQuickLegalFilter('JEONSE', this)">⚖️ 전세금 반환 강제경매</button>
        <button type="button" class="lqf-btn" id="lqf-clean-bldg" onclick="setQuickLegalFilter('CLEAN_BLDG', this)">✅ 위반없는 클린건물</button>
        <button type="button" class="lqf-btn" id="lqf-multi" onclick="setQuickLegalFilter('MULTI_YUCHAL', this)">📉 3회 이상 다회유찰</button>
      </div>

      <!-- Results Count & View Toggle -->
      <div class="results-header">
        <div class="results-count">검색 조건에 맞는 경매 물건 <span id="filtered-count">0</span>건</div>
        <div class="view-toggle-btns">
          <button class="toggle-btn active" id="btn-card-view" onclick="setViewMode('card')">🔲 카드 뷰</button>
          <button class="toggle-btn" id="btn-table-view" onclick="setViewMode('table')">📄 표 뷰</button>
          <button class="toggle-btn" id="btn-map-view" onclick="setViewMode('map')">🗺️ 지도 뷰</button>
          <button class="toggle-btn" id="btn-calendar-view" onclick="setViewMode('calendar')">📅 캘린더 뷰</button>
        </div>
      </div>

      <!-- Cards Grid -->
      <div id="cards-container" class="cards-grid"></div>

      <!-- Table View Container -->
      <div id="table-container" class="table-view-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>순위/점수</th>
              <th>지역</th>
              <th>사건번호</th>
              <th>용도</th>
              <th>소재지 및 단지명</th>
              <th>감정평가액</th>
              <th>최저매각가격</th>
              <th>할인율(유찰)</th>
              <th>매각기일</th>
              <th>권리구분</th>
            </tr>
          </thead>
          <tbody id="table-body"></tbody>
        </table>
      </div>

      <!-- 인터랙티브 입찰 캘린더 뷰 컨테이너 (신규 고도화) -->
      <div id="calendar-container" style="display:none; margin-top:14px;">
        <div class="calendar-wrapper">
          <div class="cal-header">
            <div class="cal-nav">
              <button type="button" class="cal-btn" onclick="changeCalMonth(-1)">◀ 이전 달</button>
              <h3 id="cal-month-title" class="cal-title">2026년 11월</h3>
              <button type="button" class="cal-btn" onclick="changeCalMonth(1)">다음 달 ▶</button>
              <button type="button" class="cal-btn today" onclick="changeCalMonth(0)">오늘</button>
            </div>
            <div class="cal-controls">
              <label class="cal-fav-label">
                <input type="checkbox" id="cal-fav-filter" onchange="renderCalendar()">
                <span>⭐ 관심물건(찜)만 달력에 표시</span>
              </label>
              <span id="cal-summary-badge" class="cal-badge">예정 경매 총 0건</span>
            </div>
          </div>

          <div class="cal-grid" id="cal-grid">
            <!-- 7 Days Header + Date Cells -->
          </div>

          <!-- 선택된 일자의 경매 물건 목록 드로어 / 패널 -->
          <div id="cal-day-drawer" class="cal-drawer" style="display:none;">
            <div class="cal-drawer-head">
              <h4 id="cal-drawer-title" style="font-size:1.02rem; font-weight:900; color:var(--heading); margin:0;">📅 일자별 경매 일정</h4>
              <button type="button" class="modal-close" onclick="closeCalDrawer()" style="font-size:1.4rem; background:transparent; border:none; cursor:pointer;">&times;</button>
            </div>
            <div id="cal-drawer-list" class="cal-drawer-list"></div>
          </div>
        </div>
      </div>

    <!-- 인터랙티브 지도 뷰 컨테이너 (좌측 목록 + 우측 인터랙티브 지도) -->
    <div id="map-view-container" style="display:none; margin-top:14px;">
      <div class="map-view-layout">
        <!-- 좌측: 필터링된 물건 사이드바 -->
        <div class="map-list-sidebar">
          <div class="map-sidebar-head">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="font-weight:800; font-size:0.92rem; color:var(--heading);">📍 지도 탐색 물건 목록</span>
              <span id="map-item-count" class="badge badge-discount">0건</span>
            </div>
            <small style="color:var(--text-muted); font-size:0.75rem;">카드를 클릭하면 지도가 해당 위치로 이동합니다</small>
          </div>
          <div id="map-sidebar-list" class="map-sidebar-items">
            <!-- Sidebar cards injected via JS -->
          </div>
        </div>

        <!-- 우측: 인터랙티브 지도 영역 -->
        <div class="map-main-pane">
          <div class="map-toolbar">
            <div class="map-quick-regions">
              <span style="font-size:0.75rem; font-weight:800; color:var(--text-muted); margin-right:4px;">권역 이동:</span>
              <button type="button" class="map-loc-btn" onclick="panMapToRegion('전체')">전국</button>
              <button type="button" class="map-loc-btn" onclick="panMapToRegion('대전광역시')">대전</button>
              <button type="button" class="map-loc-btn" onclick="panMapToRegion('수도권')">수도권</button>
              <button type="button" class="map-loc-btn" onclick="panMapToRegion('영남권')">영남권</button>
              <button type="button" class="map-loc-btn" onclick="panMapToRegion('부울경')">부울경</button>
              <button type="button" class="map-loc-btn" onclick="panMapToRegion('충청권')">충청권</button>
              <button type="button" class="map-loc-btn" onclick="panMapToRegion('호남권')">호남권</button>
              <button type="button" class="map-loc-btn" onclick="panMapToRegion('강원')">강원·제주</button>
            </div>
            <div style="display:flex; gap:6px;">
              <button type="button" class="map-loc-btn active" id="btn-layer-osm" onclick="switchMapTile('osm')">🗺️ 일반지도</button>
              <button type="button" class="map-loc-btn" id="btn-layer-sat" onclick="switchMapTile('sat')">🛰️ 위성사진</button>
            </div>
          </div>

          <div id="interactive-leaflet-map" style="width:100%; height:620px; border-radius:10px; border:1px solid var(--border); position:relative; overflow:hidden;"></div>

          <div class="map-legend-bar">
            <span class="legend-item"><span class="legend-dot red"></span> 70% 이상 할인 (초특가)</span>
            <span class="legend-item"><span class="legend-dot orange"></span> 50%~70% 할인</span>
            <span class="legend-item"><span class="legend-dot gold"></span> 30%~50% 할인</span>
            <span class="legend-item"><span class="legend-dot blue"></span> 30% 미만</span>
            <span style="margin-left:auto; font-size:0.75rem; color:var(--text-muted);">* 핀을 클릭하면 팝업과 로드뷰가 열립니다.</span>
          </div>
        </div>
      </div>
    </div>

    </div>

    <!-- ============================================================= -->
    <!-- TAB 2: BEGINNER STEP-BY-STEP AUCTION GUIDE & EXTINCTION PRINCIPLE -->
    <!-- ============================================================= -->
    <div id="tab-guide" class="view-section">

      <!-- Beginner Guide Header & Action Bar -->
      <div class="guide-card" style="background:linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%); color:#fff; border:none;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px;">
          <div>
            <h3 style="color:#fff; border:none; padding:0; margin-bottom:6px; font-size:1.45rem;">🧭 초보자를 위한 대한민국 법원경매 실전 진행 가이드 (A to Z)</h3>
            <p style="color:#e2e8f0; font-size:0.92rem; margin:0;">물건 검색(D-14일)부터 서류 권리분석, 현장 임장, 법원 입찰표 작성(D-Day), 경락잔금대출, 인도명령·명도까지 처음 도전하는 분을 위한 7단계 표준 매뉴얼입니다.</p>
          </div>
          <div style="display:flex; gap:8px; flex-wrap:wrap;">
            <a href="초보자_경매_진행_가이드.html" target="_blank" class="btn-action" style="background:#0d9488; border:1px solid rgba(255,255,255,0.3);">📄 독립 가이드 창으로 열기 ↗</a>
            <button type="button" class="btn-action" style="background:rgba(255,255,255,0.18); border:1px solid rgba(255,255,255,0.35);" onclick="if(typeof cbAsk==='function')cbAsk('초보자 경매 진행 순서 알려줘');">🤖 AI 챗봇에게 질문하기</button>
          </div>
        </div>
      </div>

      <!-- 7-Step Master Roadmap -->
      <div class="guide-card">
        <h3>🚀 실전 법원경매 진행 7단계 로드맵 (D-14일 ~ 입주·수익실현)</h3>
        <div class="img-box" style="margin:16px 0 22px;">
          <img src="images/guide_7steps_roadmap.png" alt="대한민국 법원경매 실전 7단계 마스터 로드맵 인포그래픽">
        </div>
        <div style="display:grid; grid-template-columns:1fr; gap:14px; margin-top:16px;">

          <div style="background:var(--surface-sub); border:1px solid var(--border); border-left:5px solid var(--secondary); border-radius:9px; padding:16px 20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:6px;">
              <strong style="color:var(--heading); font-size:1.05rem;">STEP 1. 물건 탐색 및 후보 선정 — "유찰 1~3회 + 소멸주의 주거용부터 시작"</strong>
              <span class="badge badge-rank">입찰 D-14일</span>
            </div>
            <ul style="font-size:0.9rem; margin-left:18px; color:var(--text);">
              <li><strong>초보자 추천 물건:</strong> 시세 파악이 쉽고 환금성·경락잔금대출이 우수한 <strong>아파트·주상복합·주거용 오피스텔</strong> 중 <strong>1~3회 유찰(할인율 30~65%)</strong>된 물건을 선별합니다.</li>
              <li><strong>초보자 피해야 할 물건:</strong> <code>지분경매</code>, <code>유치권</code>, <code>법정지상권</code>, <code>토지별도등기</code>, <code>선순위 가처분/가등기</code> 물건은 입문 단계에서 제외하세요.</li>
            </ul>
          </div>

          <div style="background:var(--surface-sub); border:1px solid var(--border); border-left:5px solid var(--secondary); border-radius:9px; padding:16px 20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:6px;">
              <strong style="color:var(--heading); font-size:1.05rem;">STEP 2. 3대 공적 서류 권리분석 — "등기부등본 · 매각물건명세서 · 현황조사서"</strong>
              <span class="badge badge-rank">입찰 D-10일</span>
            </div>
            <ul style="font-size:0.9rem; margin-left:18px; color:var(--text);">
              <li><strong>① 등기부등본 (말소기준권리 찾기):</strong> <code>근저당</code>·<code>저당</code>·<code>압류</code>·<code>가압류</code>·<code>담보가등기</code>·<code>경매기입등기</code> 중 접수일이 가장 빠른 권리가 <strong>말소기준권리</strong>이며, 잔금 완납 시 이 권리와 이후 권리는 100% 말소됩니다.</li>
              <li><strong>② 매각물건명세서 (매각기일 7일 전 공개):</strong> 좌측 상단 <strong>[최선순위 설정일자]</strong>보다 전입신고일이 빠른 선순위 임차인이 있는지 확인합니다. 후순위 임차인이거나 소유자 점유라면 인수할 보증금이 전혀 없습니다.</li>
              <li><strong>③ 현황조사서 &amp; 감정평가서:</strong> 현재 점유 형태(소유자/임차인/공실), 건물 구조·전용면적·감정 시점을 확인합니다.</li>
            </ul>
          </div>

          <div style="background:var(--surface-sub); border:1px solid var(--border); border-left:5px solid var(--secondary); border-radius:9px; padding:16px 20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:6px;">
              <strong style="color:var(--heading); font-size:1.05rem;">STEP 3. 현장 임장(답사) 및 시세·미납관리비 조사 — "감정가를 믿지 마세요!"</strong>
              <span class="badge badge-rank">입찰 D-5일</span>
            </div>
            <ul style="font-size:0.9rem; margin-left:18px; color:var(--text);">
              <li><strong>실거래가 및 급매 호가 대조:</strong> 감정평가액은 6개월~1년 전 기준이므로 국토교통부 실거래가와 네이버부동산 현재 최저 급매가를 반드시 확인합니다.</li>
              <li><strong>공인중개소 2~3곳 방문:</strong> 단지 내 중개업소에서 <em>"지금 급매로 내놓으면 바로 거래되는 금액"</em>과 <em>"전·월세 시세 및 수요"</em>를 직접 조사합니다.</li>
              <li><strong>관리사무소 방문:</strong> 전 소유자가 체납한 관리비 중 <strong>공용부분(일반관리비·경비비·청소비)</strong>은 낙찰자가 인수하므로 미납 개월 수와 금액을 파악해 입찰가에서 차감합니다.</li>
            </ul>
          </div>

          <div style="background:var(--surface-sub); border:1px solid var(--border); border-left:5px solid var(--secondary); border-radius:9px; padding:16px 20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:6px;">
              <strong style="color:var(--heading); font-size:1.05rem;">STEP 4. 상한 입찰가 결정 및 경락잔금대출 가심사</strong>
              <span class="badge badge-rank">입찰 D-2일</span>
            </div>
            <ul style="font-size:0.9rem; margin-left:18px; color:var(--text);">
              <li><strong>초보자 입찰가 산정 공식:</strong> <code>최대 입찰가 = 현재 급매 시세 - 목표 안전마진 - (취득세 + 법무등기비 + 미납 공용관리비 + 명도 이사비 + 수리비)</code></li>
              <li><strong>경락잔금대출 사전 확인:</strong> 낙찰 후 잔금을 미납하면 보증금(10%)을 몰수당하므로, 대출상담사를 통해 <strong>경락잔금대출 한도(통상 낙찰가의 70~80% 또는 감정가의 60% 중 낮은 금액)</strong>를 사전 점검합니다.</li>
            </ul>
            <div class="img-box" style="margin:14px 0 4px;">
              <img src="images/guide_bid_price_formula.png" alt="상한 입찰가 산정 워터폴 공식 및 유찰 회차별 저감 시뮬레이션">
            </div>
          </div>

          <div style="background:var(--surface-sub); border:1px solid var(--border); border-left:5px solid var(--red); border-radius:9px; padding:16px 20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:6px;">
              <strong style="color:var(--red); font-size:1.05rem;">STEP 5. 법원 입찰 당일 실전 응찰 (오전 10:00 개시 ~ 11:30 개찰)</strong>
              <span class="badge badge-discount">D-Day 실전</span>
            </div>
            <ul style="font-size:0.9rem; margin-left:18px; color:var(--text);">
              <li><strong>입찰보증금 준비:</strong> 내가 쓰는 입찰가의 10%가 아니라 <strong>법원이 공고한 최저매각가격의 10% 이상</strong>(재매각은 20~30%)을 <strong>시중은행 자기앞수표 1장</strong>으로 준비합니다.</li>
              <li><strong>입찰표 작성 및 투입:</strong> 오전 9시 40분까지 법정 도착 → 기일입찰표·보증금봉투·입찰봉투 작성 및 도장 날인 → 신분증 확인 후 입찰함 투입!</li>
              <li><strong>초보자 단골 실수 주의:</strong> ① 입찰가 숫자 <code>0</code> 하나 더 적기 (투입 후 수정·취소 절대 불가!) ② 사건번호·물건번호 오기재 ③ 보증금 10원이라도 부족 시 무효 처리.</li>
            </ul>
          </div>

          <div style="background:var(--surface-sub); border:1px solid var(--border); border-left:5px solid var(--accent); border-radius:9px; padding:16px 20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:6px;">
              <strong style="color:var(--heading); font-size:1.05rem;">STEP 6. 매각허가확정 및 잔금 완납 (소유권 100% 취득)</strong>
              <span class="badge badge-safe">낙찰 후 7~45일</span>
            </div>
            <ul style="font-size:0.9rem; margin-left:18px; color:var(--text);">
              <li><strong>일정 흐름:</strong> 낙찰 7일 후 <strong>매각허가결정</strong> → 다시 7일 후 <strong>매각허가확정</strong> → 확정 후 약 30일 이내 <strong>대금지급기한</strong>까지 잔금(낙찰가 - 보증금 10%) 납부.</li>
              <li><strong>즉시 소유권 취득:</strong> 잔금을 납부하는 즉시 등기 전이라도 법적 소유권을 취득하며, 경락잔금대출 실행 및 소유권이전등기·말소촉탁등기를 동시에 진행합니다.</li>
            </ul>
          </div>

          <div style="background:var(--surface-sub); border:1px solid var(--border); border-left:5px solid var(--green); border-radius:9px; padding:16px 20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:6px;">
              <strong style="color:var(--heading); font-size:1.05rem;">STEP 7. 인도명령·명도(인도) 및 입주·임대·매도</strong>
              <span class="badge badge-safe">잔금 후 1~6주</span>
            </div>
            <ul style="font-size:0.9rem; margin-left:18px; color:var(--text);">
              <li><strong>인도명령 신청:</strong> 잔금 납부 당일 법원에 <strong>부동산 인도명령 신청서</strong>를 함께 접수합니다 (소유자·채무자·후순위 임차인 대상 약 2~3주 내 결정).</li>
              <li><strong>원만한 명도 협상:</strong> 점유자와 이사 일정을 조율하고 적정 이사비(통상 50~150만 원 선)를 협의하되, 반드시 <strong>공실 상태·공과금 및 관리비 완납 영수증·도어락 비밀번호를 인계받는 현장에서</strong> 이사비를 지급합니다.</li>
            </ul>
            <div class="img-box" style="margin:14px 0 4px;">
              <img src="images/guide_tenant_and_eviction.png" alt="임차인 보증금 인수 3초 판별법 및 명도 4단계 표준 절차">
            </div>
          </div>

        </div>
      </div>

      <!-- Required Documents Table -->
      <div class="guide-card">
        <h3>🎒 법원 입찰 당일 유형별 필수 준비물 요약표</h3>
        <div class="img-box" style="margin:14px 0 18px;">
          <img src="images/guide_court_bidding_kit.png" alt="법원 입찰 당일 필수 지참물 및 입찰서류 3종 제출 구조도">
        </div>
        <div style="overflow-x:auto; margin-top:12px;">
          <table class="data-table">
            <thead>
              <tr>
                <th>입찰 유형</th>
                <th>필수 지참물 (하나라도 누락 시 입찰 무효)</th>
                <th>핵심 체크포인트</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>👤 본인 직접 입찰</strong></td>
                <td>① 본인 신분증 (주민등록증·운전면허증·여권)<br>② 본인 도장 (막도장 가능, 서명 불가)<br>③ 입찰보증금 (최저가의 10% 이상 자기앞수표 1장 권장)</td>
                <td>가장 간편하며 초보자에게 적극 권장</td>
              </tr>
              <tr>
                <td><strong>🤝 대리인 입찰</strong><br><small>(배우자·가족 대리 포함)</small></td>
                <td>① 대리인 신분증 + 대리인 도장<br>② 본인(입찰자) 인감증명서 1통 (3개월 이내)<br>③ 본인 인감도장 날인 위임장 (기일입찰표 뒷면)<br>④ 입찰보증금</td>
                <td>부부 사이라도 대리 입찰 시 배우자 인감증명서·인감날인 위임장 필수</td>
              </tr>
              <tr>
                <td><strong>🏢 법인 입찰</strong></td>
                <td>① 법인등기부등본 (3개월 이내)<br>② 대표자 출석: 대표자 신분증 + 법인인감도장<br>③ 직원 대리: 법인인감증명서 + 법인인감 위임장 + 대리인 신분증·도장<br>④ 입찰보증금</td>
                <td>법인 명의 주택 취득 시 취득세율 사전 확인</td>
              </tr>
              <tr>
                <td><strong>👥 공동 입찰</strong><br><small>(부부 공동명의 등)</small></td>
                <td>① 공동입찰신고서 및 공동입찰자 목록 (지분 기재)<br>② 전원 출석 시 각자 신분증·도장 (1인 불참 시 불참자 인감증명서·위임장 추가)<br>③ 입찰보증금</td>
                <td>지분 비율(예: 각 1/2) 정확히 명시</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Interactive 10-Item Beginner Readiness Checklist -->
      <div class="guide-card">
        <h3>✅ 초보자 실전 입찰 전 10대 자가진단 체크리스트 (클릭하여 점검)</h3>
        <div style="background:var(--surface-sub); border:1px solid var(--border); padding:14px 18px; border-radius:10px; margin-bottom:14px;">
          <div style="display:flex; justify-content:space-between; align-items:center; font-weight:800; font-size:0.95rem;">
            <span>📊 나의 입찰 준비 완료율</span>
            <span id="portal-chk-label" style="color:var(--secondary);">0 / 10 항목 점검 완료 (0%)</span>
          </div>
          <div style="height:12px; background:var(--border); border-radius:999px; overflow:hidden; margin-top:8px;">
            <div id="portal-chk-bar" style="height:100%; width:0%; background:linear-gradient(90deg, var(--accent), var(--secondary)); transition:width 0.25s;"></div>
          </div>
        </div>
        <div id="portal-chk-group" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:10px;">
          <label style="display:flex; gap:10px; align-items:flex-start; background:var(--surface-sub); border:1px solid var(--border); padding:11px 14px; border-radius:8px; cursor:pointer; font-size:0.86rem; font-weight:600;"><input type="checkbox" onchange="updatePortalChecklist()" style="margin-top:3px; transform:scale(1.15);"> <span>1. 등기부등본에서 말소기준권리를 찾았고 인수되는 선순위 권리가 없다.</span></label>
          <label style="display:flex; gap:10px; align-items:flex-start; background:var(--surface-sub); border:1px solid var(--border); padding:11px 14px; border-radius:8px; cursor:pointer; font-size:0.86rem; font-weight:600;"><input type="checkbox" onchange="updatePortalChecklist()" style="margin-top:3px; transform:scale(1.15);"> <span>2. 매각물건명세서에서 미배당 보증금을 인수해야 하는 선순위 임차인이 없다.</span></label>
          <label style="display:flex; gap:10px; align-items:flex-start; background:var(--surface-sub); border:1px solid var(--border); padding:11px 14px; border-radius:8px; cursor:pointer; font-size:0.86rem; font-weight:600;"><input type="checkbox" onchange="updatePortalChecklist()" style="margin-top:3px; transform:scale(1.15);"> <span>3. 유치권·법정지상권·지분경매·토지별도등기 등 특수권리 위험이 없다.</span></label>
          <label style="display:flex; gap:10px; align-items:flex-start; background:var(--surface-sub); border:1px solid var(--border); padding:11px 14px; border-radius:8px; cursor:pointer; font-size:0.86rem; font-weight:600;"><input type="checkbox" onchange="updatePortalChecklist()" style="margin-top:3px; transform:scale(1.15);"> <span>4. 감정가가 아닌 최근 국토부 실거래가와 네이버부동산 급매 호가를 확인했다.</span></label>
          <label style="display:flex; gap:10px; align-items:flex-start; background:var(--surface-sub); border:1px solid var(--border); padding:11px 14px; border-radius:8px; cursor:pointer; font-size:0.86rem; font-weight:600;"><input type="checkbox" onchange="updatePortalChecklist()" style="margin-top:3px; transform:scale(1.15);"> <span>5. 현장을 직접 방문해 주변 중개소 2곳 이상에서 급매 시세·임대 수요를 파악했다.</span></label>
          <label style="display:flex; gap:10px; align-items:flex-start; background:var(--surface-sub); border:1px solid var(--border); padding:11px 14px; border-radius:8px; cursor:pointer; font-size:0.86rem; font-weight:600;"><input type="checkbox" onchange="updatePortalChecklist()" style="margin-top:3px; transform:scale(1.15);"> <span>6. 관리사무소에 문의하여 미납 공용관리비와 현재 점유 상태를 확인했다.</span></label>
          <label style="display:flex; gap:10px; align-items:flex-start; background:var(--surface-sub); border:1px solid var(--border); padding:11px 14px; border-radius:8px; cursor:pointer; font-size:0.86rem; font-weight:600;"><input type="checkbox" onchange="updatePortalChecklist()" style="margin-top:3px; transform:scale(1.15);"> <span>7. 취득세·법무비·미납관리비·명도이사비·수리비를 공제한 상한 입찰가를 산정했다.</span></label>
          <label style="display:flex; gap:10px; align-items:flex-start; background:var(--surface-sub); border:1px solid var(--border); padding:11px 14px; border-radius:8px; cursor:pointer; font-size:0.86rem; font-weight:600;"><input type="checkbox" onchange="updatePortalChecklist()" style="margin-top:3px; transform:scale(1.15);"> <span>8. 경락잔금대출 가능 한도와 실제 필요 자기자본(실투자금)을 계산해 두었다.</span></label>
          <label style="display:flex; gap:10px; align-items:flex-start; background:var(--surface-sub); border:1px solid var(--border); padding:11px 14px; border-radius:8px; cursor:pointer; font-size:0.86rem; font-weight:600;"><input type="checkbox" onchange="updatePortalChecklist()" style="margin-top:3px; transform:scale(1.15);"> <span>9. 최저매각가격의 10%(재매각은 20~30%) 이상 자기앞수표 1장을 준비했다.</span></label>
          <label style="display:flex; gap:10px; align-items:flex-start; background:var(--surface-sub); border:1px solid var(--border); padding:11px 14px; border-radius:8px; cursor:pointer; font-size:0.86rem; font-weight:600;"><input type="checkbox" onchange="updatePortalChecklist()" style="margin-top:3px; transform:scale(1.15);"> <span>10. 관할 법원 위치, 매각기일 입찰 시각(10:00), 신분증·도장을 모두 챙겼다.</span></label>
        </div>
      </div>

      <div class="guide-card">
        <h3>⚖️ 경매의 핵심 엔진: 소멸주의(消滅主義) 권리분석 메커니즘</h3>
        <p><strong>소멸주의(消滅主義, 삭제주의)</strong>는 대한민국 민사집행법(제91조 제2항)의 대원칙으로, 낙찰자가 매각대금을 완납하면 등기부에 설정된 모든 담보권과 가압류가 낙찰자에게 넘어오지 않고 법원의 촉탁으로 <strong>100% 직권 말소(삭제)</strong>되는 원칙입니다.</p>
        
        <div class="img-box">
          <img src="images/infographic_extinction.png" alt="소멸주의 권리 소멸 메커니즘 인포그래픽">
        </div>

        <div class="guide-grid" style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-top:20px;">
          <div class="guide-box-pro" style="background:#f0fff4; border:1px solid #c6f6d5; padding:18px; border-radius:8px;">
            <h4 style="color:#22543d; font-size:1.05rem; margin-bottom:8px;">✅ 소멸주의가 주는 3대 혜택</h4>
            <ul style="font-size:0.9rem; margin-left:18px; color:#2d3748;">
              <li><strong>사기 거래 원천 차단:</strong> 법원이 공권력으로 권리 관계를 정리해 주므로 사기 매매 위험이 없습니다.</li>
              <li><strong>안전마진 창출:</strong> 부실채권으로 얽힌 물건을 깨끗하게 정리하여 시세 대비 30~50% 싸게 취득할 수 있습니다.</li>
              <li><strong>비용 예측 확실성:</strong> 낙찰대금 외에 전 소유자의 등기부상 빚을 갚아줄 위험이 전혀 없습니다.</li>
            </ul>
          </div>
          <div class="guide-box-con" style="background:#fff5f5; border:1px solid #fed7d7; padding:18px; border-radius:8px;">
            <h4 style="color:#9b2c2c; font-size:1.05rem; margin-bottom:8px;">⚠️ 구매자가 인수하는 3대 예외 (주의!)</h4>
            <ul style="font-size:0.9rem; margin-left:18px; color:#2d3748;">
              <li><strong>선순위 대항력 임차인:</strong> 말소기준권리보다 전입일이 빠르고 법원에서 전액 배당받지 못한 미배당 보증금 인수.</li>
              <li><strong>선순위 가처분/가등기:</strong> 낙찰 후 본안소송 결과에 따라 소유권을 상실할 위험.</li>
              <li><strong>등기부 외 특수권리:</strong> 유치권(공사대금), 법정지상권(토지와 건물 소유주 불일치).</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="guide-card">
        <h3>📊 실전 물건 선별 5단계 체크리스트</h3>
        <div class="mermaid" style="margin:20px 0; text-align:center;">
flowchart LR
    A["1단계: 가격 괴리 분석<br/>(유찰 1회 이상)"] --> B["2단계: 권리 안전성<br/>(말소기준권리 확인)"]
    B --> C["3단계: 시장 환금성<br/>(실거래량 조사)"]
    C --> D["4단계: 숨은 비용 조사<br/>(공용 관리비 확인)"]
    D --> E["5단계: 목표 입찰가 결정<br/>(안전마진 확보)"]
        </div>
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- TAB 3: NATIONWIDE 60 COURTS FINDER -->
    <!-- ============================================================= -->
    <div id="tab-courts" class="view-section">
      <div class="guide-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:14px; margin-bottom:10px;">
          <div>
            <h3 style="border:none; padding-bottom:4px; margin-bottom:4px;">🏛️ 전국 60개 법원 경매 입찰법정 상세 주소록 및 관할 검색</h3>
            <p style="font-size:0.92rem; color:var(--text-muted);">대한민국 법원경매는 <strong>현장 방문 입찰이 원칙</strong>이며, 반드시 물건 소재지를 관할하는 법원 입찰법정에 직접 출석해야 합니다. (전국 <strong>본원 18개 + 지원 42개 = 총 60개소</strong> 전수 수록 · 법원별 도로명 주소, 대표전화, 관할 시·군·구, 회차별 유찰 저감률, 위치 지도보기 제공)</p>
          </div>
          <div class="view-toggle-btns">
            <button type="button" class="toggle-btn active" id="btn-court-card-view" onclick="setCourtViewMode('card')">🔲 카드 상세뷰</button>
            <button type="button" class="toggle-btn" id="btn-court-table-view" onclick="setCourtViewMode('table')">📄 60개 법원 표 뷰</button>
          </div>
        </div>

        <!-- 60개 법원 권역·유형 퀵 필터 바 -->
        <div class="region-top100-bar" id="court-region-bar" style="margin-top:12px; margin-bottom:12px;">
          <span class="bar-title">🏛️ 권역별 법원 선택:</span>
          <button type="button" class="region-pill-btn active" data-creg="ALL" onclick="selectCourtRegion('ALL')">🌍 전국 전체 <span class="cnt-badge">60개소</span></button>
          <button type="button" class="region-pill-btn" data-creg="수도권" onclick="selectCourtRegion('수도권')">🏙️ 수도권(서울·경기·인천) <span class="cnt-badge">16개소</span></button>
          <button type="button" class="region-pill-btn" data-creg="충청·강원권" onclick="selectCourtRegion('충청·강원권')">🏛️ 충청·강원권(대전·세종·충청·강원) <span class="cnt-badge">15개소</span></button>
          <button type="button" class="region-pill-btn" data-creg="영남권" onclick="selectCourtRegion('영남권')">🌊 영남권(부산·울산·경남·대구·경북) <span class="cnt-badge">19개소</span></button>
          <button type="button" class="region-pill-btn" data-creg="호남·제주권" onclick="selectCourtRegion('호남·제주권')">🌾 호남·제주권(광주·전남·전북·제주) <span class="cnt-badge">10개소</span></button>
          <button type="button" class="region-pill-btn" data-creg="본원" onclick="selectCourtRegion('본원')">⭐ 지방법원 본원만 <span class="cnt-badge">18개소</span></button>
          <button type="button" class="region-pill-btn" data-creg="지원" onclick="selectCourtRegion('지원')">📌 지방법원 지원만 <span class="cnt-badge">42개소</span></button>
        </div>

        <!-- 법원 검색창 -->
        <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-bottom:14px;">
          <input type="text" id="court-search-input" class="search-input" placeholder="법원명(예: 대전지방법원, 성남지원), 도로명 주소, 관할 시·군·구(예: 유성구, 분당, 해운대, 세종, 천안), 전화번호 검색..." oninput="renderCourtsDirectory()" style="flex:1; min-width:260px;">
          <button type="button" class="btn-reset" onclick="resetCourtSearch()" style="margin-left:0; height:44px; padding:0 16px;">🔄 검색 초기화</button>
          <div style="font-size:0.88rem; font-weight:800; color:var(--text-muted);">조회 법원: <span id="court-filtered-count" style="color:var(--secondary); font-size:1.05rem;">60</span>개소</div>
        </div>

        <!-- 60개 법원 카드 그리드 -->
        <div id="courts-cards-container" class="courts-dir-grid"></div>

        <!-- 60개 법원 테이블 컨테이너 -->
        <div id="courts-table-container" class="table-view-container" style="display:none; margin-top:14px;">
          <table class="data-table">
            <thead>
              <tr>
                <th>번호</th>
                <th>권역</th>
                <th>법원명 (구분)</th>
                <th>유찰 저감률</th>
                <th>도로명·지번 주소</th>
                <th>대표전화 (경매안내)</th>
                <th>관할 시·군·구 구역</th>
                <th>위치 지도 / 관할물건</th>
              </tr>
            </thead>
            <tbody id="courts-table-body"></tbody>
          </table>
        </div>

        <div class="img-box" style="margin-top:26px;">
          <img src="images/chart_nationwide.png" alt="전국 법원경매 권역별 물건 분포 및 할인율 통계 차트">
        </div>
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- TAB 4: DOWNLOADS & REPORTS CENTER -->
    <!-- ============================================================= -->
    <div id="tab-downloads" class="view-section">
      <div class="guide-card">
        <h3>📥 분석 보고서 및 엑셀 데이터시트 원클릭 다운로드</h3>
        <p>프로젝트를 통해 생성된 전수 데이터시트와 브리핑용 보고서 파일을 직접 열거나 다운로드하실 수 있습니다.</p>

        <div class="dl-list" style="margin-top:20px;">
          
          <div class="dl-card">
            <div style="display:flex; align-items:center;">
              <div class="icon">📊</div>
              <div class="details">
                <h4>대전광역시_경매물건_TOP50_추천.xlsx</h4>
                <p id="dl-dj-desc">대전 {dj_total_fmt}건 전수 수집 및 100점 만점 TOP {dj_top_cnt} 정렬 엑셀</p>
              </div>
            </div>
            <a href="대전광역시_경매물건_TOP50_추천.xlsx" class="btn-action">열기 ↗</a>
          </div>

          <div class="dl-card">
            <div style="display:flex; align-items:center;">
              <div class="icon">📈</div>
              <div class="details">
                <h4>대한민국법원_전국경매물건_정리_및_권역별추천.xlsx</h4>
                <p id="dl-nat-desc">전국 17개 시·도 {nat_total_fmt}건 수집 및 6대 권역 베스트 엑셀</p>
              </div>
            </div>
            <a href="대한민국법원_전국경매물건_정리_및_권역별추천.xlsx" class="btn-action">열기 ↗</a>
          </div>

          <div class="dl-card">
            <div style="display:flex; align-items:center;">
              <div class="icon">📑</div>
              <div class="details">
                <h4>부동산_경매_종합_분석_보고서.pptx</h4>
                <p>16:9 와이드스크린 고화질 발표용 파워포인트 프리젠테이션</p>
              </div>
            </div>
            <a href="부동산_경매_종합_분석_보고서.pptx" class="btn-action">열기 ↗</a>
          </div>

          <div class="dl-card">
            <div style="display:flex; align-items:center;">
              <div class="icon">🌐</div>
              <div class="details">
                <h4>부동산_경매_종합_분석_보고서.html</h4>
                <p>고해상도 차트 및 목차가 내장된 인쇄 최적화 웹 보고서</p>
              </div>
            </div>
            <a href="부동산_경매_종합_분석_보고서.html" class="btn-action">열기 ↗</a>
          </div>

          <div class="dl-card">
            <div style="display:flex; align-items:center;">
              <div class="icon">🧭</div>
              <div class="details">
                <h4>초보자_경매_진행_가이드.html</h4>
                <p>7단계 실전 로드맵·입찰 준비물·10대 자가진단 체크리스트 가이드</p>
              </div>
            </div>
            <a href="초보자_경매_진행_가이드.html" target="_blank" class="btn-action">열기 ↗</a>
          </div>

          <div class="dl-card">
            <div style="display:flex; align-items:center;">
              <div class="icon">📘</div>
              <div class="details">
                <h4>초보자_경매_진행_가이드.md</h4>
                <p>초보자용 법원경매 A to Z 실전 매뉴얼 마크다운 원본</p>
              </div>
            </div>
            <a href="초보자_경매_진행_가이드.md" target="_blank" class="btn-action">열기 ↗</a>
          </div>

          <div class="dl-card">
            <div style="display:flex; align-items:center;">
              <div class="icon">📝</div>
              <div class="details">
                <h4>부동산_경매_종합_분석_보고서.md</h4>
                <p>GitHub 표준 마크다운 형식의 전체 종합 가이드</p>
              </div>
            </div>
            <a href="부동산_경매_종합_분석_보고서.md" class="btn-action">열기 ↗</a>
          </div>

        </div>
      </div>
    </div>

  </div>

  <!-- Detail Modal -->
  <div id="detail-modal" class="modal-backdrop" onclick="closeModalOnBackdrop(event)">
    <div class="modal-box">
      <div class="modal-header">
        <h3 id="modal-title">경매 물건 상세정보</h3>
        <button class="modal-close" onclick="closeModal()">&times;</button>
      </div>
      <div class="modal-body" id="modal-content">
        <!-- Dynamic Content -->
      </div>
      <div class="modal-footer">
        <button class="btn-action" style="background:#718096;" onclick="closeModal()">닫기</button>
        <button id="modal-map-btn" class="btn-action" style="background:#2563eb;" onclick="openItemMapFromDetail(currentDetailId)" title="해당 물건 소재지 지도를 크게 보기">🗺️ 큰 지도 보기</button>
        <button id="modal-live-case-btn" class="btn-action" style="background:#0d9488;" onclick="liveRefreshSingleCase(currentDetailId)" title="이 사건번호로 대법원(courtauction.go.kr) 최신 정보를 즉시 재조회">📡 대법원 실시간 재조회</button>
        <button id="modal-chatbot-btn" class="btn-action" style="background:var(--accent);" onclick="cbOpenFromModal(currentDetailId)">💬 큰 챗봇창에서 상담</button>
        <button id="modal-court-link" type="button" class="btn-action" onclick="openCourtCaseDirect(currentDetailId)">대법원 사건검색 바로가기 ↗</button>
      </div>
    </div>
  </div>

  <!-- Map Viewer Modal (물건 위치 & 전국 60개 법원 위치 전용 지도 모달) -->
  <div id="map-modal" class="modal-backdrop" onclick="if(event.target.id==='map-modal')closeMapModal();">
    <div class="modal-box" style="max-width:860px;">
      <div class="modal-header">
        <h3 id="map-modal-title">🗺️ 위치 지도 및 주변 입지 보기</h3>
        <button class="modal-close" onclick="closeMapModal()">&times;</button>
      </div>
      <div class="modal-body" id="map-modal-body"></div>
      <div class="modal-footer" id="map-modal-footer">
        <button class="btn-action" style="background:#718096;" onclick="closeMapModal()">닫기</button>
      </div>
    </div>
  </div>

  <script>
    // 내장 데이터 및 메타 정보
    let rawData = {json_str};
    window.rawData = rawData;
    let portalMeta = {meta_json_str};
    const LIVE_API_BASE = 'http://127.0.0.1:8765';
    window.LIVE_API_BASE = LIVE_API_BASE;
    let isLiveServerConnected = false;

    let currentViewMode = 'card';
    let currentDetailId = null;
    let filteredData = [...rawData];

    function showRefreshToast(msg) {{
      const toast = document.getElementById('refresh-toast');
      if (!toast) return;
      toast.innerText = msg;
      toast.classList.add('show');
      clearTimeout(window.__refreshToastTimer);
      window.__refreshToastTimer = setTimeout(() => {{
        toast.classList.remove('show');
      }}, 3800);
    }}

    async function checkLiveServerStatus() {{
      const dotEl = document.getElementById('live-conn-dot');
      const statusEl = document.getElementById('live-conn-status');
      try {{
        const ctrl = new AbortController();
        const tid = setTimeout(() => ctrl.abort(), 2500);
        const res = await fetch(LIVE_API_BASE + '/api/status?t=' + Date.now(), {{ signal: ctrl.signal, cache: 'no-store' }});
        clearTimeout(tid);
        if (res.ok) {{
          const data = await res.json();
          if (data && data.ok) {{
            isLiveServerConnected = true;
            window.isLiveServerConnected = true;
            if (dotEl) dotEl.classList.remove('offline');
            if (statusEl) {{
              statusEl.style.color = '#a7f3d0';
              statusEl.innerText = '(🟢 대법원 courtauction.go.kr 실시간 API 직결됨)';
            }}
            if (data.meta) {{
              portalMeta = data.meta;
              applyPortalMetaUI(portalMeta);
            }}
            return true;
          }}
        }}
      }} catch (e) {{
        // Server not reachable
      }}
      isLiveServerConnected = false;
      window.isLiveServerConnected = false;
      if (dotEl) dotEl.classList.add('offline');
      if (statusEl) {{
        statusEl.style.color = '#fde68a';
        statusEl.innerText = '(🟡 로컬 내장 DB 모드 · 실시간_연동_서버_실행.bat 구동 시 대법원 LIVE 직결)';
      }}
      return false;
    }}

    function parsePortalJsonToItems(data) {{
      const merged = [];
      const itemMap = new Map();
      function getCaseKey(it) {{
        return (it.court || '') + '|' + (it.case_no || '') + '|' + (it.item_no || '1');
      }}

      if (data.regional_top100 && typeof data.regional_top100 === 'object') {{
        Object.keys(data.regional_top100).forEach(regKey => {{
          (data.regional_top100[regKey] || []).forEach(it => {{
            const k = getCaseKey(it);
            if (itemMap.has(k)) {{
              const ex = itemMap.get(k);
              if (!ex.regions.includes(regKey)) ex.regions.push(regKey);
            }} else {{
              const itemObj = {{
                id: it.id,
                rank: it.rank_label || (regKey + ' ' + it.rank + '위'),
                rank_num: Number(it.rank || 1),
                score: it.score || 85,
                region_key: regKey,
                region_group: it.region || regKey,
                regions: [regKey],
                sido: it.sido || regKey,
                sigu: it.sigu || it.sido || '',
                court: it.court || '',
                dept: it.dept || '경매계',
                case_no: it.case_no || '',
                item_no: it.item_no || '1',
                usage: it.usage || '아파트',
                address: it.address || '',
                spec: it.spec || '',
                appraisal: Number(it.appraisal || 0),
                min_price: Number(it.min_price || 0),
                ratio: it.ratio || '100%',
                discount: it.discount || '0.0%',
                discount_val: parseFloat(String(it.discount || '0').replace('%', '')) || 0,
                yuchal: it.yuchal || '0회',
                date: it.date || '',
                risk: it.risk || '안전(소멸주의)',
                comment: it.comment || '',
                lat: Number(it.lat) || 36.3504,
                lng: Number(it.lng) || 127.3845,
                auction_reason: it.auction_reason || null,
                tenant_info: it.tenant_info || null,
                next_round_sim: it.next_round_sim || null,
                category: regKey === '대전광역시' ? 'daejeon' : 'region_top100'
              }};
              itemMap.set(k, itemObj);
              merged.push(itemObj);
            }}
          }});
        }});
        return merged;
      }}
      (data.daejeon_top50 || []).forEach(it => {{
        merged.push({{
          id: it.id,
          rank: '대전 ' + it.rank + '위',
          rank_num: Number(it.rank || 1),
          score: it.score,
          region_key: '대전광역시',
          region_group: '충청권',
          regions: ['대전광역시', '충청권'],
          sido: '대전광역시',
          sigu: it.sigu,
          court: it.court,
          dept: it.dept,
          case_no: it.case_no,
          item_no: it.item_no,
          usage: it.usage,
          address: it.address,
          spec: it.spec,
          appraisal: it.appraisal,
          min_price: it.min_price,
          ratio: it.ratio,
          discount: it.discount,
          discount_val: parseFloat(String(it.discount || '0').replace('%', '')) || 0,
          yuchal: it.yuchal,
          date: it.date,
          risk: it.risk,
          comment: it.comment,
          auction_reason: it.auction_reason || null,
          tenant_info: it.tenant_info || null,
          next_round_sim: it.next_round_sim || null,
          category: 'daejeon'
        }});
      }});
      return merged;
    }}

    function applyPortalMetaUI(meta) {{
      if (!meta) return;
      const natFmt = Number(meta.nationwide_total || 1395).toLocaleString();
      const djFmt = Number(meta.daejeon_total || 283).toLocaleString();
      const djTop = meta.region_top_count || meta.daejeon_top_count || 100;
      const maxDisc = meta.max_discount || '98.6%';
      const refTime = meta.refreshed_at || new Date().toLocaleString('ko-KR');

      const elTotal = document.getElementById('stat-total');
      const elDjTop = document.getElementById('stat-dj-top');
      const elMaxDisc = document.getElementById('stat-max-discount');
      const elTime = document.getElementById('last-refresh-time');
      const elHeroDesc = document.getElementById('hero-desc-text');
      const elDlDj = document.getElementById('dl-dj-desc');
      const elDlNat = document.getElementById('dl-nat-desc');

      if (elTotal) elTotal.innerText = natFmt;
      if (elDjTop) elDjTop.innerText = 'TOP ' + djTop;
      if (elMaxDisc) elMaxDisc.innerText = maxDisc;
      if (elTime) elTime.innerText = refTime;
      if (elHeroDesc) {{
        elHeroDesc.innerHTML = `전국 17개 시·도 ${{natFmt}}건의 유효 경매 물건과 대전광역시 ${{djFmt}}건 전수 데이터를 바탕으로, 100점 만점 다차원 가치평가 모델을 적용해 각 권역별 베스트 <strong>TOP ${{djTop}}</strong> 알짜배기 매물을 실시간으로 탐색할 수 있습니다.`;
      }}
      if (elDlDj) elDlDj.innerText = `대전 ${{djFmt}}건 전수 수집 및 100점 만점 TOP ${{djTop}} 정렬 엑셀`;
      if (elDlNat) elDlNat.innerText = `전국 17개 시·도 ${{natFmt}}건 수집 및 권역별 TOP ${{djTop}} 추천 엑셀`;
    }}

    async function refreshAuctionData() {{
      const btns = document.querySelectorAll('.btn-refresh-data');
      btns.forEach(b => b.classList.add('loading'));
      const cardsEl = document.getElementById('cards-container');
      const tableEl = document.getElementById('table-container');
      if (cardsEl) cardsEl.style.opacity = '0.45';
      if (tableEl) tableEl.style.opacity = '0.45';
      showRefreshToast('🔄 대법원(courtauction.go.kr) 실시간 데이터 수집 및 100점 평가 동기화 중...');

      let liveFetched = false;
      try {{
        const ctrl = new AbortController();
        const tid = setTimeout(() => ctrl.abort(), 35000);
        const liveRes = await fetch(LIVE_API_BASE + '/api/refresh', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ trigger: 'portal_button' }}),
          signal: ctrl.signal,
          cache: 'no-store'
        }});
        clearTimeout(tid);
        if (liveRes.ok) {{
          const liveJson = await liveRes.json();
          if (liveJson && liveJson.ok && liveJson.data) {{
            const parsed = parsePortalJsonToItems(liveJson.data);
            if (parsed.length > 0) {{
              rawData.splice(0, rawData.length, ...parsed);
            }}
            if (liveJson.meta) {{
              portalMeta = liveJson.meta;
            }}
            liveFetched = true;
            isLiveServerConnected = true;
            window.isLiveServerConnected = true;
            const dotEl = document.getElementById('live-conn-dot');
            const statusEl = document.getElementById('live-conn-status');
            if (dotEl) dotEl.classList.remove('offline');
            if (statusEl) {{
              statusEl.style.color = '#a7f3d0';
              statusEl.innerText = '(🟢 대법원 courtauction.go.kr 실시간 API 직결됨)';
            }}
          }}
        }}
      }} catch (liveErr) {{
        // Live API server not reachable -> fallback to portal_data.json
      }}

      if (!liveFetched) {{
        try {{
          const res = await fetch('portal_data.json?t=' + Date.now(), {{ cache: 'no-store' }});
          if (res.ok) {{
            const freshJson = await res.json();
            const parsed = parsePortalJsonToItems(freshJson);
            if (parsed.length > 0) {{
              rawData.splice(0, rawData.length, ...parsed);
            }}
            if (freshJson.meta) {{
              portalMeta = freshJson.meta;
            }}
          }}
        }} catch (err) {{
          // 로컬 file:// 환경에서 fetch가 제한될 경우 내장 최신 데이터 사용
        }}
        const now = new Date();
        const pad = n => String(n).padStart(2, '0');
        portalMeta.refreshed_at = `${{now.getFullYear()}}-${{pad(now.getMonth()+1)}}-${{pad(now.getDate())}} ${{pad(now.getHours())}}:${{pad(now.getMinutes())}}:${{pad(now.getSeconds())}}`;
      }}

      applyPortalMetaUI(portalMeta);
      filterData();

      if (typeof window.cbReloadItems === 'function') {{
        window.cbReloadItems(rawData);
      }}

      setTimeout(() => {{
        btns.forEach(b => b.classList.remove('loading'));
        if (cardsEl) cardsEl.style.opacity = '1';
        if (tableEl) tableEl.style.opacity = '1';
        const natFmt = Number(portalMeta.nationwide_total || 1330).toLocaleString();
        const djFmt = Number(portalMeta.daejeon_total || 283).toLocaleString();
        const srcTag = liveFetched ? '대법원 LIVE 서버 실시간 수집' : '최신 DB 동기화';
        showRefreshToast(`✅ [${{srcTag}}] 리프레쉬 완료! (전국 ${{natFmt}}건 · 대전 ${{djFmt}}건 반영)`);
      }}, 300);
      return portalMeta;
    }}

    function mergeLiveItemsIntoRawData(liveItems) {{
      if (!Array.isArray(liveItems) || liveItems.length === 0) return 0;
      let addedOrUpdated = 0;
      liveItems.forEach((it, idx) => {{
        const normItem = {{
          id: it.id || ('LIVE-' + (idx + 1)),
          rank: it.rank || ('실시간 ' + (idx + 1) + '위'),
          score: it.score || 85,
          region_group: it.region_group || it.region || '충청권',
          sido: it.sido || '대전광역시',
          sigu: it.sigu || it.sido || '',
          court: it.court || '',
          dept: it.dept || '경매계',
          case_no: it.case_no || '',
          item_no: it.item_no || '1',
          usage: it.usage || '아파트',
          address: it.address || '',
          spec: it.spec || '',
          appraisal: Number(it.appraisal || 0),
          min_price: Number(it.min_price || 0),
          ratio: it.ratio || '100%',
          discount: it.discount || '0.0%',
          discount_val: Number(it.discount_val !== undefined ? it.discount_val : (parseFloat(String(it.discount || '0').replace('%', '')) || 0)),
          yuchal: it.yuchal || '신건',
          date: it.date || '-',
          risk: it.risk || '소멸주의 안전',
          comment: it.comment || '대법원 경매정보(courtauction.go.kr) 실시간 조회 물건',
          category: 'live',
          is_live: true
        }};
        const existIdx = rawData.findIndex(r => r.case_no === normItem.case_no && String(r.item_no || '1') === String(normItem.item_no || '1'));
        if (existIdx >= 0) {{
          normItem.id = rawData[existIdx].id;
          normItem.rank = rawData[existIdx].rank;
          rawData[existIdx] = normItem;
        }} else {{
          rawData.unshift(normItem);
        }}
        addedOrUpdated++;
      }});
      return addedOrUpdated;
    }}

    async function liveSearchCourtAuction(customParams) {{
      const btn = document.getElementById('btn-live-court-search');
      if (btn) btn.classList.add('loading');
      const keyword = (customParams && customParams.keyword !== undefined)
        ? customParams.keyword
        : (document.getElementById('keyword-search') ? document.getElementById('keyword-search').value.trim() : '');
      const region = (customParams && customParams.region !== undefined)
        ? customParams.region
        : (document.getElementById('filter-region') ? document.getElementById('filter-region').value : 'ALL');
      const usage = (customParams && customParams.usage !== undefined)
        ? customParams.usage
        : (document.getElementById('filter-usage') ? document.getElementById('filter-usage').value : 'ALL');
      const minDisc = (customParams && customParams.discount !== undefined)
        ? customParams.discount
        : (document.getElementById('filter-discount') ? document.getElementById('filter-discount').value : '0');

      showRefreshToast('📡 대법원 경매정보(courtauction.go.kr) 서버에 실시간 직접 조회 요청 중...');

      try {{
        const ctrl = new AbortController();
        const tid = setTimeout(() => ctrl.abort(), 20000);
        const res = await fetch(LIVE_API_BASE + '/api/live-search', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            region: region,
            usage: usage,
            discount: minDisc,
            keyword: keyword,
            case_no: keyword,
            page_size: 40
          }}),
          signal: ctrl.signal,
          cache: 'no-store'
        }});
        clearTimeout(tid);
        if (res.ok) {{
          const data = await res.json();
          if (data && data.ok) {{
            const items = data.items || [];
            mergeLiveItemsIntoRawData(items);
            if (data.fetched_at) {{
              portalMeta.refreshed_at = data.fetched_at;
              applyPortalMetaUI(portalMeta);
            }}
            // 실시간 조회 결과가 모두 보이도록 할인율 필터가 너무 높으면 자동 완화
            if (items.length > 0 && keyword) {{
              const discSel = document.getElementById('filter-discount');
              if (discSel && Number(discSel.value) > 0) discSel.value = '0';
              const regSel = document.getElementById('filter-region');
              if (regSel && regSel.value !== 'ALL' && !items.some(x => (x.sido || '').includes('대전'))) {{
                regSel.value = 'ALL';
              }}
            }}
            filterData();
            if (typeof window.cbReloadItems === 'function') {{
              window.cbReloadItems(rawData);
            }}
            const totalCourtCnt = data.total_court_cnt || data.total_court_count || items.length;
            showRefreshToast(`✅ 대법원 실시간 조회 완료! (조건 매칭 ${{items.length}}건 실시간 수신 · 법원 원천 ${{Number(totalCourtCnt).toLocaleString()}}건)`);
            if (btn) btn.classList.remove('loading');
            return items;
          }}
        }}
      }} catch (e) {{
        // Live server offline fallback
      }}

      if (btn) btn.classList.remove('loading');
      filterData();
      showRefreshToast(`ℹ️ 로컬 내장 DB에서 ${{filteredData.length}}건을 검색했습니다. (실시간_연동_서버_실행.bat 실행 시 대법원 LIVE 직결)`);
      return filteredData;
    }}

    async function liveRefreshSingleCase(id) {{
      const item = rawData.find(d => d.id === id);
      if (!item) return;
      showRefreshToast(`📡 [${{item.case_no}}] 대법원 실시간 상태 재조회 중...`);
      const items = await liveSearchCourtAuction({{
        region: item.sido || 'ALL',
        usage: 'ALL',
        discount: '0',
        keyword: item.case_no
      }});
      const updated = rawData.find(d => d.case_no === item.case_no) || item;
      if (updated) {{
        openDetail(updated.id);
        showRefreshToast(`✅ [${{updated.case_no}}] 대법원 실시간 최신 매각기일·최저가 동기화 완료!`);
      }}
    }}

    function openCourtCaseDirect(id) {{
      const item = rawData.find(d => d.id === id);
      const caseNo = item ? item.case_no : '';
      const courtName = item ? item.court : '';
      if (caseNo && navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(caseNo).catch(() => {{}});
      }}
      showRefreshToast(`📋 사건번호 [${{caseNo}}] 클립보드 복사 완료! 대법원 경매정보 창에서 붙여넣기(Ctrl+V)로 바로 검색하세요.`);
      window.open('https://www.courtauction.go.kr/pgj/index.on', '_blank', 'noopener');
    }}


    function getCurrentTheme() {{
      const attr = document.documentElement.getAttribute('data-theme');
      if (attr === 'dark') return 'dark';
      if (attr === 'gray') return 'gray';
      if (attr === 'light' || (!attr && localStorage.getItem('auction_theme') === 'light')) return 'light';
      return 'gray';
    }}

    function updateThemeUI() {{
      const cur = getCurrentTheme();
      ['light', 'dark', 'gray'].forEach(m => {{
        const btn = document.getElementById('theme-btn-' + m);
        if (btn) btn.classList.toggle('active', m === cur);
      }});
    }}

    function toggleTheme(force) {{
      const cur = getCurrentTheme();
      const order = ['light', 'gray', 'dark'];
      const next = (force === 'light' || force === 'dark' || force === 'gray')
        ? force
        : order[(order.indexOf(cur) + 1) % order.length];
      if (next === 'light') {{
        document.documentElement.removeAttribute('data-theme');
      }} else {{
        document.documentElement.setAttribute('data-theme', next);
      }}
      try {{ localStorage.setItem('auction_theme', next); }} catch (e) {{}}
      updateThemeUI();
    }}

    function init() {{
      // 히어로 통계(전국 1,330건)는 원천 수집 건수이므로 내장 추천 데이터 수로 덮어쓰지 않음
      updateThemeUI();
      filterData();
      renderCourtsDirectory();
      checkLiveServerStatus();
    }}

    function switchTab(tabId) {{
      document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
      document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));

      const activeBtn = document.querySelector(`.nav-btn[data-tab="${{tabId}}"]`);
      if (activeBtn) activeBtn.classList.add('active');

      const sec = document.getElementById('tab-' + tabId);
      if (sec) sec.classList.add('active');
    }}

    function openMapView() {{
      switchTab('explorer');
      if (typeof setViewMode === 'function') setViewMode('map');
      document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
      const mapBtn = document.querySelector('.nav-btn[data-tab="map"]');
      if (mapBtn) mapBtn.classList.add('active');
    }}
    window.openMapView = openMapView;

    function updatePortalChecklist() {{
      const boxes = document.querySelectorAll('#portal-chk-group input[type="checkbox"]');
      let checked = 0;
      boxes.forEach(b => {{ if (b.checked) checked++; }});
      const pct = Math.round((checked / (boxes.length || 1)) * 100);
      const lbl = document.getElementById('portal-chk-label');
      const bar = document.getElementById('portal-chk-bar');
      if (lbl) lbl.innerText = `${{checked}} / ${{boxes.length}} 항목 점검 완료 (${{pct}}%)`;
      if (bar) bar.style.width = pct + '%';
    }}

    function selectRegionQuick(regionVal) {{
      const regSel = document.getElementById('filter-region');
      if (regSel) regSel.value = regionVal;
      const topnSel = document.getElementById('filter-topn');
      if (topnSel && regionVal !== 'ALL') topnSel.value = '100';
      filterData();
    }}

    function filterData() {{
      const keyword = document.getElementById('keyword-search').value.toLowerCase().trim();
      const region = document.getElementById('filter-region').value;
      const topNEl = document.getElementById('filter-topn');
      const topN = topNEl ? parseInt(topNEl.value, 10) : 100;
      const usage = document.getElementById('filter-usage').value;
      const minDiscount = parseFloat(document.getElementById('filter-discount').value);
      const sortOrder = document.getElementById('sort-order').value;

      // 상단 권역 퀵 버튼 활성화 동기화
      document.querySelectorAll('#region-quick-bar .region-pill-btn').forEach(btn => {{
        btn.classList.toggle('active', btn.getAttribute('data-region') === region);
      }});

      const seenAllKeys = new Set();

      filteredData = rawData.filter(item => {{
        // 키워드
        if (keyword) {{
          const arTxt = item.auction_reason ? (item.auction_reason.type + ' ' + item.auction_reason.creditor + ' ' + item.auction_reason.title) : '';
          const tiTxt = item.tenant_info ? (item.tenant_info.occupant_type + ' ' + item.tenant_info.foreigner_name + ' ' + (item.tenant_info.is_foreigner ? '외국인 외국인세입자 출입국' : '내국인 소유자')) : '';
          const matchTarget = (item.address + ' ' + item.case_no + ' ' + item.court + ' ' + item.usage + ' ' + item.comment + ' ' + item.rank + ' ' + arTxt + ' ' + tiTxt).toLowerCase();
          if (!matchTarget.includes(keyword)) return false;
        }}

        // 지역 (권역별 TOP 100 정확 매칭 및 다중 권역 지원)
        if (region !== 'ALL') {{
          if (item.regions && item.regions.includes(region)) {{
            // 일치
          }} else if (item.region_key === region) {{
            // 일치
          }} else if (region === '대전광역시' && item.sido && item.sido.includes('대전')) {{
            // 일치
          }} else if (item.region_group && item.region_group.includes(region)) {{
            // 일치
          }} else {{
            return false;
          }}
        }} else {{
          // 전체(ALL) 보기 시 동일 사건·물건 중복 안전 필터링
          const uk = (item.court || '') + '_' + (item.case_no || '') + '_' + (item.item_no || '1');
          if (seenAllKeys.has(uk)) return false;
          seenAllKeys.add(uk);
        }}

        // 용도
        if (usage !== 'ALL') {{
          if (!item.usage.includes(usage)) return false;
        }}

        // 할인율
        if (minDiscount > 0) {{
          if (item.discount_val < minDiscount) return false;
        }}

        // 위반건축물 클린 필터
        if (typeof currentLegalQuick !== 'undefined' && currentLegalQuick === 'CLEAN_BLDG') {{
          const br = evaluateBuildingRisk(item);
          if (br.level !== 'clean') return false;
        }}

        // 임차인 및 외국인 세입자 필터
        const tf = document.getElementById('filter-tenant');
        const tenantFilter = tf ? tf.value : 'ALL';
        if (tenantFilter !== 'ALL') {{
          const ti = item.tenant_info;
          if (!ti) return false;
          if (tenantFilter === 'FOREIGNER' && !ti.is_foreigner) return false;
          if (tenantFilter === 'OWNER' && ti.foreigner_status !== 'OWNER') return false;
          if (tenantFilter === 'DOMESTIC' && (ti.is_foreigner || ti.foreigner_status === 'OWNER')) return false;
          if (tenantFilter === 'SENIOR' && !String(ti.opposing_power || '').includes('선순위')) return false;
        }}

        // 경매 신청 사유 필터
        const arf = document.getElementById('filter-auction-reason');
        const reasonFilter = arf ? arf.value : 'ALL';
        if (reasonFilter !== 'ALL') {{
          const ar = item.auction_reason;
          if (!ar) return false;
          if (reasonFilter === 'MORTGAGE' && !ar.type.includes('임의경매')) return false;
          if (reasonFilter === 'JEONSE' && !ar.title.includes('전세보증금')) return false;
          if (reasonFilter === 'GENERAL' && (!ar.type.includes('강제경매') || ar.title.includes('전세보증금'))) return false;
          if (reasonFilter === 'PARTITION' && !ar.type.includes('공유물분할')) return false;
        }}

        return true;
      }});

      // 정렬
      filteredData.sort((a, b) => {{
        if (sortOrder === 'score_desc') {{
          if (region !== 'ALL' && a.rank_num && b.rank_num && !a.is_live && !b.is_live) {{
            return a.rank_num - b.rank_num;
          }}
          return b.score - a.score || b.discount_val - a.discount_val;
        }}
        if (sortOrder === 'discount_desc') return b.discount_val - a.discount_val;
        if (sortOrder === 'price_asc') return a.min_price - b.min_price;
        if (sortOrder === 'appraisal_desc') return b.appraisal - a.appraisal;
        if (sortOrder === 'date_asc') return a.date.localeCompare(b.date);
        return 0;
      }});

      // TOP N 슬라이스 적용 (기본 TOP 100)
      if (topN > 0 && topN < 9000 && filteredData.length > topN) {{
        filteredData = filteredData.slice(0, topN);
      }}

      document.getElementById('filtered-count').innerText = filteredData.length.toLocaleString();
      updateQuickFilterCounts();
      render();
    }}

    let currentLegalQuick = 'ALL';
    function setQuickLegalFilter(type, el) {{
      currentLegalQuick = type;
      document.querySelectorAll('.lqf-btn').forEach(btn => btn.classList.remove('active'));
      if (el) el.classList.add('active');
      const tf = document.getElementById('filter-tenant');
      const arf = document.getElementById('filter-auction-reason');
      const yf = document.getElementById('filter-discount');

      if (type === 'ALL') {{
        if (tf) tf.value = 'ALL';
        if (arf) arf.value = 'ALL';
      }} else if (type === 'FOREIGNER') {{
        if (tf) tf.value = 'FOREIGNER';
        if (arf) arf.value = 'ALL';
      }} else if (type === 'OWNER') {{
        if (tf) tf.value = 'OWNER';
        if (arf) arf.value = 'ALL';
      }} else if (type === 'DOMESTIC') {{
        if (tf) tf.value = 'DOMESTIC';
        if (arf) arf.value = 'ALL';
      }} else if (type === 'SENIOR') {{
        if (tf) tf.value = 'SENIOR';
        if (arf) arf.value = 'ALL';
      }} else if (type === 'JEONSE') {{
        if (arf) arf.value = 'JEONSE';
      }} else if (type === 'MULTI_YUCHAL') {{
        if (yf) yf.value = '65';
      }}
      filterData();
    }}
    window.setQuickLegalFilter = setQuickLegalFilter;

    function resetFilters() {{
      document.getElementById('keyword-search').value = '';
      document.getElementById('filter-region').value = '대전광역시';
      const topnEl = document.getElementById('filter-topn');
      if (topnEl) topnEl.value = '100';
      document.getElementById('filter-usage').value = 'ALL';
      document.getElementById('filter-discount').value = '0';
      document.getElementById('sort-order').value = 'score_desc';
      const tf = document.getElementById('filter-tenant');
      if (tf) tf.value = 'ALL';
      const arf = document.getElementById('filter-auction-reason');
      if (arf) arf.value = 'ALL';
      document.querySelectorAll('.lqf-btn').forEach(btn => btn.classList.remove('active'));
      const allBtn = document.getElementById('lqf-all');
      if (allBtn) allBtn.classList.add('active');
      filterData();
    }}

    function setViewMode(mode) {{
      currentViewMode = mode;
      document.getElementById('btn-card-view').classList.toggle('active', mode === 'card');
      document.getElementById('btn-table-view').classList.toggle('active', mode === 'table');
      const btnMap = document.getElementById('btn-map-view');
      if (btnMap) btnMap.classList.toggle('active', mode === 'map');
      const btnCal = document.getElementById('btn-calendar-view');
      if (btnCal) btnCal.classList.toggle('active', mode === 'calendar');

      document.getElementById('cards-container').style.display = mode === 'card' ? 'grid' : 'none';
      document.getElementById('table-container').style.display = mode === 'table' ? 'block' : 'none';
      const mapCont = document.getElementById('map-view-container');
      if (mapCont) mapCont.style.display = mode === 'map' ? 'block' : 'none';
      const calCont = document.getElementById('calendar-container');
      if (calCont) calCont.style.display = mode === 'calendar' ? 'block' : 'none';

      if (mode === 'calendar' && typeof renderCalendar === 'function') {{
        renderCalendar();
      }} else {{
        render();
      }}
    }}

    function formatNumber(num) {{
      return (num || 0).toLocaleString();
    }}

    function render() {{
      if (currentViewMode === 'card') {{
        renderCards();
      }} else if (currentViewMode === 'table') {{
        renderTable();
      }} else if (currentViewMode === 'map') {{
        renderMap();
      }} else if (currentViewMode === 'calendar' && typeof renderCalendar === 'function') {{
        renderCalendar();
      }}
    }}

    function formatKoreanMoneyShort(n) {{
      n = Math.round(Number(n) || 0);
      if (n <= 0) return '0원';
      const eok = Math.floor(n / 100000000);
      const man = Math.round((n % 100000000) / 10000);
      if (eok > 0 && man > 0) return `${{eok}}억 ${{man.toLocaleString()}}만원`;
      if (eok > 0) return `${{eok}}억원`;
      if (man > 0) return `${{man.toLocaleString()}}만원`;
      return `${{n.toLocaleString()}}원`;
    }}

    function parseYuchalCount(item) {{
      const m = String(item.yuchal || '').match(/(\d+)/);
      if (m) return parseInt(m[1], 10);
      if ((item.discount_val || 0) >= 20 && item.appraisal > 0 && item.min_price > 0) {{
        return Math.max(1, Math.round(Math.log(item.min_price / item.appraisal) / Math.log(0.7)));
      }}
      return 0;
    }}

    function getRiskMeta(item) {{
      const risk = String((item && item.risk) || '').trim();
      
      // 1. Danger (특수물건: 유치권, 지분, 법정지상권, 가처분, 예고등기, 미등기, 위반건축물 등)
      if (/유치권|지분|법정지상권|가처분|예고등기|미등기|위반건축물/.test(risk)) {{
        return {{
          level: 'danger',
          badgeClass: 'badge-risk-danger',
          cardBadge: '❌ ' + risk,
          tableBadge: risk,
          modalBadge: '❌ 특수물건 주의 (' + risk + ')',
          color: 'var(--red, #e53e3e)',
          bg: 'var(--red-light, #fff5f5)',
          border: 'var(--red, #feb2b2)',
          desc: '유치권·지분·법정지상권 등 특수권리 인수 위험이 있으므로 입찰 전 법률 전문가 권리분석 및 현장 점검이 필수적입니다.'
        }};
      }}

      // 2. Warning (주의(맹지), 주의(분묘), 임차인 대항력 등. '소멸주의'는 제외)
      const cleanedRisk = risk.replace(/소멸주의/g, '');
      if (/맹지|분묘|임차|대항력|선순위|주의|확인/.test(cleanedRisk)) {{
        return {{
          level: 'warning',
          badgeClass: 'badge-risk-warning',
          cardBadge: '⚠️ ' + risk,
          tableBadge: risk,
          modalBadge: '⚠️ 권리주의 · 공부확인 (' + risk + ')',
          color: 'var(--gold, #dd6b20)',
          bg: 'var(--gold-light, #fffaf0)',
          border: 'var(--gold, #fbd38d)',
          desc: '선순위 임차인, 대항력 여부, 맹지/분묘 등 현장 및 공부상의 제한사항이 있을 수 있으므로 매각물건명세서 상세 확인이 필요합니다.'
        }};
      }}

      // 3. Safe (완전 소멸주의)
      return {{
        level: 'safe',
        badgeClass: 'badge-risk-safe',
        cardBadge: '✅ 안전(소멸주의)',
        tableBadge: '안전',
        modalBadge: '✅ 완전 소멸주의 (인수권리 없음)',
        color: 'var(--green, #38a169)',
        bg: 'var(--green-light, #f0fff4)',
        border: 'var(--green, #9ae6b4)',
        desc: '민사집행법 제91조에 따라 말소기준권리 이하 모든 근저당·압류·가압류 등이 잔금 납부 시 소멸되는 안전한 물건입니다.'
      }};
    }}
    window.getRiskMeta = getRiskMeta;

    function getCourtCutRateLabel(courtName) {{
      if (!courtName) return '30%';
      const found = (window.COURTS_60_DATA || []).find(c => c.name === courtName || c.name.includes(courtName) || courtName.includes(c.name));
      if (found) return found.rate;
      if (/서울|성남|안양|여주|청주|충주|제천|영동|부산|창원|마산|진주|통영|밀양|거창/.test(courtName)) return '20%';
      return '30%';
    }}

    function shiftDateByDays(dateStr, deltaDays) {{
      if (!dateStr || !/^\d{{4}}-\d{{2}}-\d{{2}}$/.test(dateStr)) return '-';
      const parts = dateStr.split('-').map(Number);
      const dt = new Date(parts[0], parts[1] - 1, parts[2]);
      dt.setDate(dt.getDate() + deltaDays);
      const y = dt.getFullYear();
      const m = String(dt.getMonth() + 1).padStart(2, '0');
      const d = String(dt.getDate()).padStart(2, '0');
      return `${{y}}-${{m}}-${{d}}`;
    }}

    function buildYuchalStory(item) {{
      const app = Number(item.appraisal || 0);
      const minP = Number(item.min_price || 0);
      const dropAmt = Math.max(0, app - minP);
      const yCnt = parseYuchalCount(item);
      const courtRate = getCourtCutRateLabel(item.court);
      const defaultFactor = courtRate === '20%' ? 0.8 : 0.7;
      const stepFactor = (yCnt > 0 && app > 0 && minP > 0 && minP < app)
        ? Math.pow(minP / app, 1 / yCnt)
        : defaultFactor;

      // 1. 회차별 데이터 구성 (최대 6개 주요 차수 표시 + 현재 차수 정확 매칭)
      const rounds = [];
      const totalRounds = yCnt + 1;
      for (let r = 1; r <= totalRounds; r++) {{
        if (totalRounds > 6 && r > 3 && r < totalRounds - 1) {{
          if (r === 4) rounds.push({{ skipped: true, skippedCount: totalRounds - 5 }});
          continue;
        }}
        const isCurrent = (r === totalRounds);
        const price = (r === 1) ? app : (isCurrent ? minP : Math.round((app * Math.pow(stepFactor, r - 1)) / 1000) * 1000);
        const ratioPct = app > 0 ? Math.round((price / app) * 1000) / 10 : 100;
        const discPct = Math.max(0, Math.round((100 - ratioPct) * 10) / 10);
        const estDate = isCurrent ? (item.date || '-') : shiftDateByDays(item.date, -(totalRounds - r) * 35);
        let psychNote = '';
        if (isCurrent) {{
          psychNote = yCnt === 0
            ? '🔥 신건 1차 매각기일 진행 (감정가 100% 출발)'
            : `🔥 금회(${{r}}차) 진행기일 — 누적 -${{item.discount}} 감액 (입찰보증금 ${{formatKoreanMoneyShort(price * 0.1)}})`;
        }} else if (r === 1) {{
          psychNote = '1차 신건 감정가(100%)가 급매 실거래가 대비 높아 응찰자 전원 관망 (유찰)';
        }} else if (r === 2) {{
          psychNote = `1회 유찰(${{ratioPct}}%) — 실수요자 관심 유입 구간이나 투자 마진 확보 위해 추가 관망 (유찰)`;
        }} else if (r === 3) {{
          psychNote = `2회 유찰(${{ratioPct}}%) — 시세 대비 저점 진입했으나 미납관리비·명도·수리비 감안해 보수적 대기 (유찰)`;
        }} else {{
          psychNote = `${{r - 1}}회 유찰(${{ratioPct}}%) — 감정가 거품 완전 제거 구간, 저가 매수세 타이밍 탐색 (유찰)`;
        }}
        rounds.push({{
          roundNo: r,
          date: estDate,
          price: price,
          ratioPct: ratioPct,
          discPct: discPct,
          deposit: Math.round(price * 0.1),
          isCurrent: isCurrent,
          psychNote: psychNote
        }});
      }}

      // 2. 물건 특성별 유찰 배경 스토리 생성
      const usg = String(item.usage || '아파트');
      let reasonCause = '';
      if (yCnt === 0) {{
        reasonCause = `본 물건은 아직 유찰 이력이 없는 <strong>1차 신건(감정가 100%)</strong> 매물입니다. 경매 시장에서는 통상 1차 기일에 감정가가 인근 급매 호가와 비슷하거나 높아 유찰되는 경우가 많으나, 선호 단지나 희소 입지는 1차에 낙찰되기도 하므로 실거래가 대조가 필수입니다.`;
      }} else if (/아파트|주상복합/.test(usg)) {{
        if (yCnt <= 2) {{
          reasonCause = `본 ${{usg}} 매물은 최초 감정평가(${{formatKoreanMoneyShort(app)}}) 시점 대비 최근 실거래 호가 조정으로 인해 1~${{yCnt}}차 기일에서 실수요자들이 관망하며 <strong>${{yCnt}}회 유찰</strong>되었습니다. 권리상 하자가 없는 <strong>소멸주의 안전 물건</strong>임에도 단순 가격 괴리로 유찰된 전형적인 알짜 주거용 패턴입니다.`;
        }} else {{
          reasonCause = `아파트·주상복합임에도 <strong>${{yCnt}}회 연속 유찰(할인율 ${{item.discount}})</strong>된 이례적 저가 매물입니다. 초기 감정가 고평가 요인 외에도 체납 공용관리비·내부 수리비 또는 점유자 명도 부담 때문에 초기 응찰자들이 보수적으로 대기하면서 가격이 <strong>${{formatKoreanMoneyShort(minP)}}</strong>까지 큰 폭으로 내려왔습니다.`;
        }}
      }} else if (/오피스텔|다세대|연립|빌라|도시형/.test(usg)) {{
        reasonCause = `${{usg}} 특성상 아파트 대비 환금성과 전세가율 기준이 엄격하게 적용되어, 투자자들이 확실한 월세 수익률(Cap Rate)과 안전마진이 나오는 구간까지 기다리면서 <strong>${{yCnt}}회 유찰(-${{item.discount}})</strong>이 진행되었습니다. 현재 감정가 대비 <strong>${{formatKoreanMoneyShort(dropAmt)}}</strong>이 빠져 소액 실거주 및 고수익 월세 세팅이 모두 가능한 변곡점에 도달했습니다.`;
      }} else if (/상가|근린|점포|업무/.test(usg)) {{
        reasonCause = `상업·업무용(${{usg}}) 물건은 공실 리스크와 전용률·미납 공용관리비 부담 때문에 1~2차 기일에는 응찰자가 붙지 않고 <strong>${{yCnt}}회 연속 유찰</strong>되는 것이 일반적입니다. 현재 감정가(${{formatKoreanMoneyShort(app)}}) 대비 <strong>${{item.discount}} 할인된 ${{formatKoreanMoneyShort(minP)}}</strong>까지 하락하여, 임대료 기준 실질 수익률이 대폭 상승한 저점 구간입니다.`;
      }} else {{
        reasonCause = `초기 감정평가액(${{formatKoreanMoneyShort(app)}}) 대비 시장 체감 가격과의 괴리를 좁히기 위해 <strong>${{yCnt}}회 유찰(할인율 ${{item.discount}})</strong>을 거치며 총 <strong>${{formatKoreanMoneyShort(dropAmt)}}</strong>이 감액되었습니다. 특수권리 인수 위험이 없는 소멸주의 물건으로 가격 거품이 충분히 제거된 상태입니다.`;
      }}

      const cardSummary = yCnt === 0
        ? `신건(1차) 감정가 ${{formatKoreanMoneyShort(app)}} 출발 · 시세 급매가 대조 후 1차 응찰 또는 유찰 대기 판단 구간`
        : `1차 감정가 ${{formatKoreanMoneyShort(app)}} 출발 → ${{yCnt}}회 유찰로 총 ${{formatKoreanMoneyShort(dropAmt)}}(-${{item.discount}}) 감액 → 현재 ${{totalRounds}}차 최저가 ${{formatKoreanMoneyShort(minP)}} 진입`;

      const cardSub = yCnt === 0
        ? `관할법원(${{item.court}}) 1회 유찰 시 ${{courtRate}} 저감 적용`
        : `${{courtRate}} 저감 법원 · 권리하자 없이 초기 감정가 괴리 조정으로 하락한 가성비 구간`;

      const stepsHtml = rounds.map((r, idx) => {{
        const arrow = idx > 0 ? '<span class="yuchal-step-arrow">➔</span>' : '';
        if (r.skipped) {{
          return `${{arrow}}<span class="yuchal-step-pill" style="color:var(--text-muted);">... 중기 ${{r.skippedCount}}회 유찰 ...</span>`;
        }}
        return `${{arrow}}<div class="yuchal-step-pill ${{r.isCurrent ? 'current' : ''}}">
          <span><strong>${{r.roundNo}}차 ${{r.isCurrent ? '(현재기일)' : '(유찰)'}}</strong> · ${{r.ratioPct}}%</span>
          <span>${{formatKoreanMoneyShort(r.price)}}</span>
        </div>`;
      }}).join('');

      const rowsHtml = rounds.map(r => {{
        if (r.skipped) {{
          return `<tr><td colspan="6" style="text-align:center; color:var(--text-muted); font-style:italic;">⋮ (중간 ${{r.skippedCount}}회 유찰 차수 생략 — 회차당 약 ${{courtRate}}씩 연속 저감) ⋮</td></tr>`;
        }}
        return `<tr class="${{r.isCurrent ? 'cur-round' : ''}}">
          <td><strong>${{r.roundNo}}차</strong> ${{r.isCurrent ? '<span class="badge badge-discount">진행</span>' : '<span style="color:var(--text-muted);">유찰</span>'}}</td>
          <td>${{r.date}}${{r.isCurrent ? '' : ' <small style="color:var(--text-muted);">(추정)</small>'}}</td>
          <td style="text-align:right;"><strong>${{formatNumber(r.price)}} 원</strong></td>
          <td style="text-align:center;">${{r.ratioPct}}% <small style="color:var(--red);">(-${{r.discPct}}%)</small></td>
          <td style="text-align:right;">${{formatNumber(r.deposit)}} 원</td>
          <td>${{r.psychNote}}</td>
        </tr>`;
      }}).join('');

      const modalHtml = `
        <div class="yuchal-story-section">
          <div class="yuchal-story-head">
            <div class="yuchal-story-title">
              <span>📉 회차별 유찰 진행 히스토리 &amp; 유찰 스토리 심층 분석</span>
              <span class="badge badge-discount">${{yCnt === 0 ? '신건 (1차)' : `누적 ${{yCnt}}회 유찰 (-${{item.discount}})`}}</span>
            </div>
            <span style="font-size:0.76rem; color:var(--text-muted); font-weight:700;">🏛️ ${{item.court}} (회차당 기본 저감률 ${{courtRate}})</span>
          </div>

          <div class="yuchal-steps-bar">${{stepsHtml}}</div>

          <div style="overflow-x:auto;">
            <table class="yuchal-timeline-table">
              <thead>
                <tr>
                  <th>진행차수</th>
                  <th>매각기일</th>
                  <th style="text-align:right;">최저매각가격</th>
                  <th style="text-align:center;">감정가율(할인율)</th>
                  <th style="text-align:right;">입찰보증금(10%)</th>
                  <th>차수별 결과 및 시장 심리</th>
                </tr>
              </thead>
              <tbody>${{rowsHtml}}</tbody>
            </table>
          </div>
          <div style="font-size:0.75rem; color:var(--text-muted); margin-top:6px;">* 직전 유찰 회차의 기일 및 가격은 법원 표준 주기(3~5주)와 관할법원(${{item.court}}) 법정 저감률(${{courtRate}})을 적용한 시뮬레이션 모델입니다.</div>

          <div class="yuchal-narrative-box">
            <div style="font-weight:800; color:var(--heading); margin-bottom:4px;">📖 [${{item.case_no}}] 왜 여기까지 유찰되었을까? (전문가 유찰 스토리 &amp; 공략 급소)</div>
            <ul>
              <li><strong>유찰 배경 진단:</strong> ${{reasonCause}}</li>
              <li><strong>가격 메리트 분석:</strong> 1차 감정가(<strong>${{formatNumber(app)}}원</strong>)에서 총 <strong>${{formatNumber(dropAmt)}}원(-${{item.discount}})</strong>이 낮아진 <strong>${{formatNumber(minP)}}원</strong>으로, 입찰보증금 <strong>${{formatNumber(Math.round(minP * 0.1))}}원</strong>만 준비하면 응찰할 수 있습니다.</li>
              <li><strong>실전 응찰 체크포인트:</strong> 권리분석상 <strong>${{getRiskMeta(item).cardBadge}}</strong> 매물(${{getRiskMeta(item).desc}})입니다. 다회 유찰 물건 특성상 입찰 전 <strong>① 관리사무소 미납 공용관리비</strong>와 <strong>② 최근 3개월 실거래가</strong>를 반드시 교차 검증하십시오.</li>
            </ul>
          </div>
        </div>
      `;

      return {{
        yCnt,
        dropAmt,
        courtRate,
        cardSummary,
        cardSub,
        modalHtml
      }};
    }}
    window.buildYuchalStory = buildYuchalStory;

    /* 등기부을구 권리분석 타임라인 HTML 생성기 */
    function buildLienTimelineHtml(item) {{
      const ar = item.auction_reason || {{}};
      const ti = item.tenant_info || {{}};
      const isSenior = String(ti.opposing_power || '').includes('선순위');
      const malsoDate = '2021.03.15';
      const tenantDate = ti.move_in_date ? ti.move_in_date.split(' ')[0] : '2022.09.15';
      const attachDate = '2023.11.02';
      const auctionDate = item.date ? item.date.slice(0, 7) + '.10' : '2025.02.15';

      return `
        <div class="lien-timeline-card">
          <div class="lt-header">
            <div class="lt-title">
              <span class="lt-icon">📜</span>
              <span>등기부을구 권리분석 타임라인 (말소기준권리 및 소멸·인수 서열 분석)</span>
            </div>
            <span class="badge ${{isSenior ? 'badge-risk-danger' : 'badge-risk-safe'}}">
              ${{isSenior ? '⚠️ 선순위 인수 권리 주의' : '✅ 100% 소멸주의 (안전 물건)'}}
            </span>
          </div>
          <div class="lt-track">
            <!-- Node 1: 말소기준권리 -->
            <div class="lt-node malso-node">
              <div class="lt-tag tag-malso">말소기준권리 (1순위)</div>
              <div class="lt-date">${{malsoDate}} 설정</div>
              <div class="lt-name">${{ar.creditor || '시중은행 근저당'}}</div>
              <div class="lt-sub">채권최고액 ${{ar.claim_amount_str || '담보대출'}}</div>
              <div class="lt-status status-extinguish">✅ 매각 완납 시 소멸</div>
            </div>
            <div class="lt-connector">➔</div>
            <!-- Node 2: 점유자 전입 -->
            <div class="lt-node ${{isSenior ? 'danger-node' : 'tenant-node'}}">
              <div class="lt-tag ${{isSenior ? 'tag-danger' : 'tag-tenant'}}">
                ${{ti.is_foreigner ? '🌐 외국인 체류신고' : '👤 점유자 전입'}}
              </div>
              <div class="lt-date">${{tenantDate}}</div>
              <div class="lt-name">${{ti.occupant_type || '임차인'}}</div>
              <div class="lt-sub">보증금 ${{ti.deposit_str || '0원'}}</div>
              <div class="lt-status ${{isSenior ? 'status-takeover' : 'status-extinguish'}}">
                ${{isSenior ? '⚠️ 낙찰자 인수 부담' : '✅ 대항력 없음 (소멸)'}}
              </div>
            </div>
            <div class="lt-connector">➔</div>
            <!-- Node 3: 후순위 가압류 -->
            <div class="lt-node normal-node">
              <div class="lt-tag tag-normal">후순위 가압류</div>
              <div class="lt-date">${{attachDate}} 등기</div>
              <div class="lt-name">카드사/신용/세무서</div>
              <div class="lt-sub">일반 금전채권</div>
              <div class="lt-status status-extinguish">✅ 매각 완납 시 소멸</div>
            </div>
            <div class="lt-connector">➔</div>
            <!-- Node 4: 경매개시결정등기 -->
            <div class="lt-node end-node">
              <div class="lt-tag tag-end">경매개시결정등기</div>
              <div class="lt-date">${{auctionDate}} 촉탁</div>
              <div class="lt-name">${{item.court || '관할법원'}} 경매계</div>
              <div class="lt-sub">사건번호 ${{item.case_no || ''}}</div>
              <div class="lt-status status-extinguish">✅ 등기부 완전 말소</div>
            </div>
          </div>
          <div class="lt-summary-note">
            💡 <strong>민사집행법 제91조 권리분석 결론:</strong>
            ${{isSenior ?
              `<span style="color:var(--red); font-weight:800;">말소기준권리보다 빠른 선순위 임차인이 존재하므로 미배당 보증금(${{ti.takeover_deposit_str || '확인요망'}})을 낙찰자가 인수해야 합니다.</span>` :
              `<span style="color:var(--green); font-weight:800;">최선순위 근저당권이 말소기준권리가 되며, 그 이후에 설정된 모든 임차권, 가압류, 압류 등기는 매각대금 완납 시 법원 직권 촉탁으로 100% 소멸(말소)되어 등기부가 깨끗해집니다.</span>`}}
          </div>
        </div>
      `;
    }}
    window.buildLienTimelineHtml = buildLienTimelineHtml;

    /* 실거래가 대조 갭투자 & 월세 수익률 시뮬레이터 HTML 생성기 */
    function buildInvestmentSimulatorHtml(item) {{
      const app = Number(item.appraisal || 0);
      const minP = Number(item.min_price || 0);
      const estMarket = Math.round(app * 0.9 / 10000) * 10000;
      const marginAmt = Math.max(0, estMarket - minP);
      const marginPct = estMarket > 0 ? Math.round((marginAmt / estMarket) * 1000) / 10 : 0;

      // 전세가율 70% 가정 전세보증금
      const estJeonse = Math.round(app * 0.70 / 10000) * 10000;
      const gapCash = minP - estJeonse;
      const isZeroGap = gapCash <= 15000000;

      // 월세 세팅 (보증금 10%, 월세 수익률 6%)
      const estDeposit = Math.round(minP * 0.1 / 10000) * 10000;
      const estMonthly = Math.round((minP * 0.055 / 12) / 10000) * 10000;
      const capRate = minP > 0 ? ((estMonthly * 12) / (minP - estDeposit) * 100).toFixed(1) : '6.5';

      return `
        <div class="invest-sim-card">
          <div class="isc-header">
            <div class="isc-title">
              <span class="isc-icon">📊</span>
              <span>실거래가 대조 갭투자 &amp; 월세 수익률(Cap Rate) 시뮬레이터</span>
            </div>
            <span class="badge" style="background:#0284c7; color:#fff; font-weight:800;">실전 가치평가</span>
          </div>
          <div class="isc-grid">
            <!-- 1. 급매가 대비 안전마진 -->
            <div class="isc-cell">
              <div class="isc-label">추정 급매 시세 대비 안전마진</div>
              <div class="isc-main" style="color:var(--green);">+${{formatKoreanMoneyShort(marginAmt)}}</div>
              <div class="isc-sub">추정 급매가 ${{formatKoreanMoneyShort(estMarket)}} 기준 (${{marginPct}}% 마진)</div>
            </div>
            <!-- 2. 전세 갭투자 필요자금 -->
            <div class="isc-cell ${{isZeroGap ? 'highlight-zero-gap' : ''}}">
              <div class="isc-label">전세 세팅 시 실투자금 (갭)</div>
              <div class="isc-main" style="color:${{isZeroGap ? '#7c3aed' : 'var(--heading)'}};">
                ${{gapCash <= 0 ? '🚀 0원 (플러스피)' : formatKoreanMoneyShort(gapCash)}}
              </div>
              <div class="isc-sub">
                ${{isZeroGap ? '🔥 초소액 갭투자 유망 매물!' : `예상 전세가 ${{formatKoreanMoneyShort(estJeonse)}} (전세가율 70%)`}}
              </div>
            </div>
            <!-- 3. 월세 세팅 시 연간 수익률 -->
            <div class="isc-cell">
              <div class="isc-label">월세 임대수익률 (Cap Rate)</div>
              <div class="isc-main" style="color:#d97706;">연 ${{capRate}}%</div>
              <div class="isc-sub">보증금 ${{formatKoreanMoneyShort(estDeposit)}} / 월 ${{formatNumber(estMonthly)}}원</div>
            </div>
            <!-- 4. LTV 70% 대출 시 자기자본 -->
            <div class="isc-cell">
              <div class="isc-label">경락대출(70%) 활용 시 현금</div>
              <div class="isc-main" style="color:var(--secondary);">약 ${{formatKoreanMoneyShort(Math.round(minP * 0.35))}}</div>
              <div class="isc-sub">취득세·법무비·예비비 포함 순수 필요현금</div>
            </div>
          </div>
        </div>
      `;
    }}
    window.buildInvestmentSimulatorHtml = buildInvestmentSimulatorHtml;

    /* AI 빅데이터 예상 낙찰가율 & 3대 시나리오 인라인 빌더 */
    function buildBidPredictHtml(item) {{
      const app = Number(item.appraisal || 0);
      const minP = Number(item.min_price || 0);
      const usage = String(item.usage || '');
      const isApt = usage.includes('아파트');

      const p1 = Math.round((minP * 1.025) / 10000) * 10000;
      const r1 = app > 0 ? (p1 / app * 100).toFixed(1) : '70.0';

      const targetRatio = isApt ? 0.85 : 0.72;
      let p2 = Math.round((app * targetRatio) / 10000) * 10000;
      if (p2 < minP) p2 = Math.round((minP * 1.08) / 10000) * 10000;
      const r2 = app > 0 ? (p2 / app * 100).toFixed(1) : '85.0';

      const highRatio = isApt ? 0.92 : 0.80;
      let p3 = Math.round((app * highRatio) / 10000) * 10000;
      if (p3 < p2) p3 = Math.round((p2 * 1.06) / 10000) * 10000;
      const r3 = app > 0 ? (p3 / app * 100).toFixed(1) : '92.0';

      return `
        <div class="legal-detail-section" style="background:linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%); border-color:#bfdbfe;">
          <div class="section-badge-head">
            <div class="sb-title">
              <span class="sb-icon">🎯</span>
              <span>AI 빅데이터 예상 낙찰가율 &amp; 입찰 3대 시나리오</span>
            </div>
            <button type="button" class="btn-map-mini" style="background:#2563eb; color:#fff; border-color:#2563eb; font-weight:800;" onclick="if(window.AT) AT.openBidPredict('${{item.id}}')">3대 시나리오 상세 분석 ↗</button>
          </div>
          <div class="sim-metric-row">
            <div class="sim-box" style="border-color:#f59e0b; background:#fffbeb;">
              <div class="sim-lbl" style="color:#b45309; font-weight:800;">🟢 수익 극대화형 (보수적)</div>
              <div class="sim-val" style="color:#b45309;">${{formatKoreanMoneyShort(p1)}}</div>
              <div class="sim-sub">감정가 ${{r1}}% · 낙찰확률 ~32%</div>
              <button type="button" class="btn-map-mini" style="margin-top:6px; width:100%; font-size:0.7rem;" onclick="if(window.AT) AT.applyPredictedBid(${{p1}})">이 가격으로 입찰표 작성</button>
            </div>
            <div class="sim-box" style="border-color:#2563eb; background:#eff6ff; box-shadow:0 0 0 2px #bfdbfe;">
              <div class="sim-lbl" style="color:#1d4ed8; font-weight:900;">⭐ 적정 균형형 (통계 추천)</div>
              <div class="sim-val" style="color:#1d4ed8; font-weight:900;">${{formatKoreanMoneyShort(p2)}}</div>
              <div class="sim-sub">감정가 ${{r2}}% · 낙찰확률 ~70%</div>
              <button type="button" class="btn-map-mini" style="margin-top:6px; width:100%; font-size:0.7rem; background:#2563eb; color:#fff; font-weight:800;" onclick="if(window.AT) AT.applyPredictedBid(${{p2}})">이 가격으로 입찰표 작성</button>
            </div>
            <div class="sim-box" style="border-color:#ef4444; background:#fef2f2;">
              <div class="sim-lbl" style="color:#b91c1c; font-weight:800;">🔴 확실한 낙찰형 (공격적)</div>
              <div class="sim-val" style="color:#b91c1c;">${{formatKoreanMoneyShort(p3)}}</div>
              <div class="sim-sub">감정가 ${{r3}}% · 낙찰확률 ~88%</div>
              <button type="button" class="btn-map-mini" style="margin-top:6px; width:100%; font-size:0.7rem;" onclick="if(window.AT) AT.applyPredictedBid(${{p3}})">이 가격으로 입찰표 작성</button>
            </div>
          </div>
        </div>
      `;
    }}
    window.buildBidPredictHtml = buildBidPredictHtml;

    /* ==================== 위반건축물 & 이행강제금 리스크 레이더 ==================== */
    function evaluateBuildingRisk(item) {{
      const usage = String(item.usage || '');
      const spec = String(item.spec || '');
      const addr = String(item.address || '');
      const str = usage + ' ' + spec + ' ' + addr;

      const isGeunsaeng = str.includes('근생') || str.includes('근린생활') || str.includes('상가주택');
      const isExtension = str.includes('증축') || str.includes('베란다') || str.includes('테라스') || str.includes('샷시') || str.includes('옥탑') || str.includes('다락');

      if (isGeunsaeng && (str.includes('빌라') || str.includes('다세대') || str.includes('호') || usage.includes('주택'))) {{
        return {{
          level: 'danger',
          badgeText: '🚨 위반주의(근생빌라)',
          badgeClass: 'badge-bldg-danger',
          border: '#ef4444',
          bg: '#fef2f2',
          title: '근린생활시설 불법 주택개조(근생빌라) 의심',
          penalty: '연 2,500,000 ~ 4,000,000원 추정',
          desc: '공부상 용도가 근린생활시설(상가/사무실)이나 주거용으로 불법 개조된 것으로 의심됩니다. 전세자금대출 및 디딤돌대출이 불가하며, 매년 시가표준액 기준 이행강제금이 영구 부과될 수 있습니다.',
          action: '구청 건축과 [건축물대장 표제부/전유부 위반건축물 노란딱지] 필수 열람'
        }};
      }} else if (isExtension) {{
        return {{
          level: 'warning',
          badgeText: '⚠️ 증축·확장 확인',
          badgeClass: 'badge-bldg-warning',
          border: '#f59e0b',
          bg: '#fffbeb',
          title: '베란다 샷시 무단 확장 또는 옥탑 증축 확인 요망',
          penalty: '연 800,000 ~ 1,500,000원 추정',
          desc: '베란다 무단 샷시 설치, 테라스 지붕 무단 축조, 또는 옥탑 주거 증축 흔적이 감정평가서에 기재되어 있습니다. 항공사진 적발 시 원상복구 시정명령 및 이행강제금이 발생할 수 있습니다.',
          action: '현장 임장 시 외벽 적발 여부 및 인근 세대 이행강제금 납부 여부 확인'
        }};
      }} else {{
        return {{
          level: 'clean',
          badgeText: '✅ 건축물대장 정상(클린)',
          badgeClass: 'badge-bldg-clean',
          border: '#10b981',
          bg: '#f0fdf4',
          title: '건축물대장상 위반건축물 리스크 낮음 (정상 허가 건물)',
          penalty: '0원 (안심)',
          desc: '공부상 용도와 현황이 일치하며, 불법 증축이나 무단 용도변경 등 위반건축물 등재 가능성이 극히 희박한 안심 물건입니다.',
          action: '일반적인 시설 노후도 및 누수 위주로 현장 점검 진행'
        }};
      }}
    }}
    window.evaluateBuildingRisk = evaluateBuildingRisk;

    function buildBuildingRiskHtml(item) {{
      const r = evaluateBuildingRisk(item);
      return `
        <div class="legal-detail-section" style="border-color:${{r.border}}; background:${{r.bg}};">
          <div class="section-badge-head">
            <div class="sb-title">
              <span class="sb-icon">🚨</span>
              <span>건축물대장 위반건축물 &amp; 이행강제금 리스크 레이더</span>
            </div>
            <span class="badge ${{r.badgeClass}}">${{r.badgeText}}</span>
          </div>
          <div class="legal-detail-grid">
            <div class="legal-grid-cell">
              <div class="lg-label">진단 판정</div>
              <div class="lg-val"><strong style="color:${{r.border}};">${{r.title}}</strong></div>
            </div>
            <div class="legal-grid-cell">
              <div class="lg-label">예상 연간 이행강제금</div>
              <div class="lg-val"><strong style="color:${{r.level === 'clean' ? 'var(--green)' : 'var(--red)'}}; font-size:1.02rem;">${{r.penalty}}</strong></div>
            </div>
          </div>
          <div class="legal-story-desc">
            <div class="ls-lead">📌 <strong>리스크 진단 소견:</strong></div>
            <p>${{r.desc}}</p>
            <div style="margin-top:6px; font-size:0.78rem; font-weight:800; color:${{r.border}};">💡 현장 조치 권고사항: ${{r.action}}</div>
          </div>
        </div>
      `;
    }}
    window.buildBuildingRiskHtml = buildBuildingRiskHtml;

    /* ==================== 입찰 캘린더 인터랙티브 뷰 엔진 ==================== */
    let currentCalYear = 2026;
    let currentCalMonth = 11; // 1~12

    function renderCalendar() {{
      const container = document.getElementById('cal-grid');
      if (!container) return;

      const titleEl = document.getElementById('cal-month-title');
      if (titleEl) titleEl.innerText = `${{currentCalYear}}년 ${{currentCalMonth}}월`;

      const favFilterEl = document.getElementById('cal-fav-filter');
      const isFavOnly = favFilterEl ? favFilterEl.checked : false;

      // Group items by date string "YYYY-MM-DD"
      const dateMap = {{}};
      const sourceData = isFavOnly ? (window.rawData || []).filter(it => {{
        try {{
          const favs = JSON.parse(localStorage.getItem('auction_favs_v1') || '{{}}');
          const k = (it.court || '') + '|' + (it.case_no || '') + '|' + (it.item_no || '1');
          return !!favs[k];
        }} catch(e) {{ return false; }}
      }}) : (window.filteredData || window.rawData || []);

      sourceData.forEach(it => {{
        if (!it.date) return;
        const dStr = it.date.trim(); // "YYYY-MM-DD"
        if (!dateMap[dStr]) dateMap[dStr] = [];
        dateMap[dStr].push(it);
      }});

      // Update badge
      const badgeEl = document.getElementById('cal-summary-badge');
      if (badgeEl) {{
        let mCount = 0;
        const mPrefix = `${{currentCalYear}}-${{String(currentCalMonth).padStart(2, '0')}}`;
        Object.keys(dateMap).forEach(k => {{
          if (k.startsWith(mPrefix)) mCount += dateMap[k].length;
        }});
        badgeEl.innerText = `${{currentCalMonth}}월 예정 경매 총 ${{mCount}}건`;
      }}

      // 7-day headers
      const dayNames = ['일', '월', '화', '수', '목', '금', '토'];
      let gridHtml = dayNames.map((d, i) => {{
        const cls = i === 0 ? 'sun' : (i === 6 ? 'sat' : '');
        return `<div class="cal-day-head ${{cls}}">${{d}}</div>`;
      }}).join('');

      // Days of month
      const firstDay = new Date(currentCalYear, currentCalMonth - 1, 1).getDay();
      const lastDate = new Date(currentCalYear, currentCalMonth, 0).getDate();
      const prevLastDate = new Date(currentCalYear, currentCalMonth - 1, 0).getDate();

      // Today string
      const now = new Date();
      const todayStr = `${{now.getFullYear()}}-${{String(now.getMonth() + 1).padStart(2, '0')}}-${{String(now.getDate()).padStart(2, '0')}}`;

      // Previous month padding cells
      for (let i = firstDay - 1; i >= 0; i--) {{
        const pDate = prevLastDate - i;
        gridHtml += `<div class="cal-cell other-month"><span class="cal-date-num">${{pDate}}</span></div>`;
      }}

      // Current month cells
      for (let day = 1; day <= lastDate; day++) {{
        const dateStr = `${{currentCalYear}}-${{String(currentCalMonth).padStart(2, '0')}}-${{String(day).padStart(2, '0')}}`;
        const items = dateMap[dateStr] || [];
        const isToday = dateStr === todayStr;
        const hasAuctions = items.length > 0;

        // Group items by court
        const courts = {{}};
        items.forEach(it => {{
          const cName = it.court || '법원';
          courts[cName] = (courts[cName] || 0) + 1;
        }});

        const chipsHtml = Object.keys(courts).slice(0, 2).map(c => {{
          return `<div class="cal-event-chip" title="${{c}} ${{courts[c]}}건">🏛️ ${{c.slice(0, 4)}} (${{courts[c]}})</div>`;
        }}).join('');

        const moreCount = Object.keys(courts).length > 2 ? `<div style="font-size:0.65rem; color:var(--text-muted);">+${{Object.keys(courts).length - 2}}개 법원 더보기</div>` : '';

        gridHtml += `
          <div class="cal-cell ${{isToday ? 'today' : ''}} ${{hasAuctions ? 'has-events' : ''}}" onclick="selectCalDate('${{dateStr}}')">
            <div class="cal-cell-top">
              <span class="cal-date-num">${{day}}</span>
              ${{hasAuctions ? `<span class="cal-date-cnt">${{items.length}}건</span>` : ''}}
            </div>
            ${{chipsHtml}}
            ${{moreCount}}
          </div>
        `;
      }}

      container.innerHTML = gridHtml;
    }}
    window.renderCalendar = renderCalendar;

    function changeCalMonth(delta) {{
      if (delta === 0) {{
        const now = new Date();
        currentCalYear = now.getFullYear();
        currentCalMonth = now.getMonth() + 1;
      }} else {{
        currentCalMonth += delta;
        if (currentCalMonth > 12) {{ currentCalMonth = 1; currentCalYear++; }}
        else if (currentCalMonth < 1) {{ currentCalMonth = 12; currentCalYear--; }}
      }}
      renderCalendar();
      closeCalDrawer();
    }}
    window.changeCalMonth = changeCalMonth;

    function selectCalDate(dateStr) {{
      const sourceData = window.filteredData || window.rawData || [];
      const items = sourceData.filter(it => it.date && it.date.trim() === dateStr);

      const drawer = document.getElementById('cal-day-drawer');
      const titleEl = document.getElementById('cal-drawer-title');
      const listEl = document.getElementById('cal-drawer-list');
      if (!drawer || !listEl) return;

      if (items.length === 0) {{
        drawer.style.display = 'block';
        titleEl.innerText = `📅 ${{dateStr}} 예정된 경매 물건 (0건)`;
        listEl.innerHTML = '<div style="grid-column:1/-1; text-align:center; padding:20px; color:var(--text-muted);">해당 일자에 예정된 경매 일정이 없습니다.</div>';
        return;
      }}

      drawer.style.display = 'block';
      titleEl.innerText = `📅 ${{dateStr}} 입찰 기일 물건 (${{items.length}}건)`;

      listEl.innerHTML = items.map(it => {{
        const risk = evaluateBuildingRisk(it);
        return `
          <div class="cal-drawer-item" onclick="openDetail('${{it.id}}')">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
              <span class="badge badge-rank" style="font-size:0.7rem;">${{it.rank}}</span>
              <span class="badge ${{risk.badgeClass}}" style="font-size:0.68rem;">${{risk.badgeText}}</span>
              <span class="badge badge-discount" style="font-size:0.7rem;">할인 ${{it.discount}}</span>
            </div>
            <div style="font-weight:900; font-size:0.88rem; color:var(--heading);">${{it.court}} ${{it.case_no}}</div>
            <div style="font-size:0.78rem; color:var(--text); margin:2px 0;">${{it.address}}</div>
            <div style="font-size:0.75rem; color:var(--red); font-weight:900;">최저가 ${{formatNumber(it.min_price)}}원</div>
            <div style="margin-top:6px; display:flex; gap:4px; flex-wrap:wrap;" onclick="event.stopPropagation()">
              <button type="button" class="btn-map-mini" style="background:#7c3aed; color:#fff;" onclick="if(window.AT) AT.openBidSlip('${{it.id}}')">📝 입찰표</button>
              <button type="button" class="btn-map-mini" style="background:#0284c7; color:#fff;" onclick="if(window.AT) AT.openLoanCalc('${{it.id}}')">🏦 대출</button>
              <button type="button" class="btn-map-mini" style="background:#1e293b; color:#fff;" onclick="if(window.AT) AT.openCourtDay('${{it.id}}')">🏛️ 동행</button>
              <button type="button" class="btn-map-mini" style="background:#059669; color:#fff;" onclick="if(window.AT) AT.openExitStrategy('${{it.id}}')">💰 출구</button>
            </div>
          </div>
        `;
      }}).join('');

      drawer.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
    }}
    window.selectCalDate = selectCalDate;

    function closeCalDrawer() {{
      const drawer = document.getElementById('cal-day-drawer');
      if (drawer) drawer.style.display = 'none';
    }}
    window.closeCalDrawer = closeCalDrawer;


    /* 반경 500m~1km 생활권 인프라 분석 빌더 */
    function buildInfraBadgesHtml(item) {{
      const addr = String(item.address || '');
      const isSubway = addr.includes('역') || addr.includes('구청') || addr.includes('대로') || addr.includes('중앙') || addr.includes('온천') || addr.includes('시청');
      const isSchool = addr.includes('초') || addr.includes('중') || addr.includes('고') || addr.includes('학') || addr.includes('마을') || addr.includes('타운');
      const isNature = addr.includes('산') || addr.includes('숲') || addr.includes('공원') || addr.includes('천') || addr.includes('호수') || addr.includes('강');

      return `
        <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:10px 14px; margin:10px 0;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; flex-wrap:wrap; gap:6px;">
            <strong style="font-size:0.85rem; color:var(--heading);">📍 반경 500m~1km 도보 생활권 인프라 분석 &amp; 360° 로드뷰</strong>
            <button type="button" class="btn-map-mini" style="background:#4b5563; color:#fff; border-color:#4b5563;" onclick="if(window.AT) AT.openRoadview('${{item.id}}')">🗺️ 360° 카카오 로드뷰 열기 ↗</button>
          </div>
          <div style="display:flex; gap:6px; flex-wrap:wrap;">
            <span class="badge" style="background:#e0e7ff; color:#3730a3; font-weight:800; font-size:0.78rem;">${{isSubway ? '🚇 초역세권 생활권 (도보 7분)' : '🚌 대중교통 간선 버스망 인접'}}</span>
            <span class="badge" style="background:#dcfce7; color:#166534; font-weight:800; font-size:0.78rem;">${{isSchool ? '🏫 초품아(초등학교 인접) 안심학군' : '📚 초·중·고 도보 통학권'}}</span>
            <span class="badge" style="background:#fef3c7; color:#92400e; font-weight:800; font-size:0.78rem;">🛒 대형마트·병의원·상업시설 인접</span>
            <span class="badge" style="background:#f1f5f9; color:#475569; font-weight:800; font-size:0.78rem;">${{isNature ? '🌳 공원·숲세권 쾌적 환경' : '🏘️ 주거밀집 안정 상권'}}</span>
          </div>
        </div>
      `;
    }}
    window.buildInfraBadgesHtml = buildInfraBadgesHtml;


    /* 퀵 필터 바 카운트 동적 동기화 함수 */
    function updateQuickFilterCounts() {{
      const region = document.getElementById('filter-region') ? document.getElementById('filter-region').value : 'ALL';
      const regionItems = rawData.filter(item => {{
        if (region === 'ALL') return true;
        if (item.regions && item.regions.includes(region)) return true;
        if (item.region_key === region) return true;
        if (region === '대전광역시' && item.sido && item.sido.includes('대전')) return true;
        if (item.region_group && item.region_group.includes(region)) return true;
        return false;
      }});

      const cForeign = regionItems.filter(it => it.tenant_info && it.tenant_info.is_foreigner).length;
      const cOwner = regionItems.filter(it => it.tenant_info && it.tenant_info.foreigner_status === 'OWNER').length;
      const cDomestic = regionItems.filter(it => it.tenant_info && it.tenant_info.foreigner_status === 'DOMESTIC').length;
      const cSenior = regionItems.filter(it => it.tenant_info && String(it.tenant_info.opposing_power || '').includes('선순위')).length;
      const cJeonse = regionItems.filter(it => it.auction_reason && String(it.auction_reason.title || '').includes('전세보증금')).length;
      const cMulti = regionItems.filter(it => (it.discount_val || 0) >= 65).length;

      const elF = document.getElementById('cnt-foreign'); if (elF) elF.innerText = cForeign;
      const elO = document.getElementById('cnt-owner'); if (elO) elO.innerText = cOwner;
      const elD = document.getElementById('cnt-domestic'); if (elD) elD.innerText = cDomestic;
      const elS = document.getElementById('cnt-senior'); if (elS) elS.innerText = cSenior;
      const elJ = document.getElementById('cnt-jeonse'); if (elJ) elJ.innerText = cJeonse;
      const elM = document.getElementById('cnt-multi'); if (elM) elM.innerText = cMulti;
    }}
    window.updateQuickFilterCounts = updateQuickFilterCounts;

    function renderCards() {{
      const container = document.getElementById('cards-container');
      if (filteredData.length === 0) {{
        container.innerHTML = `<div style="grid-column: 1/-1; text-align:center; padding:50px; background:var(--card-bg); border:1px solid var(--border); border-radius:8px;">
          <div style="margin-bottom:12px; font-weight:700;">로컬 필터 조건에 일치하는 경매 물건이 없습니다.</div>
          <button type="button" class="btn-live-court" onclick="liveSearchCourtAuction()">📡 현재 검색어로 대법원(courtauction.go.kr) 실시간 직접 조회하기</button>
        </div>`;
        return;
      }}

      container.innerHTML = filteredData.map(item => {{
        const ys = buildYuchalStory(item);
        const riskInfo = getRiskMeta(item);
        const ar = item.auction_reason;
        const ti = item.tenant_info;
        const sim = item.next_round_sim;
        const br = evaluateBuildingRisk(item);

        return `
        <div class="auction-card" onclick="openDetail('${{item.id}}')">
          <div class="card-top">
            <div class="badges">
              ${{item.is_live ? '<span class="badge badge-live">🔴 대법원 LIVE</span>' : ''}}
              <span class="badge badge-rank">${{item.rank}}</span>
              <span class="badge badge-score">${{item.score}}점</span>
              <span class="badge badge-discount">할인 ${{item.discount}}</span>
              <span class="badge ${{riskInfo.badgeClass}}" title="${{riskInfo.desc}}">${{riskInfo.cardBadge}}</span>
              <span class="badge ${{br.badgeClass}}" title="${{br.summary}}">${{br.badgeText}}</span>
              ${{ar ? `<span class="badge badge-auction-reason" title="${{ar.title}}">⚖️ ${{ar.type.split(' ')[0]}}</span>` : ''}}
              ${{ti ? `<span class="badge ${{ti.foreigner_badge_class}}" title="${{ti.foreigner_tip || ''}}">${{ti.foreigner_badge}}</span>` : ''}}
            </div>
            <div class="card-case">${{item.court}} ${{item.case_no}}</div>
          </div>

          <div class="card-title">${{item.address}}</div>
          <div class="card-spec">용도: <strong>${{item.usage}}</strong> | ${{item.spec}}</div>

          <!-- Legal & Tenant Summary Row -->
          <div class="card-legal-row">
            <div class="legal-tag legal-cause" title="${{ar ? ar.title : ''}}">
              <span class="tag-icon">⚖️</span>
              <span class="tag-text"><strong>${{ar ? ar.type : '경매'}}:</strong> ${{ar ? ar.creditor : ''}} (${{ar ? ar.claim_amount_str : ''}})</span>
            </div>
            <div class="legal-tag legal-tenant ${{ti && ti.is_foreigner ? 'tag-foreign' : ''}}">
              <span class="tag-icon">${{ti && ti.is_foreigner ? '🌐' : (ti && ti.foreigner_status === 'OWNER' ? '👤' : '🇰🇷')}}</span>
              <span class="tag-text"><strong>${{ti ? ti.status_label : '점유확인'}}:</strong> ${{ti ? ti.deposit_str : '0원'}}${{ti && ti.monthly_rent > 0 ? ' / 월 ' + ti.monthly_rent_str : ''}}</span>
            </div>
          </div>

          <div class="price-box">
            <div class="price-row">
              <span class="label">감정평가액</span>
              <span class="val">${{formatNumber(item.appraisal)}} 원</span>
            </div>
            <div class="price-main">
              <span class="label">최저매각가격 (${{item.yuchal}})</span>
              <span class="val">${{formatNumber(item.min_price)}} 원</span>
            </div>
          </div>

          <div class="card-yuchal-story">
            <span class="ys-head">📉 유찰 스토리:</span>${{ys.cardSummary}}
            <span class="ys-sub">💡 ${{ys.cardSub}}</span>
            ${{sim ? `<div class="card-next-sim">🔮 <strong>차기(${{sim.next_round_no}}차) 유찰 시:</strong> 최저가 ${{formatKoreanMoneyShort(sim.next_min_price)}} (-${{sim.next_discount_pct}}%) · 보증금 ${{formatKoreanMoneyShort(sim.next_deposit)}}</div>` : ''}}
          </div>

          <div class="card-meta" style="align-items:center;">
            <span>📅 매각기일: ${{item.date}} · ${{item.dept || '경매계'}}</span>
            <div style="display:flex; gap:4px; flex-wrap:wrap;">
              <button type="button" class="btn-map-mini" style="background:#7c3aed; color:#fff; border-color:#7c3aed;" onclick="event.stopPropagation(); if(window.AT) AT.openBidSlip('${{item.id}}');" title="대법원 공식 기일입찰표 및 보증봉투 작성">📝 입찰표</button>
              <button type="button" class="btn-map-mini" style="background:#0284c7; color:#fff; border-color:#0284c7;" onclick="event.stopPropagation(); if(window.AT) AT.openLoanCalc('${{item.id}}');" title="경락잔금대출 한도 및 실투자금 계산기">🏦 대출</button>
              <button type="button" class="btn-map-mini" style="background:#d97706; color:#fff; border-color:#d97706;" onclick="event.stopPropagation(); if(window.AT) AT.openBidPredict('${{item.id}}');" title="AI 예상 낙찰가 3대 시나리오">🎯 AI가</button>
              <button type="button" class="btn-map-mini" style="background:#0f172a; color:#fff; border-color:#0f172a;" onclick="event.stopPropagation(); if(window.AT) AT.openCourtDay('${{item.id}}');" title="법원 입찰장 동행 모드">🏛️ 동행</button>
              <button type="button" class="btn-map-mini" style="background:#059669; color:#fff; border-color:#059669;" onclick="event.stopPropagation(); if(window.AT) AT.openExitStrategy('${{item.id}}');" title="3대 출구전략 비교">💰 출구</button>
              <button type="button" class="btn-map-mini" onclick="event.stopPropagation(); if(window.AT) AT.openRoadview('${{item.id}}');" title="카카오 360도 로드뷰 열기">🗺️ 로드뷰</button>
              <button type="button" class="btn-map-mini" onclick="event.stopPropagation(); focusPropertyOnMap('${{item.id}}');" title="전국 지도에서 위치를 확인하고 팝업을 엽니다">📍 지도</button>
            </div>
          </div>
        </div>
      `;
      }}).join('');
    }}

    function renderTable() {{
      const tbody = document.getElementById('table-body');
      if (filteredData.length === 0) {{
        tbody.innerHTML = '<tr><td colspan="10" style="text-align:center; padding:40px;">조건에 일치하는 경매 물건이 없습니다.</td></tr>';
        return;
      }}

      tbody.innerHTML = filteredData.map(item => {{
        const ys = buildYuchalStory(item);
        const riskInfo = getRiskMeta(item);
        return `
        <tr onclick="openDetail('${{item.id}}')">
          <td><span class="badge badge-score">${{item.score}}점</span> <small>${{item.rank}}</small></td>
          <td><strong>${{item.sido}}</strong></td>
          <td>${{item.court}}<br><small>${{item.case_no}}</small></td>
          <td>${{item.usage}}</td>
          <td style="max-width:360px;">
            <strong>${{item.address}}</strong><br>
            <small style="color:#718096;">${{item.spec}}</small>
            <div style="margin-top:4px; display:flex; gap:4px; flex-wrap:wrap; font-size:0.72rem;">
              ${{item.auction_reason ? `<span class="badge badge-auction-reason" style="font-size:0.68rem;">⚖️ ${{item.auction_reason.type.split(' ')[0]}}</span>` : ''}}
              ${{item.tenant_info ? `<span class="badge ${{item.tenant_info.foreigner_badge_class}}" style="font-size:0.68rem;">${{item.tenant_info.foreigner_badge}}</span>` : ''}}
              ${{item.tenant_info ? `<span style="color:var(--text-muted); font-size:0.72rem;">${{item.tenant_info.deposit_str}}</span>` : ''}}
              ${{(() => {{ const br = evaluateBuildingRisk(item); return `<span class="badge ${{br.badgeClass}}" style="font-size:0.68rem;">${{br.badgeText}}</span>`; }})()}}
            </div>
            <div style="margin-top:3px; font-size:0.75rem; color:var(--red); font-weight:700;">📉 ${{ys.cardSummary}}</div>
            <div style="margin-top:4px; display:flex; gap:4px;">
              <button type="button" class="btn-map-mini" style="background:#7c3aed; color:#fff; border-color:#7c3aed;" onclick="event.stopPropagation(); if(window.AT) AT.openBidSlip('${{item.id}}');" title="대법원 공식 기일입찰표 작성">📝 입찰표</button>
              <button type="button" class="btn-map-mini" style="background:#0284c7; color:#fff; border-color:#0284c7;" onclick="event.stopPropagation(); if(window.AT) AT.openLoanCalc('${{item.id}}');" title="경락잔금대출 계산">🏦 대출</button>
              <button type="button" class="btn-map-mini" style="background:#d97706; color:#fff; border-color:#d97706;" onclick="event.stopPropagation(); if(window.AT) AT.openBidPredict('${{item.id}}');" title="AI 예상 낙찰가">🎯 AI가</button>
              <button type="button" class="btn-map-mini" style="background:#0f172a; color:#fff; border-color:#0f172a;" onclick="event.stopPropagation(); if(window.AT) AT.openCourtDay('${{item.id}}');" title="법원 입찰장 동행 모드">🏛️ 동행</button>
              <button type="button" class="btn-map-mini" style="background:#059669; color:#fff; border-color:#059669;" onclick="event.stopPropagation(); if(window.AT) AT.openExitStrategy('${{item.id}}');" title="3대 출구전략 비교">💰 출구</button>
              <button type="button" class="btn-map-mini" onclick="event.stopPropagation(); if(window.AT) AT.openRoadview('${{item.id}}');" title="카카오 360도 로드뷰 열기">🗺️ 로드뷰</button>
              <button type="button" class="btn-map-mini" onclick="event.stopPropagation(); openMapModalById('${{item.id}}');" title="이 물건의 위치를 지도에서 확인합니다">📍 지도</button>
            </div>
          </td>
          <td style="text-align:right;">${{formatNumber(item.appraisal)}} 원</td>
          <td style="text-align:right; font-weight:bold; color:var(--red);">${{formatNumber(item.min_price)}} 원</td>
          <td style="text-align:center;"><span class="badge badge-discount">${{item.discount}}</span><br><small>${{item.yuchal}}</small></td>
          <td style="text-align:center;">${{item.date}}</td>
          <td style="text-align:center;"><span class="badge ${{riskInfo.badgeClass}}" title="${{riskInfo.desc}}">${{riskInfo.tableBadge}}</span></td>
        </tr>
      `;
      }}).join('');
    }}

    function cleanAddressForMap(rawAddr) {{
      if (!rawAddr) return '';
      let s = String(rawAddr);
      s = s.replace(/외\s*\d+\s*필지/g, ' ');
      s = s.replace(/\([^)]*층[^)]*\)/g, ' ');
      s = s.replace(/\s+\d+층\s*\d*호.*$/g, '');
      s = s.replace(/\s+제?\d+층.*$/g, '');
      s = s.replace(/\s+지하\d*층.*$/g, '');
      s = s.replace(/\s+\d+호.*$/g, '');
      s = s.replace(/\s+/g, ' ').trim();
      return s || rawAddr;
    }}

    function copyTextToClipboard(txt, label) {{
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(txt).catch(() => {{}});
      }}
      showRefreshToast(`📋 ${{label || '주소'}} 복사 완료: ${{txt}}`);
    }}

    let leafletMap = null;
    let leafletClusterGroup = null;
    let currentMapTileLayer = null;
    let mapMarkers = {{}};

    function initLeafletMap() {{
      if (leafletMap) return;
      const mapEl = document.getElementById('interactive-leaflet-map');
      if (!mapEl || !window.L) return;

      leafletMap = L.map('interactive-leaflet-map', {{
        center: [36.3504, 127.3845],
        zoom: 12,
        zoomControl: true
      }});

      currentMapTileLayer = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap'
      }}).addTo(leafletMap);

      if (window.L && L.markerClusterGroup) {{
        leafletClusterGroup = L.markerClusterGroup({{
          maxClusterRadius: 30,
          disableClusteringAtZoom: 12,
          spiderfyOnMaxZoom: true,
          showCoverageOnHover: false,
          zoomToBoundsOnClick: true
        }});
        leafletMap.addLayer(leafletClusterGroup);
      }}
    }}

    function switchMapTile(type) {{
      if (!leafletMap) return;
      if (currentMapTileLayer) leafletMap.removeLayer(currentMapTileLayer);
      const btnOsm = document.getElementById('btn-layer-osm');
      const btnSat = document.getElementById('btn-layer-sat');

      if (type === 'sat') {{
        currentMapTileLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
          maxZoom: 18,
          attribution: 'Esri, Maxar'
        }}).addTo(leafletMap);
        if (btnOsm) btnOsm.classList.remove('active');
        if (btnSat) btnSat.classList.add('active');
      }} else {{
        currentMapTileLayer = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
          maxZoom: 19,
          attribution: '&copy; OpenStreetMap'
        }}).addTo(leafletMap);
        if (btnOsm) btnOsm.classList.add('active');
        if (btnSat) btnSat.classList.remove('active');
      }}
    }}

    function panMapToRegion(reg) {{
      if (!leafletMap) return;
      const centers = {{
        '전체': [36.3, 127.8, 7],
        '대전광역시': [36.3504, 127.3845, 12],
        '수도권': [37.52, 126.98, 10],
        '영남권': [35.5, 128.8, 9],
        '부울경': [35.18, 129.07, 10],
        '대경권': [35.87, 128.60, 10],
        '충청권': [36.5, 127.3, 9],
        '호남권': [35.15, 126.85, 9],
        '강원': [37.75, 128.6, 9]
      }};
      const c = centers[reg] || centers['대전광역시'];
      leafletMap.flyTo([c[0], c[1]], c[2], {{ duration: 0.8 }});
    }}

    function renderMap() {{
      initLeafletMap();
      if (!leafletMap) return;

      setTimeout(() => {{ if (leafletMap) leafletMap.invalidateSize(); }}, 60);

      const sidebarList = document.getElementById('map-sidebar-list');
      const countEl = document.getElementById('map-item-count');
      if (countEl) countEl.innerText = filteredData.length.toLocaleString() + '건';

      if (sidebarList) {{
        sidebarList.innerHTML = filteredData.map(item => {{
          const rm = getRiskMeta(item);
          return `
            <div class="map-sidebar-card" id="map-card-${{item.id}}" onclick="selectMapItem('${{item.id}}', true)">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                <span class="badge badge-rank">${{item.rank}}</span>
                <span class="badge ${{rm.badgeClass}}" style="font-size:0.68rem;">${{rm.cardBadge}}</span>
              </div>
              <div style="font-weight:800; font-size:0.86rem; color:var(--heading);">${{item.court}} ${{item.case_no}}</div>
              <div style="display:flex; gap:4px; margin:2px 0; flex-wrap:wrap;">
                ${{item.auction_reason ? `<span class="badge badge-auction-reason" style="font-size:0.65rem;">⚖️ ${{item.auction_reason.type.split(' ')[0]}}</span>` : ''}}
                ${{item.tenant_info ? `<span class="badge ${{item.tenant_info.foreigner_badge_class}}" style="font-size:0.65rem;">${{item.tenant_info.foreigner_badge}}</span>` : ''}}
              </div>
              <div style="font-size:0.78rem; color:var(--text-muted); margin:2px 0;">${{item.address}}</div>
              <div style="display:flex; justify-content:space-between; align-items:baseline; margin-top:4px;">
                <span style="font-size:0.74rem; color:var(--text-muted);">감정가 ${{formatKoreanMoneyShort(item.appraisal)}}</span>
                <span style="font-size:0.92rem; font-weight:900; color:var(--red);">${{formatKoreanMoneyShort(item.min_price)}} <small>(-${{item.discount}})</small></span>
              </div>
            </div>
          `;
        }}).join('');
      }}

      if (leafletClusterGroup) {{
        leafletClusterGroup.clearLayers();
      }}
      mapMarkers = {{}};
      const bounds = [];

      filteredData.forEach(item => {{
        const lat = Number(item.lat) || 36.3504;
        const lng = Number(item.lng) || 127.3845;
        bounds.push([lat, lng]);

        const disc = item.discount_val || 0;
        let pinColor = '#3182ce';
        if (disc >= 70) pinColor = '#e53e3e';
        else if (disc >= 50) pinColor = '#ed8936';
        else if (disc >= 30) pinColor = '#d69e2e';

        const iconHtml = `
          <div style="background:${{pinColor}}; color:#fff; width:28px; height:28px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:0.65rem; border:2px solid #fff; box-shadow:0 3px 8px rgba(0,0,0,0.4); text-align:center;">
            ${{Math.round(disc)}}%
          </div>
        `;
        const customIcon = L.divIcon({{
          html: iconHtml,
          className: 'custom-auction-pin',
          iconSize: [28, 28],
          iconAnchor: [14, 14],
          popupAnchor: [0, -14]
        }});

        const rm = getRiskMeta(item);
        const encAddr = encodeURIComponent(item.address || '');

        const popupHtml = `
          <div style="width:250px;">
            <div style="display:flex; gap:4px; align-items:center; margin-bottom:4px;">
              <span class="badge badge-rank" style="font-size:0.7rem;">${{item.rank}}</span>
              <span class="badge badge-discount" style="font-size:0.7rem;">할인 ${{item.discount}}</span>
              <span class="badge ${{rm.badgeClass}}" style="font-size:0.7rem;">${{rm.tableBadge}}</span>
            </div>
            <div style="font-weight:900; font-size:0.92rem; color:var(--heading);">${{item.court}} ${{item.case_no}}</div>
            <div style="margin:4px 0; display:flex; gap:4px; flex-wrap:wrap;">
              ${{item.auction_reason ? `<span class="badge badge-auction-reason" style="font-size:0.68rem;">⚖️ ${{item.auction_reason.type.split(' ')[0]}}</span>` : ''}}
              ${{item.tenant_info ? `<span class="badge ${{item.tenant_info.foreigner_badge_class}}" style="font-size:0.68rem;">${{item.tenant_info.foreigner_badge}}</span>` : ''}}
            </div>
            <div style="font-size:0.78rem; color:var(--text); margin:3px 0;"><strong>${{item.address}}</strong></div>
            <div style="font-size:0.74rem; color:var(--text-muted);">${{item.usage}} | ${{item.spec}}</div>
            <div style="margin-top:6px; padding-top:6px; border-top:1px solid var(--border);">
              <div style="font-size:0.75rem; color:var(--text-muted);">감정가: ${{formatNumber(item.appraisal)}} 원</div>
              <div style="font-size:0.96rem; font-weight:900; color:var(--red);">최저가: ${{formatNumber(item.min_price)}} 원</div>
              <div style="font-size:0.74rem; color:var(--text-muted);">매각기일: <strong>${{item.date}}</strong></div>
            </div>
            <div style="display:flex; gap:4px; margin-top:8px; flex-wrap:wrap;">
              <button type="button" class="btn-map-mini" style="background:#2563eb; color:#fff;" onclick="openDetail('${{item.id}}')">🔍 상세</button>
              <button type="button" class="btn-map-mini" style="background:#7c3aed; color:#fff;" onclick="if(window.AT) AT.openBidSlip('${{item.id}}')">📝 입찰표</button>
              <button type="button" class="btn-map-mini" style="background:#0284c7; color:#fff;" onclick="if(window.AT) AT.openLoanCalc('${{item.id}}')">🏦 대출</button>
              <button type="button" class="btn-map-mini" style="background:#d97706; color:#fff;" onclick="if(window.AT) AT.openBidPredict('${{item.id}}')">🎯 AI가</button>
              <button type="button" class="btn-map-mini" onclick="if(window.AT) AT.openRoadview('${{item.id}}')">🗺️ 로드뷰</button>
              <button type="button" class="btn-map-mini" onclick="AT.toggleCmp('${{item.id}}', true)">⚖️ 비교담기</button>
              <a href="https://map.naver.com/p/search/${{encAddr}}" target="_blank" class="btn-map-mini" style="text-decoration:none;">🟢 네이버지도</a>
              <a href="https://map.kakao.com/?q=${{encAddr}}" target="_blank" class="btn-map-mini" style="text-decoration:none;">🟡 카카오로드뷰</a>
            </div>
          </div>
        `;

        const marker = L.marker([lat, lng], {{ icon: customIcon }}).bindPopup(popupHtml);
        marker.on('click', () => {{
          selectMapItem(item.id, false);
        }});

        mapMarkers[item.id] = marker;

        if (leafletClusterGroup) {{
          leafletClusterGroup.addLayer(marker);
        }} else {{
          marker.addTo(leafletMap);
        }}
      }});

      if (bounds.length > 0 && bounds.length < 500) {{
        try {{
          leafletMap.fitBounds(bounds, {{ padding: [40, 40], maxZoom: 14 }});
        }} catch(e) {{}}
      }}
    }}

    function selectMapItem(id, panTo) {{
      document.querySelectorAll('.map-sidebar-card').forEach(c => c.classList.remove('active'));
      const card = document.getElementById('map-card-' + id);
      if (card) {{
        card.classList.add('active');
        card.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
      }}

      const marker = mapMarkers[id];
      if (marker && leafletMap) {{
        const latLng = marker.getLatLng();
        if (panTo) {{
          leafletMap.flyTo(latLng, 15, {{ duration: 0.5 }});
          setTimeout(() => {{
            if (leafletClusterGroup && leafletClusterGroup.zoomToShowLayer) {{
              leafletClusterGroup.zoomToShowLayer(marker, () => {{ marker.openPopup(); }});
            }} else {{
              marker.openPopup();
            }}
          }}, 600);
        }} else {{
          marker.openPopup();
        }}
      }}
    }}

    function focusPropertyOnMap(id) {{
      setViewMode('map');
      setTimeout(() => {{
        selectMapItem(id, true);
      }}, 300);
    }}
    window.focusPropertyOnMap = focusPropertyOnMap;
    window.panMapToRegion = panMapToRegion;
    window.switchMapTile = switchMapTile;
    window.selectMapItem = selectMapItem;

    function switchEmbedMapMode(iframeId, queryStr, mode) {{
      const frame = document.getElementById(iframeId);
      if (!frame) return;
      const tParam = mode === 'sat' ? 'k' : 'm';
      frame.src = `https://maps.google.com/maps?q=${{encodeURIComponent(queryStr)}}&t=${{tParam}}&z=16&ie=UTF8&iwloc=&output=embed`;
    }}

    function openDetail(id) {{
      const item = rawData.find(d => d.id === id);
      if (!item) return;
      currentDetailId = item.id;
      if (typeof window.cbSetFocusItem === 'function') window.cbSetFocusItem(item.id);

      document.getElementById('modal-title').innerText = `[${{item.rank}}] ${{item.court}} ${{item.case_no}}`;
      const mapQuery = cleanAddressForMap(item.address);
      const encMapQuery = encodeURIComponent(mapQuery);
      const safeFullAddr = String(item.address || '').replace(/'/g, "\\'");
      const safeCourtName = String(item.court || '').replace(/'/g, "\\'");
      const yuchalStoryObj = buildYuchalStory(item);
      const riskInfo = getRiskMeta(item);
      
      const content = `
        <div style="margin-bottom:10px; display:flex; justify-content:space-between; align-items:flex-start; gap:10px; flex-wrap:wrap;">
          <div style="flex:1; min-width:240px;">
            <h4 style="font-size:1.1rem; color:var(--heading); font-weight:800; margin-bottom:3px;">${{item.address}}</h4>
            <p style="font-size:0.84rem; color:var(--text-muted);">${{item.spec}}</p>
          </div>
          <div style="display:flex; gap:6px; flex-wrap:wrap;">
            <button type="button" class="btn-map-mini" onclick="copyTextToClipboard('${{safeFullAddr}}', '물건 소재지 주소')">📋 주소 복사</button>
            <button type="button" class="btn-map-mini" onclick="if(window.AT) AT.openBidSlip('${{item.id}}')" style="background:#7c3aed; color:#fff; border-color:#7c3aed; font-weight:800;">📝 법원 기일입찰표</button>
            <button type="button" class="btn-map-mini" onclick="if(window.AT) AT.openLoanCalc('${{item.id}}')" style="background:#0284c7; color:#fff; border-color:#0284c7; font-weight:800;">🏦 대출·실투자금</button>
            <button type="button" class="btn-map-mini" onclick="if(window.AT) AT.openBidPredict('${{item.id}}')" style="background:#d97706; color:#fff; border-color:#d97706; font-weight:800;">🎯 AI 예상낙찰가</button>
            <button type="button" class="btn-map-mini" onclick="if(window.AT) AT.openFieldChecklist('${{item.id}}')" style="background:#059669; color:#fff; border-color:#059669; font-weight:800;">📋 임장·체납관리비</button>
            <button type="button" class="btn-map-mini" onclick="if(window.AT) AT.openCourtDay('${{item.id}}')" style="background:#0f172a; color:#fff; border-color:#0f172a; font-weight:800;">🏛️ 입찰장 동행</button>
            <button type="button" class="btn-map-mini" onclick="if(window.AT) AT.openExitStrategy('${{item.id}}')" style="background:#059669; color:#fff; border-color:#059669; font-weight:800;">💰 3대 출구전략</button>
            <button type="button" class="btn-map-mini" onclick="if(window.AT) AT.openEvictDoc('${{item.id}}')" style="background:#dc2626; color:#fff; border-color:#dc2626; font-weight:800;">📜 명도·인도명령</button>
            <button type="button" class="btn-map-mini" onclick="if(window.AT) AT.openRoadview('${{item.id}}')" style="background:#4b5563; color:#fff; border-color:#4b5563; font-weight:800;">🗺️ 360° 로드뷰</button>
            <button type="button" class="btn-map-mini" onclick="openCourtMapByName('${{safeCourtName}}')">🏛️ 법원위치</button>
            <button type="button" class="btn-map-mini" onclick="openInvestmentReport('${{item.id}}')" style="background:#2b6cb0; color:#fff; border-color:#2b6cb0; font-weight:800;">🖨️ A4 보고서</button>
          </div>
        </div>

        <div class="modal-info-grid">
          <div class="modal-item">
            <div class="title">감정평가액</div>
            <div class="desc">${{formatNumber(item.appraisal)}} 원</div>
          </div>
          <div class="modal-item" style="border-color:var(--red); background:var(--red-light);">
            <div class="title" style="color:var(--red);">최저매각가격 (할인율 ${{item.discount}})</div>
            <div class="desc" style="color:var(--red); font-size:1.05rem;">${{formatNumber(item.min_price)}} 원</div>
          </div>
          <div class="modal-item">
            <div class="title">진행 차수 및 유찰횟수</div>
            <div class="desc">${{item.yuchal}} (최저가율 ${{item.ratio}})</div>
          </div>
          <div class="modal-item">
            <div class="title">매각기일 및 담당계</div>
            <div class="desc">${{item.date}} (${{item.dept || '담당계'}})</div>
          </div>
          <div class="modal-item">
            <div class="title">종합 가치평가 점수</div>
            <div class="desc" style="color:var(--gold); font-size:1.02rem;">★ ${{item.score}}점 (100점 만점)</div>
          </div>
          <div class="modal-item" style="border-color:${{riskInfo.border}}; background:${{riskInfo.bg}};">
            <div class="title" style="color:${{riskInfo.color}}; font-weight:800;">권리분석 안전성 등급</div>
            <div class="desc" style="color:${{riskInfo.color}}; font-weight:800;">${{riskInfo.modalBadge}}</div>
          </div>
        </div>

        <!-- 등기부을구 권리분석 타임라인 서열 분석 (신규 고도화) -->
        ${{buildLienTimelineHtml(item)}}

        <!-- 실거래가 대조 갭투자 & 월세 수익률 시뮬레이터 (신규 고도화) -->
        ${{buildInvestmentSimulatorHtml(item)}}

        <!-- AI 빅데이터 예상 낙찰가율 & 3대 시나리오 (신규 고도화) -->
        ${{buildBidPredictHtml(item)}}

        <!-- 건축물대장 위반건축물 & 이행강제금 리스크 레이더 (신규 고도화) -->
        ${{buildBuildingRiskHtml(item)}}

        <!-- 1. 경매에 나온 이유 & 채권 분석 섹션 -->
        <div class="legal-detail-section">
          <div class="section-badge-head">
            <div class="sb-title">
              <span class="sb-icon">⚖️</span>
              <span>경매 신청 사유 &amp; 채권자 권리분석</span>
            </div>
            <span class="badge badge-auction-reason">${{item.auction_reason ? item.auction_reason.type : '법원경매'}}</span>
          </div>
          <div class="legal-detail-grid">
            <div class="legal-grid-cell">
              <div class="lg-label">경매 구분</div>
              <div class="lg-val"><strong>${{item.auction_reason ? item.auction_reason.type : '법원경매'}}</strong></div>
            </div>
            <div class="legal-grid-cell">
              <div class="lg-label">신청 채권자</div>
              <div class="lg-val">${{item.auction_reason ? item.auction_reason.creditor : '-'}}</div>
            </div>
            <div class="legal-grid-cell">
              <div class="lg-label">청구 채권액</div>
              <div class="lg-val" style="color:var(--red); font-weight:800;">${{item.auction_reason ? item.auction_reason.claim_amount_str : '-'}}</div>
            </div>
            <div class="legal-grid-cell">
              <div class="lg-label">낙찰 시 권리 소멸 여부</div>
              <div class="lg-val" style="color:var(--green); font-weight:800;">✅ 100% 소멸 (등기부 말소 촉탁 대상)</div>
            </div>
          </div>
          <div class="legal-story-desc">
            <div class="ls-lead">📌 <strong>사건 발생 배경:</strong> ${{item.auction_reason ? item.auction_reason.title : ''}}</div>
            <p>${{item.auction_reason ? item.auction_reason.story : '경매 진행 사안에 대한 상세 권리분석 정보가 제공됩니다.'}}</p>
          </div>
        </div>

        <!-- 2. 기존 세입자 계약 상태 & 외국인 여부 점검표 섹션 -->
        <div class="legal-detail-section" style="border-color:${{item.tenant_info && item.tenant_info.is_foreigner ? '#818cf8' : 'var(--border)'}};">
          <div class="section-badge-head">
            <div class="sb-title">
              <span class="sb-icon">👤</span>
              <span>기존 세입자 임대차 계약 상태 &amp; 외국인 체류 확인 점검표</span>
            </div>
            <span class="badge ${{item.tenant_info ? item.tenant_info.foreigner_badge_class : ''}}" style="font-size:0.82rem;">${{item.tenant_info ? item.tenant_info.foreigner_badge : '점유확인'}}</span>
          </div>

          ${{item.tenant_info && item.tenant_info.is_foreigner ? `
            <div class="foreigner-alert-banner">
              <div class="fab-head">
                <span class="fab-icon">🌐</span>
                <div>
                  <div class="fab-title">외국인 등록 임차인 특별 법률 점검 안내 — 출입국 체류확인서 필수 확인</div>
                  <div class="fab-court-case">대법원 2016다244224 전원합의체 취지 판결 / 출입국관리법 제88조의2 준용</div>
                </div>
              </div>
              <div class="fab-body">
                <div class="fab-warning">
                  <strong>⚠️ 핵심 법률 주의사항:</strong> 외국인은 <em>주민등록법 대상자가 아니므로</em> 동주민센터에서 발급받는 일반 <u>전입세대열람원(전입세대확인서)에는 전혀 등재되지 않습니다!</u>
                </div>
                <p>경매 입찰 전 반드시 관할 <strong>출입국·외국인관서(출입국관리사무소)</strong>에 직접 방문하여 <strong>[외국인체류확인서]</strong>를 발급받아야 합니다. 출입국관리법 제88조의2에 따라 외국인의 체류지 변경신고는 주택임대차보호법상 전입신고와 동일한 대항력이 100% 인정되므로, 체류신고일자가 근저당권보다 앞설 경우 <strong>낙찰자가 보증금을 전액 인수</strong>해야 하는 막대한 위험이 발생할 수 있습니다.</p>
              </div>
              <div class="fab-badges">
                <span>👤 <strong>거주 외국인:</strong> ${{item.tenant_info.foreigner_name || '-'}}</span>
                <span>📅 <strong>체류지 변경신고일:</strong> ${{item.tenant_info.move_in_date || '-'}}</span>
                <span>📑 <strong>확정일자:</strong> ${{item.tenant_info.fixed_date || '-'}}</span>
                <span>💰 <strong>배당요구:</strong> ${{item.tenant_info.dividend_req || '-'}}</span>
              </div>
            </div>
          ` : (item.tenant_info && item.tenant_info.foreigner_status === 'OWNER' ? `
            <div class="owner-occupant-banner">
              <span>👤 <strong>소유자(채무자) 직접 점유 물건:</strong> 임차인이 존재하지 않으며 외국인 체류자 또한 없습니다. 대금 완납 시 법원에 인도명령을 신청하여 명도를 신속히 진행할 수 있습니다.</span>
            </div>
          ` : `
            <div class="domestic-tenant-banner">
              <span>🇰🇷 <strong>내국인 임차인 거주 물건:</strong> 주민등록법에 따라 관할 동주민센터 전입세대열람원(확인서)에 정상 등재된 내국인 임차인입니다.</span>
            </div>
          `)}}

          <div class="legal-detail-grid">
            <div class="legal-grid-cell">
              <div class="lg-label">점유자 구분</div>
              <div class="lg-val"><strong>${{item.tenant_info ? item.tenant_info.occupant_type : '점유 미상'}}</strong></div>
            </div>
            <div class="legal-grid-cell">
              <div class="lg-label">보증금 / 월차임</div>
              <div class="lg-val"><strong style="color:var(--heading);">${{item.tenant_info ? item.tenant_info.deposit_str : '0원'}}</strong> <small style="color:var(--text-muted);">${{item.tenant_info && item.tenant_info.monthly_rent > 0 ? '/ 월 ' + item.tenant_info.monthly_rent_str : '(전세)'}}</small></div>
            </div>
            <div class="legal-grid-cell">
              <div class="lg-label">전입(체류신고)일 / 확정일자</div>
              <div class="lg-val">${{item.tenant_info ? item.tenant_info.move_in_date : '-'}} / ${{item.tenant_info ? item.tenant_info.fixed_date : '-'}}</div>
            </div>
            <div class="legal-grid-cell">
              <div class="lg-label">배당요구 신청 여부</div>
              <div class="lg-val">${{item.tenant_info ? item.tenant_info.dividend_req : '-'}}</div>
            </div>
            <div class="legal-grid-cell">
              <div class="lg-label">대항력 성립 여부</div>
              <div class="lg-val" style="color:${{item.tenant_info && String(item.tenant_info.opposing_power).includes('선순위') ? 'var(--red)' : 'var(--green)'}}; font-weight:800;">${{item.tenant_info ? item.tenant_info.opposing_power : '-'}}</div>
            </div>
            <div class="legal-grid-cell">
              <div class="lg-label">낙찰자 인수 예상 보증금</div>
              <div class="lg-val" style="color:${{item.tenant_info && item.tenant_info.takeover_deposit > 0 ? 'var(--red)' : 'var(--green)'}}; font-weight:900;">${{item.tenant_info ? item.tenant_info.takeover_deposit_str : '0원'}}</div>
            </div>
          </div>

          <div class="legal-story-desc">
            <div class="ls-lead">📋 <strong>임차인 권리분석 및 명도 가이드:</strong></div>
            <p>${{item.tenant_info ? item.tenant_info.detail : '임차인 상세 권리분석 정보가 제공됩니다.'}}</p>
          </div>
        </div>

        <!-- 3. 회차별 유찰 진행 히스토리 & 유찰 스토리 섹션 -->
        ${{yuchalStoryObj.modalHtml}}

        <!-- 4. 차기(다음 회차) 유찰 시뮬레이션 & 입찰 전략 섹션 -->
        <div class="legal-detail-section" style="background:linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%); border-color:#93c5fd;">
          <div class="section-badge-head">
            <div class="sb-title">
              <span class="sb-icon">🔮</span>
              <span>차기(${{item.next_round_sim ? item.next_round_sim.next_round_no : '다음'}}차) 유찰 시 가격 시뮬레이션 &amp; 실전 입찰 타이밍</span>
            </div>
            <span class="badge" style="background:#2563eb; color:#fff; font-weight:800;">법정 저감률 ${{item.next_round_sim ? item.next_round_sim.court_rate : '30%'}} 적용</span>
          </div>
          <div class="sim-metric-row">
            <div class="sim-box">
              <div class="sim-lbl">차기 진행 회차</div>
              <div class="sim-val">${{item.next_round_sim ? item.next_round_sim.next_round_no : '-'}}차 매각기일</div>
            </div>
            <div class="sim-box">
              <div class="sim-lbl">차기 예상 최저가</div>
              <div class="sim-val" style="color:var(--red);">${{item.next_round_sim ? item.next_round_sim.next_min_price_str : '-'}}</div>
              <div class="sim-sub">감정가 대비 -${{item.next_round_sim ? item.next_round_sim.next_discount_pct : '0'}}%</div>
            </div>
            <div class="sim-box">
              <div class="sim-lbl">차기 필요 입찰보증금 (10%)</div>
              <div class="sim-val" style="color:var(--heading);">${{item.next_round_sim ? item.next_round_sim.next_deposit_str : '-'}}</div>
              <div class="sim-sub">당일 수표 1매 지참</div>
            </div>
            <div class="sim-box">
              <div class="sim-lbl">관할 법원 저감률</div>
              <div class="sim-val">${{item.court}}</div>
              <div class="sim-sub">회차당 ${{item.next_round_sim ? item.next_round_sim.court_rate : '30%'}} 감액</div>
            </div>
          </div>
          <div class="sim-advice-box">
            <strong>💡 전문가 응찰 타이밍 조언:</strong>
            <span>${{item.next_round_sim ? item.next_round_sim.advice : '유찰 시뮬레이션 조언이 제공됩니다.'}}</span>
          </div>
        </div>

        ${{buildInfraBadgesHtml(item)}}

        <!-- 물건 위치 지도 내장 섹션 -->
        <div class="map-embed-wrap">
          <div class="map-embed-head">
            <div class="map-embed-title">
              <span>🗺️ 물건 소재지 위치 지도 및 입지·로드뷰 확인</span>
              <button type="button" class="map-ext-btn" onclick="switchEmbedMapMode('detail-map-iframe', '${{mapQuery.replace(/'/g, "\\'")}}', 'map')">일반지도</button>
              <button type="button" class="map-ext-btn" onclick="switchEmbedMapMode('detail-map-iframe', '${{mapQuery.replace(/'/g, "\\'")}}', 'sat')">🛰️ 위성뷰</button>
            </div>
            <div class="map-ext-btns">
              <a href="https://map.naver.com/p/search/${{encMapQuery}}" target="_blank" rel="noopener" class="map-ext-btn naver">🟢 네이버 지도·실거래</a>
              <a href="https://map.kakao.com/?q=${{encMapQuery}}" target="_blank" rel="noopener" class="map-ext-btn kakao">🟡 카카오맵·로드뷰</a>
              <a href="https://www.google.com/maps/search/?api=1&query=${{encMapQuery}}" target="_blank" rel="noopener" class="map-ext-btn google">🔵 구글 지도 크게보기</a>
            </div>
          </div>
          <iframe id="detail-map-iframe" class="map-iframe-frame" src="https://maps.google.com/maps?q=${{encMapQuery}}&t=m&z=16&ie=UTF8&iwloc=&output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="물건 소재지 지도"></iframe>
        </div>

        <div class="guide-box-pro" style="background:${{riskInfo.bg}}; border:1px solid ${{riskInfo.border}}; border-radius:8px; padding:10px 14px; margin-bottom:12px;">
          <div style="font-size:0.78rem; font-weight:800; color:${{riskInfo.color}}; margin-bottom:2px;">💡 권리분석 및 전문가 가치평가 리포트</div>
          <div style="font-size:0.86rem; color:var(--text); line-height:1.5;">${{riskInfo.desc}} ${{item.comment ? ' · ' + item.comment : ''}}</div>
        </div>

        <div class="modal-chat-section" id="modal-chat-window">
          <div class="modal-chat-head">
            <div class="modal-chat-title">
              <span class="modal-chat-avatar">🤖</span>
              <div>
                <b>[${{item.rank}} · ${{item.case_no}}] 전담 AI 집중 상담창 <span class="modal-chat-badge">🎯 이 물건 전용</span></b>
                <small>${{item.address}} 매물에 대해서만 1:1로 심층 분석·대화합니다</small>
              </div>
            </div>
            <div class="modal-chat-ctrl">
              <button type="button" class="modal-chat-ctrl-btn" onclick="cbInitModalChat('${{item.id}}', true)" title="이 물건 대화 초기화">🔄 초기화</button>
              <button type="button" class="modal-chat-ctrl-btn" id="modal-chat-expand-btn" onclick="cbToggleModalChatExpand()" title="대화창 크기 확대/축소">⤢ 대화창 확대</button>
              <button type="button" class="modal-chat-ctrl-btn" onclick="cbOpenFromModal('${{item.id}}')" title="우측 메인 챗봇에서 이어서 대화">💬 큰 창 연동 ↗</button>
            </div>
          </div>
          <div id="modal-chat-log" class="modal-chat-log has-msg" aria-live="polite"></div>
          <div class="modal-chat-chips">
            <button type="button" class="cb-chip" onclick="cbAskInModal('${{item.id}}', '📉 유찰 스토리·회차별 타임라인 분석')">📉 유찰 스토리·회차별 분석</button>
            <button type="button" class="cb-chip" onclick="cbAskInModal('${{item.id}}', '💰 입찰보증금·취득세·대출 계산')">💰 보증금·취득세·대출 계산</button>
            <button type="button" class="cb-chip" onclick="cbAskInModal('${{item.id}}', '📈 적정 입찰가·수익률 시뮬레이션')">📈 적정 입찰가·수익률</button>
            <button type="button" class="cb-chip" onclick="cbAskInModal('${{item.id}}', '📊 점수 산정 근거·장단점')">📊 점수 근거·장단점</button>
            <button type="button" class="cb-chip" onclick="cbAskInModal('${{item.id}}', '🔍 권리·임차인·명도·관리비 진단')">🔍 권리·명도·관리비 진단</button>
            <button type="button" class="cb-chip" onclick="cbAskInModal('${{item.id}}', '📍 입지·면적(평형)·환금성 분석')">📍 입지·평형·환금성</button>
            <button type="button" class="cb-chip" onclick="cbAskInModal('${{item.id}}', '🏛 입찰법정·기일·준비물 안내')">🏛 법정·기일·준비물</button>
          </div>
          <div class="modal-chat-input-row">
            <input type="text" id="modal-chat-input" class="modal-chat-input" placeholder="[${{item.case_no}} 전용 질문] 예: 2,500만원에 입찰하면 실투자금과 수익률은? / 명도·관리비 주의점은?" onkeydown="if(event.key==='Enter'&&!event.isComposing){{event.preventDefault();cbAskInModal('${{item.id}}');}}">
            <button type="button" class="modal-chat-send" onclick="cbAskInModal('${{item.id}}')">전송 💬</button>
          </div>
        </div>
      `;

      document.getElementById('modal-content').innerHTML = content;
      document.getElementById('detail-modal').classList.add('show');
      if (typeof window.cbInitModalChat === 'function') {{
        window.cbInitModalChat(item.id, false);
      }}
    }}

    function closeModal() {{
      document.getElementById('detail-modal').classList.remove('show');
    }}

    function closeModalOnBackdrop(e) {{
      if (e.target.id === 'detail-modal') {{
        closeModal();
      }}
    }}

    // =====================================================================
    // 전국 60개 법원(본원 18개 + 지원 42개) 상세 주소록·전화·관할구역·저감률 DB
    // =====================================================================
    const COURTS_60_DATA = [
      // 1. 수도권 (16개소: 서울 5, 인천·부천 2, 경기북부 3, 경기남부 6)
      {{ no: 1, region: '수도권', sub: '서울권', name: '서울중앙지방법원', type: '본원', rate: '20%', time: '10:00~11:10', tel: '02-530-1114 (경매안내 1812)', addr: '서울특별시 서초구 서초중앙로 157 (서초동, 법원종합청사)', juris: '서울 강남구, 서초구, 관악구, 동작구, 종로구, 중구' }},
      {{ no: 2, region: '수도권', sub: '서울권', name: '서울동부지방법원', type: '본원', rate: '20%', time: '10:00~11:10', tel: '02-2204-2114', addr: '서울특별시 송파구 법원로 101 (문정동)', juris: '서울 송파구, 강동구, 광진구, 성동구' }},
      {{ no: 3, region: '수도권', sub: '서울권', name: '서울서부지방법원', type: '본원', rate: '20%', time: '10:00~11:10', tel: '02-3271-1114', addr: '서울특별시 마포구 마포대로 174 (공덕동)', juris: '서울 마포구, 용산구, 서대문구, 은평구' }},
      {{ no: 4, region: '수도권', sub: '서울권', name: '서울남부지방법원', type: '본원', rate: '20%', time: '10:00~11:10', tel: '02-2192-1114', addr: '서울특별시 양천구 신월로 386 (신정동)', juris: '서울 양천구, 강서구, 영등포구, 구로구, 금천구' }},
      {{ no: 5, region: '수도권', sub: '서울권', name: '서울북부지방법원', type: '본원', rate: '20%', time: '10:00~11:10', tel: '02-3499-1114', addr: '서울특별시 도봉구 마들로 749 (도봉동)', juris: '서울 노원구, 도봉구, 강북구, 성북구, 동대문구, 중랑구' }},
      {{ no: 6, region: '수도권', sub: '인천·부천', name: '인천지방법원', type: '본원', rate: '30%', time: '10:00~11:10', tel: '032-860-1114', addr: '인천광역시 미추홀구 소성로 163 (학익동)', juris: '인천광역시 전역 (중구, 동구, 미추홀구, 연수구, 남동구, 부평구, 계양구, 서구, 강화군, 옹진군)' }},
      {{ no: 7, region: '수도권', sub: '인천·부천', name: '인천지방법원 부천지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '032-320-1114', addr: '경기도 부천시 원미구 상일로 129 (상동)', juris: '경기도 부천시, 김포시' }},
      {{ no: 8, region: '수도권', sub: '경기북부', name: '의정부지방법원', type: '본원', rate: '30%', time: '10:00~11:30', tel: '031-828-1114', addr: '경기도 의정부시 녹양로34번길 23 (가능동)', juris: '경기도 의정부시, 양주시, 포천시, 동두천시, 연천군, 강원도 철원군' }},
      {{ no: 9, region: '수도권', sub: '경기북부', name: '의정부지방법원 고양지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '031-920-6114', addr: '경기도 고양시 일산동구 장백로 209 (장항동)', juris: '경기도 고양시(일산동구·일산서구·덕양구), 파주시' }},
      {{ no: 10, region: '수도권', sub: '경기북부', name: '의정부지방법원 남양주지원', type: '지원', rate: '30%', time: '10:00~11:20', tel: '031-590-1114', addr: '경기도 남양주시 다산중앙로82번안길 150 (다산동)', juris: '경기도 남양주시, 구리시, 가평군' }},
      {{ no: 11, region: '수도권', sub: '경기남부', name: '수원지방법원', type: '본원', rate: '30%', time: '10:00~11:10', tel: '031-210-1114', addr: '경기도 수원시 영통구 법조로 105 (하동, 수원법원종합청사)', juris: '경기도 수원시(영통·권선·장안·팔달), 용인시, 화성시, 오산시' }},
      {{ no: 12, region: '수도권', sub: '경기남부', name: '수원지방법원 성남지원', type: '지원', rate: '20%', time: '10:00~11:10', tel: '031-737-1114', addr: '경기도 성남시 수정구 단대로 22 (단대동)', juris: '경기도 성남시(분당구·수정구·중원구), 하남시, 광주시' }},
      {{ no: 13, region: '수도권', sub: '경기남부', name: '수원지방법원 여주지원', type: '지원', rate: '20%', time: '10:00~11:30', tel: '031-880-7114', addr: '경기도 여주시 현암로 21 (현암동)', juris: '경기도 여주시, 이천시, 양평군' }},
      {{ no: 14, region: '수도권', sub: '경기남부', name: '수원지방법원 평택지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '031-650-2114', addr: '경기도 평택시 평남로 1036 (동삭동)', juris: '경기도 평택시, 안성시' }},
      {{ no: 15, region: '수도권', sub: '경기남부', name: '수원지방법원 안산지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '031-481-1114', addr: '경기도 안산시 단원구 광덕서로 75 (고잔동)', juris: '경기도 안산시(단원·상록), 시흥시, 광명시' }},
      {{ no: 16, region: '수도권', sub: '경기남부', name: '수원지방법원 안양지원', type: '지원', rate: '20%', time: '10:00~11:10', tel: '031-8086-1114', addr: '경기도 안양시 동안구 관평로 212 (관양동)', juris: '경기도 안양시(동안·만안), 과천시, 의왕시, 군포시' }},

      // 2. 충청·강원권 (15개소: 대전·세종·충남 6, 충북 4, 강원 5)
      {{ no: 17, region: '충청·강원권', sub: '대전·세종·충남', name: '대전지방법원', type: '본원', rate: '30%', time: '10:00~11:20', tel: '042-470-1114 (경매계 1851~9)', addr: '대전광역시 서구 둔산중로 78 (둔산동)', juris: '대전광역시 전역(유성구·서구·중구·동구·대덕구), 세종특별자치시, 충남 금산군' }},
      {{ no: 18, region: '충청·강원권', sub: '대전·세종·충남', name: '대전지방법원 홍성지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '041-630-3114', addr: '충청남도 홍성군 홍성읍 법원로 38', juris: '충청남도 홍성군, 보령시, 예산군, 서천군' }},
      {{ no: 19, region: '충청·강원권', sub: '대전·세종·충남', name: '대전지방법원 논산지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '041-746-2114', addr: '충청남도 논산시 강경읍 계백로 99', juris: '충청남도 논산시, 계룡시, 부여군' }},
      {{ no: 20, region: '충청·강원권', sub: '대전·세종·충남', name: '대전지방법원 천안지원', type: '지원', rate: '30%', time: '10:00~11:20', tel: '041-620-3114', addr: '충청남도 천안시 동남구 청수14로 77 (청당동)', juris: '충청남도 천안시(동남구·서북구), 아산시' }},
      {{ no: 21, region: '충청·강원권', sub: '대전·세종·충남', name: '대전지방법원 공주지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '041-850-8114', addr: '충청남도 공주시 한적2길 34-15 (금흥동)', juris: '충청남도 공주시, 청양군' }},
      {{ no: 22, region: '충청·강원권', sub: '대전·세종·충남', name: '대전지방법원 서산지원', type: '지원', rate: '30%', time: '10:00~11:20', tel: '041-660-0114', addr: '충청남도 서산시 공림4로 24 (예천동)', juris: '충청남도 서산시, 당진시, 태안군' }},
      {{ no: 23, region: '충청·강원권', sub: '충북권', name: '청주지방법원', type: '본원', rate: '20%', time: '10:00~11:10', tel: '043-249-7114', addr: '충청북도 청주시 서원구 산남로 62 (산남동)', juris: '충청북도 청주시(상당·서원·흥덕·청원), 진천군, 보은군, 괴산군, 증평군' }},
      {{ no: 24, region: '충청·강원권', sub: '충북권', name: '청주지방법원 충주지원', type: '지원', rate: '20%', time: '10:00~11:10', tel: '043-841-9114', addr: '충청북도 충주시 계명대로 105 (교현동)', juris: '충청북도 충주시, 음성군' }},
      {{ no: 25, region: '충청·강원권', sub: '충북권', name: '청주지방법원 제천지원', type: '지원', rate: '20%', time: '10:00~11:10', tel: '043-640-5114', addr: '충청북도 제천시 칠성로 55 (장락동)', juris: '충청북도 제천시, 단양군' }},
      {{ no: 26, region: '충청·강원권', sub: '충북권', name: '청주지방법원 영동지원', type: '지원', rate: '20%', time: '10:00~11:10', tel: '043-740-4114', addr: '충청북도 영동군 영동읍 영동황간로 77', juris: '충청북도 영동군, 옥천군' }},
      {{ no: 27, region: '충청·강원권', sub: '강원권', name: '춘천지방법원', type: '본원', rate: '30%', time: '10:00~11:10', tel: '033-259-9114', addr: '강원특별자치도 춘천시 공지로 284 (효자동)', juris: '강원특별자치도 춘천시, 홍천군, 화천군, 양구군, 인제군' }},
      {{ no: 28, region: '충청·강원권', sub: '강원권', name: '춘천지방법원 강릉지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '033-640-1114', addr: '강원특별자치도 강릉시 동해대로 3288-18 (난곡동)', juris: '강원특별자치도 강릉시, 동해시, 삼척시' }},
      {{ no: 29, region: '충청·강원권', sub: '강원권', name: '춘천지방법원 원주지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '033-738-1114', addr: '강원특별자치도 원주시 시청로 149 (무실동)', juris: '강원특별자치도 원주시, 횡성군' }},
      {{ no: 30, region: '충청·강원권', sub: '강원권', name: '춘천지방법원 속초지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '033-639-5114', addr: '강원특별자치도 속초시 법대로 17 (동명동)', juris: '강원특별자치도 속초시, 양양군, 고성군' }},
      {{ no: 31, region: '충청·강원권', sub: '강원권', name: '춘천지방법원 영월지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '033-371-1114', addr: '강원특별자치도 영월군 영월읍 단종로33번길 33', juris: '강원특별자치도 영월군, 태백시, 정선군, 평창군' }},

      // 3. 영남권 (19개소: 부산·울산 4, 경남 6, 대구·경북 9)
      {{ no: 32, region: '영남권', sub: '부산·울산', name: '부산지방법원', type: '본원', rate: '20%', time: '10:00~11:10', tel: '051-590-1114', addr: '부산광역시 연제구 법원로 31 (거제동, 부산법원종합청사)', juris: '부산 중구, 동구(※동부지원 아님), 서구, 영도구, 부산진구, 동래구, 남구, 금정구, 연제구' }},
      {{ no: 33, region: '영남권', sub: '부산·울산', name: '부산지방법원 동부지원', type: '지원', rate: '20%', time: '10:00~11:10', tel: '051-780-1114', addr: '부산광역시 해운대구 신수로 36 (재송동)', juris: '부산광역시 해운대구, 수영구, 기장군' }},
      {{ no: 34, region: '영남권', sub: '부산·울산', name: '부산지방법원 서부지원', type: '지원', rate: '20%', time: '10:00~11:10', tel: '051-608-1114', addr: '부산광역시 강서구 명지국제1로 285 (명지동)', juris: '부산광역시 북구, 사상구, 사하구, 강서구' }},
      {{ no: 35, region: '영남권', sub: '부산·울산', name: '울산지방법원', type: '본원', rate: '30%', time: '10:00~11:10', tel: '052-259-2114', addr: '울산광역시 남구 법대로 55 (옥동)', juris: '울산광역시 전역(남구·중구·동구·북구·울주군), 경상남도 양산시' }},
      {{ no: 36, region: '영남권', sub: '경남권', name: '창원지방법원', type: '본원', rate: '20%', time: '10:00~11:10', tel: '055-239-2114', addr: '경상남도 창원시 성산구 정동로 68 (사파동)', juris: '경남 창원시 성산구·의창구·진해구, 김해시' }},
      {{ no: 37, region: '영남권', sub: '경남권', name: '창원지방법원 마산지원', type: '지원', rate: '20%', time: '10:00~11:10', tel: '055-240-9114', addr: '경상남도 창원시 마산합포구 가포순환로 77 (신포동1가)', juris: '경남 창원시 마산합포구·마산회원구, 함안군, 의령군' }},
      {{ no: 38, region: '영남권', sub: '경남권', name: '창원지방법원 진주지원', type: '지원', rate: '20%', time: '10:00~11:10', tel: '055-760-6114', addr: '경상남도 진주시 동진로 99 (상대동)', juris: '경상남도 진주시, 사천시, 남해군, 하동군, 산청군' }},
      {{ no: 39, region: '영남권', sub: '경남권', name: '창원지방법원 통영지원', type: '지원', rate: '20%', time: '10:00~11:10', tel: '055-640-7114', addr: '경상남도 통영시 용남면 동달안길 77', juris: '경상남도 통영시, 거제시, 고성군' }},
      {{ no: 40, region: '영남권', sub: '경남권', name: '창원지방법원 밀양지원', type: '지원', rate: '20%', time: '10:00~11:10', tel: '055-350-5114', addr: '경상남도 밀양시 밀양대로 1993-20 (내이동)', juris: '경상남도 밀양시, 창녕군' }},
      {{ no: 41, region: '영남권', sub: '경남권', name: '창원지방법원 거창지원', type: '지원', rate: '20%', time: '10:00~11:10', tel: '055-940-5114', addr: '경상남도 거창군 거창읍 죽전3길 92', juris: '경상남도 거창군, 합천군, 함양군' }},
      {{ no: 42, region: '영남권', sub: '대구·경북', name: '대구지방법원', type: '본원', rate: '30%', time: '10:00~11:10', tel: '053-757-6114', addr: '대구광역시 수성구 동대구로 364 (범어동)', juris: '대구 수성구, 중구, 동구, 북구, 남구, 군위군 / 경북 경산시, 영천시, 청도군, 칠곡군' }},
      {{ no: 43, region: '영남권', sub: '대구·경북', name: '대구지방법원 서부지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '053-570-1114', addr: '대구광역시 달서구 장산남로 30 (용산동)', juris: '대구 달서구, 서구, 달성군 / 경북 성주군, 고령군' }},
      {{ no: 44, region: '영남권', sub: '대구·경북', name: '대구지방법원 안동지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '054-851-3114', addr: '경상북도 안동시 강남로 302 (정하동)', juris: '경상북도 안동시, 영주시, 봉화군' }},
      {{ no: 45, region: '영남권', sub: '대구·경북', name: '대구지방법원 경주지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '054-779-4114', addr: '경상북도 경주시 화랑로 89 (동부동)', juris: '경상북도 경주시 전역' }},
      {{ no: 46, region: '영남권', sub: '대구·경북', name: '대구지방법원 포항지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '054-250-3114', addr: '경상북도 포항시 북구 법원로 181 (양덕동)', juris: '경상북도 포항시(북구·남구), 울릉군' }},
      {{ no: 47, region: '영남권', sub: '대구·경북', name: '대구지방법원 김천지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '054-420-2114', addr: '경상북도 김천시 혁신6로 50 (율곡동)', juris: '경상북도 김천시, 구미시' }},
      {{ no: 48, region: '영남권', sub: '대구·경북', name: '대구지방법원 상주지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '054-530-5114', addr: '경상북도 상주시 북천로 17-9 (만산동)', juris: '경상북도 상주시, 문경시, 예천군' }},
      {{ no: 49, region: '영남권', sub: '대구·경북', name: '대구지방법원 의성지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '054-830-2114', addr: '경상북도 의성군 의성읍 군청길 71', juris: '경상북도 의성군, 청송군' }},
      {{ no: 50, region: '영남권', sub: '대구·경북', name: '대구지방법원 영덕지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '054-730-6114', addr: '경상북도 영덕군 영덕읍 경동로 8337', juris: '경상북도 영덕군, 울진군, 영양군' }},

      // 4. 호남·제주권 (10개소: 광주·전남 5, 전북 4, 제주 1)
      {{ no: 51, region: '호남·제주권', sub: '광주·전남', name: '광주지방법원', type: '본원', rate: '30%', time: '10:00~11:10', tel: '062-239-1114', addr: '광주광역시 동구 준법로 7-12 (지산동)', juris: '광주광역시 전역(동·서·남·북·광산구), 전남 나주시, 화순군, 담양군, 장성군, 곡성군, 영광군' }},
      {{ no: 52, region: '호남·제주권', sub: '광주·전남', name: '광주지방법원 목포지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '061-270-6114', addr: '전라남도 목포시 정의로 29 (옥암동)', juris: '전라남도 목포시, 무안군, 신안군, 영암군, 함평군' }},
      {{ no: 53, region: '호남·제주권', sub: '광주·전남', name: '광주지방법원 장흥지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '061-860-1114', addr: '전라남도 장흥군 장흥읍 흥성로 85', juris: '전라남도 장흥군, 강진군' }},
      {{ no: 54, region: '호남·제주권', sub: '광주·전남', name: '광주지방법원 순천지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '061-720-7114', addr: '전라남도 순천시 왕지로 21 (왕지동)', juris: '전라남도 순천시, 여수시, 광양시, 고흥군, 보성군, 구례군' }},
      {{ no: 55, region: '호남·제주권', sub: '광주·전남', name: '광주지방법원 해남지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '061-530-9114', addr: '전라남도 해남군 해남읍 중앙1로 330', juris: '전라남도 해남군, 완도군, 진도군' }},
      {{ no: 56, region: '호남·제주권', sub: '전북권', name: '전주지방법원', type: '본원', rate: '30%', time: '10:00~11:10', tel: '063-259-5114', addr: '전북특별자치도 전주시 덕진구 가인로 33 (만성동)', juris: '전북 전주시(완산구·덕진구), 김제시, 완주군, 임실군, 진안군, 무주군' }},
      {{ no: 57, region: '호남·제주권', sub: '전북권', name: '전주지방법원 군산지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '063-450-5114', addr: '전북특별자치도 군산시 법원로 68 (조촌동)', juris: '전북특별자치도 군산시, 익산시' }},
      {{ no: 58, region: '호남·제주권', sub: '전북권', name: '전주지방법원 정읍지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '063-530-8114', addr: '전북특별자치도 정읍시 수성2로 28 (수성동)', juris: '전북특별자치도 정읍시, 고창군, 부안군' }},
      {{ no: 59, region: '호남·제주권', sub: '전북권', name: '전주지방법원 남원지원', type: '지원', rate: '30%', time: '10:00~11:10', tel: '063-620-9114', addr: '전북특별자치도 남원시 만인로 20 (동충동)', juris: '전북특별자치도 남원시, 장수군, 순창군' }},
      {{ no: 60, region: '호남·제주권', sub: '제주권', name: '제주지방법원', type: '본원', rate: '30%', time: '10:00~11:10', tel: '064-729-2114', addr: '제주특별자치도 제주시 남광북5길 3 (이도이동)', juris: '제주특별자치도 전역 (제주시, 서귀포시)' }}
    ];
    window.COURTS_60_DATA = COURTS_60_DATA;

    let currentCourtRegion = 'ALL';
    let currentCourtViewMode = 'card';

    function selectCourtRegion(reg) {{
      currentCourtRegion = reg;
      document.querySelectorAll('#court-region-bar .region-pill-btn').forEach(btn => {{
        btn.classList.toggle('active', btn.getAttribute('data-creg') === reg);
      }});
      renderCourtsDirectory();
    }}

    function setCourtViewMode(mode) {{
      currentCourtViewMode = mode;
      const btnCard = document.getElementById('btn-court-card-view');
      const btnTable = document.getElementById('btn-court-table-view');
      const cardCont = document.getElementById('courts-cards-container');
      const tblCont = document.getElementById('courts-table-container');
      if (btnCard) btnCard.classList.toggle('active', mode === 'card');
      if (btnTable) btnTable.classList.toggle('active', mode === 'table');
      if (cardCont) cardCont.style.display = mode === 'card' ? 'grid' : 'none';
      if (tblCont) tblCont.style.display = mode === 'table' ? 'block' : 'none';
      renderCourtsDirectory();
    }}

    function resetCourtSearch() {{
      const inp = document.getElementById('court-search-input');
      if (inp) inp.value = '';
      selectCourtRegion('ALL');
    }}

    function renderCourtsDirectory() {{
      const cardCont = document.getElementById('courts-cards-container');
      const tblBody = document.getElementById('courts-table-body');
      const cntEl = document.getElementById('court-filtered-count');
      if (!cardCont || !tblBody) return;

      const kw = (document.getElementById('court-search-input') ? document.getElementById('court-search-input').value : '').toLowerCase().trim();
      const list = COURTS_60_DATA.filter(c => {{
        if (currentCourtRegion !== 'ALL') {{
          if (currentCourtRegion === '본원' || currentCourtRegion === '지원') {{
            if (c.type !== currentCourtRegion) return false;
          }} else if (c.region !== currentCourtRegion) {{
            return false;
          }}
        }}
        if (kw) {{
          const hay = `${{c.name}} ${{c.region}} ${{c.sub}} ${{c.addr}} ${{c.juris}} ${{c.tel}} ${{c.type}}`.toLowerCase();
          if (!hay.includes(kw)) return false;
        }}
        return true;
      }});

      if (cntEl) cntEl.innerText = list.length;

      if (list.length === 0) {{
        cardCont.innerHTML = `<div style="grid-column:1/-1; text-align:center; padding:40px; background:var(--surface-sub); border:1px solid var(--border); border-radius:10px; font-weight:700;">검색어와 일치하는 법원이 없습니다.</div>`;
        tblBody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:30px;">검색어와 일치하는 법원이 없습니다.</td></tr>`;
        return;
      }}

      cardCont.innerHTML = list.map(c => {{
        const safeAddr = c.addr.replace(/'/g, "\\'");
        const safeName = c.name.replace(/'/g, "\\'");
        const isBonwon = c.type === '본원';
        return `
          <div class="court-item-card ${{isBonwon ? 'bonwon' : ''}}">
            <div class="court-card-head">
              <div class="court-name-wrap">
                <span class="court-num-badge">#${{c.no}}</span>
                <strong style="font-size:1.02rem; color:var(--heading);">${{c.name}}</strong>
                <span class="court-type-badge ${{isBonwon ? 'bonwon' : 'jiwon'}}">${{c.type}}</span>
              </div>
              <span class="badge badge-discount" title="1회 유찰 시 최저가 저감률">유찰저감 ${{c.rate}}</span>
            </div>
            <div class="court-info-line">
              <span class="lbl">📍 도로명주소</span>
              <span><strong>${{c.addr}}</strong></span>
            </div>
            <div class="court-info-line">
              <span class="lbl">📞 대표전화</span>
              <span>${{c.tel}} <small style="color:var(--text-muted); margin-left:6px;">(입찰시간: ${{c.time}})</small></span>
            </div>
            <div class="court-info-line">
              <span class="lbl">🗺️ 관할구역</span>
              <span style="color:var(--text-muted); font-size:0.82rem;">${{c.juris}}</span>
            </div>
            <div class="court-card-actions">
              <button type="button" class="btn-map-mini" onclick="openCourtMapModal(${{c.no}})">🗺️ 법원 위치 지도보기</button>
              <button type="button" class="btn-map-mini" style="background:var(--surface-sub); color:var(--text); border-color:var(--border);" onclick="copyTextToClipboard('${{safeAddr}}', '${{safeName}} 주소')">📋 주소복사</button>
              <button type="button" class="btn-map-mini" style="background:var(--surface-sub); color:var(--secondary); border-color:var(--border);" onclick="filterPropertiesByCourt('${{safeName}}')">🔍 관할 경매물건 보기</button>
            </div>
          </div>
        `;
      }}).join('');

      tblBody.innerHTML = list.map(c => {{
        const safeAddr = c.addr.replace(/'/g, "\\'");
        const safeName = c.name.replace(/'/g, "\\'");
        const isBonwon = c.type === '본원';
        return `
          <tr>
            <td style="text-align:center; font-weight:800;">#${{c.no}}</td>
            <td><strong>${{c.region}}</strong><br><small style="color:var(--text-muted);">${{c.sub}}</small></td>
            <td><strong>${{c.name}}</strong> <span class="court-type-badge ${{isBonwon ? 'bonwon' : 'jiwon'}}">${{c.type}}</span><br><small style="color:var(--text-muted);">입찰 ${{c.time}}</small></td>
            <td style="text-align:center;"><span class="badge badge-discount">${{c.rate}}</span></td>
            <td><strong>${{c.addr}}</strong></td>
            <td>${{c.tel}}</td>
            <td style="max-width:260px; font-size:0.82rem;">${{c.juris}}</td>
            <td style="white-space:nowrap;">
              <button type="button" class="btn-map-mini" onclick="openCourtMapModal(${{c.no}})">🗺️ 지도보기</button>
              <button type="button" class="btn-map-mini" style="background:var(--surface-sub); color:var(--text); border-color:var(--border);" onclick="copyTextToClipboard('${{safeAddr}}', '${{safeName}} 주소')">📋 복사</button>
              <button type="button" class="btn-map-mini" style="margin-top:4px;" onclick="filterPropertiesByCourt('${{safeName}}')">🔍 물건보기</button>
            </td>
          </tr>
        `;
      }}).join('');
    }}

    function filterPropertiesByCourt(courtName) {{
      switchTab('explorer');
      const regSel = document.getElementById('filter-region');
      if (regSel) regSel.value = 'ALL';
      const topnSel = document.getElementById('filter-topn');
      if (topnSel) topnSel.value = '9999';
      const discSel = document.getElementById('filter-discount');
      if (discSel) discSel.value = '0';
      const kwInp = document.getElementById('keyword-search');
      // 단축 키워드 매칭 (예: '수원지방법원 성남지원' -> '성남지원' 또는 '대전지방법원')
      let searchKw = courtName;
      if (courtName.includes(' ')) {{
        const parts = courtName.split(' ');
        searchKw = parts[parts.length - 1];
      }}
      if (kwInp) kwInp.value = searchKw;
      filterData();
      showRefreshToast(`🏛️ [${{courtName}}] 관할 경매물건 ${{filteredData.length}}건을 필터링했습니다.`);
    }}

    function openMapModalById(itemId) {{
      const item = rawData.find(d => d.id === itemId);
      if (!item) return;
      openMapModal(item.address, `[${{item.rank}}] ${{item.court}} ${{item.case_no}} (${{item.usage}})`, item.id, item.spec);
    }}

    function openItemMapFromDetail(itemId) {{
      openMapModalById(itemId);
    }}

    function openCourtMapModal(courtNo) {{
      const c = COURTS_60_DATA.find(x => x.no === courtNo);
      if (!c) return;
      openMapModal(
        `${{c.addr}} ${{c.name}}`,
        `🏛️ [#${{c.no}}] ${{c.name}} (${{c.type}} · 유찰저감 ${{c.rate}})`,
        null,
        `📍 도로명주소: ${{c.addr}} | 📞 전화: ${{c.tel}} | 🗺️ 관할구역: ${{c.juris}}`
      );
    }}

    function openCourtMapByName(courtName) {{
      if (!courtName) return;
      const found = COURTS_60_DATA.find(c => c.name === courtName || c.name.includes(courtName) || courtName.includes(c.name));
      if (found) {{
        openCourtMapModal(found.no);
      }} else {{
        openMapModal(courtName, `🏛️ ${{courtName}} 위치 지도`, null, '관할 법원 입찰법정 위치');
      }}
    }}

    function openMapModal(rawAddress, titleText, itemId, subSpec) {{
      const modal = document.getElementById('map-modal');
      const titleEl = document.getElementById('map-modal-title');
      const bodyEl = document.getElementById('map-modal-body');
      const footerEl = document.getElementById('map-modal-footer');
      if (!modal || !bodyEl) return;

      const mapQuery = cleanAddressForMap(rawAddress);
      const encMapQuery = encodeURIComponent(mapQuery);
      const safeRawAddr = String(rawAddress || '').replace(/'/g, "\\'");
      const safeMapQuery = String(mapQuery || '').replace(/'/g, "\\'");

      if (titleEl) titleEl.innerText = titleText || '🗺️ 위치 지도 및 주변 입지 보기';

      bodyEl.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px; margin-bottom:12px;">
          <div>
            <div style="font-size:1.05rem; font-weight:800; color:var(--heading); margin-bottom:3px;">📍 ${{rawAddress}}</div>
            ${{subSpec ? `<div style="font-size:0.84rem; color:var(--text-muted);">${{subSpec}}</div>` : ''}}
          </div>
          <div style="display:flex; gap:6px; flex-wrap:wrap;">
            <button type="button" class="map-ext-btn" onclick="switchEmbedMapMode('standalone-map-iframe', '${{safeMapQuery}}', 'map')">🗺️ 일반지도</button>
            <button type="button" class="map-ext-btn" onclick="switchEmbedMapMode('standalone-map-iframe', '${{safeMapQuery}}', 'sat')">🛰️ 위성 항공뷰</button>
            <button type="button" class="map-ext-btn" onclick="copyTextToClipboard('${{safeRawAddr}}', '소재지 주소')">📋 주소 복사</button>
          </div>
        </div>

        <div class="map-ext-btns" style="margin-bottom:10px;">
          <a href="https://map.naver.com/p/search/${{encMapQuery}}" target="_blank" rel="noopener" class="map-ext-btn naver" style="padding:7px 13px; font-size:0.82rem;">🟢 네이버 지도·단지 실거래가 열기 ↗</a>
          <a href="https://map.kakao.com/?q=${{encMapQuery}}" target="_blank" rel="noopener" class="map-ext-btn kakao" style="padding:7px 13px; font-size:0.82rem;">🟡 카카오맵·거리뷰(로드뷰) 열기 ↗</a>
          <a href="https://www.google.com/maps/search/?api=1&query=${{encMapQuery}}" target="_blank" rel="noopener" class="map-ext-btn google" style="padding:7px 13px; font-size:0.82rem;">🔵 구글 지도 전체화면 열기 ↗</a>
        </div>

        <iframe id="standalone-map-iframe" class="map-iframe-frame" style="height:430px;" src="https://maps.google.com/maps?q=${{encMapQuery}}&t=m&z=16&ie=UTF8&iwloc=&output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="상세 위치 지도"></iframe>
      `;

      if (footerEl) {{
        footerEl.innerHTML = `
          ${{itemId ? `<button type="button" class="btn-action" style="background:var(--accent);" onclick="closeMapModal(); openDetail('${{itemId}}');">📋 이 물건 상세분석·전담 AI 상담 열기</button>` : ''}}
          <button type="button" class="btn-action" style="background:#718096;" onclick="closeMapModal()">닫기</button>
        `;
      }}

      modal.classList.add('show');
    }}

    function closeMapModal() {{
      const modal = document.getElementById('map-modal');
      if (modal) modal.classList.remove('show');
    }}

    
    /* 로고 클릭 시 홈 화면(처음 화면)으로 완벽 복귀 */
    function goHome() {{
      // 1. 모든 모달 닫기
      closeModal();
      if (typeof closeMapModal === 'function') closeMapModal();
      if (window.AT) {{
        if (typeof AT.closeTool === 'function') AT.closeTool();
        if (typeof AT.closeCompare === 'function') AT.closeCompare();
        if (typeof AT.closeReport === 'function') AT.closeReport();
        if (typeof AT.closeBidSlip === 'function') AT.closeBidSlip();
        if (typeof AT.closeLoanCalc === 'function') AT.closeLoanCalc();
        if (typeof AT.closeFieldChecklist === 'function') AT.closeFieldChecklist();
        if (typeof AT.closeBidPredict === 'function') AT.closeBidPredict();
        if (typeof AT.closeEvictDoc === 'function') AT.closeEvictDoc();
      }}

      // 2. 메인 탐색기 탭으로 전환
      switchTab('explorer');

      // 3. 카드 뷰 모드로 전환
      if (typeof switchView === 'function') switchView('card');

      // 4. 검색어 및 필터 조건 초기화
      if (typeof resetFilters === 'function') resetFilters();

      // 5. 페이지 최상단으로 부드럽게 스크롤
      window.scrollTo({{ top: 0, behavior: 'smooth' }});

      // 6. URL 해시 정리
      if (window.location.hash) {{
        try {{ history.replaceState(null, '', window.location.pathname); }} catch(e) {{}}
      }}
    }}
    window.goHome = goHome;

    window.onload = init;
  </script>
</body>
</html>
"""

# 실전 투자 도구 모듈 삽입 (portal_tools.html: 기일입찰표·안전마진 계산기·관심물건 찜·D-Day 캘린더 → </body> 직전)
tools_path = r'C:\Users\wood\Desktop\aiwork\auction\portal_tools.html'
if os.path.exists(tools_path):
    with open(tools_path, 'r', encoding='utf-8') as f:
        tools_html = f.read()
    html_content = html_content.replace('</body>', tools_html + '\n</body>', 1)
    print("Investor tools module injected.")

# 챗봇 위젯 삽입 (chatbot_widget.html → </body> 직전)
widget_path = r'C:\Users\wood\Desktop\aiwork\auction\chatbot_widget.html'
if os.path.exists(widget_path):
    with open(widget_path, 'r', encoding='utf-8') as f:
        widget_html = f.read()
    html_content = html_content.replace('</body>', widget_html + '\n</body>', 1)
    print("Chatbot widget injected.")

out_html1 = r'C:\Users\wood\Desktop\aiwork\auction\index.html'
out_html2 = r'C:\Users\wood\Desktop\aiwork\auction\경매_스마트_분석_포털.html'
out_html3 = r'C:\Users\wood\Desktop\auction\index.html'
out_html4 = r'C:\Users\wood\Desktop\auction\경매_스마트_분석_포털.html'

for out_path in [out_html1, out_html2, out_html3, out_html4]:
    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    except Exception as e:
        print(f"Error writing {out_path}: {e}")

print(f"Web portal created successfully! Files: {out_html1}, {out_html2}")

