# C++ Test Patterns Reference

## GoogleTest Basics

### Fundamental Assertions

```cpp
// Boolean
EXPECT_TRUE(condition);
EXPECT_FALSE(condition);

// Equality
EXPECT_EQ(expected, actual);
EXPECT_NE(val1, val2);

// Comparison
EXPECT_LT(val1, val2);  // <
EXPECT_LE(val1, val2);  // <=
EXPECT_GT(val1, val2);  // >
EXPECT_GE(val1, val2);  // >=

// Strings
EXPECT_STREQ(str1, str2);
EXPECT_STRCASEEQ(str1, str2);

// Floating point
EXPECT_FLOAT_EQ(val1, val2);
EXPECT_NEAR(val1, val2, abs_error);

// Exceptions
EXPECT_THROW(stmt, exception_type);
EXPECT_NO_THROW(stmt);
```

### Test Fixture

```cpp
class ParserTest : public ::testing::Test {
protected:
    void SetUp() override {
        parser_ = std::make_unique<FrameParser>();
    }
    
    void TearDown() override {
        parser_.reset();
    }
    
    std::unique_ptr<FrameParser> parser_;
};

TEST_F(ParserTest, ParsesValidFrame) {
    auto result = parser_->feed(valid_data, sizeof(valid_data));
    EXPECT_TRUE(result);
}
```

### Parameterized Testing

```cpp
class ByteOrderTest : public ::testing::TestWithParam<std::tuple<uint32_t, std::array<uint8_t, 4>>> {};

TEST_P(ByteOrderTest, BigEndianConversion) {
    auto [value, expected_bytes] = GetParam();
    auto result = toBigEndian(value);
    EXPECT_EQ(result, expected_bytes);
}

INSTANTIATE_TEST_SUITE_P(
    ByteOrderCases,
    ByteOrderTest,
    ::testing::Values(
        std::make_tuple(0x12345678, std::array<uint8_t, 4>{0x12, 0x34, 0x56, 0x78}),
        std::make_tuple(0x00000000, std::array<uint8_t, 4>{0x00, 0x00, 0x00, 0x00}),
        std::make_tuple(0xFFFFFFFF, std::array<uint8_t, 4>{0xFF, 0xFF, 0xFF, 0xFF})
    )
);
```

---

## Catch2 Patterns

### Basic Syntax

```cpp
#include <catch2/catch_test_macros.hpp>

TEST_CASE("Parser handles valid input", "[parser]") {
    FrameParser parser;
    
    SECTION("single frame") {
        REQUIRE(parser.feed(single_frame, len));
    }
    
    SECTION("multiple frames") {
        REQUIRE(parser.feed(multi_frame, len));
    }
}
```

### BDD Style

```cpp
SCENARIO("Client connects to server", "[net]") {
    GIVEN("a running server") {
        AsyncTcpServer server(1078);
        server.start();
        
        WHEN("client connects") {
            TcpClient client;
            client.connect("127.0.0.1", 1078);
            
            THEN("connection is accepted") {
                REQUIRE(client.isConnected());
            }
        }
    }
}
```

---

## Protocol Parsing Test Patterns

### Boundary Value Testing

```cpp
TEST(ParserTest, HandlesEmptyInput) {
    FrameParser parser;
    EXPECT_FALSE(parser.feed(nullptr, 0));
}

TEST(ParserTest, HandlesMinimalPacket) {
    std::array<uint8_t, MIN_PACKET_SIZE> minimal = {...};
    EXPECT_TRUE(parser.feed(minimal.data(), minimal.size()));
}

TEST(ParserTest, RejectsOversizedPacket) {
    std::vector<uint8_t> oversized(MAX_PACKET_SIZE + 1);
    EXPECT_FALSE(parser.feed(oversized.data(), oversized.size()));
}
```

### Endianness Testing

```cpp
TEST(ByteUtilTest, ReadBigEndian16) {
    uint8_t data[] = {0x12, 0x34};
    EXPECT_EQ(readBE16(data), 0x1234);
}

TEST(ByteUtilTest, ReadBigEndian32) {
    uint8_t data[] = {0x12, 0x34, 0x56, 0x78};
    EXPECT_EQ(readBE32(data), 0x12345678);
}
```

### Fragmentation and Reassembly Testing

```cpp
TEST(FragmentTest, ReassemblesMultipleFragments) {
    FrameParser parser;
    
    // First packet
    parser.feed(fragment_first, len1);
    EXPECT_FALSE(parser.hasCompleteFrame());
    
    // Middle packet
    parser.feed(fragment_middle, len2);
    EXPECT_FALSE(parser.hasCompleteFrame());
    
    // Last packet
    parser.feed(fragment_last, len3);
    EXPECT_TRUE(parser.hasCompleteFrame());
    
    auto frame = parser.getFrame();
    EXPECT_EQ(frame.size(), expected_total_size);
}
```

---

## Asynchronous Code Testing

### Using std::promise

```cpp
TEST(AsyncServerTest, AcceptsConnection) {
    std::promise<bool> connected;
    auto future = connected.get_future();
    
    server.setSessionHandler([&](auto session) {
        connected.set_value(true);
    });
    
    // Mock client connection
    TcpClient client;
    client.connect("127.0.0.1", 1078);
    
    EXPECT_EQ(future.wait_for(std::chrono::seconds(5)), std::future_status::ready);
    EXPECT_TRUE(future.get());
}
```

### Timeout Protection

```cpp
TEST(TimeoutTest, Operation completes in time) {
    auto start = std::chrono::steady_clock::now();
    
    // Perform operation
    auto result = performAsyncOperation();
    
    auto elapsed = std::chrono::steady_clock::now() - start;
    EXPECT_LT(elapsed, std::chrono::seconds(5));
}
```

---

## Mock Objects

### GoogleMock Example

```cpp
class MockDataCallback {
public:
    MOCK_METHOD(void, onData, (const uint8_t*, size_t), ());
};

TEST(CallbackTest, Invokes callback on data) {
    MockDataCallback mock;
    EXPECT_CALL(mock, onData(_, Gt(0)))
        .Times(AtLeast(1));
    
    parser.setCallback([&](const uint8_t* data, size_t len) {
        mock.onData(data, len);
    });
    
    parser.feed(test_data, sizeof(test_data));
}
```
