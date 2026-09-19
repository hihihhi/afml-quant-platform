# C++ system bootstrap

This directory is the actual-system side of the repository. It currently contains
only a C++20 build/status scaffold and a Python exact-arithmetic errata oracle.
It does not contain a functioning quant platform. The CLI rejects unimplemented
backtesting/trading commands rather than returning invented results.

```sh
cmake -S system -B build/native -DCMAKE_BUILD_TYPE=Debug
cmake --build build/native --parallel
ctest --test-dir build/native --output-on-failure
build/native/afml-platform --status
python system/reference/covariance_counterexample.py
```

Book-derived component code belongs here after its source/specification gates are
reviewed. Feature, strategy, model, formula and benchmark specification templates
are in `instructions/templates/`. Python tooling/oracles are not the selected
production backend. C/C++ ports need readable code and measured equivalence, not
literal transcription of the book's compressed Python style.
