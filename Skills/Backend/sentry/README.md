# Backend/sentry

## Execution contract

This is a physical StackNauta distribution, not an agent activation or an application bootstrap.
Resolve each skill's scripts and references from its SKILL.md directory. Keep the application's
working directory for project inputs and outputs. Shared resources and licences live in this bundle.

Before executing Python, Node.js, Java or Rust, resolve the **installed global asdf version** from
`~/.tool-versions`, confirm that `asdf current` selects that global file, and obtain the full executable
path with `asdf which`. A project override, missing version or missing installation must stop execution.
Use that verified executable for vendor command examples; never fall back to a system runtime,
install a runtime or auto-install a missing tool/dependency. For standard-library Python helpers,
invoke the verified Python directly instead of `uv run`. Do not execute shebangs implicitly.
Application SDKs, authenticated CLIs, hardware and services are prerequisites in the consumer's
environment, not supplied dependencies or authorization to install, publish, push or contact services.

Copy the closure recorded in catalogo.json: the selected skill, required companion skills, their
resources and the shared files. Preserve this layout and PROVENANCE.json. No symlinks are needed.
Named optional skills outside the supplied closure are unavailable: stop that optional workflow
instead of inventing or installing a replacement. Pending/internal/experimental skills are not supplied.
Agent integration and end-to-end application workflows are not certified by packaging approval.


## Included skills

- `agents-md`: `skills/agents-md/SKILL.md`
- `code-review`: `skills/code-review/SKILL.md`
- `code-simplifier`: `skills/code-simplifier/SKILL.md`
- `commit`: `skills/commit/SKILL.md`
- `create-branch`: `skills/create-branch/SKILL.md`
- `django-perf-review`: `skills/django-perf-review/SKILL.md`
- `doc-coauthoring`: `skills/doc-coauthoring/SKILL.md`
- `find-bugs`: `skills/find-bugs/SKILL.md`
- `gh-review-requests`: `skills/gh-review-requests/SKILL.md`
- `iterate-pr`: `skills/iterate-pr/SKILL.md`
- `pr-link-issue`: `skills/pr-link-issue/SKILL.md`
- `pr-screenshots`: `skills/pr-screenshots/SKILL.md`
- `pr-writer`: `skills/pr-writer/SKILL.md`
- `prompt-optimizer`: `skills/prompt-optimizer/SKILL.md`
- `typing-exclusion-worker`: `skills/typing-exclusion-worker/SKILL.md`

## Provenance

https://github.com/getsentry/skills.git at `e94f22214528d69899d09c627b3315ddc3544816`.
All file origins, hashes and adaptations are recorded in PROVENANCE.json.
