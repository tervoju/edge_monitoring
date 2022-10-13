#! /bin/bash
cd prometheus-cpp 
submodule init 
git submodule update 
mkdir _build 
cd _build
cmake .. -DBUILD_SHARED_LIBS=ON -DENABLE_PUSH=OFF -DENABLE_COMPRESSION=OFF 
cmake --build . --parallel 4 
ctest -V 
cmake --install . 
cd .. 
cmake .
make .
./main


