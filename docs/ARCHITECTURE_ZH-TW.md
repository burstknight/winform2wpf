# 架構設計（繁體中文）

## 概述

本文件說明 **wf2wpf** 的模組結構、資料模型、版面推斷、XAML 渲染與打包設計。

工具採用以下轉換流程：**解析（Parse）→ 分析（Analyze）→ 對應（Map）→ 渲染（Render）→ 報告（Report）**

```text
Designer.cs → parser.py（Control Tree） → analyzer.py（版面推斷）
→ mapper.py（屬性對應） → renderer.py（XAML）＋ report.py（報告）
→ CLI（wf2wpf convert）
```

## 目錄結構

```text
winform2wpf/
├── src/
│   └── wf2wpf/
│       ├── __init__.py      # 套件中繼資料與版本
│       ├── analyzer.py      # 版面推斷邏輯
│       ├── cli.py           # CLI 入口點
│       ├── mapper.py        # WinForms -> WPF 對應
│       ├── parser.py        # 解析 Designer.cs
│       ├── renderer.py      # 產生 XAML
│       ├── report.py        # 轉換報告
│       └── resources.py     # .resx 處理（僅骨架）
├── tests/
│   ├── fixtures/           # 合成 Designer.cs 樣本
│   ├── expected/           # Golden XAML 預期檔
│   ├── test_*.py           # 單元測試與整合測試
│   └── conftest.py
├── docs/                   # 雙語文件
├── pyproject.toml          # uv 與 hatchling 設定
├── rules.yaml              # 對應規則表
└── README*.md              # 雙語 README
```

## 核心模組

### parser.py

職責：
- 讀取 `*.Designer.cs`
- 擷取 `InitializeComponent()` 區塊
- 蒐集欄位宣告與 `new` 建立語句
- 擷取屬性設定（`Location`、`Size`、`Dock`、`Anchor`、`Text`、`TabIndex`、`Enabled`、`Visible`）
- 擷取父子關係（`Controls.Add`）
- 重建控制項樹

主要資料結構（使用 `dataclasses`，註解全英文，採用 Google docstring）：
- `Control`：代表單一 WinForms 控制項
- `ControlTree`：根節點容器與樹狀結構輔助方法

解析方式：MVP 採用**針對性 regex**。此方式對排版與 Visual Studio 產生的格式較具彈性。

### analyzer.py

職責：針對每個容器逐一推斷最適合的 WPF 版面容器。

推斷優先順序：
1. `FlowLayoutPanel` → `WrapPanel`
2. `TableLayoutPanel` → `Grid`（並產生欄列定義）
3. 有明顯 `Dock` 意圖（`Top/Bottom/Left/Right/Fill`）→ `DockPanel`
4. 子元素形成水平／垂直鏈 → `StackPanel`（`Horizontal`／`Vertical`）
5. 其他情況 → `Grid` 搭配 `Margin` 與對齊（預設不使用 `Canvas`）
6. Fallback → `Grid`

輸出：每個容器的 `panel_type`、`orientation`、`column_defs`、`row_defs` 等參數，並將推斷理由納入報告。

### mapper.py

職責：將 WinForms 型別與屬性對應至 WPF 對應值。

代表性對應：
- `Form` → `Window`（根元素）
- `UserControl` → `UserControl`
- `Name` → `x:Name`
- `Label/Button/CheckBox/RadioButton.Text` → `Content`
- `TextBox.Text` → `Text`
- `Enabled` → `IsEnabled`
- `Visible` → `Visibility`（`true/false` 對應 `Visible/Collapsed`）
- `Dock` → `DockPanel.Dock`
- `TabIndex` → `TabIndex`

對應規則儘量集中於 `rules.yaml` 管理。

### renderer.py

職責：根據 Control Tree 與 analyzer 結果遞迴產生 WPF XAML。

規格：
- 必要命名空間：`xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"`、`xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"`
- 根元素：Form 對應 `<Window>`（可包含 `Title`、`x:Name` 等）
- 依容器推斷結果產生對應 Panel，並正確附加版面屬性（`DockPanel.Dock`、`Grid.Row/Grid.Column` 等）
- 使用 `xml.etree.ElementTree` 建構與驗證 XML 結構
- 輸出格式正確的 XAML 文字

### report.py

職責：產生轉換報告。

報告內容：
- **已轉換（Converted）**：控制項清單（型別、名稱）
- **建議檢查（Needs review）**：字型、Anchor 細節、自訂／第三方控制項、未明確對應屬性等
- **略過／未對應（Skipped/Unmapped）**：暫不支援的型別或屬性
- **版面推斷決策（Layout decisions）**：每個容器的推斷結果與簡短理由
- **警告（Warnings）**：潛在問題

支援純文字（預設）與 JSON（未來）。文字輸出可搭配 `rich` 呈現。

### cli.py

入口函式：`def main() -> None:`，對應 `pyproject.toml` 中的 `wf2wpf = "wf2wpf.cli:main"`。

支援指令：
- `wf2wpf convert <input.Designer.cs> [--output <out.xaml>] [--report] [--report-format text|json]`
- `wf2wpf --help`、`wf2wpf --version`

行為：
- 路徑解析、串接 parser/analyzer/mapper/renderer/report
- 寫入 XAML 檔案
- 視需求輸出報告至 stdout
- 錯誤訊息採用清晰英文

### resources.py

`.resx` 處理的預留模組。僅包含最小骨架與英文 TODO 註解，MVP 不實作。

## 資料模型概念

- `Control.name`：WinForms 控制項名稱（可能為 `None`）
- `Control.type_name`：型別名稱（完整或簡短）
- `Control.children`：子控制項列表（樹狀結構）
- `Control.dock/anchor/location/size`：版面相關屬性
- `Control.column/row/column_span/row_span`：TableLayoutPanel 相關資訊
- `Control.properties_raw`：保留未處理的屬性設定，用於報告

## 打包與 uvx 支援

`pyproject.toml` 設定重點：
- `[build-system]`：`hatchling>=1.25.0`
- `[project.scripts]`：`wf2wpf = "wf2wpf.cli:main"`
- `[tool.hatch.build.targets.wheel]`：僅打包 `["src/wf2wpf"]`
- 開發相依：`pytest`、`pytest-cov`、`rich`、`pyyaml`

支援方式：
- `uv run wf2wpf ...`（本地開發）
- `uvx --from . wf2wpf ...`（從本地隔離執行）
- `uvx --from git+... wf2wpf ...`（從 Git 遠端執行）
- `uvx wf2wpf ...`（未來發佈至 PyPI 後執行）
