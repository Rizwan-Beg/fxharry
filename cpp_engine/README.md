# C++ Execution Engine

Optional high-performance C++ modules for ultra-low latency trading operations.

## Building

```bash
mkdir build
cd build
cmake ..
make
```

## Modules

- **execution/**: Order execution engine for HFT scenarios
- **simulation/**: High-performance market simulation

## Future Enhancements

- Direct broker API integration
- Memory-mapped I/O for market data
- Lock-free data structures
- CPU affinity pinning
- SIMD optimizations
- Custom network stack for low latency
