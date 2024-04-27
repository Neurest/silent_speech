import time
import threading

import cv2
import pandas as pd
import gradio as gr

from record_data import Recorder


SUBJECT_DB = [
    {
        "id": 0,
        "name": "Minchan Kim",
    },
    {
        "id": 1,
        "name": "Hyun Park",
    },
    {
        "id": 2,
        "name": "Suhwan Choi",
    },
]

TEXT_CORPUS = [
    "The quick brown fox jumps over the lazy dog.",
    "The five boxing wizards jump quickly.",
    "Pack my box with five dozen liquor jugs.",
]


recoder = None
emg_data = None


def emg_recording():
    global recoder, emg_data

    while True:
        time.sleep(1)  # tmp

        if recoder:
            recoder.update()
            emg_data, _, _, _ = recoder.get_data()


def get_emg_plot():
    global emg_data

    if emg_data is None:
        return None
    
    x = range(len(emg_data[0]))

    y0 = emg_data[0]
    y1 = emg_data[1]
    y2 = emg_data[2]
    y3 = emg_data[3]
    y4 = emg_data[4]
    y5 = emg_data[5]
    y6 = emg_data[6]
    y7 = emg_data[7]

    print("y0:", y0)

    plot = gr.LinePlot(
        value=pd.DataFrame({
            "x": x,
            "y0": y0,
            "y1": y1,
            "y2": y2,
            "y3": y3,
            "y4": y4,
            "y5": y5,
            "y6": y6,
            "y7": y7,
        }),
        x="x",
        y="y0",
        title="EMG Plot",
        width=600,
        height=350,
        x_lim=[0, 100],
        y_lim=[-300, 300],
    )
    return plot


def draw_face_guide(im):
    if im is None:
        return im
    return im


with gr.Blocks(css="./data_collection/app_style.css") as demo:
    gr.Markdown("# Data Collection")

    with gr.Row():
        with gr.Column():
            subject_id = gr.Slider(
                label="Subject ID",
                minimum=0,
                maximum=len(SUBJECT_DB) - 1,
                value=0,
                step=1,
            )
            subject_name = gr.Textbox(
                label="Subject Name",
                value=SUBJECT_DB[0]["name"],
            )
            sample_id = gr.Slider(
                label="Sample ID",
                minimum=0,
                maximum=len(TEXT_CORPUS) - 1,
                value=0,
                step=1,
            )
            sentence = gr.Textbox(
                label="Sentence",
                value=TEXT_CORPUS[0],
                interactive=False,
            )
            tts_audio_path = "/Users/alan.k/Desktop/dev/github/silent_speech/data_collection/output/v1.0.0/0_audio.flac"
            tts_audio = gr.Audio(
                label="TTS Audio",
                value=tts_audio_path,
            )
            with gr.Row():
                start_v_emg_recording_button = gr.Button(
                    value="Start V Recording",
                    variant="primary",
                )
                stop_v_emg_recording_button = gr.Button(
                    value="Stop V Recording",
                    variant="stop",
                )
            with gr.Row():
                start_s_emg_recording_button = gr.Button(
                    value="Start S Recording",
                    variant="primary",
                )
                stop_s_emg_recording_button = gr.Button(
                    value="Stop S Recording",
                    variant="stop",
                )
            with gr.Row():
                next_sample_button = gr.Button(
                    value="Next Sample",
                    variant="secondary",
                )
            with gr.Row():
                upload_data_button = gr.Button(
                    value="Upload Data",
                    variant="secondary",
                )
            
        with gr.Column():
            in_video = gr.Image(label="In Video", sources="webcam", streaming=True)
            out_video = gr.Image(label="Out Video")
            audio = gr.Microphone(label="Microphone")
            emg_plot = gr.LinePlot(label="EMG")

    is_recording = gr.State(value=False)

    subject_id.change(
        lambda value: SUBJECT_DB[value]["name"],
        inputs=[subject_id],
        outputs=[subject_name],
        # show_progress=False,
    )

    sample_id.change(
        lambda value: TEXT_CORPUS[value],
        inputs=[sample_id],
        outputs=[sentence],
        # show_progress=False
    )

    in_video.change(
        draw_face_guide,
        inputs=[in_video],
        outputs=[out_video],
        show_progress=False,
        preprocess=False,
        postprocess=False,
        # every=1,
    )

    def start_v_emg_recording():
        global recoder
        recoder = Recorder(debug=True, display=False)
        recoder.__enter__()
        return True

    def stop_v_emg_recording():
        global recoder
        recoder.__exit__(None, None, None)
        recoder = None
        return False

    def start_s_emg_recording():
        global recoder
        recoder = Recorder(debug=True, display=False)
        recoder.__enter__() 
        return True

    def stop_s_emg_recording():
        global recoder
        recoder.__exit__(None, None, None)
        recoder = None
        return False

    def next_sample(sample_id):
        new_sample_id = (sample_id + 1) % len(TEXT_CORPUS)
        new_sentence = TEXT_CORPUS[new_sample_id]
        return new_sample_id, new_sentence
    
    def upload_data():
        return None
    
    start_v_emg_recording_button.click(
        start_v_emg_recording,
        inputs=[],
        outputs=[is_recording],
    )

    stop_v_emg_recording_button.click(
        stop_v_emg_recording,
        inputs=[],
        outputs=[is_recording],
    )

    start_s_emg_recording_button.click(
        start_s_emg_recording,
        inputs=[],
        outputs=[is_recording],
    )

    stop_s_emg_recording_button.click(
        stop_s_emg_recording,
        inputs=[],
        outputs=[is_recording],
    )

    next_sample_button.click(
        next_sample,
        inputs=[sample_id],
        outputs=[sample_id, sentence],
    )

    upload_data_button.click(
        upload_data,
        inputs=[],
        outputs=[],
    )

    demo.load(get_emg_plot, None, emg_plot, every=1e-5)


if __name__ == "__main__":
    recording_thread = threading.Thread(target=emg_recording, daemon=True)
    recording_thread.start()
    demo.queue().launch()
