from epubconv.epubconv import convertEPUB, config
import asyncio
import websockets
import os
from threading import Timer, Thread

settings = config.load()
def send(websocket, *args):
    Thread(target=lambda: asyncio.new_event_loop().run_until_complete(websocket.send(*args))).start()

async def api(websocket, path):
    file_path = f'./temp/{await websocket.recv()}.epub'
    result = convertEPUB(file_path, lambda x: send(websocket, x))
    if (result['status']):
        await websocket.send(">>>>> 正在傳輸轉換結果...")
        await websocket.send(result['id'])

        confirm = await websocket.recv()
        while (confirm != result['id']):
            confirm = await websocket.recv()

        Timer(settings['tempTime'], lambda x: os.remove(x) if os.path.isfile(x) else None, [f"./temp/{result['id']}.epub"]).start()
        
    else:
        await websocket.send(f"轉換失敗。\n錯誤: {result['error']}")



start_server = websockets.serve(api, settings["apiHost"], settings["apiPort"])

print("///// EPUB 轉換服務已啟動 /////")
print(f'ws://{settings["apiHost"]}:{settings["apiPort"]}')

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

