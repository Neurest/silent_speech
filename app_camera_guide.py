import numpy as np
import gradio as gr


import cv2
def draw(im):
    # im = cv2.cicle(im,(50,50), (200,200), (0, 255, 255), 2)
    print(im.shape) #(720, 1280, 3)
    im = cv2.ellipse(im, (640, 360), (150, 200), 0, 0, 360, (255, 0, 0), 2)
    return im


with gr.Blocks() as demo:
    # inp = gr.Image(source="webcam", shape=(250,250), streaming=True)
    inp = gr.Image(sources="webcam", streaming=True)
    out = gr.Image(label='Out-Calibration', )
    inp.change(draw, inp, out, show_progress=False)#, preprocess=False, postprocess=False)


if __name__ == "__main__":
    demo.queue().launch()