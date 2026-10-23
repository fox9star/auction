@echo off
chcp 65001 >nul
title 대한민국 대법원 경매정보(courtauction.go.kr) 실시간 연동 API 서버
echo ============================================================================
echo [대한민국 대법원 경매정보 실시간 연동 브릿지 서버]
echo - 연동 대상: https://www.courtauction.go.kr (대법원 법원경매정보)
echo - 로컬 서버: http://127.0.0.1:8765/경매_스마트_분석_포털.html
echo ============================================================================
echo.
start "" "http://127.0.0.1:8765/경매_스마트_분석_포털.html"
python "%~dp0auction_live_server.py"
pause
