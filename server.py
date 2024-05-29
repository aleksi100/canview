from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from stream import getCanFrames
import threading


pgn_mask = (0b11 << 16) | 0xffff


def parseFrame(frame):
    parsed = {}
    time, _, payload = frame.split()
    id, data = payload.split("#")
    id = int(id, 16)
    data = int(data, 16)
    parsed["id"] = id
    parsed["pgn"] = (id >> 8) & pgn_mask
    parsed["sa"] = id & 0xff
    parsed["time"] = time[1:-1]
    parsed["data"] = data
    parsed["count"] = 1
    return parsed


class Frames:
    frames = {}

    def updateFrames(self, frame):
        """
            This funtion gets called from another thread running getCanFrames in stream.py
            Expected frame format "(time) interface id#data)"

            frame is considered new according to id field of the frame
        """
        frame = parseFrame(frame)
        if frame["id"] in self.frames:
            # modifying existing frame
            frame["count"] = self.frames[frame["id"]]["count"] + 1
            self.frames[frame["id"]] = frame
        else:
            # adding new frame
            self.frames[frame["id"]] = frame

    def addFrame(self, id, frame):
        self.frames[id] = frame

    def getFrames(self):
        return self.frames


myFrames = Frames()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global myFrames
    t = threading.Thread(target=getCanFrames, args=(
        myFrames.updateFrames,), daemon=True)
    t.start()
    yield
    print("exiting")

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/data")
def data():
    global myFrames
    return myFrames.getFrames()
