import time
import json
import threading
from enum import Enum

import cv2
import pandas as pd
import gradio as gr
from glob import glob

from record_data import Recorder


## Data ##
DATA_DIR = "./data_collection/emg_data"
KO_DATA_DIR = "./data_collection/ko_emg_data"
TTS_DATA_DIR = "./data_collection/tts_emg_data"
INTERMEDIATE_DIR = "voiced_parallel_data/5-4"

FILES = glob(f"{DATA_DIR}/{INTERMEDIATE_DIR}/*.json")
KO_FILES = glob(f"{KO_DATA_DIR}/{INTERMEDIATE_DIR}/*.txt")
TTS_FILES = glob(f"{TTS_DATA_DIR}/{INTERMEDIATE_DIR}/*.wav")

def read_data():
    data = []

    for ko_file in KO_FILES:
        index = ko_file.split("/")[-1].split("_")[0]

        file = f"{DATA_DIR}/{INTERMEDIATE_DIR}/{index}_info.json"

        with open(file, "r") as f:
            info = json.load(f)
            sentence_en = info["text"]

        with open(ko_file, "r") as f:
            sentence_kr = f.read()

        tts_audio_path = f"{TTS_DATA_DIR}/{INTERMEDIATE_DIR}/{index}_tts.wav"

        sample = {
            "original_index": int(index),
            "sentence_en": sentence_en,
            "sentence_kr": sentence_kr,
            "tts_audio_path": tts_audio_path,
        }

        data.append(sample)

    data = sorted(data, key=lambda x: x["original_index"])

    return data

DATA = read_data()

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


## Style ##
EMG_PLOT_WIDTH = 600
EMG_PLOT_HEIGHT = 100


## Progress ##
class Progress(Enum):
    START = "START"
    VOCALIZED_SPEECH_RECORDING_IN_PROGRESS = "VOCALIZED_SPEECH_RECORDING_IN_PROGRESS"
    VOCALIZED_SPEECH_RECORDING_DONE = "VOCALIZED_SPEECH_RECORDING_DONE"
    SILENT_SPEECH_RECORDING_IN_PROGRESS = "SILENT_SPEECH_RECORDING_IN_PROGRESS"
    SILENT_SPEECH_RECORDING_DONE = "SILENT_SPEECH_RECORDING_DONE"


PROGRESS_INSTRUCTION_MAP = {
    Progress.START.value: "Step 1. Press Vocalized Speech Button",
    Progress.VOCALIZED_SPEECH_RECORDING_IN_PROGRESS.value: "Step 2. Press Stop Button",
    Progress.VOCALIZED_SPEECH_RECORDING_DONE.value: "Step 3. Press Silent Speech Button",
    Progress.SILENT_SPEECH_RECORDING_IN_PROGRESS.value: "Step 4. Press Stop Button",
    Progress.SILENT_SPEECH_RECORDING_DONE.value: "Step 5. Press Next Sample Button",
}


## EMG Recording ##
recoder = None
emg_data = None


def emg_recording():
    global recoder, emg_data

    while True:
        time.sleep(1)  # TODO (alan): is this necessary?

        if recoder:
            recoder.update()
            emg_data, _, _, _ = recoder.get_data()


def get_emg_plot():
    global emg_data

    if emg_data is None:
        return None

    x = range(len(emg_data[0]))

    df0 = pd.DataFrame({
        "Time": x,
        "Amplitude": emg_data[0],
        "Channel": "Channel 0",
    })
    df1 = pd.DataFrame({
        "Time": x,
        "Amplitude": emg_data[1],
        "Channel": "Channel 1",
    })
    df2 = pd.DataFrame({
        "Time": x,
        "Amplitude": emg_data[2],
        "Channel": "Channel 2",
    })
    df3 = pd.DataFrame({
        "Time": x,
        "Amplitude": emg_data[3],
        "Channel": "Channel 3",
    })
    df4 = pd.DataFrame({
        "Time": x,
        "Amplitude": emg_data[4],
        "Channel": "Channel 4",
    })
    df5 = pd.DataFrame({
        "Time": x,
        "Amplitude": emg_data[5],
        "Channel": "Channel 5",
    })
    df6 = pd.DataFrame({
        "Time": x,
        "Amplitude": emg_data[6],
        "Channel": "Channel 6",
    })
    df7 = pd.DataFrame({
        "Time": x,
        "Amplitude": emg_data[7],
        "Channel": "Channel 7",
    })
    df = pd.concat([df0, df1, df2, df3, df4, df5, df6, df7], axis=0)

    print(df)

    emg_plot = gr.LinePlot(
        value=df,
        x="Time",
        y="Amplitude",
        color="Channel",
        color_legend_position="bottom",
        title="EMG",
        tooltip=["Time", "Amplitude", "Channel"],
        width=EMG_PLOT_WIDTH,
        height=EMG_PLOT_HEIGHT,
        x_lim=[0, 15],
        y_lim=[-500, 500],
        container=False,
    )

    return emg_plot


