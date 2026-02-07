#!/usr/bin/env python3
"""
C++ Key Function Finder

Scans C++ headers to identify key functions and categorize them by priority.

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
    """Function information"""
    name: str
    full_name: str  # Includes class name
    file: str
    line: int
    signature: str
    return_type: str
    priority: str  # P0, P1, P2, P3
    category: str  # protocol, network, business, utility


# Mapping keywords to category/priority
KEYWORD_PATTERNS = {
    # P0: Protocol/Parsing - Highest priority
    "protocol": {
        "keywords": ["parse", "decode", "serialize", "deserialize", "encode", "unpack", "pack"],
        "priority": "P0",
        "category": "protocol"
    },
    # P1: Core Business
    "business": {
        "keywords": ["handle", "process", "execute", "transition", "validate"],
        "priority": "P1", 
        "category": "business"
    },
    # P2: Network I/O
    "network": {
        "keywords": ["send", "receive", "read", "write", "connect", "accept", "async"],
        "priority": "P2",
        "category": "network"
    },
    # P3: Utilities
    "utility": {
        "keywords": ["to", "from", "convert", "format", "get", "set", "is", "has"],
        "priority": "P3",
        "category": "utility"
    }
}

# Regex for function signature
FUNCTION_PATTERN = re.compile(
    r'''
    (?:virtual\s+)?                     # virtual (optional)
    (?:static\s+)?                      # static (optional)
    (?:inline\s+)?                      # inline (optional)
    ([\w:<>,\s\*&]+?)                   # Return type
    \s+
    ([\w~]+)                            # Function name
    \s*
    \(([^)]*)\)                         # Parameters
    \s*
    (?:const)?                          # const (optional)
    (?:\s*noexcept)?                    # noexcept (optional)
    (?:\s*override)?                    # override (optional)
    \s*
    (?:;|=|\{)                          # End of signature
    ''',
    re.VERBOSE | re.MULTILINE
)

# Regex for class definition
CLASS_PATTERN = re.compile(r'(?:class|struct)\s+(\w+)\s*(?::\s*[^{]+)?\s*\{')


def classify_function(name: str) -> tuple[str, str]:
    """Categorize functions based on name"""
    name_lower = name.lower()
    
    for category_name, config in KEYWORD_PATTERNS.items():
        for keyword in config["keywords"]:
            if keyword in name_lower:
                return config["priority"], config["category"]
    
    return "P3", "utility"


def extract_functions(file_path: Path) -> List[FunctionInfo]:
    """Extract functions from a header file"""
    functions = []
    
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return functions
    
    lines = content.split('\n')
    current_class = None
    brace_depth = 0
    
    # Simplified class tracking
    for i, line in enumerate(lines, 1):
        # Track class definitions
        class_match = CLASS_PATTERN.search(line)
        if class_match:
            current_class = class_match.group(1)
            brace_depth = 0
        
        # Track braces
        brace_depth += line.count('{') - line.count('}')
        if brace_depth <= 0:
            current_class = None
            brace_depth = 0
    
    # Re-scan to extract functions
    for match in FUNCTION_PATTERN.finditer(content):
        return_type = match.group(1).strip()
        func_name = match.group(2).strip()
        params = match.group(3).strip()
        
        # Skip constructors/destructors
        if func_name.startswith('~') or return_type == func_name:
            continue
        
        # Skip operator overloads
        if func_name.startswith('operator'):
            continue
        
        # Calculate line number
        line_num = content[:match.start()].count('\n') + 1
        
        # Attempt to determine parent class
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
    """Scan all header files in a directory"""
    all_functions = []
    root = Path(include_dir)
    
    for header in root.rglob("*.hpp"):
        functions = extract_functions(header)
        # Update relative path
        for func in functions:
            func.file = str(header.relative_to(root))
        all_functions.extend(functions)
    
    # Also scan .h files
    for header in root.rglob("*.h"):
        functions = extract_functions(header)
        for func in functions:
            func.file = str(header.relative_to(root))
        all_functions.extend(functions)
    
    return all_functions


def format_output(functions: List[FunctionInfo], format: str) -> str:
    """Format output results"""
    # Sort by priority
    sorted_funcs = sorted(functions, key=lambda f: (f.priority, f.category, f.name))
    
    if format == "json":
        return json.dumps([asdict(f) for f in sorted_funcs], indent=2, ensure_ascii=False)
    else:
        lines = ["# Key Functions List", ""]
        
        # Group by priority
        for priority in ["P0", "P1", "P2", "P3"]:
            group = [f for f in sorted_funcs if f.priority == priority]
            if not group:
                continue
            
            priority_names = {
                "P0": "Protocol/Parsing (Highest Priority)",
                "P1": "Core Business",
                "P2": "Network I/O",
                "P3": "Utilities"
            }
            
            lines.extend([
                f"## {priority}: {priority_names.get(priority, '')}",
                ""
            ])
            
            for func in group:
                lines.append(f"- `{func.full_name}` [{func.file}:{func.line}]")
                lines.append(f"  - Signature: `{func.signature}`")
                lines.append(f"  - Category: {func.category}")
                lines.append("")
        
        # Statistics
        lines.extend([
            "---",
            f"Total: {len(functions)} functions",
            f"  P0: {len([f for f in functions if f.priority == 'P0'])}",
            f"  P1: {len([f for f in functions if f.priority == 'P1'])}",
            f"  P2: {len([f for f in functions if f.priority == 'P2'])}",
            f"  P3: {len([f for f in functions if f.priority == 'P3'])}",
        ])
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="C++ Key Function Finder")
    parser.add_argument("include_dir", help="Include directory path")
    parser.add_argument("--output", choices=["json", "text"], default="text",
                       help="Output format")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.include_dir):
        print(f"Error: Directory does not exist: {args.include_dir}")
        return 1
    
    functions = scan_directory(args.include_dir)
    print(format_output(functions, args.output))
    return 0


if __name__ == "__main__":
    exit(main())
