param(
  [Parameter(Mandatory = $true)]
  [string]$Task,
  [string]$Url = "http://localhost:4096"
)

opencode run --attach $Url --agent lead-engineer --title "plan: $Task" "Read AGENTS.md, program.md, docs/architecture.md, and docs/roadmap.md first. Then plan this task without editing code: $Task"
