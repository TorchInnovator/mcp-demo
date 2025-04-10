@echo off
echo Stopping any existing MCP server processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq uvicorn*" > nul 2>&1
echo Done.
pause 