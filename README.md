# Stable Path Problem (SPP) Benchmark

Prepare AS-level topology datasets:

``` bash
make prepare
```

Generate test results:

``` bash
# create a directory to save results
mkdir -p pickle

# run test
python3 -m spp_benchmark.test --as-rel data/20200701.as-rel.txt --as-country data/as-country.txt --save-dir pickle
```
