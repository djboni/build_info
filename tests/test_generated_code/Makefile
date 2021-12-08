#!/usr/bin/python3
# Build Info - https://github.com/djboni/build_info
# MIT License - Copyright (c) 2021 Djones A. Boni

INPUT = info.json
OUTPUT = info

CC = gcc
CFLAGS = -Wall -Wextra
OBJ = $(OUTPUT).o main.o
EXEC = main

all: run

$(OUTPUT).c: $(INPUT)
	python3 ../../src/build_info.py $(INPUT) $(OUTPUT)

%.o: %.c $(OUTPUT).h
	$(CC) $(CFLAGS) -c $< -o $@

$(EXEC): $(OBJ)
	$(CC) $(OBJ) -o $(EXEC)

run: $(EXEC)
	./$(EXEC)

clean:
	rm -f $(OUTPUT).h $(OUTPUT).c *.o $(EXEC)