## Utility Functions ##
def draw_face_guide(im):
    if im is None:
        return im
    H, W, _ = im.shape
    im = cv2.ellipse(im, (W//2, H//2), (300, 400), 0, 0, 360, (255, 0, 0), 2)
    return im


def save_data(emg_data, audio, video, sample_id, subject_id, speech_type):
    # TODO (alan): implement this function
    pass


## Gradio ##
with gr.Blocks(title="EMG Data Collection", css="./data_collection/style.css") as demo:

    with gr.Row():

        with gr.Column(scale=99):
            gr.HTML(value="<h1>EMG Data Collection</h1>")

        with gr.Column(scale=1, min_width=150, variant="compact"):
            subject_id = gr.Dropdown(
                label="Subject ID",
                choices=[subject["id"] for subject in SUBJECT_DB],
                value=SUBJECT_DB[0]["id"],
            )

        with gr.Column(scale=1, min_width=150, variant="compact"):
            subject_name = gr.Textbox(
                label="Subject Name",
                value=SUBJECT_DB[0]["name"],
                interactive=False,
            )

    with gr.Row():

        with gr.Column(scale=55):

            with gr.Row():
                sample_id = gr.Slider(
                    label="Sample ID",
                    minimum=0,
                    maximum=len(DATA) - 1,
                    value=0,
                    step=1,
                )

            with gr.Row():
                sentence = gr.Label(
                    label="Sentence (en)",
                    show_label=False,
                    value=DATA[0]["sentence_en"],
                )

            with gr.Row():
                tts_audio = gr.Audio(
                    label="TTS Audio",
                    show_label=False,
                    value=DATA[0]["tts_audio_path"],
                    interactive=False,
                    autoplay=True,
                )

            with gr.Row():
                sentence_kr = gr.Textbox(
                    label="Translation",
                    value=DATA[0]["sentence_kr"],
                    interactive=False,
                )

            with gr.Row():
                progress = gr.Textbox(
                    label="Steps",
                    value=PROGRESS_INSTRUCTION_MAP[Progress.START.value],
                    interactive=False,
                )

            with gr.Row():

                with gr.Column(min_width=50) as start_v_emg_recording_column:
                    start_v_emg_recording_button = gr.Button(
                        value="Vocalized Speech",
                        variant="primary",
                        size="lg",
                    )

                with gr.Column(min_width=50, visible=False) as stop_v_emg_recording_column:
                    stop_v_emg_recording_button = gr.Button(
                        value="Stop",
                        variant="stop",
                        size="lg",
                    )

                with gr.Column(min_width=50) as start_s_emg_recording_column:
                    start_s_emg_recording_button = gr.Button(
                        value="Silent Speech",
                        variant="primary",
                        size="lg",
                    )

                with gr.Column(min_width=50, visible=False) as stop_s_emg_recording_column:
                    stop_s_emg_recording_button = gr.Button(
                        value="Stop",
                        variant="stop",
                        size="lg",
                    )

                with gr.Column(min_width=50):
                    next_sample_button = gr.Button(
                        value="Next Sample",
                        variant="secondary",
                        size="lg",
                    )
            
        with gr.Column(scale=45):

            with gr.Row():
                microphone = gr.Microphone(
                    label="Microphone",
                    scale=70,
                )
                webcam = gr.Image(
                    label="Webcam",
                    sources="webcam",
                    streaming=True,
                    scale=30,
                )

            with gr.Row():
                emg_plot = gr.LinePlot(
                    label="EMG",
                    width=EMG_PLOT_WIDTH,
                    height=EMG_PLOT_HEIGHT,
                )

    is_recording = gr.State(value=False)
    current_progress = gr.Textbox(value=Progress.START.value, visible=False)

    def start_v_emg_recording(progress):
        if progress not in [Progress.START.value, Progress.VOCALIZED_SPEECH_RECORDING_DONE.value]:
            gr.Warning("You already finished vocalized speech recording.")
            return {
                is_recording: False,
                current_progress: progress,
                start_v_emg_recording_column: gr.Column(visible=True),
                stop_v_emg_recording_column: gr.Column(visible=False),
            }
        
        global recoder
        # recoder = Recorder(debug=True, display=False)
        # recoder.__enter__()
        return {
            is_recording: True,
            current_progress: Progress.VOCALIZED_SPEECH_RECORDING_IN_PROGRESS.value,
            start_v_emg_recording_column: gr.Column(visible=False),
            stop_v_emg_recording_column: gr.Column(visible=True),
        }

    def stop_v_emg_recording():
        global recoder
        # TODO (alan): save EMG data
        # emg_data, _, _, _ = recoder.get_data()
        # save_data(emg_data, audio, video, sample_id, subject_id, "vocalized")
        # recoder.__exit__(None, None, None)
        # recoder = None
        return {
            is_recording: False,
            current_progress: Progress.VOCALIZED_SPEECH_RECORDING_DONE.value,
            start_v_emg_recording_column: gr.Column(visible=True),
            stop_v_emg_recording_column: gr.Column(visible=False),
        }

    def start_s_emg_recording(progress):
        if progress not in [Progress.VOCALIZED_SPEECH_RECORDING_DONE.value, Progress.SILENT_SPEECH_RECORDING_DONE.value]:
            gr.Warning("You must finish vocalized speech recording first.")
            return {
                is_recording: False,
                current_progress: progress,
                start_s_emg_recording_column: gr.Column(visible=True),
                stop_s_emg_recording_column: gr.Column(visible=False),
            }

        global recoder
        # recoder = Recorder(debug=True, display=False)
        # recoder.__enter__()
        return {
            is_recording: True,
            current_progress: Progress.SILENT_SPEECH_RECORDING_IN_PROGRESS.value,
            start_s_emg_recording_column: gr.Column(visible=False),
            stop_s_emg_recording_column: gr.Column(visible=True),
        }

    def stop_s_emg_recording():
        global recoder
        # TODO (alan): save EMG data
        # emg_data, _, _, _ = recoder.get_data()
        # save_data(emg_data, audio, video, sample_id, subject_id, "silent")
        # recoder.__exit__(None, None, None)
        # recoder = None
        return {
            is_recording: False,
            current_progress: Progress.SILENT_SPEECH_RECORDING_DONE.value,
            start_s_emg_recording_column: gr.Column(visible=True),
            stop_s_emg_recording_column: gr.Column(visible=False),
        }

    def next_sample(progress, sample_id: int):
        if progress != Progress.SILENT_SPEECH_RECORDING_DONE.value:
            gr.Warning("You must finish both vocalized and silent speech recording first.")
            return sample_id

        new_sample_id = (sample_id + 1) % len(DATA)
        return new_sample_id
    
    def update_sample_id(sample_id: int):
        next_sentence = DATA[sample_id]["sentence_en"]
        next_sentence_kr = DATA[sample_id]["sentence_kr"]
        next_tts_audio_path = DATA[sample_id]["tts_audio_path"]
        next_progress = Progress.START.value
        return next_sentence, next_sentence_kr, next_tts_audio_path, next_progress
    
    def update_progress(progress):
        return PROGRESS_INSTRUCTION_MAP[progress]
    
    start_v_emg_recording_button.click(
        start_v_emg_recording,
        inputs=[current_progress],
        outputs=[is_recording, current_progress, start_v_emg_recording_column, stop_v_emg_recording_column],
    )

    stop_v_emg_recording_button.click(
        stop_v_emg_recording,
        inputs=[],
        outputs=[is_recording, current_progress, start_v_emg_recording_column, stop_v_emg_recording_column],
    )

    start_s_emg_recording_button.click(
        start_s_emg_recording,
        inputs=[current_progress],
        outputs=[is_recording, current_progress, start_s_emg_recording_column, stop_s_emg_recording_column],
    )

    stop_s_emg_recording_button.click(
        stop_s_emg_recording,
        inputs=[],
        outputs=[is_recording, current_progress, start_s_emg_recording_column, stop_s_emg_recording_column],
    )

    next_sample_button.click(
        next_sample,
        inputs=[current_progress, sample_id],
        outputs=[sample_id],
    )

    subject_id.change(
        lambda value: SUBJECT_DB[value]["name"],
        inputs=[subject_id],
        outputs=[subject_name],
        show_progress=False,
    )

    sample_id.change(
        update_sample_id,
        inputs=[sample_id],
        outputs=[sentence, sentence_kr, tts_audio, current_progress],
        show_progress=False,
    )

    current_progress.change(
        update_progress,
        inputs=[current_progress],
        outputs=[progress],
    )

    demo.load(
        get_emg_plot,
        None,
        emg_plot,
        every=1e-5,
    )


if __name__ == "__main__":
    recording_thread = threading.Thread(target=emg_recording, daemon=True)
    recording_thread.start()
    demo.queue().launch()
