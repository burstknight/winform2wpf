# 開發計畫（繁體中文）

## 概述

**wf2wpf** 是一個以 Python 實作的 CLI 工具，用於將 WinForms 的 `*.Designer.cs` 檔案轉換成 WPF 的 `*.xaml` 檔案。核心原則是：「還原版面意圖」（infer layout intent），而不是複製絕對座標。

本工具優先產生符合 WPF 自動排版慣例的容器（`WrapPanel`、`DockPanel`、`StackPanel`、`Grid`），僅在版面推斷完全失敗時才以 `Canvas` 作為最後的 fallback。

## 目標

- 提供半自動化轉換，減少將 WinForms UI 重刻為 WPF UI 所需的重複工作
- 產出人類可讀且易於後續編輯的 WPF XAML
- 同時支援現代 .NET WinForms 與舊版 .NET Framework WinForms（兩者的 `Designer.cs` 格式大致相容）
- 採用 `uv` + `pytest`，並以合成測試樣本與 Golden File 確保可測試性
- 支援未來以 `uvx` 執行（使用 `hatchling` 建構、採用 `src/` 佈局）

## MVP 範圍

### 包含

- [ ] 解析單一 `*.Designer.cs` 並建立控制項樹（Control Tree）
- [ ] 抽取：控制項名稱、型別、位置、大小、父子關係、`Dock`、`Anchor`、`TabIndex`、`Text`、`Enabled`、`Visible`
- [ ] 版面推斷優先順序：`WrapPanel`（FlowLayoutPanel） > `DockPanel`（Dock 意圖） > `StackPanel`（水平/垂直鏈） > `Grid`（TableLayoutPanel 或 fallback）
- [ ] 基本控制項：`Label`、`Button`、`TextBox`、`CheckBox`、`RadioButton`、`Panel`、`GroupBox`
- [ ] 常見容器：`FlowLayoutPanel`、`TableLayoutPanel`、`TabControl`（結構感知）
- [ ] 產生合法的 WPF XAML（含必要命名空間）
- [ ] 產生轉換報告（已轉換／建議檢查／未對應）
- [ ] CLI：`wf2wpf convert <input.Designer.cs> [--output ...] [--report] [--report-format text|json]`

### 不包含（MVP）

- 完整的 `.resx` 圖片／圖示轉換（僅保留骨架）
- 執行期動態新增的控制項
- 像素級完全還原
- 自動編譯產生的 WPF 專案
- 第三方或自訂控制項的深度對應（僅列入報告）

## 版面推斷規則

| 優先順序 | 條件 | WPF 容器 | 備註 |
|---|---|---|---|
| 1 | 容器為 `FlowLayoutPanel` | `WrapPanel` | 最接近 FlowLayout 的流動＋換行行為 |
| 2 | 容器為 `TableLayoutPanel` 且有欄列定義 | `Grid` | 根據 `ColumnStyles/RowStyles` 產生 `ColumnDefinitions/RowDefinitions`（Absolute/Auto/Percent 對應 px/Auto/*） |
| 3 | 子元素明顯使用 `Dock = Top/Bottom/Left/Right/Fill` | `DockPanel` | 適合工具列、側邊欄、主內容等框架式排版 |
| 4 | 子元素呈現明顯的「水平鏈」或「垂直鏈」（Y 或 X 座標近似、間距規律） | `StackPanel`（`Horizontal`／`Vertical`） | 鼓勵使用自動排版而非絕對位置 |
| 5 | 無法明確歸類 | `Grid` 搭配 `Margin` 與 `HorizontalAlignment/VerticalAlignment` | 預設不使用 `Canvas`，較符合 WPF 思路且易於後續調整 |
| Fallback | 極端邊角情況 | `Grid` | 保險機制 |

## 開發階段

1. **規劃＋骨架（本階段）**：雙語文件、`pyproject.toml`、`src/` 模組骨架、`rules.yaml`、合成樣本＋Golden File、pytest 測試
2. **Parser 實作**：以 regex 為主解析 `Designer.cs` 中的 `InitializeComponent()`，建立 Control Tree
3. **Analyzer 實作**：依據推斷規則針對每個容器選擇最適合的 WPF 容器
4. **Mapper＋Renderer 實作**：屬性對應與遞迴產生 XAML
5. **Report＋CLI 實作**：轉換報告與 CLI 功能完善
6. **驗證與調整**：執行 `uv run pytest` 驗證骨架與邏輯；未來以真實樣本微調

## 風險與因應

- **Regex 與 AST 的取捨**：初版採用針對性 regex，除錯與調整較容易。若日後遇到複雜情況再考慮改用 `tree-sitter-c-sharp`
- **版面歸類模糊**：傾向使用 `Grid+Margin` 而非 `Canvas`，並將推斷決策記錄於報告中
- **.NET Framework 差異**：採用純文字解析且僅抓取關鍵語句，對舊版 `Designer.cs` 格式較具彈性。待取得真實樣本再補充案例
- **過度通用化**：規則採用明確條件，並配合單元測試逐一驗證

## 非功能性需求

- Python 程式碼：註解一律用英文，docstring 採用 Google 格式，全面加上 Type Hints
- 文件雙語（英文＋繁體中文）
- 僅在本地執行 git commit，不執行 git push
- 變動幅度較大時分多次 commit
- 使用 `uv` 管理環境，使用 `pytest` 撰寫與執行測試
- 採用 `src/wf2wpf` 佈局，配合 `hatchling` 建構系統以支援 `uvx`
