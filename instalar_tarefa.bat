@echo off
rem Cria (ou atualiza) a tarefa agendada "Radar DJEN": segunda a sexta, 09:00.
rem Execute uma vez, com o botao direito > "Executar como administrador" se o Windows pedir.
setlocal
set "SCRIPT=%~dp0coletor_local.bat"

schtasks /Create /F /TN "Radar DJEN" /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 09:00 /TR "\"%SCRIPT%\"" /RL LIMITED
if errorlevel 1 (
  echo.
  echo Nao foi possivel criar a tarefa. Tente executar este arquivo como administrador.
  pause
  exit /b 1
)

echo.
echo Tarefa "Radar DJEN" criada: segunda a sexta, 09:00.
echo Para testar agora:  schtasks /Run /TN "Radar DJEN"
echo Para remover:       schtasks /Delete /TN "Radar DJEN" /F
echo.
pause
