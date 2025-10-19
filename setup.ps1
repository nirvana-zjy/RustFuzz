# RustFuzz 快速启动脚本 (Windows)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  RustFuzz - Rust 漏洞挖掘工具快速启动" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ 未找到 Python，请先安装 Python 3.10+" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python 已安装" -ForegroundColor Green

# 检查 Rust
if (!(Get-Command rustc -ErrorAction SilentlyContinue)) {
    Write-Host "❌ 未找到 Rust，请先安装 Rust 工具链" -ForegroundColor Red
    Write-Host "   访问: https://rustup.rs/" -ForegroundColor Yellow
    exit 1
}
$rustVersion = rustc --version
Write-Host "✅ Rust 已安装: $rustVersion" -ForegroundColor Green

# 检查 cargo-fuzz
if (!(Get-Command cargo-fuzz -ErrorAction SilentlyContinue)) {
    Write-Host "⚠️  未找到 cargo-fuzz" -ForegroundColor Yellow
    $response = Read-Host "是否现在安装? (y/n)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        cargo install cargo-fuzz
    } else {
        Write-Host "请手动安装: cargo install cargo-fuzz" -ForegroundColor Yellow
        exit 1
    }
}
Write-Host "✅ cargo-fuzz 已安装" -ForegroundColor Green

# 安装 Python 依赖
Write-Host ""
Write-Host "正在安装 Python 依赖..." -ForegroundColor Cyan
pip install -r requirements.txt

# 检查配置文件
if (!(Test-Path "config.toml")) {
    Write-Host ""
    Write-Host "⚠️  未找到 config.toml" -ForegroundColor Yellow
    $response = Read-Host "是否创建默认配置? (y/n)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        python RustFuzz.py configure --init
    }
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  🎉 RustFuzz 环境准备完成！" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步:" -ForegroundColor Yellow
Write-Host "1. 编辑 config.toml 配置 LLM API"
Write-Host "2. 编辑 libraries.toml 添加目标 crate"
Write-Host "3. 运行: python RustFuzz.py preprocess -L <library>"
Write-Host ""
Write-Host "查看完整教程: Get-Content TUTORIAL.md"
Write-Host "================================================" -ForegroundColor Cyan
