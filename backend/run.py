import platform, os

if platform.system() == "Windows":
    os.system("uvicorn app.main:app --reload --loop asyncio")
else:
    os.system("uvicorn app.main:app --reload")
