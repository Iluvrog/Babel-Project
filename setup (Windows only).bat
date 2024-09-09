@echo off

set PYTHON="python"
set LIBRARIES=pycdlib chardet requests

rem Check if python3 exists
where /q %PYTHON%

rem If not, install it
if %errorlevel% equ '0' (
	echo install python
	winget install %PYTHON%
) else (
	echo python found
)

rem Install pip libraries
echo Install pip libraries if necessary
for %%l in (%LIBRARIES%) do (
	%PYTHON% -m pip install %%l
)

pause