# RustFuzz - Rust 漏洞挖掘工具

<p align="left">
  <img src="https://img.shields.io/badge/language-Rust-orange.svg" alt="Language">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
</p>

<p align="left">
  <strong>基于 PromeFuzz 框架改进的 Rust 漏洞挖掘工具</strong><br>
  使用大语言模型自动生成高质量的 Rust Fuzz Harness
</p>

---

## 📋 目录

- [项目简介](#-项目简介)
- [核心特性](#-核心特性)
- [系统要求](#-系统要求)
- [快速开始](#-快速开始)
- [完整教程](#-完整教程)
- [高级配置](#-高级配置)
- [常见问题](#-常见问题)
- [文档导航](#-文档导航)
- [贡献指南](#-贡献指南)

---

## 🎯 项目简介

RustFuzz 是专门针对 Rust 生态系统优化的 Fuzzing Harness 自动生成工具。它利用大语言模型 (LLM) 理解 Rust 代码结构、API 语义和所有权系统，自动生成高质量的 fuzz target，帮助开发者快速发现潜在的安全漏洞。

### 适用场景

- ✅ Rust crate 安全性测试
- ✅ unsafe 代码块漏洞挖掘
- ✅ FFI 接口安全性验证
- ✅ 第三方依赖审计
- ✅ 解析器和序列化库测试

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🦀 **Rust 专项优化** | 深度理解所有权、生命周期、trait 系统 |
| 🤖 **AI 驱动生成** | 使用 LLM 智能生成符合习惯的测试代码 |
| ⚡ **全自动流程** | 从代码分析到漏洞发现的端到端自动化 |
| 🎯 **精准测试** | 重点关注 unsafe 代码和高风险区域 |
| 🔧 **易于集成** | 与 Cargo 和 cargo-fuzz 无缝对接 |

---

## 🛠️ 系统要求

### 必需组件

- **Python**: 3.10+
- **Rust**: 最新稳定版 (rustc, cargo)
- **cargo-fuzz**: Rust fuzzing 工具
  ```bash
  cargo install cargo-fuzz
  ```
- **LLVM/Clang**: 用于代码分析

### Python 依赖

详见 [`requirements.txt`](requirements.txt)

---

## 🚀 快速开始

### 第 1 步：安装工具

```bash
# 克隆项目
git clone <repository>
cd RustFuzz

# Windows 用户
.\setup.ps1

# Linux/Mac 用户
./setup.sh
```

### 第 2 步：配置 LLM

编辑 `config.toml` 配置文件：

```toml
[llm]
# OpenAI API 配置
openai_api_key = "your-api-key-here"
openai_api_base = "https://api.openai.com/v1"
openai_model = "gpt-4"

# 或使用 Ollama 本地模型
use_ollama = false
ollama_host = "http://localhost:11434"
ollama_model = "codellama:13b"
```

### 第 3 步：配置目标库

在 `libraries.toml` 中添加你要测试的 Rust crate：

```toml
[my_crate]
language = "rust"
crate_path = "/path/to/your/crate"
source_paths = ["src"]
output_path = "output/my_crate"
```

### 第 4 步：运行工具

```bash
# 1️⃣ 预处理：分析目标 crate 的代码结构
python RustFuzz.py preprocess -L my_crate

# 2️⃣ 理解：使用 LLM 理解 API 语义
python RustFuzz.py comprehend -L my_crate

# 3️⃣ 生成：生成 fuzz target
python RustFuzz.py generate -L my_crate --count 10

# 4️⃣ 执行：运行 fuzzing
python RustFuzz.py fuzz -L my_crate

# 5️⃣ 分析：查看结果
python RustFuzz.py analyze -L my_crate
```

---

## 📚 完整教程

### 工作流程详解

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 预处理阶段   │───▶│ 理解阶段     │───▶│ 生成阶段     │
│ Preprocess  │    │ Comprehend  │    │ Generate    │
└─────────────┘    └─────────────┘    └─────────────┘
      │                   │                   │
      ▼                   ▼                   ▼
   分析AST             理解API             生成代码
   提取类型           建立依赖            编译测试
      │                   │                   │
      └───────────────────┴───────────────────┘
                          │
                          ▼
              ┌─────────────────────┐
              │   执行与分析阶段      │
              │   Fuzz & Analyze    │
              └─────────────────────┘
                          │
                          ▼
                    发现漏洞
```

### 阶段一：预处理

分析 Rust 代码的 AST，提取结构化信息：

```bash
python RustFuzz.py preprocess -L target_crate
```

**输出文件**：
- `{output_path}/ast.json` - AST 分析结果
- `{output_path}/apis.json` - API 列表
- `{output_path}/types.json` - 类型信息

### 阶段二：理解

使用 LLM 理解 API 的语义和使用方式：

```bash
python RustFuzz.py comprehend -L target_crate
```

**工作内容**：
1. 提取 API 文档注释
2. 分析 API 参数和返回值
3. 识别 API 之间的依赖关系
4. 理解 unsafe 代码的安全约束

### 阶段三：生成

生成 fuzz target 代码：

```bash
# 生成指定数量的 fuzz target
python RustFuzz.py generate -L target_crate --count 20

# 生成覆盖所有 API 的 fuzz target
python RustFuzz.py generate -L target_crate --task allcover

# 针对特定函数生成
python RustFuzz.py generate -L target_crate --functions "parse_data,process_input"
```

生成的代码保存在 `{output_path}/fuzz_targets/`

### 阶段四：执行 Fuzzing

```bash
# 编译并运行所有 fuzz target
python RustFuzz.py fuzz -L target_crate

# 运行特定的 fuzz target
python RustFuzz.py fuzz -L target_crate --target fuzz_target_1

# 指定运行时间（秒）
python RustFuzz.py fuzz -L target_crate --timeout 3600
```

### 阶段五：分析结果

```bash
# 分析崩溃
python RustFuzz.py analyze -L target_crate

# 查看统计信息和覆盖率
python RustFuzz.py stats -L target_crate --coverage
```

---

## 🔧 高级配置

### config.toml 配置详解

```toml
[preprocessor]
# 是否提取测试用例作为 API 使用示例
extract_test_cases = true
# 是否分析 unsafe 代码块
analyze_unsafe_blocks = true

[comprehender]
# LLM 配置
embedding_llm = "text-embedding-ada-002"
comprehension_llm = "gpt-4"
# RAG 检索的文档数量
retrieve_top_k = 3

[generator]
# 生成使用的 LLM
generation_llm = "gpt-4"
# 每个 fuzz target 包含的函数数量
function_set_size = 3
# 最大生成轮次
max_rounds = 50
# 是否生成 arbitrary 实现
generate_arbitrary = true

[fuzzer]
# fuzzing 引擎 (libfuzzer, afl++)
engine = "libfuzzer"
# 并行任务数
jobs = 4
# 单个 target 的超时时间（秒）
timeout = 3600
# sanitizer 配置
sanitizers = ["address", "memory"]
```

### libraries.toml 配置示例

```toml
[serde_json]
language = "rust"
crate_path = "/path/to/serde_json"
source_paths = ["src"]
test_paths = ["tests"]
output_path = "output/serde_json"

# 指定要测试的模块
target_modules = ["de", "ser", "value"]

# 排除的路径
exclude_paths = ["benches"]

# 额外的依赖
dependencies = ["serde"]

# Cargo features
features = ["raw_value", "arbitrary_precision"]
```

---

## 🐛 常见问题

<details>
<summary><strong>Q: 生成的 fuzz target 无法编译？</strong></summary>

**A**: 检查以下几点：
1. 确保 `Cargo.toml` 中的依赖版本正确
2. 检查是否需要添加 feature flags
3. 查看生成的代码中是否有未导入的类型
4. 查看日志文件 `logs/` 获取详细错误信息
</details>

<details>
<summary><strong>Q: Fuzzing 没有发现任何 crash？</strong></summary>

**A**: 尝试以下方法：
1. 增加 fuzzing 运行时间
2. 提供初始种子文件到 `corpus/` 目录
3. 调整 fuzz target 的输入生成策略
4. 检查是否启用了合适的 sanitizer (AddressSanitizer, MemorySanitizer)
5. 查看覆盖率信息，确保代码路径被执行
</details>

<details>
<summary><strong>Q: 如何针对 unsafe 代码进行测试？</strong></summary>

**A**: 在 `config.toml` 中启用 `analyze_unsafe_blocks = true`，工具会优先生成测试 unsafe 代码的 target。
</details>

<details>
<summary><strong>Q: LLM API 调用失败？</strong></summary>

**A**: 检查：
1. API Key 是否正确配置
2. 网络连接是否正常
3. API 配额是否充足
4. 考虑使用本地 Ollama 模型作为替代方案
</details>

---

## 📚 文档导航

### 核心文档

| 文档 | 说明 | 适合人群 | 阅读时长 |
|------|------|---------|---------|
| **[快速开始](docs/01-快速开始.md)** ⭐ | 10分钟上手指南 | 新手 | 10分钟 |
| **[完整教程](docs/02-完整教程.md)** ⭐ | 详细使用教程 | 所有人 | 30分钟 |
| **[简单示例](docs/03-简单示例.md)** | 实战案例演示 | 实践者 | 15分钟 |
| **[命令速查](docs/04-命令速查.md)** ⭐ | 快速查找命令 | 日常使用 | 随用随查 |
| **[技术设计](docs/05-技术设计.md)** | 架构和原理 | 开发者 | 20分钟 |
| **[配置说明](docs/06-配置说明.md)** | 配置文件详解 | 进阶用户 | 15分钟 |

### 推荐阅读路径

```
新手路径 🔰
  └─ 快速开始 → 简单示例 → 完整教程

快速上手 ⚡
  └─ 快速开始 → 命令速查 → 实践操作

深入学习 📖
  └─ 完整教程 → 技术设计 → 配置说明
```

---

## 📊 示例项目

`examples/` 目录包含了常见 Rust crate 的配置示例：

- 📦 `serde_json` - JSON 序列化/反序列化
- 🔤 `regex` - 正则表达式引擎
- 🖼️ `image` - 图像处理库
- ⚡ `tokio` - 异步运行时
- 🌐 `hyper` - HTTP 库

查看 [简单示例文档](examples/SIMPLE_EXAMPLE.md) 了解详细用法。

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 如何贡献

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目基于 PromeFuzz 修改，遵循原项目的开源许可证。

---

## 🙏 致谢

- 基于 [PromeFuzz](https://github.com/PrometheusFuzz/PromeFuzz) 框架
- 使用 [tree-sitter-rust](https://github.com/tree-sitter/tree-sitter-rust) 进行代码解析
- 集成 [cargo-fuzz](https://github.com/RustFuzz/cargo-fuzz) 作为 fuzzing 引擎

---

## 📞 获取帮助

- 📖 查看 [完整文档](docs/README.md)
- 💬 提交 [Issue](https://github.com/your-repo/RustFuzz/issues)
- 🔧 查看 `logs/` 目录中的日志文件

---

<p align="center">
  <strong>准备好开始你的 Rust 漏洞挖掘之旅了吗？</strong> 🦀🔍
  <br><br>
  <a href="docs/01-快速开始.md">📖 立即开始 →</a>
</p>
