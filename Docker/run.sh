#!/bin/bash

# Prompt the usr for the input file path
INPUT_TEXT_FILE=$1
echo "Enter the path to your input file: $1"



# Check if the provided file exists
if [ ! -f "$INPUT_TEXT_FILE" ]; then
    echo "Error: File not found at $INPUT_TEXT_FILE"
    exit 1
fi

python /app/MT-Preparation/subwording/2-subword.py /app/target.model /app/source.model "$INPUT_TEXT_FILE" /app/split_val2023_10kto100k.vi

INPUT_TEXT_FILE+=".subword"

# Run the translation and evaluation commands with GPU if available, otherwise use CPU
if [ -x /usr/bin/nvidia-smi ]; then
    onmt_translate -model /app/model.lovi_step_32000.pt \
    -src "$INPUT_TEXT_FILE" \
    -output /app/UN.vi.translated -gpu 0 -min_length 1
else
    onmt_translate -model /app/model.lovi_step_32000.pt \
    -src "$INPUT_TEXT_FILE" \
    -output /app/UN.vi.translated -min_length 1
fi

python /app/MT-Preparation/subwording/3-desubword.py /app/source.model /app/UN.vi.translated