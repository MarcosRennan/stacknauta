# Mobile/expo

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

- `eas-app-stores`: `skills/eas-app-stores/SKILL.md`
- `eas-hosting`: `skills/eas-hosting/SKILL.md`
- `eas-observe`: `skills/eas-observe/SKILL.md`
- `eas-simulator`: `skills/eas-simulator/SKILL.md`
- `eas-update`: `skills/eas-update/SKILL.md`
- `eas-update-insights`: `skills/eas-update-insights/SKILL.md`
- `eas-workflows`: `skills/eas-workflows/SKILL.md`
- `expo-animation`: `skills/expo-animation/SKILL.md`
- `expo-app-clip`: `skills/expo-app-clip/SKILL.md`
- `expo-brownfield`: `skills/expo-brownfield/SKILL.md`
- `expo-data-fetching`: `skills/expo-data-fetching/SKILL.md`
- `expo-design-system`: `skills/expo-design-system/SKILL.md`
- `expo-dev-client`: `skills/expo-dev-client/SKILL.md`
- `expo-dom`: `skills/expo-dom/SKILL.md`
- `expo-examples`: `skills/expo-examples/SKILL.md`
- `expo-module`: `skills/expo-module/SKILL.md`
- `expo-native-ui`: `skills/expo-native-ui/SKILL.md`
- `expo-overview`: `skills/expo-overview/SKILL.md`
- `expo-project-structure`: `skills/expo-project-structure/SKILL.md`
- `expo-router`: `skills/expo-router/SKILL.md`
- `expo-ui`: `skills/expo-ui/SKILL.md`
- `expo-upgrade`: `skills/expo-upgrade/SKILL.md`
- `expo-web-to-native`: `skills/expo-web-to-native/SKILL.md`

## Provenance

https://github.com/expo/skills.git at `a9e5bd3fa00b4e61f632e43f85da73aee1942582`.
All file origins, hashes and adaptations are recorded in PROVENANCE.json.
