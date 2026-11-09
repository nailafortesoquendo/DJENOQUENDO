@echo off
rem Radar DJEN - coleta diaria no computador do escritorio.
rem Atualiza o repositorio, consulta o DJEN, grava os dados e envia ao GitHub.
rem O envio dispara a publicacao do site pelo GitHub Actions.
setlocal
cd /d "%~dp0"
set "LOG=%~dp0coletor.log"

echo. >> "%LOG%"
echo ==== %date% %time% ==== >> "%LOG%"

where py >nul 2>&1 && (set "PY=py -3") || (set "PY=python")

git pull --rebase --quiet origin Radar-de >> "%LOG%" 2>&1
if errorlevel 1 (
  echo ERRO: nao foi possivel atualizar o repositorio. Veja acima. >> "%LOG%"
  exit /b 1
)

%PY% coletor.py %* >> "%LOG%" 2>&1
if errorlevel 1 echo AVISO: o coletor terminou com erro. Veja acima. >> "%LOG%"

git add site/data >> "%LOG%" 2>&1
git diff --cached --quiet
if not errorlevel 1 (
  echo Sem novidades para enviar. >> "%LOG%"
  exit /b 0
)

git -c user.name="Radar DJEN" -c user.email="radar-djen@users.noreply.github.com" commit --quiet -m "DJEN: coleta local de %date%" >> "%LOG%" 2>&1
git push --quiet origin Radar-de >> "%LOG%" 2>&1
if errorlevel 1 (
  echo ERRO: nao foi possivel enviar ao GitHub. Veja acima. >> "%LOG%"
  exit /b 1
)
echo Enviado ao GitHub. >> "%LOG%"
exit /b 0
