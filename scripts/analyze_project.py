#!/usr/bin/env python3
"""
C++ Project Structure Analyzer

分析 C++ 项目结构，提取模块信息、依赖关系和构建目标。

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
    """项目模块信息"""
    name: str
    namespace: str = ""
    headers: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class BuildTarget:
    """CMake 构建目标"""
    name: str
    type: str  # executable, library
    sources: List[str] = field(default_factory=list)


@dataclass
class ProjectInfo:
    """项目信息摘要"""
    name: str = ""
    cpp_standard: str = ""
    build_targets: List[BuildTarget] = field(default_factory=list)
    modules: List[Module] = field(default_factory=list)
    external_deps: List[str] = field(default_factory=list)


def parse_cmake(cmake_path: Path) -> Dict[str, Any]:
    """解析 CMakeLists.txt 提取构建信息"""
    info = {
        "project_name": "",
        "cpp_standard": "",
        "targets": [],
        "find_packages": [],
    }
    
    if not cmake_path.exists():
        return info
    
    content = cmake_path.read_text(encoding='utf-8', errors='ignore')
    
    # 项目名称
    match = re.search(r'project\s*\(\s*(\w+)', content, re.IGNORECASE)
    if match:
        info["project_name"] = match.group(1)
    
    # C++ 标准
    match = re.search(r'CMAKE_CXX_STANDARD\s+(\d+)', content)
    if match:
        info["cpp_standard"] = match.group(1)
    
    # 构建目标
    for match in re.finditer(r'add_(executable|library)\s*\(\s*(\w+)', content, re.IGNORECASE):
        info["targets"].append({
            "type": match.group(1).lower(),
            "name": match.group(2)
        })
    
    # 外部依赖
    for match in re.finditer(r'find_package\s*\(\s*(\w+)', content, re.IGNORECASE):
        info["find_packages"].append(match.group(1))
    
    return info


def scan_headers(include_dir: Path) -> Dict[str, Module]:
    """扫描头文件目录，识别模块"""
    modules: Dict[str, Module] = {}
    
    if not include_dir.exists():
        return modules
    
    for header in include_dir.rglob("*.hpp"):
        # 从路径推断模块名
        relative = header.relative_to(include_dir)
        parts = relative.parts
        
        if len(parts) > 1:
            module_name = parts[0]
        else:
            module_name = "root"
        
        if module_name not in modules:
            modules[module_name] = Module(name=module_name)
        
        modules[module_name].headers.append(str(relative))
        
        # 尝试提取命名空间
        try:
            content = header.read_text(encoding='utf-8', errors='ignore')
            ns_match = re.search(r'namespace\s+(\w+(?:::\w+)*)\s*\{', content)
            if ns_match and not modules[module_name].namespace:
                modules[module_name].namespace = ns_match.group(1)
        except Exception:
            pass
    
    return modules


def scan_sources(src_dir: Path) -> List[str]:
    """扫描源文件目录"""
    sources = []
    
    if not src_dir.exists():
        return sources
    
    for ext in ['*.cpp', '*.cc', '*.cxx']:
        for src in src_dir.rglob(ext):
            sources.append(str(src.relative_to(src_dir)))
    
    return sources


def analyze_project(project_root: str) -> ProjectInfo:
    """分析整个项目"""
    root = Path(project_root)
    info = ProjectInfo()
    
    # 解析 CMakeLists.txt
    cmake_info = parse_cmake(root / "CMakeLists.txt")
    info.name = cmake_info.get("project_name", root.name)
    info.cpp_standard = cmake_info.get("cpp_standard", "")
    info.external_deps = cmake_info.get("find_packages", [])
    
    # 构建目标
    for target in cmake_info.get("targets", []):
        info.build_targets.append(BuildTarget(
            name=target["name"],
            type=target["type"]
        ))
    
    # 扫描头文件
    include_dirs = ["include", "inc", "headers"]
    for inc_dir in include_dirs:
        inc_path = root / inc_dir
        if inc_path.exists():
            modules = scan_headers(inc_path)
            info.modules.extend(modules.values())
            break
    
    # 扫描源文件
    src_dirs = ["src", "source", "sources"]
    for src_dir in src_dirs:
        src_path = root / src_dir
        if src_path.exists():
            sources = scan_sources(src_path)
            # 关联到默认模块
            if info.modules:
                info.modules[0].sources = sources
            break
    
    return info


def format_output(info: ProjectInfo, format: str) -> str:
    """格式化输出"""
    if format == "json":
        return json.dumps(asdict(info), indent=2, ensure_ascii=False)
    else:
        lines = [
            f"项目: {info.name}",
            f"C++ 标准: C++{info.cpp_standard}" if info.cpp_standard else "",
            "",
            "构建目标:",
        ]
        for target in info.build_targets:
            lines.append(f"  - [{target.type}] {target.name}")
        
        lines.extend(["", "模块:"])
        for module in info.modules:
            lines.append(f"  - {module.name} ({module.namespace or 'no namespace'})")
            lines.append(f"    头文件: {len(module.headers)} 个")
            lines.append(f"    源文件: {len(module.sources)} 个")
        
        if info.external_deps:
            lines.extend(["", "外部依赖:"])
            for dep in info.external_deps:
                lines.append(f"  - {dep}")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="C++ 项目结构分析器")
    parser.add_argument("project_root", help="项目根目录路径")
    parser.add_argument("--output", choices=["json", "text"], default="text",
                       help="输出格式")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.project_root):
        print(f"错误: 目录不存在: {args.project_root}")
        return 1
    
    info = analyze_project(args.project_root)
    print(format_output(info, args.output))
    return 0


if __name__ == "__main__":
    exit(main())
