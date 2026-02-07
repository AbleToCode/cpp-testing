#!/usr/bin/env python3
"""
C++ Project Structure Analyzer

Analyzes C++ project structure to extract module information, dependencies, and build targets.

Usage:
    python analyze_project.py <project_root> [--output json|text]

Example:
    python analyze_project.py /path/to/project --output json
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict


@dataclass
class Module:
    """Project module information"""
    name: str
    namespace: str = ""
    headers: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class BuildTarget:
    """CMake build target"""
    name: str
    type: str  # executable, library
    sources: List[str] = field(default_factory=list)


@dataclass
class ProjectInfo:
    """Project information summary"""
    name: str = ""
    cpp_standard: str = ""
    build_targets: List[BuildTarget] = field(default_factory=list)
    modules: List[Module] = field(default_factory=list)
    external_deps: List[str] = field(default_factory=list)


def parse_cmake(cmake_path: Path) -> Dict[str, Any]:
    """Parse CMakeLists.txt to extract build information"""
    info = {
        "project_name": "",
        "cpp_standard": "",
        "targets": [],
        "find_packages": [],
    }
    
    if not cmake_path.exists():
        return info
    
    content = cmake_path.read_text(encoding='utf-8', errors='ignore')
    
    # Project name
    match = re.search(r'project\s*\(\s*(\w+)', content, re.IGNORECASE)
    if match:
        info["project_name"] = match.group(1)
    
    # C++ standard
    match = re.search(r'CMAKE_CXX_STANDARD\s+(\d+)', content)
    if match:
        info["cpp_standard"] = match.group(1)
    
    # Build targets
    for match in re.finditer(r'add_(executable|library)\s*\(\s*(\w+)', content, re.IGNORECASE):
        info["targets"].append({
            "type": match.group(1).lower(),
            "name": match.group(2)
        })
    
    # External dependencies
    for match in re.finditer(r'find_package\s*\(\s*(\w+)', content, re.IGNORECASE):
        info["find_packages"].append(match.group(1))
    
    return info


def scan_headers(include_dir: Path) -> Dict[str, Module]:
    """Scan headers directory to identify modules"""
    modules: Dict[str, Module] = {}
    
    if not include_dir.exists():
        return modules
    
    for header in include_dir.rglob("*.hpp"):
        # Infer module name from path
        relative = header.relative_to(include_dir)
        parts = relative.parts
        
        if len(parts) > 1:
            module_name = parts[0]
        else:
            module_name = "root"
        
        if module_name not in modules:
            modules[module_name] = Module(name=module_name)
        
        modules[module_name].headers.append(str(relative))
        
        # Try to extract namespace
        try:
            content = header.read_text(encoding='utf-8', errors='ignore')
            ns_match = re.search(r'namespace\s+(\w+(?:::\w+)*)\s*\{', content)
            if ns_match and not modules[module_name].namespace:
                modules[module_name].namespace = ns_match.group(1)
        except Exception:
            pass
    
    return modules


def scan_sources(src_dir: Path) -> List[str]:
    """Scan sources directory"""
    sources = []
    
    if not src_dir.exists():
        return sources
    
    for ext in ['*.cpp', '*.cc', '*.cxx']:
        for src in src_dir.rglob(ext):
            sources.append(str(src.relative_to(src_dir)))
    
    return sources


def analyze_project(project_root: str) -> ProjectInfo:
    """Analyze the entire project"""
    root = Path(project_root)
    info = ProjectInfo()
    
    # Parse CMakeLists.txt
    cmake_info = parse_cmake(root / "CMakeLists.txt")
    info.name = cmake_info.get("project_name", root.name)
    info.cpp_standard = cmake_info.get("cpp_standard", "")
    info.external_deps = cmake_info.get("find_packages", [])
    
    # Build targets
    for target in cmake_info.get("targets", []):
        info.build_targets.append(BuildTarget(
            name=target["name"],
            type=target["type"]
        ))
    
    # Scan headers
    include_dirs = ["include", "inc", "headers"]
    for inc_dir in include_dirs:
        inc_path = root / inc_dir
        if inc_path.exists():
            modules = scan_headers(inc_path)
            info.modules.extend(modules.values())
            break
    
    # Scan sources
    src_dirs = ["src", "source", "sources"]
    for src_dir in src_dirs:
        src_path = root / src_dir
        if src_path.exists():
            sources = scan_sources(src_path)
            # Associate with the first module by default
            if info.modules:
                info.modules[0].sources = sources
            break
    
    return info


def format_output(info: ProjectInfo, format: str) -> str:
    """Format output results"""
    if format == "json":
        return json.dumps(asdict(info), indent=2, ensure_ascii=False)
    else:
        lines = [
            f"Project: {info.name}",
            f"C++ Standard: C++{info.cpp_standard}" if info.cpp_standard else "",
            "",
            "Build Targets:",
        ]
        for target in info.build_targets:
            lines.append(f"  - [{target.type}] {target.name}")
        
        lines.extend(["", "Modules:"])
        for module in info.modules:
            lines.append(f"  - {module.name} ({module.namespace or 'no namespace'})")
            lines.append(f"    Headers: {len(module.headers)} files")
            lines.append(f"    Sources: {len(module.sources)} files")
        
        if info.external_deps:
            lines.extend(["", "External dependencies:"])
            for dep in info.external_deps:
                lines.append(f"  - {dep}")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="C++ Project Structure Analyzer")
    parser.add_argument("project_root", help="Project root directory path")
    parser.add_argument("--output", choices=["json", "text"], default="text",
                       help="Output format")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.project_root):
        print(f"Error: Directory does not exist: {args.project_root}")
        return 1
    
    info = analyze_project(args.project_root)
    print(format_output(info, args.output))
    return 0


if __name__ == "__main__":
    exit(main())
