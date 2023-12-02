from fastapi import HTTPException
import requests, json

url = 'http://20.246.201.88/'

# Mendapatkan token
def get_token():
    token_url = url+'authentications/login'
    token_response = requests.post(token_url, data={'username': 'dzikri123', 'password': '12345678'});
    token = token_response.json().get('access_token')
    return token

# utils
def usernameToId(username):
    # TODO get all user dulu
    headers = {'Authorization': f'Bearer {get_token()}'}
    users = requests.get(url+'users', headers=headers)
    # TODO bakalan dapet array of array
    # TODO laukan iterasi pada array yang luar
    for element in users:
        # TODO lakukan pengecekan jika index ke 5 sama dengan username, return index ke 0 
        if(element[5] == username):
            return element[0]
    return -1


# Menggunakan token untuk mengakses endpoint tertentu



def createCustomizationRequests(specialInstructions, username, price, stock, font, color, size, productType, descriptions):
    userId = usernameToId(username)
    if(userId != -1):
        # ! REQUEST UNTUK MEMBUAT PRODUCT
        headers= {'Authorization': f'Bearer {get_token()}'}
        data1 = {
            "descriptions": descriptions,
            "price":price,
            "stock": stock,
            "font": font,
            "color":color,
            "size": size,
            "productType": productType
        }
        json_data1 = json.dumps(data1)
        urlEndpoint1 = url+"products"
        res1 = requests.post(urlEndpoint1, data=json_data1, headers=headers)

        # ! AMBIL ID PRODUCT YANG BARU DIINPUT dengan get all product
        urlEndpoint2 = url+"products"
        res2 = requests.get(urlEndpoint2, headers=headers)
        idProductLuar = res2[len(res2)-1][0]


        # ! REQUEST UNTUK MEMBUAT CUSTOMIZATION REQ
        data = {
            "userID": userId,
            "productID": idProductLuar,
            "specialInstructions": specialInstructions
        }
        json_data = json.dumps(data)
        urlEndpoint = url+"customizationRequests"
        res = requests.post(urlEndpoint, data=json_data, headers=headers)

        # ! AMBIL JUGA ID DARI CUSTOMIZATIONNYA KARENA KITA BUTUH
        urlEndpoint3 = url+"customizationRequests"
        res3 = requests.get(urlEndpoint3, headers=headers)
        idCustomization = res3[len(res3)-1][0]

        return {res1, res, res2, idProductLuar, idCustomization}
    else:
        raise HTTPException(
		    status_code=400, detail=f'not authenticated'
	    )



def deleteCustomizationRequests(idCustomization):
    headers = {'Authorization': f'Bearer {get_token()}'}
    urlEndpoint = url+"customizationRequests/"+str(idCustomization)
    res = requests.delete(urlEndpoint, headers=headers)
    return res






# for psy in arr:
#     print(psy)