#!/usr/bin/env python3
"""
C++ Key Function Finder

扫描 C++ 头文件，识别关键函数并按优先级分类。

Usage:
    python find_key_functions.py <include_dir> [--output json|text]

Example:
    python find_key_functions.py /path/to/project/include --output json
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, field, asdict


@dataclass
class FunctionInfo:
    """函数信息"""
    name: str
    full_name: str  # 包含类名
    file: str
    line: int
    signature: str
    return_type: str
    priority: str  # P0, P1, P2, P3
    category: str  # protocol, network, business, utility


# 关键词到类别/优先级的映射
KEYWORD_PATTERNS = {
    # P0: 协议/解析 - 最高优先级
    "protocol": {
        "keywords": ["parse", "decode", "serialize", "deserialize", "encode", "unpack", "pack"],
        "priority": "P0",
        "category": "protocol"
    },
    # P1: 核心业务
    "business": {
        "keywords": ["handle", "process", "execute", "transition", "validate"],
        "priority": "P1", 
        "category": "business"
    },
    # P2: 网络 I/O
    "network": {
        "keywords": ["send", "receive", "read", "write", "connect", "accept", "async"],
        "priority": "P2",
        "category": "network"
    },
    # P3: 工具类
    "utility": {
        "keywords": ["to", "from", "convert", "format", "get", "set", "is", "has"],
        "priority": "P3",
        "category": "utility"
    }
}

# 函数签名正则
FUNCTION_PATTERN = re.compile(
    r'''
    (?:virtual\s+)?                     # virtual (可选)
    (?:static\s+)?                      # static (可选)
    (?:inline\s+)?                      # inline (可选)
    ([\w:<>,\s\*&]+?)                   # 返回类型
    \s+
    ([\w~]+)                            # 函数名
    \s*
    \(([^)]*)\)                         # 参数
    \s*
    (?:const)?                          # const (可选)
    (?:\s*noexcept)?                    # noexcept (可选)
    (?:\s*override)?                    # override (可选)
    \s*
    (?:;|=|\{)                          # 结束
    ''',
    re.VERBOSE | re.MULTILINE
)

# 类定义正则
CLASS_PATTERN = re.compile(r'(?:class|struct)\s+(\w+)\s*(?::\s*[^{]+)?\s*\{')


def classify_function(name: str) -> tuple[str, str]:
    """根据函数名分类"""
    name_lower = name.lower()
    
    for category_name, config in KEYWORD_PATTERNS.items():
        for keyword in config["keywords"]:
            if keyword in name_lower:
                return config["priority"], config["category"]
    
    return "P3", "utility"


def extract_functions(file_path: Path) -> List[FunctionInfo]:
    """从头文件提取函数"""
    functions = []
    
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return functions
    
    lines = content.split('\n')
    current_class = None
    brace_depth = 0
    
    # 简化的类跟踪
    for i, line in enumerate(lines, 1):
        # 跟踪类定义
        class_match = CLASS_PATTERN.search(line)
        if class_match:
            current_class = class_match.group(1)
            brace_depth = 0
        
        # 跟踪大括号
        brace_depth += line.count('{') - line.count('}')
        if brace_depth <= 0:
            current_class = None
            brace_depth = 0
    
    # 重新扫描提取函数
    for match in FUNCTION_PATTERN.finditer(content):
        return_type = match.group(1).strip()
        func_name = match.group(2).strip()
        params = match.group(3).strip()
        
        # 跳过构造函数/析构函数
        if func_name.startswith('~') or return_type == func_name:
            continue
        
        # 跳过运算符重载
        if func_name.startswith('operator'):
            continue
        
        # 计算行号
        line_num = content[:match.start()].count('\n') + 1
        
        # 尝试确定所属类
        class_name = ""
        search_pos = match.start()
        for class_match in CLASS_PATTERN.finditer(content[:search_pos]):
            class_name = class_match.group(1)
        
        full_name = f"{class_name}::{func_name}" if class_name else func_name
        priority, category = classify_function(func_name)
        
        signature = f"{return_type} {func_name}({params})"
        
        functions.append(FunctionInfo(
            name=func_name,
            full_name=full_name,
            file=str(file_path.name),
            line=line_num,
            signature=signature,
            return_type=return_type,
            priority=priority,
            category=category
        ))
    
    return functions


def scan_directory(include_dir: str) -> List[FunctionInfo]:
    """扫描目录下所有头文件"""
    all_functions = []
    root = Path(include_dir)
    
    for header in root.rglob("*.hpp"):
        functions = extract_functions(header)
        # 更新相对路径
        for func in functions:
            func.file = str(header.relative_to(root))
        all_functions.extend(functions)
    
    # 也扫描 .h 文件
    for header in root.rglob("*.h"):
        functions = extract_functions(header)
        for func in functions:
            func.file = str(header.relative_to(root))
        all_functions.extend(functions)
    
    return all_functions


def format_output(functions: List[FunctionInfo], format: str) -> str:
    """格式化输出"""
    # 按优先级排序
    sorted_funcs = sorted(functions, key=lambda f: (f.priority, f.category, f.name))
    
    if format == "json":
        return json.dumps([asdict(f) for f in sorted_funcs], indent=2, ensure_ascii=False)
    else:
        lines = ["# 关键函数列表", ""]
        
        # 按优先级分组
        for priority in ["P0", "P1", "P2", "P3"]:
            group = [f for f in sorted_funcs if f.priority == priority]
            if not group:
                continue
            
            priority_names = {
                "P0": "协议/解析 (最高优先级)",
                "P1": "核心业务",
                "P2": "网络 I/O",
                "P3": "工具类"
            }
            
            lines.extend([
                f"## {priority}: {priority_names.get(priority, '')}",
                ""
            ])
            
            for func in group:
                lines.append(f"- `{func.full_name}` [{func.file}:{func.line}]")
                lines.append(f"  - 签名: `{func.signature}`")
                lines.append(f"  - 分类: {func.category}")
                lines.append("")
        
        # 统计
        lines.extend([
            "---",
            f"总计: {len(functions)} 个函数",
            f"  P0: {len([f for f in functions if f.priority == 'P0'])}",
            f"  P1: {len([f for f in functions if f.priority == 'P1'])}",
            f"  P2: {len([f for f in functions if f.priority == 'P2'])}",
            f"  P3: {len([f for f in functions if f.priority == 'P3'])}",
        ])
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="C++ 关键函数查找器")
    parser.add_argument("include_dir", help="头文件目录路径")
    parser.add_argument("--output", choices=["json", "text"], default="text",
                       help="输出格式")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.include_dir):
        print(f"错误: 目录不存在: {args.include_dir}")
        return 1
    
    functions = scan_directory(args.include_dir)
    print(format_output(functions, args.output))
    return 0


if __name__ == "__main__":
    exit(main())
