# RustFuzz 简单示例

这是一个完整的示例，展示如何使用 RustFuzz 测试一个简单的 Rust 库。

## 示例库：simple_parser

假设我们有一个简单的解析器库：

### 1. 目标代码结构

```
simple_parser/
├── Cargo.toml
└── src/
    └── lib.rs
```

`src/lib.rs`:
```rust
pub fn parse_int(s: &str) -> Result<i32, String> {
    s.parse::<i32>()
        .map_err(|e| format!("Parse error: {}", e))
}

pub fn parse_list(s: &str) -> Result<Vec<i32>, String> {
    s.split(',')
        .map(|part| part.trim().parse::<i32>())
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| format!("Parse error: {}", e))
}

pub unsafe fn parse_unsafe(ptr: *const u8, len: usize) -> Result<String, String> {
    if ptr.is_null() {
        return Err("Null pointer".to_string());
    }
    
    let slice = std::slice::from_raw_parts(ptr, len);
    String::from_utf8(slice.to_vec())
        .map_err(|e| format!("UTF-8 error: {}", e))
}
```

### 2. 配置 RustFuzz

`libraries.toml`:
```toml
[simple_parser]
language = "rust"
crate_path = "examples/simple_parser"
source_paths = ["src"]
output_path = "output/simple_parser"
api_hints = [
    "parse_int() 解析整数字符串",
    "parse_list() 解析逗号分隔的整数列表",
    "parse_unsafe() 是 unsafe 函数，需要特别测试"
]
```

### 3. 运行 RustFuzz

```bash
# 预处理
python RustFuzz.py preprocess -L simple_parser

# 生成 fuzz target
python RustFuzz.py generate -L simple_parser --count 3

# 运行 fuzzing
python RustFuzz.py fuzz -L simple_parser --timeout 600
```

### 4. 生成的 Fuzz Target 示例

`output/simple_parser/fuzz_targets/fuzz_target_1.rs`:
```rust
#![no_main]
use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: &[u8]| {
    // 转换为字符串
    if let Ok(s) = std::str::from_utf8(data) {
        // 测试 parse_int
        let _ = simple_parser::parse_int(s);
        
        // 测试 parse_list
        let _ = simple_parser::parse_list(s);
    }
});
```

`output/simple_parser/fuzz_targets/fuzz_target_2.rs`:
```rust
#![no_main]
use libfuzzer_sys::fuzz_target;
use arbitrary::Arbitrary;

#[derive(Arbitrary, Debug)]
struct Input {
    data: Vec<u8>,
    offset: usize,
}

fuzz_target!(|input: Input| {
    if input.data.is_empty() {
        return;
    }
    
    let len = input.data.len().saturating_sub(input.offset);
    if len == 0 {
        return;
    }
    
    // 测试 unsafe 函数
    unsafe {
        let ptr = input.data.as_ptr().add(input.offset.min(input.data.len()));
        let _ = simple_parser::parse_unsafe(ptr, len);
    }
});
```

### 5. 预期结果

运行 fuzzing 后可能发现：

1. **整数溢出**: `parse_int("999999999999999999")`
2. **空字符串**: `parse_list("")`
3. **无效 UTF-8**: `parse_unsafe()` 传入无效字节序列
4. **边界条件**: 非常长的输入

### 6. 查看结果

```bash
# 查看统计
python RustFuzz.py stats -L simple_parser

# 分析 crash
python RustFuzz.py analyze -L simple_parser
```

输出示例：
```
==========================================================
代码分析统计
==========================================================
函数: 3
结构体: 0
枚举: 0
Trait: 0
Unsafe 块: 1
==========================================================
Fuzz Target 统计
==========================================================
已生成: 3
==========================================================
发现 2 个 crash
- crash-001: parse_int integer overflow
- crash-002: parse_unsafe invalid UTF-8
==========================================================
```

## 完整工作流程演示

```bash
# 1. 环境准备
./setup.sh

# 2. 配置
# 编辑 config.toml 和 libraries.toml

# 3. 预处理
python RustFuzz.py preprocess -L simple_parser

# 4. 生成
python RustFuzz.py generate -L simple_parser --count 5 --task allcover

# 5. Fuzzing (运行 10 分钟)
python RustFuzz.py fuzz -L simple_parser --timeout 600

# 6. 分析
python RustFuzz.py analyze -L simple_parser
python RustFuzz.py stats -L simple_parser

# 7. 复现 crash
cd output/simple_parser/fuzz_project
cargo fuzz run fuzz_target_1 ../../../artifacts/crash-xxx
```

## 手动优化示例

如果生成的 fuzz target 不够理想，可以手动编辑：

```rust
#![no_main]
use libfuzzer_sys::fuzz_target;
use arbitrary::Arbitrary;

#[derive(Arbitrary, Debug)]
struct ParseInput {
    int_str: String,
    list_str: String,
}

fuzz_target!(|input: ParseInput| {
    // 测试不同长度的输入
    for len in 0..input.int_str.len() {
        let _ = simple_parser::parse_int(&input.int_str[..len]);
    }
    
    // 测试列表解析
    let _ = simple_parser::parse_list(&input.list_str);
    
    // 测试边界情况
    let _ = simple_parser::parse_int("");
    let _ = simple_parser::parse_int("-");
    let _ = simple_parser::parse_int("0");
});
```

## 总结

这个简单示例展示了：
1. ✅ 如何配置 RustFuzz
2. ✅ 如何生成和运行 fuzz target
3. ✅ 如何分析结果
4. ✅ 如何手动优化

对于更复杂的项目，流程是相同的，只是需要：
- 更详细的配置
- 更多的 fuzz target
- 更长的运行时间
- 更深入的分析
