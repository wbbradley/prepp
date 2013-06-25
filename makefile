BUILD_DIR = build

CFLAGS := \
	-I. \
	-c \
	-Wall \
	-pthread \
	-DDEBUG \
	-g \

PREPP = python prepp.py cpp 
PREPPII = python prepp.py match 

all: build-dir build/test

build-dir:
	@if test ! -d $(BUILD_DIR); then mkdir -p $(BUILD_DIR); fi

build/test.cpp: test.prepp
	$(PREPP) $< > $@

build/test.ii: build/test.cpp
	clang -x c++ -E $< > $@

build/test: build/test.ii
	clang -x c++ $< -g -o $@

CLEAN = rm -rf $(BUILD_DIR)

clean:
	$(CLEAN)

