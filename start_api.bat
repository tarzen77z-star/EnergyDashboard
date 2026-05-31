@echo off
echo ============================================
echo  Energy Dashboard - Local API Server
echo ============================================
echo.

echo Installing required packages...
pip install flask flask-cors --quiet

echo.
echo Starting API server...
echo Open your browser to http://localhost:5000/health to verify
echo Then open energy-dashboard.html
echo.
echo Press Ctrl+C to stop the server
echo.

python energy_api.py
pause
