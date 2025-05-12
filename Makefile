
all: match

match: src/main.cpp src/freq_loader.cpp src/ncd.cpp src/utils.cpp
	g++ -std=c++17 -O2 -o match src/main.cpp src/freq_loader.cpp src/ncd.cpp src/utils.cpp \
         -lz -lbz2 -lzstd -llzma -llzo2 -lsnappy



clean:
	rm -f match
