@echo off
echo Building CV from Doxygen source...
powershell -ExecutionPolicy Bypass -File "build-cv.ps1" %*
pause
