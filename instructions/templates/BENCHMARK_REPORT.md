# Benchmark report template

Question and representative workload; source/specification IDs; dataset hash and
licensing; host CPU/RAM/storage/network; OS/toolchain/dependency versions; exact
build flags; correctness tests run first; warm-up/cold-cache policy; threading and
NUMA placement; workload size and burst profile; measurement clock; repetitions;
p50/p95/p99/max latency, throughput, allocations, memory and error bounds; durability
level and what start/end timestamps measure; saturation/backpressure/failure cases;
baseline implementation and fair comparison; raw result artifact hashes; limitations.

A blank template is not a measured benchmark. Do not claim network, database, UI or
provider latency from a local arithmetic microbenchmark.
