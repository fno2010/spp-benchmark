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

# plot graphs
python3 -m spp_benchmark.plot pickle
```

You can also use Docker without having to install python/networkx in the following way:
```bash
# compile the docker file, which will set up the correct environment, this can take a minute
docker build -t spp-benchmark .

# run the docker file, to enter the bash environment
docker run -it -v `pwd`:`pwd` -w `pwd` spp-benchmark /bin/bash

# now, you can execute the python3 commands from above, for testing, ploting, etc
```
