# wf2wpf（繁體中文）

**wf2wpf** 是一個 Python CLI 工具，用於將 WinForms 的 `*.Designer.cs` 檔案轉換成 WPF 的 `*.xaml` 檔案。此工具的設計原則是「還原版面意圖」（layout intent），而不是單純複製絕對座標。它會根據 WinForms 設計中的線索（如 `Dock`、`FlowLayoutPanel`、`TableLayoutPanel`、排列關係等）推斷出更符合 WPF 慣例的版面容器（`StackPanel`、`DockPanel`、`WrapPanel`、`Grid`）。

## 功能特色

- 解析 WinForms `*.Designer.cs`，建立控制項樹（Control Tree）
- 智慧推斷版面：優先使用 `WrapPanel`、`DockPanel`、`StackPanel`、`Grid`，僅在完全無法推斷時才使用 `Canvas`
- 將常見的 WinForms 控制項與屬性對應至 WPF 等效項目
- 遞迴產生結構正確、含完整命名空間的 WPF XAML
- 產生轉換報告，清楚列出需人工檢查的項目
- 同時適用於現代 .NET WinForms 與舊版 .NET Framework WinForms 專案

## 環境需求

- Python >= 3.11
- [uv](https://github.com/astral-sh/uv)（用於環境與套件管理）

## 安裝與使用方式

### 本地開發環境

```bash
# 進入專案目錄
cd winform2wpf

# 同步開發相依套件
uv sync --dev

# 執行 CLI
uv run wf2wpf --help
uv run wf2wpf convert path/to/Form.Designer.cs
```

### 使用 uvx 從本地目錄執行

```bash
uvx --from . wf2wpf --help
uvx --from . wf2wpf convert path/to/Form.Designer.cs
```

### 使用 uvx 從 Git 執行（未來）

```bash
uvx --from git+https://github.com/<your-repo>/winform2wpf wf2wpf convert path/to/Form.Designer.cs
```

### 使用 uvx 從 PyPI 執行（未來）

```bash
uvx wf2wpf convert path/to/Form.Designer.cs
```

## 開發指令

```bash
# 執行所有單元測試
uv run pytest

# 執行測試並顯示覆蓋率
uv run pytest --cov=src/wf2wpf --cov-report=term-missing

# 驗證 CLI 入口
uv run wf2wpf --help
```

## MVP 限制

- 僅針對 `*.Designer.cs` 中的 `InitializeComponent()` 做解析
- 支援常見控制項：`Label`、`Button`、`TextBox`、`CheckBox`、`RadioButton`、`Panel`、`GroupBox`、`FlowLayoutPanel`、`TableLayoutPanel`、`TabControl` 等
- 不處理執行期動態新增的控制項
- MVP 初版僅提供 `.resx` 處理骨架（暫不完整實作）
- 自訂或第三方控制項可能需要人工調整

## 文件連結

- [開發計畫（英文）](docs/DEVELOPMENT_PLAN_EN.md) / [（繁體中文）](docs/DEVELOPMENT_PLAN_ZH-TW.md)
- [架構設計（英文）](docs/ARCHITECTURE_EN.md) / [（繁體中文）](docs/ARCHITECTURE_ZH-TW.md)
- [測試策略（英文）](docs/TEST_STRATEGY_EN.md) / [（繁體中文）](docs/TEST_STRATEGY_ZH-TW.md)
