@echo off

echo Running Black
black . 
echo ---------------------------

echo Running Ruff
ruff check .  --fix
echo ---------------------------

echo Running isort
isort . 
echo ---------------------------

echo Running mypy
mypy --exclude venv .