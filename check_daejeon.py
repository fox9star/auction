import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8',
    'Referer': 'https://www.courtauction.go.kr/pgj/index.on'
})

def query_daejeon(lcl="", mcl="", scl="", flbd_min=""):
    payload = {
        "dma_pageInfo": {
            "pageNo": 1, "pageSize": 40, "bfPageNo": "", "startRowNo": "",
            "totalCnt": "", "totalYn": "Y", "groupTotalCount": ""
        },
        "dma_srchGdsDtlSrchInfo": {
            "rletDspslSpcCondCd": "", "bidDvsCd": "", "mvprpRletDvsCd": "00031R",
            "cortAuctnSrchCondCd": "0004601", "rprsAdongSdCd": "30",
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
            "bidBgngYmd": "20261017", "bidEndYmd": "20261130",
            "dspslDxdyYmd": "", "fstDspslHm": "", "scdDspslHm": "", "thrdDspslHm": "", "fothDspslHm": "",
            "dspslPlcNm": "", "lwsDspslPrcMin": "", "lwsDspslPrcMax": "",
            "grbxTypCd": "", "gdsVendNm": "", "fuelKndCd": "", "carMdyrMax": "", "carMdyrMin": "", "carMdlNm": ""
        }
    }
    res = session.post('https://www.courtauction.go.kr/pgj/pgjsearch/searchControllerMain.on', json=payload, timeout=12)
    data = res.json().get('data', {})
    info = data.get('dma_pageInfo', {})
    return info.get('totalCnt', 0), data.get('dlt_srchResult', [])

# 전체 부동산(건물+토지 등) 조회
total_all, sample_all = query_daejeon(lcl="", flbd_min="")
total_bld, _ = query_daejeon(lcl="20000", flbd_min="")
total_apt, _ = query_daejeon(lcl="20000", mcl="20100", scl="20104", flbd_min="")
total_land, _ = query_daejeon(lcl="10000", flbd_min="")

print(f"대전 전체 부동산 경매 물건 수: {total_all}건")
print(f" - 건물(주거/상업/공장 등): {total_bld}건 (그 중 아파트: {total_apt}건)")
print(f" - 토지: {total_land}건")
if sample_all:
    print(f"샘플 물건 1: {sample_all[0].get('printCsNo')}, {sample_all[0].get('dspslUsgNm')}, {sample_all[0].get('printSt')}")

