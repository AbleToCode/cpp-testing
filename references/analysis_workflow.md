# Project Analysis Workflow

## Step 1: Build Configuration Analysis

### CMakeLists.txt Parsing

Extract the following information:

```python
# Key pattern matching
patterns = {
    'project_name': r'project\((\w+)',
    'targets': r'add_(?:executable|library)\((\w+)',
    'sources': r'(?:SOURCES?|SRCS?)\s+([^)]+)',
    'includes': r'target_include_directories\([^)]+\s+(\S+)',
    'dependencies': r'find_package\((\w+)',
}
```

### vcpkg.json Dependencies

```json
{
  "dependencies": ["asio", "gtest", "catch2"]
}
```

---

## Step 2: Header File Scanning

### Priority Scan Order

1. `include/` - Public API
2. `src/*.hpp` - Internal headers  
3. `include/**/detail/` - Implementation details (low priority)

### Function Signature Extraction

```cpp
// Identify public functions
// Pattern: [virtual] <return_type> <name>(<params>) [const] [noexcept] [override]

// Example output:
// - bool parse(const uint8_t* data, size_t len)
// - void setCallback(DataCallback cb)
// - std::optional<Frame> getNextFrame()
```

---

## Step 3: Module Boundary Identification

### Namespace Mapping

```
namespace simple {
    namespace net { /* Network Layer */ }
    namespace protocol { /* Protocol Layer */ }
    namespace util { /* Utility Classes */ }
}
```

### Dependency Direction Check

```
net → protocol → util  (Correct)
util → net            (Error: Circular dependency warning)
```

---

## Step 4: Output Report

### JSON Format

```json
{
  "project": {
    "name": "stream_test",
    "type": "executable",
    "cpp_standard": "17"
  },
  "modules": [
    {
      "name": "net",
      "namespace": "simple::net",
      "headers": ["async_tcp_server.hpp"],
      "dependencies": ["asio"]
    }
  ],
  "key_functions": [
    {
      "name": "FrameParser::feed",
      "file": "jtt1078_parser.hpp",
      "priority": "P0",
      "category": "protocol"
    }
  ]
}
```
