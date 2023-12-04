import datetime
from pstats import Stats
import statistics
from typing import Annotated
from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, Response, applications
import json
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError
from fastapi import FastAPI
import bcrypt
from config.database import users
from config.database import datas
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from starlette.middleware.base import BaseHTTPMiddleware
import requests, json

templates = Jinja2Templates(directory="templates")



# ! TIPE DATA
class Product(BaseModel):
    idProduct: int
    name: str
    price: int
    categoryId: int
    link: str

class ProductStock(BaseModel):
    idProduct: int
    stock: int
    ukuran: str

class Category(BaseModel): 
    categoryId: int
    categoryName: str

class Discount(BaseModel):
    idProduct: int
    discount: int

class MarkUp(BaseModel):
    idProduct: int
    markUp: int

class User(BaseModel):
    username: str
    password: str = ""

class Customization(BaseModel):
    productId: int
    specialInstructions: str
    font: str
    color: str
    descriptions: str
    size: str
    imageUrl: str





# ! FAST API
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# ! READ FILE (MIDDLEWARE)
@app.middleware("http")
async def readMiddleware(request: Request, call_next):
    global data, user
    # json_filename = "Data.json"
    # with open(json_filename, "r") as read_file: 
    #     data = json.load(read_file)
    hasil_query_datas = list(datas.find())
    for i in hasil_query_datas:
        i["_id"] = str(i["_id"])

    data = jsonable_encoder(hasil_query_datas)[0]


    # json_filename_user = "User.json"
    # with open(json_filename_user, "r") as read_file: 
    #     user = json.load(read_file)
    hasil_query_users = list(users.find())

    # Mengonversi ObjectId menjadi string di dalam hasil kueri

    for item in hasil_query_users:
        item["_id"] = str(item["_id"])

    user =  jsonable_encoder(hasil_query_users)[0]
    response = await call_next(request)
    return response

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "e275e4502c134f27aada8275862d418d9a8ad8283b02dadd4e0b3b56a63b2930"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24*60

def isAdmin(token: str):
    # TODO balikkan lagi tokennya menjadi username
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    # TODO cari username yang sesuai dan lihat rolenya
    foundUser = False
    for pengguna in user['users']:
        if(pengguna['username'] == username):
            foundUser = True
            currentUser = pengguna
            break
    if(foundUser):
        return currentUser['role'] == "admin"
        # TODO return role == admin
    else:
        raise HTTPException(status_code=401, detail="User not found")

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        user = User(username=username)
        return user
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



url = 'http://localhost:8004/'

def create_user_external(username, password):
    headers = {'Authorization': ''}
    params = {
        "firstname": "APIDzikri",
        "lastname": "APIDzikri",
        "phonenumber": "0812345",
        "address": "APIDzikri",
        "email": f"{username}@gmail.com",
        "password": password,
        "username": username,
        "role": "admin"
    }

    url_endpoint = url + 'authentications/register'
    res = requests.post(url_endpoint, params=params, headers=headers).json()
    return res



def get_token_eksternal(username, password):
    token_url = url+'authentications/login'
    token_response = requests.post(token_url, data={'username': username, 'password': password})
    token = token_response.json().get('access_token')
    return token


