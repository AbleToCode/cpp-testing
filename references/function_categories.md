# 函数分类指南

## 分类维度

### 1. 按职责分类

| 类别 | 关键词 | 示例 |
|------|--------|------|
| **解析/编码** | `parse`, `decode`, `serialize`, `deserialize` | `parseFrame()`, `decodeHeader()` |
| **网络 I/O** | `send`, `receive`, `read`, `write`, `connect` | `asyncRead()`, `sendPacket()` |
| **状态管理** | `set`, `get`, `update`, `transition` | `setState()`, `getStatus()` |
| **回调/事件** | `on`, `callback`, `handler`, `notify` | `onDataReceived()`, `handleEvent()` |
| **工具/转换** | `to`, `from`, `convert`, `format` | `toBigEndian()`, `formatTime()` |
| **生命周期** | `init`, `start`, `stop`, `close`, `reset` | `initialize()`, `shutdown()` |

### 2. 按复杂度分类

| 等级 | 特征 | 测试策略 |
|------|------|----------|
| **简单** | 纯函数、无副作用 | 单元测试、参数化测试 |
| **中等** | 依赖内部状态 | Fixture + 状态验证 |
| **复杂** | 异步、多线程、I/O | Mock + 集成测试 |

### 3. 按风险等级分类

| 等级 | 识别方式 | 测试覆盖要求 |
|------|----------|--------------|
| **高风险** | 安全相关、金融计算、协议解析 | 100% 分支覆盖 |
| **中风险** | 业务逻辑、状态机 | 主要路径 + 边界 |
| **低风险** | 日志、格式化、辅助函数 | 基本功能验证 |

---

## 优先级决策树

```
函数是否处理外部输入？
├── 是 → 解析/网络 → P0 (最高优先级)
│   └── 边界值、恶意输入、模糊测试
└── 否 → 是否影响核心流程？
    ├── 是 → 业务逻辑 → P1
    │   └── 状态转换、异常处理
    └── 否 → 是否有副作用？
        ├── 是 → I/O 操作 → P2
        │   └── Mock、集成测试
        └── 否 → 工具函数 → P3
            └── 边界条件验证
```

---

## 识别模式

### 高优先级函数特征

```cpp
// P0: 直接处理外部数据
bool parse(const uint8_t* data, size_t len);
Result decode(std::span<const std::byte> buffer);

// P1: 状态转换
void transition(State newState);
bool handleMessage(MessageType type);

// P2: I/O 操作
void asyncRead(ReadCallback cb);
bool sendData(const Buffer& buf);
```

### 低优先级函数特征

```cpp
// P3: 纯工具函数
std::string formatTime(time_t t);
uint32_t crc32(const void* data, size_t len);
```

---

## 函数签名分析

### 输入类型暗示

| 参数类型 | 暗示 | 测试关注点 |
|----------|------|------------|
| `const uint8_t*` | 原始字节流 | 边界、字节序 |
| `std::span<>` | 缓冲区 | 空span、越界 |
| `std::string_view` | 文本输入 | 空串、Unicode |
| `enum` | 状态/类型 | 无效枚举值 |

### 返回类型暗示

| 返回类型 | 暗示 | 测试关注点 |
|----------|------|------------|
| `bool` | 成功/失败 | 两种路径都覆盖 |
| `std::optional<T>` | 可能无结果 | `std::nullopt` 情况 |
| `Result<T, Error>` | 错误处理 | 所有错误码 |
| `void` | 副作用 | 状态变化验证 |
