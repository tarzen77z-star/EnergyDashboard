@echo off
echo ============================================
echo  Energy Dashboard - Local Web Server
echo ============================================
echo.
echo Starting local web server...
echo Open your browser to: http://localhost:8080/energy-dashboard.html
echo.
echo Press Ctrl+C to stop
echo.
start "" "http://localhost:8080/energy-dashboard.html"
python -m http.server 8080
pause
