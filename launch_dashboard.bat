@echo off
echo Starting Dashboard... > dashboard.log
.\.venv\Scripts\python.exe -m streamlit run src/presentation/dashboard/app.py --server.port 8501 --server.address 127.0.0.1 >> dashboard.log 2>&1
if %errorlevel% neq 0 (
    echo Failed with error code %errorlevel% >> dashboard.log
)
