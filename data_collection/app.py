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

TEXT_CORPUS_KR = [
    "빠른 갈색 여우가 게으른 개를 뛰어넘습니다.",
    "다섯 명의 복싱 마법사들이 빨리 뛰어넘습니다.",
    "내 상자에는 다섯 다스의 술병이 들어 있습니다.",
]

EMG_PLOT_WIDTH = 600

EMG_PLOT_HEIGHT = 100


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
        return None, None, None, None, None, None, None, None

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

    # print(df)

    print(len(emg_data[0]))

    emg_c0_plot = gr.LinePlot(
        value=df,
        x="x",
        y="y0",
        title="EMG Channel 0",
        width=EMG_PLOT_WIDTH,
        height=EMG_PLOT_HEIGHT,
        x_lim=[0, 15],
        y_lim=[-500, 500],
    )

    emg_c1_plot = gr.LinePlot(
        value=df,
        x="x",
        y="y1",
        title="EMG Channel 1",
        width=EMG_PLOT_WIDTH,
        height=EMG_PLOT_HEIGHT,
        x_lim=[0, 15],
        y_lim=[-500, 500],
    )

    emg_c2_plot = gr.LinePlot(
        value=df,
        x="x",
        y="y2",
        title="EMG Channel 2",
        width=EMG_PLOT_WIDTH,
        height=EMG_PLOT_HEIGHT,
        x_lim=[0, 15],
        y_lim=[-500, 500],
    )

    emg_c3_plot = gr.LinePlot(
        value=df,
        x="x",
        y="y3",
        title="EMG Channel 3",
        width=EMG_PLOT_WIDTH,
        height=EMG_PLOT_HEIGHT,
        x_lim=[0, 15],
        y_lim=[-500, 500],
    )
    
    emg_c4_plot = gr.LinePlot(
        value=df,
        x="x",
        y="y4",
        title="EMG Channel 4",
        width=EMG_PLOT_WIDTH,
        height=EMG_PLOT_HEIGHT,
        x_lim=[0, 15],
        y_lim=[-500, 500],
    )

    emg_c5_plot = gr.LinePlot(
        value=df,
        x="x",
        y="y5",
        title="EMG Channel 5",
        width=EMG_PLOT_WIDTH,
        height=EMG_PLOT_HEIGHT,
        x_lim=[0, 15],
        y_lim=[-500, 500],
    )

    emg_c6_plot = gr.LinePlot(
        value=df,
        x="x",
        y="y6",
        title="EMG Channel 6",
        width=EMG_PLOT_WIDTH,
        height=EMG_PLOT_HEIGHT,
        x_lim=[0, 15],
        y_lim=[-500, 500],
    )

    emg_c7_plot = gr.LinePlot(
        value=df,
        x="x",
        y="y7",
        title="EMG Channel 7",
        width=EMG_PLOT_WIDTH,
        height=EMG_PLOT_HEIGHT,
        x_lim=[0, 15],
        y_lim=[-500, 500],
    )

    return emg_c0_plot, emg_c1_plot, emg_c2_plot, emg_c3_plot, emg_c4_plot, emg_c5_plot, emg_c6_plot, emg_c7_plot


