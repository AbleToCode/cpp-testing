# 项目分析工作流

## 步骤 1: 构建配置分析

### CMakeLists.txt 解析

提取以下信息：

```python
# 关键模式匹配
patterns = {
    'project_name': r'project\((\w+)',
    'targets': r'add_(?:executable|library)\((\w+)',
    'sources': r'(?:SOURCES?|SRCS?)\s+([^)]+)',
    'includes': r'target_include_directories\([^)]+\s+(\S+)',
    'dependencies': r'find_package\((\w+)',
}
```

### vcpkg.json 依赖

```json
{
  "dependencies": ["asio", "gtest", "catch2"]
}
```

---

## 步骤 2: 头文件扫描

### 优先扫描顺序

1. `include/` - 公开 API
2. `src/*.hpp` - 内部头文件  
3. `include/**/detail/` - 实现细节（低优先级）

### 函数签名提取

```cpp
// 识别公开函数
// 模式: [virtual] <return_type> <name>(<params>) [const] [noexcept] [override]

// 示例输出:
// - bool parse(const uint8_t* data, size_t len)
// - void setCallback(DataCallback cb)
// - std::optional<Frame> getNextFrame()
```

---

## 步骤 3: 模块边界识别

### 命名空间映射

```
namespace simple {
    namespace net { /* 网络层 */ }
    namespace protocol { /* 协议层 */ }
    namespace util { /* 工具类 */ }
}
```

### 依赖方向检查

```
net → protocol → util  (正确)
util → net            (错误: 循环依赖警告)
```

---

## 步骤 4: 输出报告

### JSON 格式

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
