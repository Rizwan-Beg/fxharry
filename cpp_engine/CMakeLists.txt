cmake_minimum_required(VERSION 3.15)
project(fxharry_cpp_engine)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native")

# Source files
set(EXECUTION_SOURCES
    execution/order_executor.cpp
)

set(SIMULATION_SOURCES
    simulation/market_simulator.cpp
)

# Executables
add_executable(order_executor ${EXECUTION_SOURCES})
add_executable(market_simulator ${SIMULATION_SOURCES})

# Include directories
target_include_directories(order_executor PRIVATE .)
target_include_directories(market_simulator PRIVATE .)

# TODO: Add dependencies as needed:
# - Boost (for networking, async I/O)
# - ZeroMQ (for message passing)
# - Google Protocol Buffers (for serialization)
# - Intel TBB (for parallel processing)
