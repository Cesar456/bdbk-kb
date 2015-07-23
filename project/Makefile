CXX	:= clang++
RM	:= rm -f
MAKEP	:= bdbk/linkbuilder/
CPPFLAGS:= -O3 -std=c++11
SRCS	:= $(MAKEP)max_common_string_in_set.cpp
OBJS	:= $(subst .cpp,.o,$(SRCS))
TARGET	:= $(MAKEP)max_common_string_in_set

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) -o $(TARGET) $(OBJS)

OBJS: $(SRCS)

clean:
	$(RM) $(OBJS)

dist-clean: clean
	$(RM) $(TARGET)
