@echo off
cd /d %~dp0
py -m streamlit run script.py
pause