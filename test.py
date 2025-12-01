import asyncio
import websockets

async def test():
    url = "wss://sockets.streamlabs.com/v1/socket?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6IkQ0NDU2QjlCRTc2OEI2RkZDQTk0MzIwOTJDNzkwMkVCMzE5MTA5N0VEMTAxMjc5RDFENEEyN0YzOUY1REY3NThFMjQwQkVDRTNEMTk4MDVEMERBOTk3NkVDRTY1MzhDNTVFMkJBNjEwNUY3MTNBMzg5NENCOTNGMDgwRkNEMUU3QUYxNTRENkM0RUQ0Rjc0MTFERTIzQ0Q5Mzg3RUNEMjFBN0RCMUQ0Q0JFNDYyN0M0NTdEM0NFMkNFRkI1MjFBQzc2OEY4MzNEMUEzQjE2Q0NDQ0E2NTU1QTYyN0IyM0U5ODVBQURCMzQwODhFMDNCMDYyREEzRTU4RDgiLCJyZWFkX29ubHkiOnRydWUsInByZXZlbnRfbWFzdGVyIjp0cnVlLCJraWNrX2lkIjoiNjkzMjIwNDIifQ.vBa6gDl9rdFy2UfIQQ5cwN4eXR7Dh1aYjKzF74my7sY"

    try:
        ws = await websockets.connect(url)
        print("Conectou!")
    except Exception as e:
        print("Erro:", e)

asyncio.run(test())
