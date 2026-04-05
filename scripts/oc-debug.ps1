param(
  [Parameter(Mandatory = $true)]
  [string]$Issue,
  [string]$Url = "http://localhost:4027"
)

opencode run --attach $Url --agent debug-engineer --title "debug: $Issue" "Read AGENTS.md first. Investigate this issue in stepcas: $Issue. Reproduce it, find the smallest failing case, explain likely cause, and propose the smallest safe fix and regression tests."
