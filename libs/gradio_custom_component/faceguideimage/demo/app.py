
import gradio as gr
from gradio_faceguideimage import FaceGuideImage

with gr.Blocks() as demo:
    input_img = FaceGuideImage(sources=["webcam"], mirror_webcam=True)

if __name__ == "__main__":
    demo.queue().launch()
