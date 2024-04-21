import os
import json
import argparse
from glob import glob
from tqdm import tqdm
from transformers import pipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Translation')
    parser.add_argument('--input_folder', default='data/emg_data', help='Input folder')
    parser.add_argument('--output_folder', default='data/ko_emg_data', help='Output folder')
    args = parser.parse_args()

    pipe = pipeline("translation", model="Helsinki-NLP/opus-mt-tc-big-en-ko")
    pipe.to('cuda')

    for info_path in tqdm(glob(f"{args.input_folder}/**/*_info.json", recursive=True)):
        info = json.load(open(info_path))

        out_file_path = info_path.replace(args.input_folder, args.output_folder).replace('_info.json', '_ko.txt')
        os.makedirs(os.path.dirname(out_file_path), exist_ok=True)

        text = info['text']
        if isinstance(text, str) and len(text) > 0:
            text_ko = pipe("2, 4, 6 etc. are even numbers.")
            with open(out_file_path, 'w') as f:
                f.write(text_ko)
