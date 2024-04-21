import os
import json
import argparse
from glob import glob
from tqdm import tqdm
from TTS.api import TTS

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TTS')
    parser.add_argument('--tts_model', default='tts_models/multilingual/multi-dataset/xtts_v2', help='TTS model')
    parser.add_argument('--input_folder', default='data/emg_data', help='Input folder')
    parser.add_argument('--output_folder', default='data/tts_emg_data', help='Output folder')
    parser.add_argument('--speaker_voice', default='voice_template/nemo.wav', help='Speaker voice')
    parser.add_argument('--language', default='en', help='Language')
    args = parser.parse_args()

    tts = TTS(args.tts_model)
    tts.to('cuda')

    for info_path in tqdm(glob(f"{args.input_folder}/**/*_info.json", recursive=True)):
        info = json.load(open(info_path))

        out_file_path = info_path.replace(args.input_folder, args.output_folder).replace('_info.json', '_tts.wav')
        os.makedirs(os.path.dirname(out_file_path), exist_ok=True)

        text = info['text']
        if isinstance(text, str) and len(text) > 0:
            tts.tts_to_file(
                text=text,
                file_path=out_file_path,
                speaker_wav=args.speaker_voice,
                language=args.language
            )