@app.post("/token")
def login_for_access_token(response: Response, newUsers: User):
    # TODO Melakukan pemerikasaan terhadap username (apakah terdapat dalam database)
    # melakukan pencarian terhadap username
    newUser = newUsers.dict()
    foundUsername = False
    for pengguna in user['users']:
        if(pengguna['username'] == newUser['username']):
            foundUsername = True
            currentUser = pengguna
            break
    # TODO jika email tidak ditemukan, raise http exception ("username not found")
    print("masuk1")
    if(not foundUsername):
        raise HTTPException(
        status_code=404, detail=f'user not found'
    )

    # TODO melakukan pemeriksaan apakah passwordnya benar atau salah 
    # TODO jika passwordnya salah, raise http exception ("incorrect password")
    print("masuk2")
    if not bcrypt.checkpw(newUser['password'].encode('utf-8'), currentUser['password'].encode('utf-8')):
        raise HTTPException(
        status_code=401, detail=f'incorrect password'
    )
    # TODO jika benar, tambahkan data user, kemudian kembalikan berupa jwt
    # Jika informasi pengguna benar, buat token JWT
    print("masuk3")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    print("masuk4")
    tokenEksternal = get_token_eksternal(newUser['username'], newUser['password'])
    print(tokenEksternal)
    print("masuk5")
    access_token = create_access_token(
        data={"sub": newUser['username'], "tokenEksternal": tokenEksternal}, expires_delta=access_token_expires
    )
    response.set_cookie(key="access_token", value=f"{access_token}", expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    print("masuk6")
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/createUAdmin")
async def createAdmin(newUser: User):
    # TODO LAKUKAN PENGECEKAN TERHADAP USERNAME
    foundUsername = False
    for admin in user['users']:
        if(admin['username'] == newUser['username']):
            foundUsername = True
            break
    # TODO JIKA USERNAME TELAH TERDAFTAR, RAISE HTTP EXCEPTION (USERNAME HAS ALREADY BEEN TAKEN)
    if(foundUsername):
        raise HTTPException(
		status_code=400, detail=f'username has already been taken'
	)
    else:
        # TODO JIKA USERNAME BELUM TERDAFTAR, CEK PASSWORD  
        if(len(newUser['password']) < 6):
            # TODO JIKA PASSWORD KURANG DARI 6 KARAKTER, RAISE HTTP EXCEPTION (PASSWORD MUST BE 6 CHARACTERS OR MORE)
            raise HTTPException(
		    status_code=400, detail=f'password must be 6 characters or more'
	    )
        else:
            # ! JANGAN LUPA KITA BUATKAN AKUN JUGA DI API LUAR
            respon = create_user_external(newUser['username'], newUser['password'])

            if(respon):
                password = bcrypt.hashpw(newUser['password'].encode('utf-8'), bcrypt.gensalt())
                password_string = password.decode('utf-8')
                user_dict = {"username": newUser['username'], "password": password_string, "role": "admin"}
                # TODO JIKA SUDAH SESUAI, TULISKAN KE DALAM JSON
                user['users'].append(user_dict)
            #    save ke database
                filterCriteria = {"_id": ObjectId(user['_id'])}
                updateQuery = {
                    "$set": {
                        "users": user["users"]
                    }
                }
                users.update_one(filterCriteria, updateQuery)


                # with open(json_filename_user, "w") as write_file: 
                #     json.dump(user, write_file)
                return {"message": "Data added sucessfully"}
            else:
                raise HTTPException(
		status_code=400, detail=f'user creation failed'
	)



@app.post("/createUser")
async def createUser(newUsers: User):
    # TODO LAKUKAN PENGECEKAN TERHADAP USERNAME
    foundUsername = False
    newUser = newUsers.dict()
    for pengguna in user['users']:
        if(pengguna['username'] == newUser['username']):
            foundUsername = True
            break
    # TODO JIKA USERNAME TELAH TERDAFTAR, RAISE HTTP EXCEPTION (USERNAME HAS ALREADY BEEN TAKEN)
    if(foundUsername):
        raise HTTPException(
		status_code=404, detail=f'username has already been taken'
	)
    else:
        # TODO JIKA USERNAME BELUM TERDAFTAR, CEK PASSWORD  
        if(len(newUser['password']) < 6):
            # TODO JIKA PASSWORD KURANG DARI 6 KARAKTER, RAISE HTTP EXCEPTION (PASSWORD MUST BE 6 CHARACTERS OR MORE)
            raise HTTPException(
		    status_code=404, detail=f'password must be 6 characters or more'
	    )
        else:
            # ! JANGAN LUPA KITA BUATKAN AKUN JUGA DI API LUAR
            respon = create_user_external(newUser['username'], newUser['password'])
            if(respon):
                password = bcrypt.hashpw(newUser['password'].encode('utf-8'), bcrypt.gensalt())
                password_string = password.decode('utf-8')
                user_dict = {"username": newUser['username'], "password": password_string, "role": "user"}
                # TODO JIKA SUDAH SESUAI, TULISKAN KE DALAM JSON
                user['users'].append(user_dict)
            #    save ke database
                filterCriteria = {"_id": ObjectId(user['_id'])}
                updateQuery = {
                    "$set": {
                        "users": user["users"]
                    }
                }
                users.update_one(filterCriteria, updateQuery)
                # with open(json_filename_user, "w") as write_file: 
                #     json.dump(user, write_file)
                return {"message": "Data added sucessfully"}
            else:
                raise HTTPException(
		status_code=400, detail=f'user creation failed'
	)





#! ROUTING Product
@app.get('/product')
async def getAllProduct(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return data['product']
    except PyJWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get('/product/id/{idProduct}')
async def getProductById(idProduct: int, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        for product in data['product']:
            if(product['idProduct'] == idProduct):
                return product
        raise HTTPException(
            status_code=404, detail=f'product not found'
        )
    except PyJWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get('/product/category/{category}')
async def getProductByCategory(category: str, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # dapetin dulu categoryIdnya
        categoryID = -1
        found = False
        for kategori in data['category']:
            if(kategori['categoryName'] == category):
                categoryID = kategori['categoryId']
                found = True
        if found:
            productFound = False
            hasil = []
            for product in data['product']:
                if(product['categoryId'] == categoryID):
                    productFound = True
                    hasil.append(product)
            if productFound:
                return hasil
            if not productFound:
                return "there is no product with that category"
        if not found: 
            raise HTTPException(
            status_code=404, detail=f'category not found'
        )
        
            
        raise HTTPException(
            status_code=404, detail=f'category not found'
        )
    except PyJWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

@app.post('/product')
async def postProduct(product: Product, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if(not isAdmin(token)):
            raise HTTPException(
		status_code=404, detail=f'only admin can access')
        product_dict = product.dict()
        productFound = False
        for product in data['product']:
            if(product['idProduct']==product_dict['idProduct']):
                # ketemu product
                productFound = True
                return "Product with ID"+str(product_dict['idProduct'])+"already exist"
        if not productFound:
            data['product'].append(product_dict)
            # save ke json
            filterCriteria = {"_id": ObjectId(data['_id'])}
            updateQuery1 = {
                "$set": {
                    "product": data['product']
                }
            }
            updateQuery2 = {
                "$set": {
                    "product_stock": data["product_stock"]
                }
            }
            updateQuery3 = {
                "$set": {
                    "category": data["category"]
                }
            }
            datas.update_one(filterCriteria, updateQuery1)
            datas.update_one(filterCriteria, updateQuery2)
            datas.update_one(filterCriteria, updateQuery3)

            # with open(json_filename, "w") as write_file: 
            #     json.dump(data, write_file)
            
            return product_dict
        
        raise HTTPException(
            status_code=404, detail=f'product not found'
        )
    except PyJWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.put('/product')
async def updateProduct(product: Product, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if(not isAdmin(token)):
            raise HTTPException(
		status_code=404, detail=f'only admin can access')
        product_dict = product.dict()
        productFound = False
        for product_idx, product in enumerate(data['product']):
            if(product['idProduct'] == product_dict['idProduct']):
                productFound=True
                data['product'][product_idx] = product_dict
                # save ke json
                filterCriteria = {"_id": ObjectId(data['_id'])}
                updateQuery1 = {
                    "$set": {
                        "product": data["product"]
                    }
                }
                updateQuery2 = {
                    "$set": {
                        "product_stock": data["product_stock"]
                    }
                }
                updateQuery3 = {
                    "$set": {
                        "category": data["category"]
                    }
                }
                datas.update_one(filterCriteria, updateQuery1)
                datas.update_one(filterCriteria, updateQuery2)
                datas.update_one(filterCriteria, updateQuery3)
                # with open(json_filename, "w") as write_file:
                #     json.dump(data, write_file)
                return product_dict
            
        if not productFound:
            raise HTTPException(
            status_code=404, detail=f'product not found'
        )
        
        raise HTTPException(
            status_code=404, detail=f'product not found'
        )
    except PyJWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        
@app.delete('/product/{idProduct}')
async def deleteProduct(idProduct: int, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if(not isAdmin(token)):
            raise HTTPException(
		status_code=404, detail=f'only admin can access')
        productFound = False
        for product_idx, product in enumerate(data['product']):
            if(product['idProduct'] == idProduct):
                productFound = True
                data['product'].pop(product_idx)
                # save ke json
                filterCriteria = {"_id": ObjectId(data['_id'])}
                updateQuery1 = {
                    "$set": {
                        "product": data["product"]
                    }
                }
                updateQuery2 = {
                    "$set": {
                        "product_stock": data["product_stock"]
                    }
                }
                updateQuery3 = {
                    "$set": {
                        "category": data["category"]
                    }
                }
                datas.update_one(filterCriteria, updateQuery1)
                datas.update_one(filterCriteria, updateQuery2)
                datas.update_one(filterCriteria, updateQuery3)
                # with open(json_filename, "w") as write_file: 
                #     json.dump(data, write_file)
                return "Product deleted"
            
        if not productFound:
            raise HTTPException(
            status_code=404, detail=f'product not found'
        )
        
        raise HTTPException(
            status_code=404, detail=f'product not found'
        )
    except PyJWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.put('/product/disc')
async def productDisc(discount: Discount, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if(not isAdmin(token)):
            raise HTTPException(
		status_code=404, detail=f'only admin can access')
        # TODO cari prudct yang id nya sama
        productFound = False
        discount_dict = discount.dict()
        for productIdx, product in enumerate(data['product']):
            if(product['idProduct'] == discount_dict['idProduct']):
                # TODO jika ketemu lakukan dicount terhadap product
                data['product'][productIdx]['price'] = data['product'][productIdx]['price'] - (data['product'][productIdx]['price'] * (discount_dict['discount'])/100)
                productFound = True
                # save ke json
                filterCriteria = {"_id": ObjectId(data['_id'])}
                updateQuery1 = {
                    "$set": {
                        "product": data["product"]
                    }
                }
                updateQuery2 = {
                    "$set": {
                        "product_stock": data["product_stock"]
                    }
                }
                updateQuery3 = {
                    "$set": {
                        "category": data["category"]
                    }
                }
                datas.update_one(filterCriteria, updateQuery1)
                datas.update_one(filterCriteria, updateQuery2)
                datas.update_one(filterCriteria, updateQuery3)
                # masukkan ke dalam json
                # with open(json_filename, "w") as write_file: 
                #     json.dump(data, write_file)
                return "Data upadated"
        if not productFound:
        # TODO kalau tidak, lakukan http exception (product not found)
            raise HTTPException(
            status_code=404, detail=f'product not found'
        )
    except PyJWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.put('/product/markUp')
async def productMarkUp(markUp: MarkUp, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if(not isAdmin(token)):
            raise HTTPException(
		status_code=404, detail=f'only admin can access')
        # TODO cari prudct yang id nya sama
        productFound = False
        markup_dict = markUp.dict()
        for productIdx, product in enumerate(data['product']):
            if(product['idProduct'] == markup_dict['idProduct']):
                # TODO jika ketemu lakukan dicount terhadap product
                data['product'][productIdx]['price'] = data['product'][productIdx]['price'] + (data['product'][productIdx]['price'] * (markup_dict['markUp'])/100)
                productFound = True
                # masukkan ke dalam json
                # save ke json
                filterCriteria = {"_id": ObjectId(data['_id'])}
                updateQuery1 = {
                    "$set": {
                        "product": data["product"]
                    }
                }
                updateQuery2 = {
                    "$set": {
                        "product_stock": data["product_stock"]
                    }
                }
                updateQuery3 = {
                    "$set": {
                        "category": data["category"]
                    }
                }
                datas.update_one(filterCriteria, updateQuery1)
                datas.update_one(filterCriteria, updateQuery2)
                datas.update_one(filterCriteria, updateQuery3)
                # with open(json_filename, "w") as write_file: 
                #     json.dump(data, write_file)
                return "Data upadated"
        if not productFound:
        # TODO kalau tidak, lakukan http exception (product not found)
            raise HTTPException(
            status_code=404, detail=f'product not found'
        )
    except PyJWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

#! ROUTING Categoy
@app.get('/category')
async def getAllcategory(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return data['category']
    except PyJWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get('/category/{categoryId}')
async def getcategoryById(categoryId: int, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        for category in data['category']:
            if(category['categoryId'] == categoryId):
                return category
        raise HTTPException(
            status_code=404, detail=f'category not found'
        )
    except PyJWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post('/category')
async def postcategory(category: Category, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if(not isAdmin(token)):
            raise HTTPException(
		status_code=404, detail=f'only admin can access')
        category_dict = category.dict()
        categoryFound = False
        for category in data['category']:
            if(category['categoryId']==category_dict['categoryId']):
                # ketemu category
                categoryFound = True
                return "category with ID"+str(category_dict['categoryId'])+"already exist"
        if not categoryFound:
            data['category'].append(category_dict)
                # save ke json
            filterCriteria = {"_id": ObjectId(data['_id'])}
            updateQuery1 = {
                "$set": {
                    "product": data["product"]
                }
            }
            updateQuery2 = {
                "$set": {
                    "product_stock": data["product_stock"]
                }
            }
            updateQuery3 = {
                "$set": {
                    "category": data["category"]
                }
            }
            datas.update_one(filterCriteria, updateQuery1)
            datas.update_one(filterCriteria, updateQuery2)
            datas.update_one(filterCriteria, updateQuery3)
            # save ke json
            # with open(json_filename, "w") as write_file: 
            #     json.dump(data, write_file)
            
            return category_dict
        
        raise HTTPException(
            status_code=404, detail=f'category not found'
        )
    except PyJWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.put('/category')
async def updatecategory(category: Category, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if(not isAdmin(token)):
            raise HTTPException(
		status_code=404, detail=f'only admin can access')
        category_dict = category.dict()
        categoryFound = False
        for category_idx, category in enumerate(data['category']):
            if(category['categoryId'] == category_dict['categoryId']):
                categoryFound=True
                data['category'][category_idx] = category_dict
                # save ke json
                filterCriteria = {"_id": ObjectId(data['_id'])}
                updateQuery1 = {
                    "$set": {
                        "product": data["product"]
                    }
                }
                updateQuery2 = {
                    "$set": {
                        "product_stock": data["product_stock"]
                    }
                }
                updateQuery3 = {
                    "$set": {
                        "category": data["category"]
                    }
                }
                datas.update_one(filterCriteria, updateQuery1)
                datas.update_one(filterCriteria, updateQuery2)
                datas.update_one(filterCriteria, updateQuery3)
                # with open(json_filename, "w") as write_file:
                #     json.dump(data, write_file)
                return category_dict
            
        if not categoryFound:
            raise HTTPException(
            status_code=404, detail=f'category not found'
        )
        
        raise HTTPException(
            status_code=404, detail=f'category not found'
        )
    except PyJWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        
@app.delete('/category/{categoryId}')
async def deletecategory(categoryId: int, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if(not isAdmin(token)):
            raise HTTPException(
		status_code=404, detail=f'only admin can access')
        categoryFound = False
        for category_idx, category in enumerate(data['category']):
            if(category['categoryId'] == categoryId):
                categoryFound = True
                data['category'].pop(category_idx)
                # save ke json
                filterCriteria = {"_id": ObjectId(data['_id'])}
                updateQuery1 = {
                    "$set": {
                        "product": data["product"]
                    }
                }
                updateQuery2 = {
                    "$set": {
                        "product_stock": data["product_stock"]
                    }
                }
                updateQuery3 = {
                    "$set": {
                        "category": data["category"]
                    }
                }
                datas.update_one(filterCriteria, updateQuery1)
                datas.update_one(filterCriteria, updateQuery2)
                datas.update_one(filterCriteria, updateQuery3)
                # masukkan ke dalam json
                # with open(json_filename, "w") as write_file: 
                #     json.dump(data, write_file)
                return "category deleted"
            
        if not categoryFound:
            raise HTTPException(
            status_code=404, detail=f'category not found'
        )

        
        raise HTTPException(
            status_code=404, detail=f'category not found'
        )
    except PyJWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


#! ROUTING Stock
@app.get('/product_stock')
async def getAllProductStock(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return data['product_stock']
    except PyJWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get('/product_stock/{idProduct}/{ukuran}')
async def getProductStockbyIdProductAndUkuran(idProduct: int, ukuran: str, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        for row in data['product_stock']:
            if(row['idProduct'] == idProduct and row['ukuran'] == ukuran):
                return row
        raise HTTPException(
            status_code=404, detail=f'data not found'
        )
    except PyJWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post('/product_stock')
async def postnNewRow(newRow: ProductStock, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if(not isAdmin(token)):
            raise HTTPException(
		status_code=404, detail=f'only admin can access')
        row_dict = newRow.dict()
        rowFound = False
        for row in data['product_stock']:
            if(row['idProduct'] == row_dict['idProduct'] and row['ukuran'] == row_dict['ukuran']):
                rowFound = True
                return "Data already exist"
        if not rowFound:
            data['product_stock'].append(row_dict)
                # save ke json
            filterCriteria = {"_id": ObjectId(data['_id'])}
            updateQuery1 = {
                "$set": {
                    "product": data["product"]
                }
            }
            updateQuery2 = {
                "$set": {
                    "product_stock": data["product_stock"]
                }
            }
            updateQuery3 = {
                "$set": {
                    "category": data["category"]
                }
            }
            datas.update_one(filterCriteria, updateQuery1)
            datas.update_one(filterCriteria, updateQuery2)
            datas.update_one(filterCriteria, updateQuery3)
            # save ke json
            # with open(json_filename, "w") as write_file: 
            #     json.dump(data, write_file)
            
            return row_dict
        
        raise HTTPException(
            status_code=404, detail=f'Data not found'
        )
    except PyJWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.put('/product_stock')
async def updateStock(newRow: ProductStock, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if(not isAdmin(token)):
            raise HTTPException(
		status_code=404, detail=f'only admin can access')
        row_dict = newRow.dict()
        rowFound = False
        for row_idx, row in enumerate(data['product_stock']):
            if(row['idProduct'] == row_dict['idProduct'] and row['ukuran'] == row_dict['ukuran']):
                rowFound=True
                data['product_stock'][row_idx] = row_dict
                # save ke json
                filterCriteria = {"_id": ObjectId(data['_id'])}
                updateQuery1 = {
                    "$set": {
                        "product": data["product"]
                    }
                }
                updateQuery2 = {
                    "$set": {
                        "product_stock": data["product_stock"]
                    }
                }
                updateQuery3 = {
                    "$set": {
                        "category": data["category"]
                    }
                }
                datas.update_one(filterCriteria, updateQuery1)
                datas.update_one(filterCriteria, updateQuery2)
                datas.update_one(filterCriteria, updateQuery3)
                # with open(json_filename, "w") as write_file:
                #     json.dump(data, write_file)
                return row_dict
            
        if not rowFound:
            raise HTTPException(
            status_code=404, detail=f'data not found'
        )
        
        raise HTTPException(
            status_code=404, detail=f'data not found'
        )
    except PyJWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ! FETCH API LUAR
def decode_to_eksternal_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        externalToken: str = payload.get("tokenEksternal")
        if externalToken is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return externalToken
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def decode_to_eksternal_username(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# utils
def usernameToId(username, eksternalToken):
    # TODO get all user dulu
    headers = {'Authorization': f'Bearer {eksternalToken}'}
    users = requests.get(url+'users', headers=headers).json()
    # TODO bakalan dapet array of array
    # TODO laukan iterasi pada array yang luar
    for element in users:
        # TODO lakukan pengecekan jika index ke 6 sama dengan username, return index ke 0 
        if(element[6] == username):
            return element[0]
    return -1


# Menggunakan token untuk mengakses endpoint tertentu

def createCustomizationRequests(specialInstructions, username, price, stock, font, color, size, productType, descriptions, imageUrl, eksternalToken ):
    userId = usernameToId(username, eksternalToken)
    if(userId != -1):
        # ! REQUEST UNTUK MEMBUAT PRODUCT
        headers= {'Authorization': f'Bearer {eksternalToken}'}
        data1 = {
            "description": descriptions,
            "price":price,
            "stock": stock,
            "default_font": font,
            "default_color":color,
            "size": size,
            "productType": productType,
            "imageurl": imageUrl
        }
        urlEndpoint1 = url+"products"
        res1 = requests.post(urlEndpoint1, params=data1, headers=headers).json()

        # ! AMBIL ID PRODUCT YANG BARU DIINPUT dengan get all product
        urlEndpoint2 = url+"products"
        res2 = requests.get(urlEndpoint2, headers=headers).json()
        idProductLuar = res2[len(res2)-1][0]


        # ! REQUEST UNTUK MEMBUAT CUSTOMIZATION REQ
        data = {
            "userID": userId,
            "productID": idProductLuar,
            "specialInstructions": specialInstructions
        }
        print(data)
        urlEndpoint = url+"customizationRequests"
        res = requests.post(urlEndpoint, params=data, headers=headers).json()

        # ! AMBIL JUGA ID DARI CUSTOMIZATIONNYA KARENA KITA BUTUH
        urlEndpoint3 = url+"customizationRequests"
        res3 = requests.get(urlEndpoint3, headers=headers).json()
        idCustomization = res3[len(res3)-1][0]
        
        return {
            "res1": res1,
            "res2": res2,
            "res":res,
            "idProductLuar":idProductLuar,
            "idCustomization": idCustomization
        }
    else:
        raise HTTPException(
		    status_code=400, detail=f'not authenticated'
	    )

def getRequestByCustomerId(externalToken, customerId):
    url = 'http://localhost:8004/'
    headers = {'Authorization': f'Bearer {externalToken}'}
    hasil = []
    res = requests.get(url+f'customizationRequests/{customerId}', headers=headers).json()[0]
    if(len(res) > 0):
        for element in res:
            product = requests.get(url+f'products/{element[2]}', headers=headers).json()[0]
            inst = {
                "customizationId": element[0],
                "productId": element[2],
                "specialInstructions": element[3],
                "font": product[4],
                "color": product[5],
                "descriptions": product[1],
                "price": product[2],
                "stock": product[3],
                "size": product[6],
                "productType": product[7]
            }
            hasil.append(inst)
        return hasil
    else:
        return {"messages": "you don't have any fashion customization request yet"}

def deleteCustomizationRequests(idCustomization, eksternalToken):
    headers = {'Authorization': f'Bearer {eksternalToken}'}
    urlEndpoint = url+"customizationRequests/"+str(idCustomization)
    # ! hapus juga productnya pada external api
    urlEndpointGet = url+"customizationRequests"
    arrRequest = requests.get(urlEndpointGet, headers=headers).json()
    idProduk = -1
    for element in arrRequest:
        if(element[0] == idCustomization):
            idProduk = element[2]
            break
    urlEndpointDelete = url+f"products/{idProduk}"
    res = requests.delete(urlEndpoint, headers=headers).json()
    res1 = requests.delete(urlEndpointDelete, headers=headers)
    return res

@app.post('/customization')
async def createCustomization(rowBaru: Customization, token: str = Depends(oauth2_scheme)):
    try:
        newRow = rowBaru.dict()
        print(newRow)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        externalToken: str = payload.get("tokenEksternal")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        #  todo ambil dulu si product yang sesuai dengan productId
        productDalam = await getProductById(newRow['productId'], token=token)
        # todo ambil juga row dari productStocknya
        productStockDalam = await getProductStockbyIdProductAndUkuran(idProduct=newRow['productId'], ukuran=newRow['size'], token=token)
        # todo ambil juga kategorinya
        kategoriDalam = await getcategoryById(productDalam['categoryId'], token=token)
        # todo panggil fungsi yang telah dibuat untuk memanggil api luar dengan data-data yang dibutuhkan berada di dalam product
        res = createCustomizationRequests(newRow["specialInstructions"], username, productDalam['price'], productStockDalam['stock'], newRow['font'], newRow['color'], newRow['size'], kategoriDalam['categoryName'], newRow['descriptions'], newRow['imageUrl'], eksternalToken=externalToken)
        # todo kembalikan bahwa customization request berhasil dibuat
        return "customization request has been added sucessfully"
    except PyJWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get('/Mycustomization')
async def getMyCustomization(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        externalToken: str = payload.get("tokenEksternal")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        print("username")
        # todo panggil dulu fungsi untuk mengubah username menjadi userId luar
        userIdLuar = usernameToId(username, externalToken)
        # todo lakukan fetch ke api luar get request by id
        hasil = getRequestByCustomerId(externalToken, userIdLuar)
        # todo return hasilnya
        return hasil
    except PyJWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.delete('/customization')
async def DeleteMyCustomization(idCustomization : int,token: str = Depends(oauth2_scheme)):
    # todo panggil delete customization Request
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        externalToken: str = payload.get("tokenEksternal")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        res = deleteCustomizationRequests(idCustomization, externalToken)
        return "customization request has been deleted sucessfully"
    except PyJWTError: 
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
@app.get("/")
async def login(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("login.html", context)

@app.get("/dashboard")
async def dashboard(request: Request, access_token: str = Cookie(default=None)):
    try: 
        if(access_token is None):
            raise HTTPException(status_code=401, detail="Unauthorized")
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        data = await getAllProduct(token=access_token)
        context = {"request": request, "username": username, "data": data}
        return templates.TemplateResponse("dashboard.html", context)
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
@app.get("/categoryDashboard")
async def categorydashboard(request: Request, access_token: str = Cookie(default=None)):
    try: 
        if(access_token is None):
            raise HTTPException(status_code=401, detail="Unauthorized")
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        data = await getAllcategory(token=access_token)
        context = {"request": request, "username": username, "data": data}
        return templates.TemplateResponse("categoryDashboard.html", context)
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/stockDashboard")
async def stockdashboard(request: Request, access_token: str = Cookie(default=None)):
    try: 
        if(access_token is None):
            raise HTTPException(status_code=401, detail="Unauthorized")
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        dataStock = await getAllProductStock(token=access_token)
        data = await getAllProduct(token=access_token)
        context = {"request": request, "username": username, "data": data, "dataStock": dataStock}
        return templates.TemplateResponse("stockDashboard.html", context)
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
@app.get("/customizationDashboard")
async def stockdashboard(request: Request, access_token: str = Cookie(default=None)):
    try: 
        print("satu")
        if(access_token is None):
            raise HTTPException(status_code=401, detail="Unauthorized")
        print("dua")
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        print("tiga")
        username: str = payload.get("sub")
        print("empat")
        dataStock = await getAllProductStock(token=access_token)
        print("lima")
        dataCustomization = await getMyCustomization(token=access_token)
        print("enal")
        context = {"request": request, "username": username, "dataCustomization": dataCustomization, "dataStock": dataStock}
        print("tujuh")
        return templates.TemplateResponse("customizationDashboard.html", context)
    except PyJWTError:
        print("sembilan")
        raise HTTPException(status_code=401, detail="Invalid token")
    