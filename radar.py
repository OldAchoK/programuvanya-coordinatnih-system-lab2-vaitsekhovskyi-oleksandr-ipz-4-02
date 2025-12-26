import asyncio
import websockets


async def connect_to_radar():
    # Адреса вашого контейнера (localhost, бо порт 4000 прокинуто на Windows)
    uri = "ws://localhost:4000"

    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Підключено до радара за адресою {uri}")

            # Якщо радар вимагає запит для початку передачі даних:
            # await websocket.send("START_SCAN")

            while True:
                # Очікування даних від контейнера
                data = await websocket.recv()
                print(f"📡 Отримано дані: {data}")

    except ConnectionRefusedError:
        print("❌ Помилка: Контейнер не запущений або порт 4000 закритий.")
    except Exception as e:
        print(f"⚠️ Виникла помилка: {e}")


if __name__ == "__main__":
    asyncio.run(connect_to_radar())