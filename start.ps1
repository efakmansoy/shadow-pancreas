# Shadow Pancreas: yerel LLM + uygulama sunucusunu başlatır.
# Kullanım:  powershell -ExecutionPolicy Bypass -File start.ps1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Llama = "D:\downloads\down3\llama\llama-server.exe"
$Model = "E:\model\gemma4-e4b.gguf"            # LLM karşılaştırmasıyla seçildi (reports/llm_bakeoff.json)
$Template = "E:\model\gemma4-official.jinja"

$llm = $null
try {
    $null = Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 http://127.0.0.1:8081/health
    Write-Host "llama-server zaten çalışıyor (8081)."
} catch {
    Write-Host "llama-server başlatılıyor: $Model"
    $llm = Start-Process -FilePath $Llama -PassThru -WindowStyle Minimized -ArgumentList @(
        "-m", $Model, "--chat-template-file", $Template, "-ngl", "99", "-c", "8192", "--jinja",
        "--reasoning", "off", "--temp", "0.2", "--host", "127.0.0.1", "--port", "8081", "-fa", "on", "--no-webui")
}

Write-Host "Uygulama hazır olunca: http://127.0.0.1:8000  (ilk açılış ~20 sn sürebilir)"
try {
    Push-Location $Root
    python app/server.py
} finally {
    Pop-Location
    if ($llm) { Stop-Process -Id $llm.Id -ErrorAction SilentlyContinue }
}
