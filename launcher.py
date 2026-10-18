"""Windows launcher for AAII AI 3D Studio local web UI."""
import os,sys,traceback
from pathlib import Path
def main():
    if getattr(sys,"frozen",False):
        home=Path(sys.executable).resolve().parent
        os.chdir(home)
        os.environ.setdefault("GRADIO_TEMP_DIR",str(home/"gradio_tmp"))
    from app import app
    app.queue(max_size=3).launch(server_name="127.0.0.1",server_port=int(os.getenv("AAII_PORT","7860")),inbrowser=True,show_error=True)
if __name__=="__main__":
    try: main()
    except Exception:
        p=Path.home()/"AAII_AI_3D_Studio_error.log"
        p.write_text(traceback.format_exc(),encoding="utf8")
        print("Startup error; see",p)
        traceback.print_exc()
        try: input("Press Enter to close...")
        except EOFError: pass
        sys.exit(1)
