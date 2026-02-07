# Function Categorization Guide

## Categorization Dimensions

### 1. By Responsibility

| Category | Keywords | Examples |
|------|--------|------|
| **Parsing/Encoding** | `parse`, `decode`, `serialize`, `deserialize` | `parseFrame()`, `decodeHeader()` |
| **Network I/O** | `send`, `receive`, `read`, `write`, `connect` | `asyncRead()`, `sendPacket()` |
| **State Management** | `set`, `get`, `update`, `transition` | `setState()`, `getStatus()` |
| **Callback/Event** | `on`, `callback`, `handler`, `notify` | `onDataReceived()`, `handleEvent()` |
| **Utility/Conversion** | `to`, `from`, `convert`, `format` | `toBigEndian()`, `formatTime()` |
| **Lifecycle** | `init`, `start`, `stop`, `close`, `reset` | `initialize()`, `shutdown()` |

### 2. By Complexity

| Grade | Features | Test Strategy |
|------|----------|--------------|
| **Simple** | Pure functions, no side effects | Unit testing, parameterized testing |
| **Medium** | Dependent on internal state | Fixture + State verification |
| **Complex** | Async, multi-threaded, I/O | Mocking + Integration testing |

### 3. By Risk Level

| Grade | Identification | Testing Requirement |
|------|----------|--------------|
| **High Risk** | Security related, calculations, protocols | 100% branch coverage |
| **Medium Risk** | Business logic, state machines | Main path + Boundaries |
| **Low Risk** | Logging, formatting, helpers | Basic functional verification |

---

## Priority Decision Tree

```
Does the function handle external input?
├── Yes → Parsing/Network → P0 (Highest Priority)
│   └── Boundary values, malicious input, fuzzing
└── No → Does it affect core flow?
    ├── Yes → Business logic → P1
    │   └── State transitions, exception handling
    └── No → Does it have side effects?
        ├── Yes → I/O operation → P2
        │   └── Mocking, integration testing
        └── No → Utility function → P3
            └── Boundary condition verification
```

---

## Identification Patterns

### High Priority Function Features

```cpp
// P0: Directly handles external data
bool parse(const uint8_t* data, size_t len);
Result decode(std::span<const std::byte> buffer);

// P1: State transitions
void transition(State newState);
bool handleMessage(MessageType type);

// P2: I/O operations
void asyncRead(ReadCallback cb);
bool sendData(const Buffer& buf);
```

### Low Priority Function Features

```cpp
// P3: Pure utility functions
std::string formatTime(time_t t);
uint32_t crc32(const void* data, size_t len);
```

---

## Function Signature Analysis

### Input Type Hints

| Parameter Type | Hint | Test Focus |
|----------|------|------------|
| `const uint8_t*` | Raw byte stream | Boundaries, endianness |
| `std::span<>` | Buffer | Empty span, out of bounds |
| `std::string_view` | Text input | Empty string, Unicode |
| `enum` | State/Type | Invalid enum values |

### Return Type Hints

| Return Type | Hint | Test Focus |
|----------|------|------------|
| `bool` | Success/Failure | Both paths covered |
| `std::optional<T>` | May have no result | `std::nullopt` case |
| `Result<T, Error>` | Error handling | All error codes |
| `void` | Side effects | State change verification |
