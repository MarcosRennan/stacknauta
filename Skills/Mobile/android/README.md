# Mobile/android

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

- `adaptive`: `skills/adaptive/SKILL.md`
- `agp-9-upgrade`: `skills/agp-9-upgrade/SKILL.md`
- `android-cli`: `skills/android-cli/SKILL.md`
- `android-for-cars-parked-apps`: `skills/android-for-cars-parked-apps/SKILL.md`
- `android-profiler`: `skills/android-profiler/SKILL.md`
- `anr-audit-and-fix`: `skills/anr-audit-and-fix/SKILL.md`
- `appfunctions`: `skills/appfunctions/SKILL.md`
- `camerax`: `skills/camerax/SKILL.md`
- `display-glasses-with-jetpack-compose-glimmer`: `skills/display-glasses-with-jetpack-compose-glimmer/SKILL.md`
- `edge-to-edge`: `skills/edge-to-edge/SKILL.md`
- `engage-sdk-integration`: `skills/engage-sdk-integration/SKILL.md`
- `glance-appwidget-updates-and-memory`: `skills/glance-appwidget-updates-and-memory/SKILL.md`
- `glance-canonical-layouts`: `skills/glance-canonical-layouts/SKILL.md`
- `ink-app-builder`: `skills/ink-app-builder/SKILL.md`
- `ink-custom-brush-builder`: `skills/ink-custom-brush-builder/SKILL.md`
- `jetpack-compose-performance`: `skills/jetpack-compose-performance/SKILL.md`
- `leanback-to-compose-tv-migration`: `skills/leanback-to-compose-tv-migration/SKILL.md`
- `litert-lm`: `skills/litert-lm/SKILL.md`
- `litert-runtime`: `skills/litert-runtime/SKILL.md`
- `media3-cast-integration`: `skills/media3-cast-integration/SKILL.md`
- `migrate-xml-views-to-jetpack-compose`: `skills/migrate-xml-views-to-jetpack-compose/SKILL.md`
- `ml-kit-genai-prompt-api`: `skills/ml-kit-genai-prompt-api/SKILL.md`
- `mlkit-agent-api`: `skills/mlkit-agent-api/SKILL.md`
- `navigation-3`: `skills/navigation-3/SKILL.md`
- `navigation-event`: `skills/navigation-event/SKILL.md`
- `play-billing-library-version-upgrade`: `skills/play-billing-library-version-upgrade/SKILL.md`
- `play-policy-insights`: `skills/play-policy-insights/SKILL.md`
- `projected-hardware`: `skills/projected-hardware/SKILL.md`
- `restore-credentials`: `skills/restore-credentials/SKILL.md`
- `testing-setup`: `skills/testing-setup/SKILL.md`
- `verified-email`: `skills/verified-email/SKILL.md`
- `wear-compose-m3`: `skills/wear-compose-m3/SKILL.md`
- `wear-widgets`: `skills/wear-widgets/SKILL.md`

## Provenance

https://github.com/android/skills.git at `5815d27fda564aa9f07ebdcb5e57ed3e8d904e0d`.
All file origins, hashes and adaptations are recorded in PROVENANCE.json.
