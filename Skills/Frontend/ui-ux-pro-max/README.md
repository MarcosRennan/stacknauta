# Frontend/ui-ux-pro-max

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

- `banner-design`: `skills/banner-design/SKILL.md`
- `brand`: `skills/brand/SKILL.md`
- `ui-styling`: `skills/ui-styling/SKILL.md`
- `ui-ux-pro-max`: `skills/ui-ux-pro-max/SKILL.md`

## Provenance

https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git at `6ae86f61f520d6ca229d2f40e070410638c908c5`.
All file origins, hashes and adaptations are recorded in PROVENANCE.json.
