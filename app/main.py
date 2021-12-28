from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor
from app import models
from app.database import engine
from app.routers import post, user, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

try:
    conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres',
                            password='934jh45', cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print("Database connection was successful!")
except Exception as error:
    print("Connecting to database failed")
    print("Error: ", error)
    exit(1)

my_posts = [
    {"title": "title of first post", "content": "post content", "id": 1},
    {"title": "favorite foods", "content": "i like pizza", "id": 2}
]


def find_post(id):
    for item in my_posts:
        if item['id'] == id:
            return item
    return


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "My API"}
