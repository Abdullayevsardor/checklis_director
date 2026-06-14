#!/usr/bin/env pwsh
Write-Host "Running backend tests (pytest)..."
$proc = Start-Process -FilePath pytest -ArgumentList '-q' -NoNewWindow -PassThru -Wait
if ($proc.ExitCode -ne 0) {
  Write-Host "Tests failed. Push aborted. Fix tests before pushing." -ForegroundColor Red
  exit $proc.ExitCode
}
Write-Host "Tests passed. Proceeding with push." -ForegroundColor Green
exit 0
