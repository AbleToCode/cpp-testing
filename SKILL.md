---
name: cpp-testing
description: 泛化 C++ 项目测试 Skill。分析项目结构、识别关键函数、根据项目意图编写测试代码。当用户需要为 C++ 项目添加单元测试、验证关键函数正确性、进行回归测试、检查协议解析器、测试网络模块时使用此 skill。支持 GoogleTest 和 Catch2 测试框架。
---

# C++ Testing Skill

分析 C++ 项目结构，识别关键函数，生成针对性测试代码。

## 工作流程

```
1. 分析项目 → 2. 函数分类 → 3. 测试策略 → 4. 测试生成 → 5. 验证执行
```

---

## 阶段 1: 项目分析

扫描以下内容建立项目模型：

| 文件/目录 | 提取信息 |
|-----------|----------|
| `CMakeLists.txt` | 构建目标、依赖库、编译选项 |
| `include/` | 公开 API、类定义、函数签名 |
| `src/` | 实现细节、内部函数 |
| `README.md` / `doc/` | 项目意图、设计目标 |

**输出**: 模块列表 + 依赖关系

---

## 阶段 2: 函数分类

按测试优先级分类：

| 优先级 | 类别 | 特征 | 测试重点 |
|--------|------|------|----------|
| **P0** | 协议/解析 | `parse`, `decode`, `serialize` | 边界值、异常输入、字节序 |
| **P1** | 核心业务 | 状态机、会话管理 | 状态转换、并发安全 |
| **P2** | 网络 I/O | `send`, `receive`, 回调 | Mock、集成测试 |
| **P3** | 工具类 | 配置、日志、转换 | 边界条件 |

运行 `scripts/find_key_functions.py` 辅助识别。

---

## 阶段 3: 测试策略

### 框架选择

| 场景 | 推荐框架 | 理由 |
|------|----------|------|
| 已有 GoogleTest | GoogleTest | 保持一致 |
| 新项目 | Catch2 | 单头文件、BDD 风格 |
| 需要 Mock | GoogleMock | 与 GoogleTest 集成 |

### 测试模式

参考 [test_patterns.md](references/test_patterns.md)：
- 边界值测试
- 异常输入测试
- 状态机测试
- 异步代码测试

---

## 阶段 4: 测试生成

### 文件命名规范

```
tests/
├── test_<module>_<component>.cpp
├── mock_<interface>.hpp
└── fixtures/
    └── <testdata>
```

### GoogleTest 模板

```cpp
#include <gtest/gtest.h>
#include "<header_under_test>.hpp"

class <Component>Test : public ::testing::Test {
protected:
    void SetUp() override { /* 初始化 */ }
    void TearDown() override { /* 清理 */ }
};

TEST_F(<Component>Test, <BehaviorDescription>) {
    // Arrange
    // Act
    // Assert
    EXPECT_EQ(expected, actual);
}
```

### Catch2 模板

```cpp
#include <catch2/catch_test_macros.hpp>
#include "<header_under_test>.hpp"

TEST_CASE("<Component> <behavior>", "[<tag>]") {
    SECTION("<scenario>") {
        // Arrange
        // Act
        // Assert
        REQUIRE(condition);
    }
}
```

---

## 阶段 5: 验证执行

### 构建测试
```bash
cmake -DBUILD_TESTING=ON ..
cmake --build . --target all_tests
```

### 运行测试
```bash
ctest --output-on-failure
# 或直接运行
./tests/<test_executable>
```

### 覆盖率 (可选)
```bash
cmake -DCMAKE_CXX_FLAGS="--coverage" ..
lcov --capture --directory . --output-file coverage.info
genhtml coverage.info --output-directory coverage_report
```

---

## 快速命令

| 任务 | 命令 |
|------|------|
| 分析项目结构 | `python scripts/analyze_project.py <project_root>` |
| 查找关键函数 | `python scripts/find_key_functions.py <include_dir>` |

---

## 参考文档

- [分析工作流详解](references/analysis_workflow.md)
- [测试模式参考](references/test_patterns.md)
- [函数分类指南](references/function_categories.md)
