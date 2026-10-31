# Skills

Grok auto-loads `.grok/skills/` (and `~/.grok/skills/`). `docs/skills/` stays on-demand playbooks — this path is **not** auto-loaded.

**Staff kit** = always-on process docs (`PROCESS`, `Coding_Standards`, Change_Log norms) at `docs/` root.

| Location | Contents |
|----------|----------|
| [`.grok/skills/`](../../.grok/skills/) | Auto-loaded by Grok Build (e.g. `git-workflow-and-versioning`) |
| `~/.grok/skills/` | Auto-loaded user skills (do **not** vendor kit skills there) |
| [General/](General/) | Portable playbooks, attached when a task needs one |
| [Domain/](Domain/) | Product/domain skills — empty in the template |

## Skills vs documentation

| | Auto-loaded (`.grok/skills/`) | On-demand (`docs/skills/`) | Docs (staff kit / app) |
|--|-------------------------------|----------------------------|-------------------------|
| **When used** | Grok loads matching skills | Paste/attach for a job | Always available; open on demand by pointer |
| **Examples** | Git commit shape / PR detail | “How I want UI screenshots reviewed” | PROCESS, Change_Log, schema |
| **Agents** | Auto when task matches | Load when the prompt names them | Load only files named by AGENTS / prompt |

Both skill trees are Markdown. Auto-loaded skills are **task depth Grok already sees**. `docs/skills/` is **optional depth you attach**. Staff kit is **how the project runs**. Parallel-session worktree and branch-delete rules live in [AGENTS.md](../../AGENTS.md) and [PROCESS.md](../PROCESS.md); they override the vendored git skill.
