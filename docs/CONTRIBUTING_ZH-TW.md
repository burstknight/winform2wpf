# 維護指南（繁體中文）

## 概述

本文件記錄此儲存庫的維護流程與注意事項。所有參與此專案的人員（包含 AI agent）都必須遵守。英文版本請見 [CONTRIBUTING_EN.md](CONTRIBUTING_EN.md)。

## 開發環境

- 以 `uv` 管理環境（參見 `pyproject.toml` 與 `uv.lock`）
- 同步環境：`uv sync --dev`
- 執行測試：`uv run pytest`
- 執行 CLI：`uv run wf2wpf --help`

## Git 規則

### 可以 commit，但絕不 push

- 修改專案時可以建立 commit
- 絕不執行 `git push`；push 由維護者自行決定與執行

### 大幅度變更拆成多個 commit

- 若變更幅度較大，應拆成多個邏輯 commit
- 每個 commit 必須能單獨成立：程式碼一致、測試通過

### Commit message 必須說明「改了什麼」和「為什麼改」

- Subject 行：conventional prefix（`feat:`、`fix:`、`docs:`、`doc:`、`test:`、`chore:`）＋colon 後大寫開頭（沿用既有 git 歷史風格）
- Body：實際修改了什麼、為什麼需要這個變更
- 範例：

  ```
  fix: Capture form-level Name/Text in parser

  The parser previously ignored properties assigned on the form itself,
  so the generated XAML lost the window title and root name.
  ```

## 每次 Commit 前的驗證

1. `uv sync --dev`
2. `uv run pytest` — 所有測試必須通過才能 commit

## CHANGELOG 紀律

- 任何程式碼變動（修正錯誤、新增功能、行為改變）都必須更新 `CHANGELOG.md` 的 `## [Unreleased]`，並放入正確分類：
  - `[Added]` — 新增功能
  - `[Changed]` — 既有行為的變更
  - `[Fixed]` — 錯誤修正
  - `[Security]`、`[Removed]`、`[Deprecated]` — 依情況使用
- 值得注意的文件新增也可以記錄

## TODO.md

- 若本次變更過程中發現後續需要處理的事項（已知不足、未來改善、待重構），請新增到 `TODO.md`，避免遺漏

## 文件政策

- 對外文件必須提供英文與繁體中文成對版本：
  - `docs/*_EN.md` + `docs/*_ZH-TW.md`
  - `README_EN.md` + `README_ZH-TW.md`
- 更新文件時兩個語言版本必須同步修改
- 程式碼註解與 docstring 可使用英文撰寫（Google-style docstring）
