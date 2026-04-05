param(
    [Parameter(Mandatory=$true)][string]$Id,
    [Parameter(Mandatory=$true)][string]$Title,
    [Parameter(Mandatory=$true)][string]$Agent,
    [Parameter(Mandatory=$true)][string]$Command,
    [int]$Priority = 100,
    [string]$Branch = "",
    [string]$Notes = ""
)

$path = ".\company\tasks.json"
$data = Get-Content $path -Raw | ConvertFrom-Json
$newTask = [PSCustomObject]@{
    id = $Id
    title = $Title
    agent = $Agent
    command = $Command
    status = "queued"
    priority = $Priority
    branch = $Branch
    notes = $Notes
}
$data += $newTask
$data | ConvertTo-Json -Depth 5 | Set-Content $path
Write-Host "Added task $Id"
