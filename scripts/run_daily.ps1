param(
  [string]$Date = (Get-Date -Format "yyyy-MM-dd"),
  [switch]$SendWecom,
  [string]$Python = "G:\gj\python\python.exe"
)

$ErrorActionPreference = "Stop"

if ($SendWecom) {
  & $Python -m src.news_lianbo_daily.cli --date $Date --send-wecom
} else {
  & $Python -m src.news_lianbo_daily.cli --date $Date
}
