CXX	:= g++
RM	:= rm -f
CPPFLAGS:= -O3 -std=c++11
SRCS 	:= $(wildcard *.cpp)

all: $(SRCS:.cpp=)

.cpp:
	$(CXX) $(CPPFLAGS) $< -o $@

clean:
	$(RM) $(subst .cpp,,$(wildcard *.cpp))
