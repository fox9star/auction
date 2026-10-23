import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import requests

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\wood\Desktop\aiwork\auction"
MIRROR_DIR = r"c:\Users\wood\Desktop\auction"
PORTAL_JSON_PATH = os.path.join(BASE_DIR, "portal_data.json")
COURT_API_URL = "https://www.courtauction.go.kr/pgj/pgjsearch/searchControllerMain.on"

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json; charset=UTF-8",
    "Referer": "https://www.courtauction.go.kr/pgj/index.on"
})

SIDO_CODES = {
    "서울": ("11", "서울특별시", "수도권"),
    "서울특별시": ("11", "서울특별시", "수도권"),
    "경기": ("41", "경기도", "수도권"),
    "경기도": ("41", "경기도", "수도권"),
    "인천": ("28", "인천광역시", "수도권"),
    "인천광역시": ("28", "인천광역시", "수도권"),
    "부산": ("26", "부산광역시", "영남권(부울경)"),
    "부산광역시": ("26", "부산광역시", "영남권(부울경)"),
    "울산": ("31", "울산광역시", "영남권(부울경)"),
    "울산광역시": ("31", "울산광역시", "영남권(부울경)"),
    "경남": ("48", "경상남도", "영남권(부울경)"),
    "경상남도": ("48", "경상남도", "영남권(부울경)"),
    "대구": ("27", "대구광역시", "영남권(대경권)"),
    "대구광역시": ("27", "대구광역시", "영남권(대경권)"),
    "경북": ("47", "경상북도", "영남권(대경권)"),
    "경상북도": ("47", "경상북도", "영남권(대경권)"),
    "대전": ("30", "대전광역시", "충청권"),
    "대전광역시": ("30", "대전광역시", "충청권"),
    "세종": ("36", "세종특별자치시", "충청권"),
    "세종특별자치시": ("36", "세종특별자치시", "충청권"),
    "충남": ("44", "충청남도", "충청권"),
    "충청남도": ("44", "충청남도", "충청권"),
    "충북": ("43", "충청북도", "충청권"),
    "충청북도": ("43", "충청북도", "충청권"),
    "광주": ("29", "광주광역시", "호남권"),
    "광주광역시": ("29", "광주광역시", "호남권"),
    "전남": ("46", "전라남도", "호남권"),
    "전라남도": ("46", "전라남도", "호남권"),
    "전북": ("52", "전북특별자치도", "호남권"),
    "전북특별자치도": ("52", "전북특별자치도", "호남권"),
    "강원": ("51", "강원특별자치도", "강원·제주권"),
    "강원특별자치도": ("51", "강원특별자치도", "강원·제주권"),
    "제주": ("50", "제주특별자치도", "강원·제주권"),
    "제주특별자치도": ("50", "제주특별자치도", "강원·제주권"),
}

REGION_SIDOS = {
    "대전광역시": [("30", "대전광역시", "충청권")],
    "수도권": [("11", "서울특별시", "수도권"), ("41", "경기도", "수도권"), ("28", "인천광역시", "수도권")],
    "영남권": [("26", "부산광역시", "영남권(부울경)"), ("27", "대구광역시", "영남권(대경권)"), ("48", "경상남도", "영남권(부울경)"), ("47", "경상북도", "영남권(대경권)"), ("31", "울산광역시", "영남권(부울경)")],
    "충청권": [("30", "대전광역시", "충청권"), ("44", "충청남도", "충청권"), ("43", "충청북도", "충청권"), ("36", "세종특별자치시", "충청권")],
    "호남권": [("29", "광주광역시", "호남권"), ("46", "전라남도", "호남권"), ("52", "전북특별자치도", "호남권")],
    "강원": [("51", "강원특별자치도", "강원·제주권"), ("50", "제주특별자치도", "강원·제주권")],
}

RISK_KEYWORDS = ['유치권', '지분', '법정지상권', '분묘', '가등기', '가처분', '재매각', '위반건축물', '맹지', '토지만매각', '건물만매각']


