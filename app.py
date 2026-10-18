"""AAII AI 3D Studio V1.2: video frames, optional AI backend, Roblox GLB export."""
import os
import gradio as gr
from core import new_job,read_video_frame,video_metadata,save_views,run_multiview_ai,silhouette_preview,roblox_export

def info(video):
    if not video:return "Upload a video first."
    m=video_metadata(video)
    return f"{m['width']} x {m['height']} | {m['fps']} fps | {m['duration']} seconds"
def frame(video,t):
    try:return read_video_frame(video,t)
    except Exception as e:raise gr.Error(str(e))
def generate(front,left,back,right,method,height):
    try:
        folder=new_job()
        views=save_views(front,left,back,right,folder)
        if method=="Configured Multi-view AI":
            src=run_multiview_ai(views,folder)
            mode="External AI model"
        else:
            src=silhouette_preview(views,folder)
            mode="Coarse NON-AI silhouette"
        glb,report,metrics=roblox_export(src,height)
        return str(src),str(src),str(glb),str(report),f"{mode}: {metrics['triangles']} triangles. Validate scale and orientation in Roblox Studio."
    except Exception as e:raise gr.Error(str(e))
CSS="#hero{background:linear-gradient(120deg,#15233c,#4937a3);color:white;padding:18px;border-radius:18px}"
with gr.Blocks(title="AAII AI 3D Studio V1.2",theme=gr.themes.Soft(),css=CSS) as app:
    gr.HTML('<div id="hero"><h1>AAII AI 3D Studio V1.2</h1><p>Video → 3D → Roblox GLB</p></div>')
    gr.Markdown("**AI model is optional and must be configured externally.** Silhouette preview is not AI and requires background-removed RGBA PNG images.")
    video=gr.Video(label="Upload video (.mp4/.mov)")
    meta=gr.Textbox(label="Video metadata",interactive=False)
    video.change(info,[video],[meta])
    with gr.Row():
        with gr.Column():
            tf=gr.Number(value=2,label="Front time (sec)",minimum=0)
            bf=gr.Button("Extract Front")
            front=gr.Image(type="pil",image_mode="RGBA",label="Front")
        with gr.Column():
            tl=gr.Number(value=9,label="Left time (sec)",minimum=0)
            bl=gr.Button("Extract Left")
            left=gr.Image(type="pil",image_mode="RGBA",label="Left 90°")
    with gr.Row():
        with gr.Column():
            tb=gr.Number(value=15,label="Back time (sec)",minimum=0)
            bb=gr.Button("Extract Back")
            back=gr.Image(type="pil",image_mode="RGBA",label="Back 180°")
        with gr.Column():
            tr=gr.Number(value=0,label="Right time (sec)",minimum=0)
            br=gr.Button("Extract Right")
            right=gr.Image(type="pil",image_mode="RGBA",label="Right 270° optional")
    for b,t,img in [(bf,tf,front),(bl,tl,left),(bb,tb,back),(br,tr,right)]:
        b.click(frame,[video,t],[img])
    method=gr.Radio(["Configured Multi-view AI","Silhouette preview (non-AI)"],value="Silhouette preview (non-AI)",label="Generation method")
    height=gr.Slider(1,20,value=6,step=.25,label="Roblox target height (studs)")
    start=gr.Button("Generate GLB",variant="primary")
    status=gr.Textbox(label="Result",interactive=False)
    with gr.Row():
        model=gr.Model3D(label="3D Preview")
        with gr.Column():
            raw=gr.File(label="Raw GLB")
            ready=gr.File(label="Scaled Roblox GLB")
            report=gr.File(label="Validation report")
    start.click(generate,[front,left,back,right,method,height],[model,raw,ready,report,status])
if __name__=="__main__":
    app.queue(max_size=3).launch(server_name="127.0.0.1",server_port=int(os.getenv("AAII_PORT","7860")),inbrowser=True)
