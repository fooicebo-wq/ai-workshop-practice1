# ============================================================
#  AI 工作坊環境一鍵安裝腳本
#  作者：集思室內設計 GIS DESIGN
#  用法：在 PowerShell 執行以下指令
#  irm https://raw.githubusercontent.com/fooicebo-wq/ai-workshop-practice1/master/install.ps1 | iex
# ============================================================

$ErrorActionPreference = "Stop"

function Write-Step { param($msg) Write-Host "`n▶ $msg" -ForegroundColor Cyan }
function Write-OK   { param($msg) Write-Host "  ✅ $msg" -ForegroundColor Green }
function Write-SKIP { param($msg) Write-Host "  ⏭️  $msg (已安裝，略過)" -ForegroundColor Yellow }
function Write-FAIL { param($msg) Write-Host "  ❌ $msg" -ForegroundColor Red }

Clear-Host
Write-Host @"
╔══════════════════════════════════════════╗
║   AI 工作坊  一鍵安裝工具  v1.0          ║
║   集思室內設計 GIS DESIGN                ║
╚══════════════════════════════════════════╝
"@ -ForegroundColor Magenta

Write-Host "  安裝項目：Node.js、Wrangler、GitHub CLI、MCP SDK" -ForegroundColor Gray
Write-Host "  預計時間：3-5 分鐘" -ForegroundColor Gray
Write-Host ""
Read-Host "  按 Enter 開始安裝..."

# ── 1. Node.js ──────────────────────────────────────────────
Write-Step "安裝 Node.js LTS"
try {
    $nodeVer = node --version 2>$null
    if ($nodeVer) { Write-SKIP "Node.js $nodeVer" }
} catch {
    Write-Host "  正在下載安裝 Node.js..." -ForegroundColor Gray
    winget install --id OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements
    # 重新整理 PATH
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
    Write-OK "Node.js 安裝完成"
}

# ── 2. 更新 PATH ─────────────────────────────────────────────
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")

# ── 3. Wrangler CLI ──────────────────────────────────────────
Write-Step "安裝 Wrangler CLI（Cloudflare 部署工具）"
try {
    $wVer = wrangler --version 2>$null
    if ($wVer) { Write-SKIP "Wrangler $wVer" }
} catch {
    npm install -g wrangler | Out-Null
    Write-OK "Wrangler 安裝完成"
}

# ── 4. GitHub CLI ────────────────────────────────────────────
Write-Step "安裝 GitHub CLI"
try {
    $ghVer = gh --version 2>$null
    if ($ghVer) { Write-SKIP ($ghVer | Select-Object -First 1) }
} catch {
    winget install --id GitHub.cli --silent --accept-package-agreements --accept-source-agreements
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
    Write-OK "GitHub CLI 安裝完成"
}

# ── 5. MCP SDK & 相依套件 ────────────────────────────────────
Write-Step "安裝 MCP 相依套件（@modelcontextprotocol/sdk、zod）"
npm install -g @modelcontextprotocol/sdk zod node-fetch 2>$null | Out-Null
Write-OK "MCP 套件安裝完成"

# ── 6. puppeteer-cli（HTML 轉 PDF）──────────────────────────
Write-Step "安裝 puppeteer-cli（HTML 轉 PDF）"
npm install -g puppeteer-cli 2>$null | Out-Null
Write-OK "puppeteer-cli 安裝完成"

# ── 完成 ─────────────────────────────────────────────────────
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")

Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   🎉  所有工具安裝完成！                 ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

# 版本確認
Write-Host "  安裝結果確認：" -ForegroundColor Cyan
try { Write-Host "  Node.js  : $(node --version)" -ForegroundColor White } catch { Write-Host "  Node.js  : 請重新開啟終端機" -ForegroundColor Yellow }
try { Write-Host "  npm      : $(npm --version)" -ForegroundColor White } catch {}
try { Write-Host "  Wrangler : $(wrangler --version)" -ForegroundColor White } catch { Write-Host "  Wrangler : 請重新開啟終端機" -ForegroundColor Yellow }
try { Write-Host "  gh       : $((gh --version)[0])" -ForegroundColor White } catch { Write-Host "  gh       : 請重新開啟終端機" -ForegroundColor Yellow }

Write-Host ""
Write-Host "  ⚠️  請關閉並重新開啟 PowerShell 讓設定生效" -ForegroundColor Yellow
Write-Host ""
Write-Host "  下一步：" -ForegroundColor Cyan
Write-Host "  1. wrangler login    # 登入 Cloudflare" -ForegroundColor Gray
Write-Host "  2. gh auth login     # 登入 GitHub" -ForegroundColor Gray
Write-Host ""
Read-Host "  按 Enter 關閉..."