def fetch_court_page(sd_cd="", page_no=1, page_size=40, flbd_min="", lcl="", mcl="", scl=""):
    today_str = datetime.now().strftime("%Y%m%d")
    end_str = (datetime.now() + timedelta(days=45)).strftime("%Y%m%d")
    payload = {
        "dma_pageInfo": {
            "pageNo": page_no,
            "pageSize": page_size,
            "bfPageNo": "",
            "startRowNo": "",
            "totalCnt": "",
            "totalYn": "Y" if page_no == 1 else "N",
            "groupTotalCount": ""
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
            "bidBgngYmd": today_str, "bidEndYmd": end_str,
            "dspslDxdyYmd": "", "fstDspslHm": "", "scdDspslHm": "", "thrdDspslHm": "", "fothDspslHm": "",
            "dspslPlcNm": "", "lwsDspslPrcMin": "", "lwsDspslPrcMax": "",
            "grbxTypCd": "", "gdsVendNm": "", "fuelKndCd": "", "carMdyrMax": "", "carMdyrMin": "", "carMdlNm": ""
        }
    }
    res = SESSION.post(COURT_API_URL, json=payload, timeout=12)
    if res.status_code == 200:
        return res.json().get("data", {})
    return {}


def normalize_and_score_item(it, sido_name="대전광역시", region_group="충청권", idx=1, prefix="LIVE"):
    try:
        appraisal_amt = int(it.get("gamevalAmt") or 0)
    except Exception:
        appraisal_amt = 0

    try:
        min_price = int(it.get("notifyMinmaePrice1") or 0)
        if min_price == 0:
            min_price = int(it.get("minmaePrice") or 0)
    except Exception:
        min_price = 0

    yuchal_cnt = int(it.get("yuchalCnt") or 0)
    if appraisal_amt > 0 and min_price > 0:
        ratio = round((min_price / appraisal_amt) * 100, 1)
        discount_rate = round(100 - ratio, 1)
    else:
        ratio = float(it.get("notifyMinmaePriceRate1") or 0)
        discount_rate = round(100 - ratio, 1) if ratio > 0 else 0.0

    mae_date = it.get("maeGiil", "")
    mae_date_fmt = f"{mae_date[:4]}-{mae_date[4:6]}-{mae_date[6:8]}" if len(mae_date) == 8 else mae_date

    mul_bigo = it.get("mulBigo") or ""
    matched_risks = [rk for rk in RISK_KEYWORDS if rk in mul_bigo]
    has_risk = len(matched_risks) > 0
    risk_label = f"주의({','.join(matched_risks)})" if has_risk else "안전(소멸주의)"

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

    score_risk = 30 if not has_risk else -15

    usg = it.get("dspslUsgNm", "아파트")
    if any(k in usg for k in ["아파트", "주상복합"]):
        score_usg = 20
    elif any(k in usg for k in ["오피스텔", "다세대", "연립", "빌라"]):
        score_usg = 16
    elif any(k in usg for k in ["단독", "다가구", "상가주택"]):
        score_usg = 14
    elif any(k in usg for k in ["근린생활", "상가", "점포", "업무"]):
        score_usg = 12
    else:
        score_usg = 9

    sigu = it.get("hjguSigu", "")
    addr = it.get("printSt", "")
    if any(k in sigu or k in addr for k in ["유성구", "강남구", "서초구", "송파구", "분당구", "해운대구", "수성구"]):
        score_loc = 10
    elif any(k in sigu or k in addr for k in ["서구", "마포구", "용산구", "수원", "성남", "고양", "연수구"]):
        score_loc = 9
    else:
        score_loc = 7

    total_score = max(0, score_price + score_risk + score_usg + score_loc)

    comments = []
    comments.append("권리분석 안전(특수권리 없음)" if not has_risk else f"권리상 주의 요망({','.join(matched_risks)})")
    if discount_rate >= 50:
        comments.append(f"감정가 대비 {discount_rate}% 폭넓은 할인(유찰 {yuchal_cnt}회)")
    elif discount_rate >= 20:
        comments.append(f"감정가 대비 {discount_rate}% 저감(유찰 {yuchal_cnt}회)")
    else:
        comments.append("신건(1회차 진행)")
    if mul_bigo:
        comments.append(f"비고: {mul_bigo[:60]}")

    return {
        "id": f"{prefix}_{idx}",
        "rank": f"실시간 {idx}위",
        "score": total_score,
        "region_group": region_group,
        "sido": sido_name,
        "sigu": sigu or sido_name,
        "court": it.get("jiwonNm", ""),
        "dept": it.get("jpDeptNm", "경매계"),
        "case_no": it.get("srnSaNo", ""),
        "item_no": str(it.get("maemulSer", "1")),
        "usage": usg,
        "address": addr,
        "spec": it.get("convAddr", ""),
        "appraisal": appraisal_amt,
        "min_price": min_price,
        "ratio": f"{ratio}%",
        "discount": f"{discount_rate}%",
        "discount_val": discount_rate,
        "yuchal": f"{yuchal_cnt}회",
        "date": mae_date_fmt,
        "risk": risk_label,
        "comment": " | ".join(comments),
        "category": "daejeon" if "대전" in sido_name else "nationwide_best",
        "is_live": True
    }


