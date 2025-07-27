# Kill any existing kubectl port-forward processes
Get-Process | Where-Object {$_.ProcessName -eq "kubectl" -and $_.CommandLine -like "*port-forward*"} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Starting Kubernetes port-forwarding..." -ForegroundColor Green

# Start port forwarding for all services
$jobs = @()
$jobs += Start-Job -ScriptBlock { kubectl port-forward svc/order-api 32000:8000 }
$jobs += Start-Job -ScriptBlock { kubectl port-forward svc/processor-api 32001:8001 }
$jobs += Start-Job -ScriptBlock { kubectl port-forward svc/kafka-ui 32002:8080 }
$jobs += Start-Job -ScriptBlock { kubectl -n portainer port-forward svc/portainer 32003:9000 }
$jobs += Start-Job -ScriptBlock { kubectl -n kubernetes-dashboard port-forward svc/kubernetes-dashboard 32004:443 }

Write-Host "Port forwarding started:" -ForegroundColor Yellow
Write-Host "  Order API       → http://localhost:32000" -ForegroundColor Cyan
Write-Host "  Processor API   → http://localhost:32001" -ForegroundColor Cyan
Write-Host "  Kafka UI        → http://localhost:32002" -ForegroundColor Cyan
Write-Host "  Portainer       → http://localhost:32003" -ForegroundColor Cyan
Write-Host "  Dashboard       → https://localhost:32004  (accept cert warning)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all port forwarding" -ForegroundColor Red

# Function to cleanup on exit
function Cleanup {
    Write-Host "Stopping port forwarding..." -ForegroundColor Yellow
    $jobs | Stop-Job -PassThru | Remove-Job
    Get-Process | Where-Object {$_.ProcessName -eq "kubectl" -and $_.CommandLine -like "*port-forward*"} | Stop-Process -Force -ErrorAction SilentlyContinue
}

# Register cleanup on exit
Register-EngineEvent PowerShell.Exiting -Action { Cleanup }

try {
    # Wait for Ctrl+C
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
finally {
    Cleanup
}