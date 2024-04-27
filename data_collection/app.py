import time
import threading
from enum import Enum

import cv2
import pandas as pd
import gradio as gr

from record_data import Recorder


## Constants ##
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

TEXT_CORPUS_EN = [
    "The quick brown fox jumps over the lazy dog.",
    "The five boxing wizards jump quickly.",
    "Pack my box with five dozen liquor jugs.",
]

TEXT_CORPUS_KR = [
    "빠른 갈색 여우가 게으른 개를 뛰어넘습니다.",
    "다섯 명의 복싱 마법사들이 빨리 뛰어넘습니다.",
    "내 상자에는 다섯 다스의 술병이 들어 있습니다.",
]

DATA_DIR = "./data_collection/emg_data"

EMG_PLOT_WIDTH = 600

EMG_PLOT_HEIGHT = 100


## Progress ##
class Progress(Enum):
    START = 0
    LISTEN_TTS_AUDIO_DONE = 1
    VOCALIZED_SPEECH_RECORDING_DONE = 2
    SILENT_SPEECH_RECORDING_DONE = 3


PROGRESS_INSTRUCTION_MAP = {
    Progress.START.value: "Press TTS Audio Button (0/3)",
    Progress.LISTEN_TTS_AUDIO_DONE.value: "Press Vocalized Speech Recording button (1/3)",
    Progress.VOCALIZED_SPEECH_RECORDING_DONE.value: "Press Silent Speech Recording Button (2/3)",
    Progress.SILENT_SPEECH_RECORDING_DONE.value: "Press Next Sample Button (3/3)",
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
        return (None,) * 8

    x = range(len(emg_data[0]))

    df = pd.DataFrame({
        "x": x,
        "y0": emg_data[0],
        "y1": emg_data[1],
        "y2": emg_data[2],
        "y3": emg_data[3],
        "y4": emg_data[4],
        "y5": emg_data[5],
        "y6": emg_data[6],
        "y7": emg_data[7],
    })

    print(df)

    emg_c0_plot = gr.LinePlot(
        value=df,
        x="x",
        y="y0",
        title="EMG C0",
        width=EMG_PLOT_WIDTH,
        height=EMG_PLOT_HEIGHT,
        x_lim=[0, 15],
        y_lim=[-500, 500],
    )
    emg_c1_plot = gr.LinePlot(
        value=df,
        x="x",
        y="y1",
        title="EMG C1",
        width=EMG_PLOT_WIDTH,
        height=EMG_PLOT_HEIGHT,
        x_lim=[0, 15],
        y_lim=[-500, 500],
    )
    emg_c2_plot = gr.LinePlot(
        value=df,
        x="x",
        y="y2",
        title="EMG C2",
        width=EMG_PLOT_WIDTH,
        height=EMG_PLOT_HEIGHT,
        x_lim=[0, 15],
        y_lim=[-500, 500],
    )
    emg_c3_plot = gr.LinePlot(
        value=df,
        x="x",
        y="y3",
        title="EMG C3",
        width=EMG_PLOT_WIDTH,
        height=EMG_PLOT_HEIGHT,
        x_lim=[0, 15],
        y_lim=[-500, 500],
    )
    emg_c4_plot = gr.LinePlot(
        value=df,
        x="x",
        y="y4",
        title="EMG C4",
        width=EMG_PLOT_WIDTH,
        height=EMG_PLOT_HEIGHT,
        x_lim=[0, 15],
        y_lim=[-500, 500],
    )
    emg_c5_plot = gr.LinePlot(
        value=df,
        x="x",
        y="y5",
        title="EMG C5",
        width=EMG_PLOT_WIDTH,
        height=EMG_PLOT_HEIGHT,
        x_lim=[0, 15],
        y_lim=[-500, 500],
    )
    emg_c6_plot = gr.LinePlot(
        value=df,
        x="x",
        y="y6",
        title="EMG C6",
        width=EMG_PLOT_WIDTH,
        height=EMG_PLOT_HEIGHT,
        x_lim=[0, 15],
        y_lim=[-500, 500],
    )
    emg_c7_plot = gr.LinePlot(
        value=df,
        x="x",
        y="y7",
        title="EMG C7",
        width=EMG_PLOT_WIDTH,
        height=EMG_PLOT_HEIGHT,
        x_lim=[0, 15],
        y_lim=[-500, 500],
    )

    return emg_c0_plot, emg_c1_plot, emg_c2_plot, emg_c3_plot, emg_c4_plot, emg_c5_plot, emg_c6_plot, emg_c7_plot


## Utility Functions ##
def draw_face_guide(im):
    if im is None:
        return im
    H, W, _ = im.shape
    im = cv2.ellipse(im, (W//2, H//2), (300, 400), 0, 0, 360, (255, 0, 0), 2)
    return im


## Gradio ##
with gr.Blocks(title="Data Collection", css="./data_collection/style.css") as demo:

    with gr.Row():

        with gr.Column():
            gr.Markdown("# Data Collection")

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

    with gr.Row():

        with gr.Column(scale=50):
            sample_id = gr.Slider(
                label="Sample ID",
                minimum=0,
                maximum=len(TEXT_CORPUS_EN) - 1,
                value=0,
                step=1,
            )
            sentence = gr.Label(
                label="Sentence (en)",
                value=TEXT_CORPUS_EN[0],
            )
            sentence_kr = gr.Textbox(
                label="Sentence (kr)",
                value=TEXT_CORPUS_KR[0],
                interactive=False,
            )
            progress = gr.Textbox(
                label="Progress",
                value=PROGRESS_INSTRUCTION_MAP[Progress.START.value],
                interactive=False,
            )
            with gr.Row():
                listen_tts_audio_button = gr.Button(
                    value="▶ TTS Audio",
                    variant="secondary",
                )
                start_v_emg_recording_button = gr.Button(
                    value="Vocalized Speech Recording",
                    variant="primary",
                )
                stop_v_emg_recording_button = gr.Button(
                    value="Stop",
                    variant="stop",
                    visible=False,
                )
                start_s_emg_recording_button = gr.Button(
                    value="Silent Speech Recording",
                    variant="primary",
                )
                stop_s_emg_recording_button = gr.Button(
                    value="Stop",
                    variant="stop",
                    visible=False,
                )
                next_sample_button = gr.Button(
                    value="Next Sample",
                    variant="secondary",
                )
            
        with gr.Column(scale=50):
            with gr.Row():
                microphone = gr.Microphone(
                    label="Microphone",
                    scale=2,
                )
                webcam = gr.Image(
                    label="Webcam",
                    sources="webcam",
                    streaming=True,
                    scale=1,
                )
            with gr.Row():
                emg_c0 = gr.LinePlot(
                    label="EMG C0",
                    width=EMG_PLOT_WIDTH,
                    height=EMG_PLOT_HEIGHT,
                )
                emg_c1 = gr.LinePlot(
                    label="EMG C1",
                    width=EMG_PLOT_WIDTH,
                    height=EMG_PLOT_HEIGHT,
                )
                emg_c2 = gr.LinePlot(
                    label="EMG C2",
                    width=EMG_PLOT_WIDTH,
                    height=EMG_PLOT_HEIGHT,
                )
                emg_c3 = gr.LinePlot(
                    label="EMG C3",
                    width=EMG_PLOT_WIDTH,
                    height=EMG_PLOT_HEIGHT,
                )
                emg_c4 = gr.LinePlot(
                    label="EMG C4",
                    width=EMG_PLOT_WIDTH,
                    height=EMG_PLOT_HEIGHT,
                )
                emg_c5 = gr.LinePlot(
                    label="EMG C5",
                    width=EMG_PLOT_WIDTH,
                    height=EMG_PLOT_HEIGHT,
                )
                emg_c6 = gr.LinePlot(
                    label="EMG C6",
                    width=EMG_PLOT_WIDTH,
                    height=EMG_PLOT_HEIGHT,
                )
                emg_c7 = gr.LinePlot(
                    label="EMG C7",
                    width=EMG_PLOT_WIDTH,
                    height=EMG_PLOT_HEIGHT,
                )

    is_recording = gr.State(value=False)
    current_progress = gr.Textbox(value=Progress.START.value, visible=False)

    def listen_tts_audio():
        # TODO (alan) play TTS audio
        next_progress = Progress.LISTEN_TTS_AUDIO_DONE.value
        return next_progress

    def start_v_emg_recording(start_button, stop_button):
        global recoder
        # recoder = Recorder(debug=True, display=False)
        # recoder.__enter__()
        is_recording = True
        return is_recording, start_button, stop_button

    def stop_v_emg_recording():
        global recoder
        # recoder.__exit__(None, None, None)
        # recoder = None
        is_recording = False
        next_progress = Progress.VOCALIZED_SPEECH_RECORDING_DONE.value
        return is_recording, next_progress

    def start_s_emg_recording():
        global recoder
        # recoder = Recorder(debug=True, display=False)
        # recoder.__enter__()
        is_recording = True
        return is_recording

    def stop_s_emg_recording():
        global recoder
        # recoder.__exit__(None, None, None)
        # recoder = None
        is_recording = False
        next_progress = Progress.SILENT_SPEECH_RECORDING_DONE.value
        return is_recording, next_progress

    def next_sample(sample_id: int):
        new_sample_id = (sample_id + 1) % len(TEXT_CORPUS_EN)
        new_sentence = TEXT_CORPUS_EN[new_sample_id]
        next_progress = Progress.START.value
        return new_sample_id, new_sentence, next_progress
    
    def update_progress(current_progress: str, progress=gr.Progress()):
        current_progress = Progress(int(current_progress))

        if current_progress == Progress.START:
            progress(0, desc="A")
        elif current_progress == Progress.LISTEN_TTS_AUDIO_DONE:
            progress(1, desc="B")
        elif current_progress == Progress.VOCALIZED_SPEECH_RECORDING_DONE:
            progress(2, desc="C")
        elif current_progress == Progress.SILENT_SPEECH_RECORDING_DONE:
            progress(3, desc="D")
        return PROGRESS_INSTRUCTION_MAP[current_progress.value]
    
    listen_tts_audio_button.click(
        listen_tts_audio,
        inputs=[],
        outputs=[current_progress],
    )
    
    start_v_emg_recording_button.click(
        start_v_emg_recording,
        inputs=[start_v_emg_recording_button, stop_v_emg_recording_button],
        outputs=[is_recording, start_v_emg_recording_button, stop_v_emg_recording_button],
        js="",
    )

    stop_v_emg_recording_button.click(
        stop_v_emg_recording,
        inputs=[],
        outputs=[is_recording, current_progress],
        js="",
    )

    start_s_emg_recording_button.click(
        start_s_emg_recording,
        inputs=[],
        outputs=[is_recording],
        js="",
    )

    stop_s_emg_recording_button.click(
        stop_s_emg_recording,
        inputs=[],
        outputs=[is_recording, current_progress],
        js="",
    )

    next_sample_button.click(
        next_sample,
        inputs=[sample_id],
        outputs=[sample_id, sentence, current_progress],
    )

    subject_id.change(
        lambda value: SUBJECT_DB[value]["name"],
        inputs=[subject_id],
        outputs=[subject_name],
        show_progress=False,
    )

    sample_id.change(
        lambda value: (TEXT_CORPUS_EN[value], TEXT_CORPUS_KR[value]),
        inputs=[sample_id],
        outputs=[sentence, sentence_kr],
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
        [emg_c0, emg_c1, emg_c2, emg_c3, emg_c4, emg_c5, emg_c6, emg_c7],
        every=1e-5,
    )


if __name__ == "__main__":
    recording_thread = threading.Thread(target=emg_recording, daemon=True)
    recording_thread.start()
    demo.queue().launch()
