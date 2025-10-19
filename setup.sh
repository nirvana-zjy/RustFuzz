#!/bin/bash
# RustFuzz 快速启动脚本

echo "================================================"
echo "  RustFuzz - Rust 漏洞挖掘工具快速启动"
echo "================================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python 3.10+"
    exit 1
fi
echo "✅ Python3 已安装"

# 检查 Rust
if ! command -v rustc &> /dev/null; then
    echo "❌ 未找到 Rust，请先安装 Rust 工具链"
    echo "   运行: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    exit 1
fi
echo "✅ Rust 已安装: $(rustc --version)"

# 检查 cargo-fuzz
if ! command -v cargo-fuzz &> /dev/null; then
    echo "⚠️  未找到 cargo-fuzz"
    read -p "是否现在安装? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cargo install cargo-fuzz
    else
        echo "请手动安装: cargo install cargo-fuzz"
        exit 1
    fi
fi
echo "✅ cargo-fuzz 已安装"

# 安装 Python 依赖
echo ""
echo "正在安装 Python 依赖..."
pip install -r requirements.txt

# 检查配置文件
if [ ! -f "config.toml" ]; then
    echo ""
    echo "⚠️  未找到 config.toml"
    read -p "是否创建默认配置? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python RustFuzz.py configure --init
    fi
fi

echo ""
echo "================================================"
echo "  🎉 RustFuzz 环境准备完成！"
echo "================================================"
echo ""
echo "下一步:"
echo "1. 编辑 config.toml 配置 LLM API"
echo "2. 编辑 libraries.toml 添加目标 crate"
echo "3. 运行: python RustFuzz.py preprocess -L <library>"
echo ""
echo "查看完整教程: cat TUTORIAL.md"
echo "================================================"
