from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.param_functions import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
from .import models
from .database import engine, get_db
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()



# the in memory schema
class Post(BaseModel):
    title: str
    content: str
    published: bool = True


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


@app.get("/")
def root():
    return {"message": "My API"}


@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts(title, content, published) VALUES(%s, %s, %s) RETURNING * """,
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}


@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts where ID=%s""", str(id))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id:{id} was not found.")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message': f"post with id:{id} was not found."}
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", str(id))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post_filter = db.query(models.Post).filter(models.Post.id == id)

    if post_filter.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post id={id} does not exist")

    post_filter.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, updated_post: Post, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
    #                (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_filter = db.query(models.Post).filter(models.Post.id == id)
    post = post_filter.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post id={id} does not exist")
    post_filter.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return {'data': post_filter.first()}
