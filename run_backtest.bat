@echo off
set PYTHONPATH=%CD%
echo Starting backtest... > backtest_debug.log
e:\Sach\DuAn\Hinto_Stock\.venv\Scripts\python.exe -u scripts/backtesting/run_backtest.py >> backtest_debug.log 2>&1
if %errorlevel% neq 0 (
    echo Python command failed with error level %errorlevel% >> backtest_debug.log
)
type backtest_debug.log
