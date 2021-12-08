#!/usr/bin/python3
# Build Info - https://github.com/djboni/build_info
# MIT License - Copyright (c) 2021 Djones A. Boni

INPUT = input.json
OUTPUT = output

CC = gcc
CFLAGS = -Wall -Wextra

all: $(OUTPUT).o

$(OUTPUT).c: $(INPUT)
	python3 ../../src/build_info.py $(INPUT) $(OUTPUT)

$(OUTPUT).o: $(OUTPUT).c $(OUTPUT).h
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OUTPUT).h $(OUTPUT).c *.o
