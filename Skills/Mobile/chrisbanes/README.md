# Mobile/chrisbanes

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

- `android-benchmark-comparison`: `skills/android-benchmark-comparison/SKILL.md`
- `changelog`: `skills/changelog/SKILL.md`
- `compose-animations`: `skills/compose-animations/SKILL.md`
- `compose-component-design`: `skills/compose-component-design/SKILL.md`
- `compose-focus-navigation`: `skills/compose-focus-navigation/SKILL.md`
- `compose-performance`: `skills/compose-performance/SKILL.md`
- `compose-state-and-effects`: `skills/compose-state-and-effects/SKILL.md`
- `compose-ui-testing-patterns`: `skills/compose-ui-testing-patterns/SKILL.md`
- `gradle-run`: `skills/gradle-run/SKILL.md`
- `grounded-writing`: `skills/grounded-writing/SKILL.md`
- `kotlin-api-design`: `skills/kotlin-api-design/SKILL.md`
- `kotlin-concurrency-and-flow`: `skills/kotlin-concurrency-and-flow/SKILL.md`
- `kotlin-control-flow`: `skills/kotlin-control-flow/SKILL.md`
- `release-kotlin-library`: `skills/release-kotlin-library/SKILL.md`
- `shepherd`: `skills/shepherd/SKILL.md`

## Provenance

https://github.com/chrisbanes/skills.git at `50d54366e577460b769ce05b50da007de9939783`.
All file origins, hashes and adaptations are recorded in PROVENANCE.json.
