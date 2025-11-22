.venv) E:\Sach\DuAn\Hinto_Stock>pytest tests/test_signal_generator_strict.py
=================================== test session starts ===================================
platform win32 -- Python 3.13.7, pytest-9.0.1, pluggy-1.6.0 -- E:\Sach\DuAn\Hinto_Stock\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: E:\Sach\DuAn\Hinto_Stock
configfile: pytest.ini
plugins: cov-7.0.0
collected 14 items                                                                         

tests/test_signal_generator_strict.py::TestSignalGeneratorStrictMode::test_strict_mode_enabled_by_default PASSED [  7%]
tests/test_signal_generator_strict.py::TestSignalGeneratorStrictMode::test_strict_mode_can_be_disabled PASSED [ 14%]
tests/test_signal_generator_strict.py::TestSignalGeneratorStrictMode::test_strict_mode_volume_threshold PASSED [ 21%]
tests/test_signal_generator_strict.py::TestSignalGeneratorStrictMode::test_buy_signal_requires_rsi_below_25_strict PASSED [ 28%]
tests/test_signal_generator_strict.py::TestSignalGeneratorStrictMode::test_buy_signal_passes_with_rsi_below_25_strict PASSED [ 35%]
tests/test_signal_generator_strict.py::TestSignalGeneratorStrictMode::test_sell_signal_requires_rsi_above_75_strict PASSED [ 42%]
tests/test_signal_generator_strict.py::TestSignalGeneratorStrictMode::test_sell_signal_passes_with_rsi_above_75_strict PASSED [ 50%]
tests/test_signal_generator_strict.py::TestSignalGeneratorStrictMode::test_strict_mode_requires_3_conditions PASSED [ 57%]
tests/test_signal_generator_strict.py::TestSignalGeneratorStrictMode::test_normal_mode_requires_2_conditions PASSED [ 64%]
tests/test_signal_generator_strict.py::TestSignalGeneratorStrictMode::test_strict_mode_checks_price_vs_ema25 PASSED [ 71%]
tests/test_signal_generator_strict.py::TestSignalGeneratorStrictMode::test_normal_mode_checks_price_vs_ema7 PASSED [ 78%]
tests/test_signal_generator_strict.py::TestSignalGeneratorStrictMode::test_strict_mode_with_filters_integration PASSED [ 85%]
tests/test_signal_generator_strict.py::TestSignalGeneratorStrictMode::test_backward_compatibility_normal_mode PASSED [ 92%]
tests/test_signal_generator_strict.py::TestSignalGeneratorStrictMode::test_strict_mode_reason_messages PASSED [100%]

=================================== 14 passed in 0.94s ====================================