def live_refresh_portal_data():
    """대법원 경매정보(courtauction.go.kr)에서 실시간으로 대전 및 전국 주요 권역 데이터를 보강·정제하여 각 권역별 TOP 100 portal_data.json을 즉시 갱신"""
    try:
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "extract_data.py")], cwd=BASE_DIR, timeout=30)
    except Exception:
        pass

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(PORTAL_JSON_PATH, "r", encoding="utf-8") as f:
        portal_data = json.load(f)

    try:
        from enrich_engine import enrich_all_portal_data
        portal_data = enrich_all_portal_data(portal_data)
    except Exception:
        pass

    if "meta" not in portal_data:
        portal_data["meta"] = {}
    portal_data["meta"]["refreshed_at"] = now_str
    portal_data["meta"]["region_top_count"] = 100
    portal_data["meta"]["source"] = "courtauction.go.kr (대법원 경매정보 실시간 API)"

    with open(PORTAL_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(portal_data, f, ensure_ascii=False, indent=2)
    try:
        with open(os.path.join(MIRROR_DIR, "portal_data.json"), "w", encoding="utf-8") as f:
            json.dump(portal_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    def _rebuild():
        try:
            subprocess.run([sys.executable, os.path.join(BASE_DIR, "build_portal.py")], cwd=BASE_DIR, timeout=20)
        except Exception:
            pass

    threading.Thread(target=_rebuild, daemon=True).start()
    return portal_data


def live_search_court_auction(region="ALL", usage="ALL", min_discount=0.0, keyword=""):
    """사용자 검색 조건으로 대법원 경매정보(courtauction.go.kr)를 실시간 직접 조회"""
    target_sidos = []
    kw = (keyword or "").strip()

    # 키워드에 시도명이 포함된 경우 자동 매핑
    for k_name, s_tuple in SIDO_CODES.items():
        if k_name in kw:
            target_sidos = [s_tuple]
            break

    if not target_sidos:
        if region in REGION_SIDOS:
            target_sidos = REGION_SIDOS[region]
        elif region == "ALL":
            target_sidos = [
                ("30", "대전광역시", "충청권"),
                ("11", "서울특별시", "수도권"),
                ("41", "경기도", "수도권"),
                ("26", "부산광역시", "영남권(부울경)"),
                ("27", "대구광역시", "영남권(대경권)"),
                ("29", "광주광역시", "호남권"),
            ]
        else:
            target_sidos = [("30", "대전광역시", "충청권")]

    flbd_min = "1" if min_discount >= 20 else ""
    lcl, mcl, scl = ("20000", "20100", "20104") if usage == "아파트" else ("", "", "")

    raw_results = []
    total_court_cnt = 0
    seen = set()

    for sd_cd, sd_name, reg_grp in target_sidos[:4]:
        d1 = fetch_court_page(sd_cd=sd_cd, page_no=1, page_size=40, flbd_min=flbd_min, lcl=lcl, mcl=mcl, scl=scl)
        total_court_cnt += int(d1.get("dma_pageInfo", {}).get("totalCnt", 0) or 0)
        items_p1 = d1.get("dlt_srchResult", [])
        for it in items_p1:
            uk = it.get("groupmaemulser") or f"{it.get('boCd')}_{it.get('saNo')}_{it.get('maemulSer')}_{it.get('mokmulSer')}"
            if uk in seen:
                continue
            seen.add(uk)
            norm = normalize_and_score_item(it, sd_name, reg_grp, len(raw_results) + 1, "LIVE")
            raw_results.append(norm)

        # 키워드 검색이거나 단일 지역이면 2페이지도 추가 조회
        if (kw or len(target_sidos) == 1) and len(items_p1) == 40:
            d2 = fetch_court_page(sd_cd=sd_cd, page_no=2, page_size=40, flbd_min=flbd_min, lcl=lcl, mcl=mcl, scl=scl)
            for it in d2.get("dlt_srchResult", []):
                uk = it.get("groupmaemulser") or f"{it.get('boCd')}_{it.get('saNo')}_{it.get('maemulSer')}_{it.get('mokmulSer')}"
                if uk in seen:
                    continue
                seen.add(uk)
                norm = normalize_and_score_item(it, sd_name, reg_grp, len(raw_results) + 1, "LIVE")
                raw_results.append(norm)

    # 필터링 적용
    filtered = []
    for it in raw_results:
        if usage != "ALL" and usage not in it["usage"]:
            continue
        if min_discount > 0 and it["discount_val"] < min_discount:
            continue
        if kw:
            haystack = f"{it['address']} {it['case_no']} {it['court']} {it['usage']} {it['sigu']} {it['sido']}".lower()
            if kw.lower() not in haystack:
                continue
        filtered.append(it)

    filtered.sort(key=lambda x: (x["score"], x["discount_val"]), reverse=True)
    for idx, it in enumerate(filtered, start=1):
        it["rank"] = f"대법원실시간 {idx}위"
        it["rank_num"] = idx
        it["region_key"] = region if region != "ALL" else it["region_group"]

    return {
        "ok": True,
        "source": "courtauction.go.kr (대법원 경매정보 실시간 연동)",
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_court_cnt": total_court_cnt,
        "matched_cnt": len(filtered),
        "items": filtered[:100]
    }


class AuctionLiveHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        if parsed.path == "/api/status":
            meta = {}
            if os.path.exists(PORTAL_JSON_PATH):
                try:
                    with open(PORTAL_JSON_PATH, "r", encoding="utf-8") as f:
                        meta = json.load(f).get("meta", {})
                except Exception:
                    pass
            return self._send_json({
                "ok": True,
                "live_connected": True,
                "court_endpoint": COURT_API_URL,
                "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "meta": meta
            })

        if parsed.path == "/api/refresh":
            try:
                fresh_data = live_refresh_portal_data()
                return self._send_json({"ok": True, "data": fresh_data})
            except Exception as e:
                return self._send_json({"ok": False, "error": str(e)}, status=500)

        if parsed.path == "/api/live-search":
            region = qs.get("region", ["ALL"])[0]
            usage = qs.get("usage", ["ALL"])[0]
            min_disc = float(qs.get("min_discount", ["0"])[0] or 0)
            keyword = qs.get("keyword", [""])[0]
            try:
                res = live_search_court_auction(region=region, usage=usage, min_discount=min_disc, keyword=keyword)
                return self._send_json(res)
            except Exception as e:
                return self._send_json({"ok": False, "error": str(e)}, status=500)

        try:
            return super().do_GET()
        except (ConnectionResetError, BrokenPipeError):
            pass

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0) or 0)
        body_raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            body = json.loads(body_raw)
        except Exception:
            body = {}

        if parsed.path == "/api/refresh":
            try:
                fresh_data = live_refresh_portal_data()
                return self._send_json({"ok": True, "data": fresh_data})
            except Exception as e:
                return self._send_json({"ok": False, "error": str(e)}, status=500)

        if parsed.path == "/api/live-search":
            try:
                res = live_search_court_auction(
                    region=body.get("region", "ALL"),
                    usage=body.get("usage", "ALL"),
                    min_discount=float(body.get("min_discount", 0) or 0),
                    keyword=body.get("keyword", "")
                )
                return self._send_json(res)
            except Exception as e:
                return self._send_json({"ok": False, "error": str(e)}, status=500)

        return self._send_json({"ok": False, "error": "Not found"}, status=404)


if __name__ == "__main__":
    port = int(os.environ.get("AUCTION_PORT", "8765"))
    server = ThreadingHTTPServer(("127.0.0.1", port), AuctionLiveHandler)
    print(f"🚀 대법원 경매정보 실시간 연동 서버 가동 중: http://127.0.0.1:{port}")
    print(f" - 실시간 포털 접속: http://127.0.0.1:{port}/경매_스마트_분석_포털.html")
    print(f" - 실시간 API 상태: http://127.0.0.1:{port}/api/status")
    print(f" - 실시간 대법원 조회: http://127.0.0.1:{port}/api/live-search")
    server.serve_forever()
