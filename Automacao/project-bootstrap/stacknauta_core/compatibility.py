"""Política explícita de compatibilidade; sem inferência de texto livre ou tecnologias."""


def rule(languages=(), frameworks=(), features=(), *, architecture=None, all_frameworks=(), blocked=None, tools=(), runtimes=()):
    return {"languages_any": set(languages), "frameworks_any": set(frameworks), "features_all": set(features),
            "architecture": architecture, "frameworks_all": set(all_frameworks), "blocked": blocked,
            "tools": set(tools), "runtimes": set(runtimes)}


def policies():
    result = {
        "fastapi:fastapi": rule(["python"], ["fastapi"]),
        "remy:hexagonal-python": rule(["python"], features=["api"], architecture="hexagonal-ddd"),
        "remy:hexagonal-typescript": rule(["typescript"], features=["api"], architecture="hexagonal-ddd"),
        "remy:hexagonal-go": rule(["go"], features=["api"], architecture="hexagonal-ddd"),
        "ui-ux-pro-max:ui-ux-pro-max": rule(features=["ui"]),
        "ui-ux-pro-max:banner-design": rule(features=["banners"]),
        "ui-ux-pro-max:brand": rule(features=["branding"], runtimes=["nodejs"]),
        "ui-ux-pro-max:ui-styling": rule(["javascript", "typescript"], features=["ui"], all_frameworks=["shadcn", "tailwind"], runtimes=["nodejs"]),
    }
    expo_features = {
        "expo-overview": (), "eas-app-stores": ("deployment",), "eas-hosting": ("deployment",),
        "eas-workflows": ("ci",), "eas-observe": ("observability",), "eas-simulator": ("simulator",),
        "eas-update-insights": ("ota", "observability"), "eas-update": ("ota",),
        "expo-animation": ("animation",), "expo-app-clip": ("app-clip",), "expo-brownfield": ("brownfield",),
        "expo-data-fetching": ("networking",), "expo-design-system": ("design-tokens",),
        "expo-dev-client": ("dev-client",), "expo-dom": ("web-migration",), "expo-examples": ("examples",),
        "expo-module": ("native-modules",), "expo-native-ui": ("ui",), "expo-project-structure": (),
        "expo-router": ("navigation",), "expo-ui": ("ui",), "expo-upgrade": ("sdk-upgrade",),
        "expo-web-to-native": ("web-migration",),
    }
    for name, features in expo_features.items():
        result["expo:"+name] = rule(["javascript", "typescript"], ["expo"], features)
    for name in ("compose-animations", "compose-component-design", "compose-focus-navigation", "compose-state-and-effects"):
        feature = "animation" if name == "compose-animations" else "navigation" if name == "compose-focus-navigation" else "ui"
        result["chrisbanes:"+name] = rule(["kotlin"], ["jetpack-compose"], [feature])
    result.update({
        "chrisbanes:compose-performance": rule(["kotlin"], ["jetpack-compose"], ["performance"]),
        "chrisbanes:compose-ui-testing-patterns": rule(["kotlin"], ["jetpack-compose"], ["testing"]),
        "chrisbanes:android-benchmark-comparison": rule(["kotlin", "java"], ["android"], ["benchmark"]),
        "chrisbanes:gradle-run": rule(["kotlin", "java"], features=["gradle"]),
        "chrisbanes:changelog": rule(["kotlin"], features=["release"]),
        "chrisbanes:release-kotlin-library": rule(["kotlin"], features=["release", "gradle"]),
        "chrisbanes:grounded-writing": rule(features=["documentation"]),
        "chrisbanes:shepherd": rule(features=["git-workflow"], blocked="Autenticação e capacidades de controle de PR exigem validação do agente na Etapa 2B"),
    })
    for name in ("kotlin-api-design", "kotlin-concurrency-and-flow", "kotlin-control-flow"):
        result["chrisbanes:"+name] = rule(["kotlin"])
    android_features = {
        "agp-9-upgrade": "sdk-upgrade", "camerax": "camera", "android-for-cars-parked-apps": "cars",
        "appfunctions": "appfunctions", "litert-lm": "on-device-ai", "litert-runtime": "on-device-ai",
        "ml-kit-genai-prompt-api": "on-device-ai", "mlkit-agent-api": "on-device-ai",
        "android-cli": None, "restore-credentials": "identity", "verified-email": "identity",
        "adaptive": "adaptive-layout", "ink-app-builder": "ink", "ink-custom-brush-builder": "ink",
        "jetpack-compose-performance": "performance", "migrate-xml-views-to-jetpack-compose": "xml-migration",
        "media3-cast-integration": "casting", "navigation-3": "navigation", "navigation-event": "navigation",
        "anr-audit-and-fix": "anr", "engage-sdk-integration": "play-engage",
        "play-billing-library-version-upgrade": "billing", "play-policy-insights": "play-policy",
        "android-profiler": "profiling", "android-intent-security": "intents",
        "android-permissions-security": "permissions", "edge-to-edge": "edge-to-edge",
        "glance-appwidget-updates-and-memory": "widgets", "glance-canonical-layouts": "widgets",
        "testing-setup": "testing", "leanback-to-compose-tv-migration": "tv", "wear-compose-m3": "wear",
        "wear-widgets": "wear", "display-glasses-with-jetpack-compose-glimmer": "xr", "projected-hardware": "xr",
    }
    compose_only = {"adaptive", "ink-app-builder", "ink-custom-brush-builder", "jetpack-compose-performance", "wear-compose-m3", "display-glasses-with-jetpack-compose-glimmer"}
    for name, feature in android_features.items():
        result["android:"+name] = rule(["kotlin"] if name in compose_only else ["kotlin", "java"],
                                       ["android"], [feature] if feature else (),
                                       all_frameworks=["jetpack-compose"] if name in compose_only else ())
    result.update({
        "sentry:django-access-review": rule(["python"], ["django"], ["security-review"]),
        "sentry:django-perf-review": rule(["python"], ["django"], ["performance"]),
        "sentry:gha-security-review": rule(features=["github-actions", "security-review"]),
        "sentry:security-review": rule(features=["security-review"]),
        "sentry:secret-serialization": rule(features=["secret-serialization"]),
        "sentry:security-model": rule(features=["security-model"], tools=["git"]),
        "sentry:agents-md": rule(features=["documentation"]),
        "sentry:code-review": rule(features=["code-review"]),
        "sentry:code-simplifier": rule(features=["refactoring"]),
        "sentry:commit": rule(features=["git-workflow"], tools=["git"]),
        "sentry:create-branch": rule(features=["git-workflow"], tools=["git"]),
        "sentry:doc-coauthoring": rule(features=["documentation"]),
        "sentry:find-bugs": rule(features=["code-review"], tools=["git"], blocked="Consulta autenticada ao GitHub ainda exige validação do agente"),
        "sentry:typing-exclusion-worker": rule(["python"], features=["typing"]),
        "sentry:prompt-optimizer": rule(features=["prompts"]),
    })
    for name in ("gh-review-requests", "iterate-pr", "pr-link-issue", "pr-screenshots", "pr-writer"):
        result["sentry:"+name] = rule(features=["git-workflow"], blocked="GitHub/browser autenticado deve ser validado pelo agente antes de incluir esta rotina operacional")
    return result


def mismatch(policy, config):
    if policy is None:
        return "Sem política de compatibilidade explícita nesta versão do núcleo"
    languages = set(config["stack"]["languages"])
    frameworks = {f["name"] for f in config["stack"]["frameworks"]}
    features = set(config["requirements"]["features"])
    if policy["languages_any"] and not policy["languages_any"] & languages:
        return "Linguagem exigida não declarada: "+", ".join(sorted(policy["languages_any"]))
    if policy["frameworks_any"] and not policy["frameworks_any"] & frameworks:
        return "Framework exigido não declarado: "+", ".join(sorted(policy["frameworks_any"]))
    if policy["frameworks_all"] - frameworks:
        return "Frameworks obrigatórios não declarados: "+", ".join(sorted(policy["frameworks_all"] - frameworks))
    if policy["features_all"] - features:
        return "Funcionalidades obrigatórias não declaradas: "+", ".join(sorted(policy["features_all"] - features))
    if policy["architecture"] and config["stack"]["architecture"] != policy["architecture"]:
        return "Arquitetura explícita exigida: "+policy["architecture"]
    return policy["blocked"]
