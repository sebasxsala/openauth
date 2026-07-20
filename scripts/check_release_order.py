#!/usr/bin/env python3
"""Validate the documented publish order against Cargo workspace metadata."""

from __future__ import annotations

import collections
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
RELEASE_FILE = REPO_ROOT / "RELEASE.md"
PUBLISH_ORDER_HEADING = "## Publish order"
PUBLISH_ORDER_ENTRY = re.compile(r"^(\d+)\.\s+`([^`]+)`(?:\s|$)")


def load_metadata(repo_root: Path) -> dict[str, Any]:
    result = subprocess.run(
        ["cargo", "metadata", "--format-version", "1", "--no-deps", "--locked"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def is_publishable(package: dict[str, Any]) -> bool:
    allowed_registries = package.get("publish")
    return allowed_registries is None or bool(allowed_registries)


def is_packaged_dependency(dependency: dict[str, Any]) -> bool:
    kind = dependency.get("kind")
    if kind in (None, "normal", "build"):
        return True
    if kind == "dev":
        return dependency.get("req") not in (None, "*")
    return False


def is_same_workspace_dependency(
    dependency: dict[str, Any], workspace_package: dict[str, Any]
) -> bool:
    dependency_path = dependency.get("path")
    if dependency_path is None:
        return False
    package_path = Path(workspace_package["manifest_path"]).parent
    return Path(dependency_path).resolve() == package_path.resolve()


def build_publish_graph(metadata: dict[str, Any]) -> dict[str, set[str]]:
    workspace_member_ids = set(metadata["workspace_members"])
    workspace_packages = {
        package["name"]: package
        for package in metadata["packages"]
        if package["id"] in workspace_member_ids
    }
    published_packages = {
        name: package
        for name, package in workspace_packages.items()
        if is_publishable(package)
    }

    graph = {name: set() for name in published_packages}
    for package_name, package in published_packages.items():
        for dependency in package["dependencies"]:
            dependency_name = dependency["name"]
            dependency_package = published_packages.get(dependency_name)
            if (
                dependency_package is not None
                and is_same_workspace_dependency(dependency, dependency_package)
                and is_packaged_dependency(dependency)
            ):
                graph[package_name].add(dependency_name)
    return graph


def parse_publish_order_text(contents: str) -> list[tuple[int, str]]:
    lines = contents.splitlines()
    try:
        heading_index = next(
            index
            for index, line in enumerate(lines)
            if line.strip() == PUBLISH_ORDER_HEADING
        )
    except StopIteration as error:
        raise ValueError(f"missing `{PUBLISH_ORDER_HEADING}` section") from error

    entries = []
    for line in lines[heading_index + 1 :]:
        if line.startswith("## "):
            break
        if match := PUBLISH_ORDER_ENTRY.match(line):
            entries.append((int(match.group(1)), match.group(2)))

    if not entries:
        raise ValueError("publish order section has no numbered package entries")
    return entries


def find_cycle(graph: dict[str, set[str]]) -> list[str] | None:
    states: dict[str, int] = {}
    stack: list[str] = []
    stack_positions: dict[str, int] = {}

    def visit(package: str) -> list[str] | None:
        states[package] = 1
        stack_positions[package] = len(stack)
        stack.append(package)

        for dependency in sorted(graph[package]):
            if states.get(dependency, 0) == 0:
                if cycle := visit(dependency):
                    return cycle
            elif states[dependency] == 1:
                start = stack_positions[dependency]
                return [*stack[start:], dependency]

        stack.pop()
        stack_positions.pop(package)
        states[package] = 2
        return None

    for package in sorted(graph):
        if states.get(package, 0) == 0:
            if cycle := visit(package):
                return cycle
    return None


def validate_release_order(
    graph: dict[str, set[str]], entries: list[tuple[int, str]]
) -> list[str]:
    errors = []
    numbers = [number for number, _ in entries]
    package_names = [package for _, package in entries]

    expected_numbers = list(range(1, len(entries) + 1))
    if numbers != expected_numbers:
        errors.append(
            "publish order numbering must be consecutive from 1 "
            f"(found {numbers})"
        )

    duplicate_packages = sorted(
        package
        for package, count in collections.Counter(package_names).items()
        if count > 1
    )
    if duplicate_packages:
        errors.append(
            "duplicate packages in publish order: " + ", ".join(duplicate_packages)
        )

    documented = set(package_names)
    published = set(graph)
    missing = sorted(published - documented)
    extra = sorted(documented - published)
    if missing:
        errors.append("published packages missing from RELEASE.md: " + ", ".join(missing))
    if extra:
        errors.append(
            "unpublished or unknown packages in publish order: " + ", ".join(extra)
        )

    if cycle := find_cycle(graph):
        errors.append("packaged workspace dependency cycle: " + " -> ".join(cycle))

    if not duplicate_packages and documented == published:
        positions = {package: index for index, package in enumerate(package_names)}
        for dependent in sorted(graph):
            for dependency in sorted(graph[dependent]):
                if positions[dependency] >= positions[dependent]:
                    errors.append(
                        f"`{dependency}` must appear before dependent `{dependent}`"
                    )
    return errors


def main() -> int:
    try:
        metadata = load_metadata(REPO_ROOT)
        graph = build_publish_graph(metadata)
        entries = parse_publish_order_text(RELEASE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f"release-order preflight failed: {error}", file=sys.stderr)
        return 1

    errors = validate_release_order(graph, entries)
    if errors:
        print("release-order preflight failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    edge_count = sum(len(dependencies) for dependencies in graph.values())
    print(
        "release-order preflight passed: "
        f"{len(graph)} publishable workspace packages, "
        f"{edge_count} packaged workspace dependency edges."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
