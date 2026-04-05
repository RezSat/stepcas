param(
  [Parameter(Mandatory = $true)]
  [string]$Task,
  [string]$Url = "http://localhost:4096"
)

opencode run --attach $Url --agent lead-engineer --title "build: $Task" "Read AGENTS.md, program.md, docs/architecture.md, and docs/roadmap.md first. Implement this one scoped task in stepcas: $Task. Keep the change narrow, add or update tests, run focused verification, and summarize the result."
