"""AAII AI 3D Studio V1.2 processing. Optional AI backend is NOT bundled."""
from pathlib import Path
import os,shlex,subprocess,uuid,json
import cv2,numpy as np,trimesh
from PIL import Image
ROOT=Path.cwd()
OUT=ROOT/"outputs"
def new_job():
    p=OUT/uuid.uuid4().hex
    p.mkdir(parents=True,exist_ok=True)
    return p
def video_metadata(path):
    c=cv2.VideoCapture(str(path))
    try:
        if not c.isOpened():raise ValueError("Video cannot be opened")
        fps=c.get(cv2.CAP_PROP_FPS)
        return dict(width=int(c.get(cv2.CAP_PROP_FRAME_WIDTH)),height=int(c.get(cv2.CAP_PROP_FRAME_HEIGHT)),fps=round(fps,3),duration=round(c.get(cv2.CAP_PROP_FRAME_COUNT)/fps,2) if fps else 0)
    finally:c.release()
def read_video_frame(path,time):
    if not path:raise ValueError("Upload a video first")
    m=video_metadata(path)
    if time<0 or time>m["duration"]:raise ValueError("Timestamp outside video duration")
    c=cv2.VideoCapture(str(path))
    try:
        c.set(cv2.CAP_PROP_POS_MSEC,float(time)*1000)
        ok,img=c.read()
        if not ok:raise ValueError("Could not decode frame")
        return Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
    finally:c.release()
def save_views(front,left,back,right,folder):
    images=dict(front=front,left=left,back=back,right=right)
    if any(images[k] is None for k in ("front","left","back")):raise ValueError("Front, left and back are required")
    result={}
    for name,im in images.items():
        if im is not None:
            p=folder/(name+".png");im.convert("RGBA").save(p);result[name]=p
    return result
def validate_mesh(path):
    scene=trimesh.load(str(path),force="scene")
    meshes=[m for m in scene.dump() if isinstance(m,trimesh.Trimesh)]
    if not meshes or sum(len(m.faces) for m in meshes)==0:raise ValueError("GLB has no triangles")
    return dict(meshes=len(meshes),triangles=sum(len(m.faces) for m in meshes),watertight_all=all(m.is_watertight for m in meshes))
def run_multiview_ai(views,folder):
    cmd=os.environ.get("AAII_MULTIVIEW_COMMAND","").strip()
    if not cmd:raise RuntimeError("No multi-view AI engine configured. Set AAII_MULTIVIEW_COMMAND.")
    if "{output}" not in cmd:raise ValueError("Command must have {output}")
    out=folder/"multiview_ai.glb"
    replacements={"{"+k+"}":str(p) for k,p in views.items()}
    replacements["{output}"]=str(out)
    tokens=shlex.split(cmd,posix=(os.name!="nt"))
    for token in tokens:
        for key in ("front","left","back","right"):
            if "{"+key+"}" in token and key not in views:raise ValueError("Missing "+key)
    args=[]
    for token in tokens:
        for key,value in replacements.items():token=token.replace(key,value)
        args.append(token)
    result=subprocess.run(args,cwd=str(ROOT),capture_output=True,text=True,timeout=1800)
    if result.returncode:raise RuntimeError("AI backend failed: "+(result.stderr or result.stdout)[-1000:])
    if not out.is_file() or not out.stat().st_size:raise RuntimeError("AI backend produced no GLB")
    validate_mesh(out)
    return out
def silhouette_preview(views,folder,resolution=72):
    masks={}
    for name,path in views.items():
        alpha=np.asarray(Image.open(path).convert("RGBA").getchannel("A"))
        if np.min(alpha)>0:raise ValueError(name+" needs a transparent background in NON-AI silhouette mode")
        mask=Image.fromarray((alpha>127).astype("uint8")*255).resize((resolution,resolution),Image.Resampling.NEAREST)
        masks[name]=np.asarray(mask)>0
    fx=masks["front"][:,::-1];bk=masks["back"];side=masks["left"][:,::-1]
    vox=np.zeros((resolution,resolution,resolution),dtype=bool)
    for yi in range(resolution):
        row=resolution-yi-1
        mx=fx[row]&bk[row];mz=side[row]
        if "right" in masks:mz &= masks["right"][row,::-1]
        vox[:,yi,:]=mx[:,None]&mz[None,:]
    if vox.sum()<80:raise ValueError("Insufficient silhouette overlap. Align/crop views.")
    mesh=trimesh.voxel.ops.matrix_to_marching_cubes(vox)
    mesh.vertices=(mesh.vertices-resolution/2)/resolution*2
    mesh.visual.vertex_colors=[184,193,211,255]
    out=folder/"silhouette_preview.glb"
    out.write_bytes(trimesh.Scene(mesh).export(file_type="glb"))
    validate_mesh(out)
    return out
def roblox_export(source,height_studs=6.0):
    if height_studs<=0:raise ValueError("Target height must be positive")
    scene=trimesh.load(str(source),force="scene")
    if not scene.geometry:raise ValueError("Empty mesh")
    bounds=np.array(scene.bounds);size=float(bounds[1,1]-bounds[0,1])
    if not np.isfinite(size) or size<=1e-6:raise ValueError("Mesh has zero Y-axis height")
    scale=float(height_studs)/size
    scene.apply_scale(scale)
    shift=np.zeros(3);shift[1]=-scene.bounds[0,1]
    scene.apply_translation(shift)
    out=Path(source).parent/"roblox_ready.glb"
    out.write_bytes(scene.export(file_type="glb"))
    report=validate_mesh(out)
    report.update(target_height_studs=height_studs,scale_factor=scale,axis_assumption="Y-up",warning="Scale normalization only; not an avatar rig or certified Roblox asset.")
    p=Path(source).parent/"roblox_export_report.json"
    p.write_text(json.dumps(report,indent=2),encoding="utf8")
    return out,p,report
