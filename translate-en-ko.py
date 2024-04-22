import os
import json
import argparse
from glob import glob
from tqdm import tqdm
import transformers
import torch


def translation(text):
    messages = [
        {"role": "system", "content": "너는 21세기 최고의 영어->한국어 번역가야. 오직 한국어만 말할 수 있어."},
        {"role": "user", "content": f"다음 문장을 오직 한국어로만 번역하고, 답은 번역한 문장만 줘. \n 번역 문장: {text}"},
    ]
    prompt = pipeline.tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
    )
    outputs = pipeline(
        prompt,
        max_new_tokens=256,
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
    )
    return outputs[0]["generated_text"][len(prompt):]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Translation')
    parser.add_argument('--input_folder', default='data/emg_data', help='Input folder')
    parser.add_argument('--output_folder', default='data/ko_emg_data', help='Output folder')
    args = parser.parse_args()

    # model_id = "meta-llama/Meta-Llama-3-70B-Instruct"
    # model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
    model_id = "NousResearch/Meta-Llama-3-8B-Instruct"
    pipeline = transformers.pipeline(
        "text-generation",
        model=model_id,
        model_kwargs={"torch_dtype": torch.bfloat16},
        device="cuda",
    )

    terminators = [
        pipeline.tokenizer.eos_token_id,
        pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]

    for info_path in tqdm(glob(f"{args.input_folder}/**/*_info.json", recursive=True)):
        info = json.load(open(info_path))

        out_file_path = info_path.replace(args.input_folder, args.output_folder).replace('_info.json', '_ko.txt')
        os.makedirs(os.path.dirname(out_file_path), exist_ok=True)

        text = info['text']
        if isinstance(text, str) and len(text) > 0:
            text_ko = translation(text)
            print(f"Input: {text}")
            print(f"Output: {text_ko}")

            with open(out_file_path, 'w') as f:
                f.write(text_ko)
