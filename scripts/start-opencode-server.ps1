param(
  [int]$Port = 4027
)

$env:OPENCODE_SERVER_PASSWORD = if ($env:OPENCODE_SERVER_PASSWORD) { $env:OPENCODE_SERVER_PASSWORD } else { "stepcas-local" }
Write-Host "Starting OpenCode headless server on port $Port"
Write-Host "Password is set from OPENCODE_SERVER_PASSWORD"
opencode serve --port $Port
