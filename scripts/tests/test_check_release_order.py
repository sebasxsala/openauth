from __future__ import annotations

import sys
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts import check_release_order


def dependency(
    name: str, kind: str | None, requirement: str, path: str | None
) -> dict[str, str | None]:
    return {"name": name, "kind": kind, "req": requirement, "path": path}


def package(
    name: str,
    dependencies: list[dict[str, str | None]],
    publish: list[str] | None = None,
) -> dict[str, object]:
    return {
        "id": name,
        "name": name,
        "dependencies": dependencies,
        "manifest_path": f"/workspace/{name}/Cargo.toml",
        "publish": publish,
    }


class ReleaseOrderTests(unittest.TestCase):
    def test_graph_includes_versioned_dev_dependencies_only(self) -> None:
        packages = [
            package("base", []),
            package("app", [dependency("base", None, "^1", "/workspace/base")]),
            package(
                "verifier", [dependency("base", "dev", "^1", "/workspace/base")]
            ),
            package(
                "path-only-tests",
                [dependency("base", "dev", "*", "/workspace/base")],
            ),
            package(
                "unpublished",
                [dependency("app", None, "^1", "/workspace/app")],
                publish=[],
            ),
        ]
        metadata = {
            "workspace_members": [package["id"] for package in packages],
            "packages": packages,
        }

        self.assertEqual(
            check_release_order.build_publish_graph(metadata),
            {
                "base": set(),
                "app": {"base"},
                "verifier": {"base"},
                "path-only-tests": set(),
            },
        )

    def test_graph_ignores_registry_dependency_with_workspace_package_name(self) -> None:
        packages = [
            package("base", []),
            package("local-user", [dependency("base", None, "^1", "/workspace/base")]),
            package("registry-user", [dependency("base", None, "^0.9", None)]),
        ]
        metadata = {
            "workspace_members": [package["id"] for package in packages],
            "packages": packages,
        }

        self.assertEqual(
            check_release_order.build_publish_graph(metadata),
            {
                "base": set(),
                "local-user": {"base"},
                "registry-user": set(),
            },
        )

    def test_find_cycle_returns_closed_dependency_path(self) -> None:
        graph = {
            "first": {"second"},
            "second": {"third"},
            "third": {"first"},
        }

        self.assertEqual(
            check_release_order.find_cycle(graph),
            ["first", "second", "third", "first"],
        )

    def test_validation_reports_order_drift(self) -> None:
        entries = check_release_order.parse_publish_order_text(
            """
## Publish order

1. `app` — depends on base.
2. `base` — no dependencies.

## Next section
"""
        )

        self.assertEqual(
            check_release_order.validate_release_order(
                {"base": set(), "app": {"base"}}, entries
            ),
            ["`base` must appear before dependent `app`"],
        )

    def test_validation_reports_duplicate_missing_and_extra_packages(self) -> None:
        self.assertEqual(
            check_release_order.validate_release_order(
                {"base": set(), "app": {"base"}},
                [(1, "base"), (2, "base"), (3, "unknown")],
            ),
            [
                "duplicate packages in publish order: base",
                "published packages missing from RELEASE.md: app",
                "unpublished or unknown packages in publish order: unknown",
            ],
        )


if __name__ == "__main__":
    unittest.main()
