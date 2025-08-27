@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem Nome do arquivo de saída
set "OUTPUT=projeto_concatenado.txt"

rem (Opcional) Força UTF-8 no console; pode não afetar o arquivo em todos os casos
chcp 65001 >nul

rem Apaga saída anterior e escreve cabeçalho
> "%OUTPUT%" echo ==== Projeto concatenado - %date% %time% ====

for %%E in (py html css js) do (
  for /r %%F in (*.%%E) do (
    set "f=%%F"

    rem Pula caminhos indesejados
    set "DOIT=1"
    if not "!f:\node_modules\=!"=="!f!" set "DOIT="
    if not "!f:\.git\=!"=="!f!" set "DOIT="
    if not "!f:\venv\=!"=="!f!" set "DOIT="
    if not "!f:\env\=!"=="!f!" set "DOIT="
    if not "!f:\dist\=!"=="!f!" set "DOIT="
    if not "!f:\build\=!"=="!f!" set "DOIT="

    if defined DOIT (
      >>"%OUTPUT%" echo.
      >>"%OUTPUT%" echo ===== [%%~xF] %%~fF =====
      type "%%F" >> "%OUTPUT%"
    )
  )
)

echo Concluido: %OUTPUT%
endlocal