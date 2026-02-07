---
name: cpp-testing
description: Generalized C++ project testing skill. Analyze project structure, identify key functions, and write test code based on project intent. Use this skill when users need to add unit tests, verify key functions, perform regression testing, check protocol parsers, or test network modules for C++ projects. Supports GoogleTest and Catch2 frameworks.
---

# C++ Testing Skill

Analyze C++ project structure, identify key functions, and generate targeted test code.

## Workflow

```
1. Analyze Project → 2. Categorize Functions → 3. Test Strategy → 4. Generate Tests → 5. Verify Execution
```

---

## Phase 1: Project Analysis

Scan the following content to build a project model:

| File/Directory | Information to Extract |
|-----------|----------|
| `CMakeLists.txt` | Build targets, dependencies, compile options |
| `include/` | Public API, class definitions, function signatures |
| `src/` | Implementation details, internal functions |
| `README.md` / `doc/` | Project intent, design goals |

**Output**: Module list + Dependencies

---

## Phase 2: Function Categorization

Categorize functions by test priority:

| Priority | Category | Features | Test Focus |
|--------|------|------|----------|
| **P0** | Protocol/Parsing | `parse`, `decode`, `serialize` | Boundary values, abnormal inputs, endianness |
| **P1** | Core Business | State machine, session management | State transitions, concurrency safety |
| **P2** | Network I/O | `send`, `receive`, callbacks | Mocking, integration testing |
| **P3** | Utilities | Config, logging, conversion | Boundary conditions |

Run `scripts/find_key_functions.py` for automated identification.

---

## Phase 3: Test Strategy

### Framework Selection

| Scenario | Recommended Framework | Reason |
|------|----------|------|
| Existing GoogleTest | GoogleTest | Maintain consistency |
| New Project | Catch2 | Single header, BDD style |
| Need Mocking | GoogleMock | Integrated with GoogleTest |

### Test Patterns

Refer to [test_patterns.md](references/test_patterns.md):
- Boundary value testing
- Abnormal input testing
- State machine testing
- Asynchronous code testing

---

## Phase 4: Test Generation

### File Naming Convention

```
tests/
├── test_<module>_<component>.cpp
├── mock_<interface>.hpp
└── fixtures/
    └── <testdata>
```

### GoogleTest Template

```cpp
#include <gtest/gtest.h>
#include "<header_under_test>.hpp"

class <Component>Test : public ::testing::Test {
protected:
    void SetUp() override { /* Initialization */ }
    void TearDown() override { /* Cleanup */ }
};

TEST_F(<Component>Test, <BehaviorDescription>) {
    // Arrange
    // Act
    // Assert
    EXPECT_EQ(expected, actual);
}
```

### Catch2 Template

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

## Phase 5: Verify Execution

### Build Tests
```bash
cmake -DBUILD_TESTING=ON ..
cmake --build . --target all_tests
```

### Run Tests
```bash
ctest --output-on-failure
# Or run directly
./tests/<test_executable>
```

### Coverage (Optional)
```bash
cmake -DCMAKE_CXX_FLAGS="--coverage" ..
lcov --capture --directory . --output-file coverage.info
genhtml coverage.info --output-directory coverage_report
```

---

## Quick Commands

| Task | Command |
|------|------|
| Analyze project structure | `python scripts/analyze_project.py <project_root>` |
| Find key functions | `python scripts/find_key_functions.py <include_dir>` |

---

## Reference Documents

- [Analysis Workflow Details](references/analysis_workflow.md)
- [Test Patterns Reference](references/test_patterns.md)
- [Function Categorization Guide](references/function_categories.md)
