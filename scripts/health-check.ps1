# =============================================================================
# kafka-eda-lab - Health Check Script (PowerShell)
# =============================================================================

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  kafka-eda-lab - Health Check" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$services = @(
    @{Name="Kafka"; Url="http://localhost:9092"; Check="tcp"},
    @{Name="Schema Registry"; Url="http://localhost:8081/subjects"; Check="http"},
    @{Name="Kafka UI"; Url="http://localhost:8090"; Check="http"},
    @{Name="Prometheus"; Url="http://localhost:9090/-/healthy"; Check="http"},
    @{Name="Grafana"; Url="http://localhost:3000/api/health"; Check="http"},
    @{Name="Loki"; Url="http://localhost:3100/ready"; Check="http"},
    @{Name="Jaeger"; Url="http://localhost:16686"; Check="http"}
)

$allHealthy = $true

foreach ($service in $services) {
    $status = "UNKNOWN"
    $color = "Yellow"

    try {
        if ($service.Check -eq "http") {
            $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                $status = "OK"
                $color = "Green"
            } else {
                $status = "WARN ($($response.StatusCode))"
                $color = "Yellow"
            }
        } elseif ($service.Check -eq "tcp") {
            $tcpClient = New-Object System.Net.Sockets.TcpClient
            $uri = [System.Uri]$service.Url
            $tcpClient.Connect($uri.Host, $uri.Port)
            if ($tcpClient.Connected) {
                $status = "OK"
                $color = "Green"
                $tcpClient.Close()
            }
        }
    } catch {
        $status = "FAIL"
        $color = "Red"
        $allHealthy = $false
    }

    $paddedName = $service.Name.PadRight(20)
    Write-Host "  $paddedName " -NoNewline
    Write-Host "[$status]" -ForegroundColor $color
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan

if ($allHealthy) {
    Write-Host "  All services are healthy!" -ForegroundColor Green
} else {
    Write-Host "  Some services are not available." -ForegroundColor Red
    Write-Host "  Run 'docker-compose ps' for details." -ForegroundColor Yellow
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# URLs d'accès
Write-Host "  Service URLs:" -ForegroundColor White
Write-Host "  - Dashboard:    http://localhost:8080" -ForegroundColor Gray
Write-Host "  - Grafana:      http://localhost:3000" -ForegroundColor Gray
Write-Host "  - Jaeger:       http://localhost:16686" -ForegroundColor Gray
Write-Host "  - Kafka UI:     http://localhost:8090" -ForegroundColor Gray
Write-Host "  - Prometheus:   http://localhost:9090" -ForegroundColor Gray
Write-Host ""
