# TO DO List

- Reconcile renderer output with golden files in `tests/expected/`: they have drifted apart (pre-existing). Current `render_xaml` output differs from the golden files by more than whitespace:
  - `05_tablelayout`: the `Grid` children (`Label`, `TextBox`) are missing from the rendered output (likely a bug).
  - `04_flowlayout`: an extra nested `WrapPanel` is emitted (likely a bug).
  - Vertical `StackPanel`s gain an explicit `Orientation="Vertical"`; `03_dockpanel_like` gains `DockPanel.Dock="Fill"` on `panelMain` and a different attribute order.
- Add a golden-file comparison test: `tests/test_integration.py` imports `get_expected_path` but never compares rendered XAML against `tests/expected/`.
- Extend source encoding detection: apply it to `.resx` parsing (`parse_resx`) once implemented, and add a config-file source (e.g. `winform2wpf.config.json`) so encoding overrides can be shared per repo. Other languages (GBK/GB18030/Shift_JIS) can be added via `--encoding-fallbacks` today, but a heuristic detector may be worth evaluating if real cases exceed the Big5/CP950 scope.

