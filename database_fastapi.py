from sqlalchemy import create_engine 
from sqlalchemy.dialects.sqlite import * 
from sqlalchemy.orm import Session , sessionmaker 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column , Integer , String
from typing import List
from pydantic import BaseModel , constr
from fastapi import FastAPI , Depends
import uvicorn

    
#DATABASE CONNECTION  
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/newdb"  
# 🔹 Replace with your MySQL username, password, and database name
#create database 'newdb' in mysql 


engine = create_engine(SQLALCHEMY_DATABASE_URL )
sessionlocal = sessionmaker(autocommit = False , autoflush=False , bind = engine)
Base = declarative_base()


#SQLALCHEMY DATABASE ORM Model 

class Books(Base):
    __tablename__ = 'book'
    id = Column(Integer,primary_key=True,nullable=False)
    title=Column(String(50),unique=True)
    author = Column(String(50),nullable= False)
    publisher=Column(String(50),nullable= False)
    

#creating the table 
Base.metadata.create_all(bind = engine)
    
#creating pydantic model    
class Bookschema(BaseModel):
    id : int 
    title : str
    author: str
    publisher : str

    class Config:
        orm_mode = True


#creating fastapi app
app = FastAPI()

# Dependency to get DB session
def  get_db():
    db = sessionlocal()
    try:
        yield db
    finally :
        db.close()


#adding items to database 
@app.get("/add_items",response_model=Bookschema)
def add_book(b1:Bookschema,db: Session =  Depends(get_db)):
    bk = Books(**b1.dict())
    db.add(bk)
    db.commit()
    db.refresh(bk)
    return bk


#Displaying the data 
@app.get("/display_book",response_model=Bookschema)
def get_book(db: Session = Depends(get_db)):
    recs = db.query(Books).all()
    return recs
    
#updating the data 
#here 'put' method is used to update the data 
@app.put("/update/{id}", response_model=Bookschema)
def update_book(id: int, book: Bookschema , db: Session = Depends(get_db)):
    b1 = db.query(Books).filter(Books.id == id).first()
    b1.id = book.id
    b1.title = book.title
    b1.author = book.author
    b1.publisher = book.publisher
    db.commit()
    return b1


#Deleting the data 
#here 'delete' method is used ot delete the data 
@app.delete("/delete/{id}",response_model=Bookschema)
def delete_data(id : int , db: Session = Depends(get_db)):
    try:
        db.query(Books).filter(Books.id == id).delete()
        db.commit()        
    except Exception as e :
        raise Exception(e)
    return {"delete status":"success"}



if __name__ == "__main__":
    uvicorn.run("database_fastapi:app", host="127.0.0.1", port=8000, reload=True)