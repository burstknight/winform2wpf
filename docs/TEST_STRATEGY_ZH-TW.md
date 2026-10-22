# 測試策略（繁體中文）

## 目標

- 確保 parser、analyzer、mapper、renderer、CLI 的正確性
- 在調整版面推斷規則時能及早發現 regression
- 以合成測試樣本驗證行為，不需依賴真實公司樣本
- 測試快速且具決定性
- 符合 `uv` + `pytest` 的開發流程

## 測試類型

- **單元測試（Unit）**：針對個別模組（parser/analyzer/mapper/renderer）進行測試，使用小型的構造輸入
- **整合測試（Integration）**：從 `Designer.cs` 到 XAML 的端對端測試，針對合成樣本比對 Golden File，採用結構性斷言

## 測試資料

`tests/fixtures/` 下的合成樣本涵蓋以下代表性版面：

| 編號 | 檔名 | 情境 | 預期 Panel |
|---|---|---|---|
| 01 | `01_simple_form.Designer.cs` | 簡單表單（Label + TextBox + Button） | `StackPanel`（垂直）或 `Grid` |
| 02 | `02_horizontal_buttons.Designer.cs` | 水平按鈕群組 | `StackPanel`（Horizontal） |
| 03 | `03_dockpanel_like.Designer.cs` | 類 Dock 佈局（Top/Left/Fill） | `DockPanel` |
| 04 | `04_flowlayout.Designer.cs` | 類 FlowLayoutPanel 流動排列 | `WrapPanel` |
| 05 | `05_tablelayout.Designer.cs` | TableLayoutPanel 表單欄位 | `Grid`（含欄列定義） |
| 06 | `06_nested_panel.Designer.cs` | 巢狀容器 | 每個容器各自獨立推斷 |
| 07 | `07_modern_style.Designer.cs` | 不帶 `this.` 前綴的設計師檔 | 與傳統寫法結果相同 |
| 08 | `08_colors.Designer.cs` | 群組與子項的 ForeColor/BackColor | `Foreground`/`Background` 與顏色繼承 |
| 09 | `09_fonts.Designer.cs` | 字型大小與樣式 | `FontFamily`/`FontSize`/`FontWeight`/`FontStyle` |

`tests/expected/` 存放各案例對應的預期 XAML 結構（Golden File）。

## 測試檔案

- `tests/test_parser.py`：控制項抽取、屬性、父子關係、樹狀結構
- `tests/test_analyzer.py`：版面推斷規則（FlowLayout→WrapPanel、TableLayout→Grid、Dock→DockPanel、鏈狀→StackPanel、fallback→Grid）
- `tests/test_mapper.py`：型別與屬性對應（Text→Content、x:Name、Visibility/IsEnabled、Dock）
- `tests/test_renderer.py`：命名空間、根元素、Panel 類型、巢狀結構、版面屬性、XML 可解析性
- `tests/test_styles.py`：色彩與字型轉換（具名色、`Color.FromArgb`、系統色、字型家族／大小／樣式）
- `tests/test_integration.py`：端對端測試，針對 Golden File 進行結構性比對
- `tests/test_xaml_load.py`：以真正的 WPF 解析器（透過 Windows PowerShell 5.1 呼叫 `System.Windows.Markup.XamlReader`）解析 Golden XAML；缺少 PowerShell 或 WPF 組件時自動略過
- `tests/conftest.py`：共用 fixture 與輔助函式（載入 fixtures/expected、暫存路徑等）

## Golden File 比對原則

採用**結構性斷言（structural assertion）**而非逐字元比對：

- 驗證根元素與預期 Panel 類型是否存在
- 驗證原本有 WinForms Name 的控制項是否產生 `x:Name`
- 驗證關鍵屬性（`Content`、`Text`、`DockPanel.Dock`、`Grid.Row`、`Grid.Column` 等）
- 驗證巢狀結構是否與 Control Tree 一致
- 驗證產出的 XAML 可用 `xml.etree.ElementTree.parse` 正確解析

這樣可避免因空白、屬性順序或排版微調而造成不必要的測試失敗。

## 執行測試

```bash
# 同步開發環境
uv sync --dev

# 執行全部測試
uv run pytest

# 詳細輸出
uv run pytest -v

# 顯示覆蓋率
uv run pytest --cov=src/wf2wpf --cov-report=term-missing

# 執行特定測試檔
uv run pytest tests/test_analyzer.py -v
```

## 驗收標準

- `uv run pytest` 全部通過（回傳 0）
- `uv run wf2wpf --help` 正常顯示說明
- `uvx --from . wf2wpf --help` 正常顯示說明（驗證打包設定）
- 套件不會意外從 `tests/` 匯入模組
- 測試能有效驗證「版面意圖」推斷（尤其是 `StackPanel`、`DockPanel`、`WrapPanel`、`Grid` 的選擇邏輯）
