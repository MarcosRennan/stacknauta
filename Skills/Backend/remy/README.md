# Backend/remy

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

- `hexagonal-go`: `skills/hexagonal-go/SKILL.md`
- `hexagonal-python`: `skills/hexagonal-python/SKILL.md`
- `hexagonal-typescript`: `skills/hexagonal-typescript/SKILL.md`

## Provenance

https://github.com/Remy349/skills.git at `5d9eae132afea72518ba0f1f41919f9e37964362`.
All file origins, hashes and adaptations are recorded in PROVENANCE.json.
