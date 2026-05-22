import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from engine.pipeline import Pipeline

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "DFE_V1 online"}

@app.post("/api/run")
async def run(files: list[UploadFile] = File(default=[])):
    tmp = tempfile.mkdtemp()
    paths = []
    try:
        for f in files:
            p = os.path.join(tmp, f.filename)
            with open(p, "wb") as out:
                shutil.copyfileobj(f.file, out)
            paths.append(p)
        pipe = Pipeline()
        pipe.run(paths)
        return {
            "ok": True,
            "summary":    pipe.summary(),
            "manifest":   pipe.manifest,
            "profile":    pipe.profiles,
            "normalized": pipe.get_normalized_serialized(),
            "clusters":   pipe.clusters,
            "cross_refs": pipe.cross_refs,
            "inferences": pipe.inferences,
            "unresolved": pipe.unresolved,
        }
    except Exception as e:
        import traceback
        return {"ok": False, "error": str(e), "trace": traceback.format_exc()}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)