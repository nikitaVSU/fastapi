from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
from xml.etree.ElementTree import fromstring
from json import dumps

from database import SessionLocal, engine
import models as models
import schemas
from auth1 import authenticate, create_access_token, is_authorized

app = FastAPI()

# Генерация JWT токена
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


# Создание соединения с базой данных
models.Base.metadata.create_all(bind=engine)


# Получение экземпляра сессии базы данных
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# Регистрация
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(username=user.username, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Аутентификация и создание токена
@app.post("/token/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Эндпоинт для загрузки XML-файла и сохранения его в базе данных
@app.post("/xml/")
async def create_xml(xml_file: UploadFile = File(...), db: Session = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme)):
    if not is_authorized(token):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Чтение XML-файла и сохранение его в базе данных
    xml_data = xml_file.file.read()
    xml_string = xml_data.decode('utf-8')
    xml = fromstring(xml_string)
    db_xml = models.XML(content=xml_string)
    db.add(db_xml)
    db.commit()
    db.refresh(db_xml)

    return {"message": "XML file saved"}

# Эндпоинт для получения всех сохраненных XML-файлов в формате JSON
@app.get("/xml/")
async def read_all_xml(db: Session = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme)):
    if not is_authorized(token):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Получение всех сохраненных XML-файлов из базы данных и преобразование их в JSON
    db_xmls = db.query(models.XML).all()
    xmls = [fromstring(xml.content) for xml in db_xmls]
    jsons = [dumps(xml.attrib) for xml in xmls]

    return jsons

#Текстовое сообщение
@app.post("/messages/")
async def create_message(message: schemas.MessageCreate, db: Session = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme)):
    if not is_authorized(token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    db_message = models.Message(text=message.text)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