def draw_face_guide(im):
    if im is None:
        return im
    H, W, _ = im.shape
    im = cv2.ellipse(im, (W//2, H//2), (300, 400), 0, 0, 360, (255, 0, 0), 2)
    return im


with gr.Blocks(css="./data_collection/style.css", title="Data Collection") as demo:
    with gr.Row():
        with gr.Column():
            gr.Markdown("# Data Collection")
        with gr.Column():
            with gr.Row():
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
                maximum=len(TEXT_CORPUS) - 1,
                value=0,
                step=1,
            )
            sentence = gr.Textbox(
                label="Sentence (en)",
                value=TEXT_CORPUS[0],
                interactive=False,
            )
            sentence_kr = gr.Textbox(
                label="Sentence (kr)",
                value=TEXT_CORPUS_KR[0],
                interactive=False,
            )
            progress = gr.Slider(
                label="Progress",
                minimum=0,
                maximum=3,
                value=0,
                step=1,
                interactive=False,
            )
            with gr.Row():
                # tts_audio_path = "/Users/alan.k/Desktop/dev/github/silent_speech/data_collection/output/v1.0.0/0_audio.flac"
                # tts_audio = gr.Audio(
                #     label="TTS Audio",
                #     value=tts_audio_path,
                # )
                listen_tts_audio_button = gr.Button(
                    
                    value="▶ TTS",
                    variant="secondary",
                )
                start_v_emg_recording_button = gr.Button(
                    value="Vocalized Speech Recording",
                    variant="primary",
                )
                # stop_v_emg_recording_button = gr.Button(
                #     value="Stop V Recording",
                #     variant="stop",
                # )
                start_s_emg_recording_button = gr.Button(
                    value="Silent Speech Recording",
                    variant="primary",
                )
                # stop_s_emg_recording_button = gr.Button(
                #     value="Stop S Recording",
                #     variant="stop",
                next_sample_button = gr.Button(
                    value="Next",
                    variant="secondary",
                )
            
        with gr.Column(scale=50):
            with gr.Row():
                audio = gr.Microphone(
                    label="Microphone",
                    scale=2,
                )
                in_video = gr.Image(
                    label="Video",
                    sources="webcam",
                    streaming=True,
                    scale=1,
                )
                # out_video = gr.Image(label="Out Video")
            with gr.Row():
                emg_c0 = gr.LinePlot(
                    label="EMG Channel 0",
                    width=EMG_PLOT_WIDTH,
                    height=EMG_PLOT_HEIGHT,
                )
                emg_c1 = gr.LinePlot(
                    label="EMG Channel 1",
                    width=EMG_PLOT_WIDTH,
                    height=EMG_PLOT_HEIGHT,
                )
                emg_c2 = gr.LinePlot(
                    label="EMG Channel 2",
                    width=EMG_PLOT_WIDTH,
                    height=EMG_PLOT_HEIGHT,
                )
                emg_c3 = gr.LinePlot(
                    label="EMG Channel 3",
                    width=EMG_PLOT_WIDTH,
                    height=EMG_PLOT_HEIGHT,
                )
                emg_c4 = gr.LinePlot(
                    label="EMG Channel 4",
                    width=EMG_PLOT_WIDTH,
                    height=EMG_PLOT_HEIGHT,
                )
                emg_c5 = gr.LinePlot(
                    label="EMG Channel 5",
                    width=EMG_PLOT_WIDTH,
                    height=EMG_PLOT_HEIGHT,
                )
                emg_c6 = gr.LinePlot(
                    label="EMG Channel 6",
                    width=EMG_PLOT_WIDTH,
                    height=EMG_PLOT_HEIGHT,
                )
                emg_c7 = gr.LinePlot(
                    label="EMG Channel 7",
                    width=EMG_PLOT_WIDTH,
                    height=EMG_PLOT_HEIGHT,
                )

    is_recording = gr.State(value=False)

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
    
    start_v_emg_recording_button.click(
        start_v_emg_recording,
        inputs=[],
        outputs=[is_recording],
    )

    # stop_v_emg_recording_button.click(
    #     stop_v_emg_recording,
    #     inputs=[],
    #     outputs=[is_recording],
    # )

    start_s_emg_recording_button.click(
        start_s_emg_recording,
        inputs=[],
        outputs=[is_recording],
    )

    # stop_s_emg_recording_button.click(
    #     stop_s_emg_recording,
    #     inputs=[],
    #     outputs=[is_recording],
    # )

    next_sample_button.click(
        next_sample,
        inputs=[sample_id],
        outputs=[sample_id, sentence],
    )

    demo.load(
        get_emg_plot,
        None,
        [emg_c0, emg_c1, emg_c2, emg_c3, emg_c4, emg_c5, emg_c6, emg_c7],
        every=1e-5,
    )

    subject_id.change(
        lambda value: SUBJECT_DB[value]["name"],
        inputs=[subject_id],
        outputs=[subject_name],
        show_progress=False,
    )

    sample_id.change(
        lambda value: (TEXT_CORPUS[value], TEXT_CORPUS_KR[value]),
        inputs=[sample_id],
        outputs=[sentence, sentence_kr],
        show_progress=False,
    )

    # in_video.change(
    #     draw_face_guide,
    #     inputs=[in_video],
    #     outputs=[out_video],
    #     show_progress=False,
    #     # preprocess=False,
    #     # postprocess=False,
    #     # every=1,
    # )


if __name__ == "__main__":
    recording_thread = threading.Thread(target=emg_recording, daemon=True)
    recording_thread.start()
    demo.queue().launch()
