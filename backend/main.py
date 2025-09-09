import uvicorn

# from app.main import app

if __name__ == "__main__":

    print("Starting server on port " + str(8000))
    uvicorn.run("app.main:app", host="0.0.0.0", reload=True, port=8000)
