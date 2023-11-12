import datetime
from pstats import Stats
import statistics
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Request, applications
import json
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
    password: str



# ! FAST API
app = FastAPI()

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

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):

    # TODO Melakukan pemerikasaan terhadap username (apakah terdapat dalam database)
    # melakukan pencarian terhadap username
    foundUsername = False
    for pengguna in user['users']:
        if(pengguna['username'] == form_data.username):
            foundUsername = True
            currentUser = pengguna
            break
    # TODO jika email tidak ditemukan, raise http exception ("username not found")
    if(not foundUsername):
        raise HTTPException(
		status_code=404, detail=f'user not found'
	)

    # TODO melakukan pemeriksaan apakah passwordnya benar atau salah 
    # TODO jika passwordnya salah, raise http exception ("incorrect password")
    if not bcrypt.checkpw(form_data.password.encode('utf-8'), currentUser['password'].encode('utf-8')):
        raise HTTPException(
		status_code=401, detail=f'incorrect password'
	)
    # TODO jika benar, tambahkan data user, kemudian kembalikan berupa jwt
    # Jika informasi pengguna benar, buat token JWT

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/createUAdmin")
async def createAdmin(form_data: OAuth2PasswordRequestForm = Depends()):
    # TODO LAKUKAN PENGECEKAN TERHADAP USERNAME
    foundUsername = False
    for admin in user['users']:
        if(admin['username'] == form_data.username):
            foundUsername = True
            break
    # TODO JIKA USERNAME TELAH TERDAFTAR, RAISE HTTP EXCEPTION (USERNAME HAS ALREADY BEEN TAKEN)
    if(foundUsername):
        raise HTTPException(
		status_code=404, detail=f'username has already been taken'
	)
    else:
        # TODO JIKA USERNAME BELUM TERDAFTAR, CEK PASSWORD  
        if(len(form_data.password) < 6):
            # TODO JIKA PASSWORD KURANG DARI 6 KARAKTER, RAISE HTTP EXCEPTION (PASSWORD MUST BE 6 CHARACTERS OR MORE)
            raise HTTPException(
		    status_code=404, detail=f'password must be 6 characters or more'
	    )
        else:
            password = bcrypt.hashpw(form_data.password.encode('utf-8'), bcrypt.gensalt())
            password_string = password.decode('utf-8')
            user_dict = {"username": form_data.username, "password": password_string, "role": "admin"}
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



@app.post("/createUser")
async def createUser(form_data: OAuth2PasswordRequestForm = Depends()):
    # TODO LAKUKAN PENGECEKAN TERHADAP USERNAME
    foundUsername = False
    for pengguna in user['users']:
        if(pengguna['username'] == form_data.username):
            foundUsername = True
            break
    # TODO JIKA USERNAME TELAH TERDAFTAR, RAISE HTTP EXCEPTION (USERNAME HAS ALREADY BEEN TAKEN)
    if(foundUsername):
        raise HTTPException(
		status_code=404, detail=f'username has already been taken'
	)
    else:
        # TODO JIKA USERNAME BELUM TERDAFTAR, CEK PASSWORD  
        if(len(form_data.password) < 6):
            # TODO JIKA PASSWORD KURANG DARI 6 KARAKTER, RAISE HTTP EXCEPTION (PASSWORD MUST BE 6 CHARACTERS OR MORE)
            raise HTTPException(
		    status_code=404, detail=f'password must be 6 characters or more'
	    )
        else:
            password = bcrypt.hashpw(form_data.password.encode('utf-8'), bcrypt.gensalt())
            password_string = password.decode('utf-8')
            user_dict = {"username": form_data.username, "password": password_string, "role": "user"}
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