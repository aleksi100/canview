from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from stream import getCanFrames
import threading


pgn_mask = (0b11 << 16) | 0xffff

# pgn that is being send many times a second
# and you dont want to focus on those
spam_pgns = ("0xf013", )


def parseFrame(frame):
    parsed = {}
    time, _, payload = frame.split()
    id, data = payload.split("#")
    id = int(id, 16)
    data = int(data, 16)
    parsed["id"] = id
    parsed["pgn"] = hex((id >> 8) & pgn_mask)
    parsed["sa"] = hex(id & 0xff)
    parsed["time"] = time[1:-1]
    parsed["data"] = hex(data)
    parsed["count"] = 1
    parsed["name_id"] = '?'
    return parsed


class Frames:
    frames = []

    def updateFrames(self, raw_frame):
        """
            This funtion gets called from another thread running getCanFrames in stream.py
            Expected raw_frame format "(time) interface id#data)"
        """

        parsed = parseFrame(raw_frame)
        last = False
        if len(self.frames) > 0:
            last = self.frames[-1]

        # if the pgn is spam_pgn and is already stored, we only update its values
        if (parsed["pgn"] in spam_pgns) and (parsed["id"] in [f["id"] for f in self.frames]):

            # find the frame and modify it
            for i, f in enumerate(self.frames):
                if f["id"] == parsed["id"]:
                    last = self.frames[i]
                    last["time"] = parsed["time"]
                    last["count"] += 1
                    last["data"] = parsed["data"]
                    self.frames[i] = last
                    break

        else:
            self.frames.append(parsed)
            # we dont want to store all frames so we start dropping them
            if len(self.frames) > 50:
                self.frames.pop(0)

        # Adress claim pgn
        if parsed["pgn"] == "0xeeff":
            # ectract the id from name
            # we have to do some processing becaus the 21bit id is stoded in little endian
            idstr = parsed["data"][2:8]
            arr = bytearray.fromhex(idstr)
            arr.reverse()
            # adding name_id filed to the current frame
            # self.addAdresses copies that to all frames with same address
            self.frames[-1]["name_id"] = arr.hex()

        # if name id is known for incoming frame source address we want to add the name id to the frame
        self.addAdresses()

    def addAdresses(self):
        known = {}
        for frame in self.frames:
            if frame["name_id"] != "?":
                known[frame["sa"]] = frame["name_id"]

        for i, frame in enumerate(self.frames):
            if frame["sa"] in known:
                self.frames[i]["name_id"] = known[frame["sa"]]

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
