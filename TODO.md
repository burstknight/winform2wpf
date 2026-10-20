# TO DO List

- Populate the conversion report: `generate_report` never fills `converted`/`needs_review`/`unmapped`, so `wf2wpf convert --report` always prints zeros even though the conversion succeeded.
- Parse `ColumnStyles`/`RowStyles` styles: `SizeType.Absolute` pixel sizes should render as literal pixel values (`Width="123"`), and mixed `Percent` sizes should map to proportional star lengths; today all definitions are equal `*` (fine for the uniform percent layouts seen so far).
- Extend source encoding detection: apply it to `.resx` parsing (`parse_resx`) once implemented, and add a config-file source (e.g. `winform2wpf.config.json`) so encoding overrides can be shared per repo. Other languages (GBK/GB18030/Shift_JIS) can be added via `--encoding-fallbacks` today, but a heuristic detector may be worth evaluating if real cases exceed the Big5/CP950 scope.
- Validate WPF load-time behavior: the golden test proves well-formed XAML, but nothing compiles/loads the output (no .NET toolchain in this repo yet); a smoke test opening the rendered window would catch property or attached-property errors.
- Evaluate layout heuristics against more real-world samples: the linear/scattered thresholds (20px) are untested outside the current fixtures; larger corpora may need tunable rules (e.g. via `rules.yaml`).
