const allSideMenu = document.querySelectorAll('#sidebar .side-menu.top li a');

function longRunningOperation() {
    // Menampilkan overlay atau elemen pemuatan saat operasi dimulai
    document.getElementById('loading-overlay').style.display = 'flex';

    // Proses operasi yang membutuhkan waktu lama
    setTimeout(function () {
        // Selesai, menyembunyikan overlay atau elemen pemuatan
        document.getElementById('loading-overlay').style.display = 'none';
    }, 3000); // Contoh: Menunggu 3 detik
}

const updateTabelProduk = function (data, idContainer) {
    const dataContainer = document.getElementById(idContainer);
    if (data.detail) {
        const tipe = typeof data.detail;
        if (tipe == "string") {

            dataContainer.innerHTML = `<div class="alert alert-danger" role="alert">
            ${data.detail}
            </div>`
        }
        else {
            dataContainer.innerHTML = `<div class="alert alert-danger" role="alert">
            please input a valid number
            </div>`

        }
    }
    else {
        let kumpulan = `<table>
        <thead>
          <tr>
            <th>Product Id</th>
            <th>Name</th>
            <th>Price</th>
            <th>Category Id</th>
            <th>Video</th>
          </tr>
        </thead>
        <tbody>`
        data.forEach((el) => {
            kumpulan = kumpulan + `<tr>
        <td>
        ${el.idProduct}
        </td>
        <td>
        ${el.name}
        </td>
        <td>
        ${el.price}
        </td>
        <td>
        ${el.categoryId}
        </td>
        <td>
                      <iframe
                        width="560"
                        height="315"
                        src="${el.link}"
                        frameborder="0"
                        allowfullscreen
                      ></iframe>
                    </td>
      </tr>`
        })
        kumpulan = kumpulan + `
        </tbody>
      </table>`
        dataContainer.innerHTML = kumpulan
    }
}

const updateTabelProdukSingle = function (data, idContainer) {
    const dataContainer = document.getElementById(idContainer);
    if (data.detail) {
        const tipe = typeof data.detail;
        if (tipe == "string") {

            dataContainer.innerHTML = `<div class="alert alert-danger" role="alert">
            ${data.detail}
            </div>`
        }
        else {
            dataContainer.innerHTML = `<div class="alert alert-danger" role="alert">
            please input a valid number
            </div>`

        }
    }
    else {
        dataContainer.innerHTML = `<table>
        <thead>
          <tr>
            <th>Product Id</th>
            <th>Name</th>
            <th>Price</th>
            <th>Category Id</th>
            <th>Video</th>
          </tr>
        </thead>
        <tbody>
        <tr>
        <td>
        ${data.idProduct}
        </td>
        <td>
        ${data.name}
        </td>
        <td>
        ${data.price}
        </td>
        <td>
        ${data.categoryId}
        </td>
        <td>
                      <iframe
                        width="560"
                        height="315"
                        src="${data.link}"
                        frameborder="0"
                        allowfullscreen
                      ></iframe>
                    </td>
      </tr>
      </tbody>
      </table>`
    }
}

const returnLayar = function (data, idContainer) {
    const dataContainer = document.getElementById(idContainer);
    if (data.detail) {
        const tipe = typeof data.detail;
        if (tipe == "string") {

            dataContainer.innerHTML = `<div class="alert alert-danger" role="alert">
            ${data.detail}
            </div>`
        }
        else {
            dataContainer.innerHTML = `<div class="alert alert-danger" role="alert">
            please input a valid input
            </div>`

        }
    }
    else {
        dataContainer.innerHTML = `<div class="alert alert-primary" role="alert">
        ${data}
      </div>`;
    }
}

const returnLayarPost = function (data, idContainer) {
    const dataContainer = document.getElementById(idContainer);
    if (data.detail) {
        const tipe = typeof data.detail;
        if (tipe == "string") {

            dataContainer.innerHTML = `<div class="alert alert-danger" role="alert">
            ${data.detail}
            </div>`
        }
        else {
            dataContainer.innerHTML = `<div class="alert alert-danger" role="alert">
            please input a valid input
            </div>`

        }
    }
    else {
        dataContainer.innerHTML = `<div class="alert alert-primary" role="alert">
        Product added successfully
      </div>`;
    }
}

allSideMenu.forEach(item => {
    const li = item.parentElement;

    item.addEventListener('click', function () {
        allSideMenu.forEach(i => {
            i.parentElement.classList.remove('active');
        })
        li.classList.add('active');
    })
});




// TOGGLE SIDEBAR
const menuBar = document.querySelector('#content nav .bx.bx-menu');
const sidebar = document.getElementById('sidebar');

menuBar.addEventListener('click', function () {
    sidebar.classList.toggle('hide');
})







const searchButton = document.querySelector('#content nav form .form-input button');
const searchButtonIcon = document.querySelector('#content nav form .form-input button .bx');
const searchForm = document.querySelector('#content nav form');

// searchButton.addEventListener('click', function (e) {
//     if (window.innerWidth < 576) {
//         e.preventDefault();
//         searchForm.classList.toggle('show');
//         if (searchForm.classList.contains('show')) {
//             searchButtonIcon.classList.replace('bx-search', 'bx-x');
//         } else {
//             searchButtonIcon.classList.replace('bx-x', 'bx-search');
//         }
//     }
// })





// if (window.innerWidth < 768) {
//     sidebar.classList.add('hide');
// } else if (window.innerWidth > 576) {
//     searchButtonIcon.classList.replace('bx-x', 'bx-search');
//     searchForm.classList.remove('show');
// }


// window.addEventListener('resize', function () {
//     if (this.innerWidth > 576) {
//         searchButtonIcon.classList.replace('bx-x', 'bx-search');
//         searchForm.classList.remove('show');
//     }
// })



const switchMode = document.getElementById('switch-mode');

switchMode.addEventListener('change', function () {
    if (this.checked) {
        document.body.classList.add('dark');
    } else {
        document.body.classList.remove('dark');
    }
    console.log(document.body);
})

const getAllProductExecuteButton = document.getElementById("getAllProductExecute")
console.log(getAllProductExecuteButton);
getAllProductExecuteButton.addEventListener("click", async function (e) {
    e.preventDefault();
    longRunningOperation();
    // todo hit api getAllProduct
    const url = "/product"
    // ambil dulu token dari localstorage
    const token = localStorage.getItem("token")
    const option = {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
    }
    const result = await fetch(url, option);
    const data = await result.json()
    updateTabelProduk(data, "getAllProduct");
    // todo ambil datanya dan ubah dulu menjadi json
    // todo jalankan fungsi updateTabelProduk
})

const getProductByIdExecute = document.getElementById("getProductByIdExecute");
const inputProductId = document.getElementById("inputProductId")
getProductByIdExecute.addEventListener("click", async (e) => {
    e.preventDefault();
    longRunningOperation();
    // todo hit api getAllProduct
    const url = `/product/id/${inputProductId.value}`;
    // ambil dulu token dari localstorage
    const token = localStorage.getItem("token")
    const option = {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
    }
    const result = await fetch(url, option);
    const data = await result.json()
    updateTabelProdukSingle(data, "getProductById");
    // todo ambil datanya dan ubah dulu menjadi json
    // todo jalankan fungsi updateTabelProduk
})



const productIdPost = document.getElementById("productIdPost")
const namePost = document.getElementById("namePost")
const pricePost = document.getElementById("pricePost")
const categoryIdPost = document.getElementById("categoryIdPost")
const linkPost = document.getElementById("linkPost")
const productSubmitPost = document.getElementById("productSubmitPost");

// console.log({ productIdPost, namePost, pricePost, categoryIdPost, linkPost, productSubmitPost });
productSubmitPost.addEventListener("click", async function (e) {
    e.preventDefault();
    longRunningOperation();
    const data = {
        idProduct: productIdPost.value,
        name: namePost.value,
        price: pricePost.value,
        categoryId: categoryIdPost.value,
        link: linkPost.value
    }
    const url = `/product`;
    // ambil dulu token dari localstorage
    const token = localStorage.getItem("token")
    const option = {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }
    const result = await fetch(url, option);
    const dataHasil = await result.json();
    console.log(dataHasil);
    returnLayarPost(dataHasil, "productPost");
    if (dataHasil.detail == undefined) {
        location.assign("/dashboard")
    }
})

const deleteProductButton = document.querySelectorAll(".deleteProductButton");
console.log(deleteProductButton);
console.log("halo");
if (deleteProductButton.length > 0) {
    for (let i = 0; i < deleteProductButton.length; i++) {
        deleteProductButton[i].addEventListener("click", async (e) => {
            e.preventDefault();
            longRunningOperation();
            const dataId = deleteProductButton[i].getAttribute("data-id");
            const url = `/product/${dataId}`;
            // ambil dulu token dari localstorage
            const token = localStorage.getItem("token")
            const option = {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
            }
            const result = await fetch(url, option);
            const dataHasil = await result.json();
            if (dataHasil.detail) {
                returnLayar(dataHasil, "productDelete");
            }
            else {
                location.assign("/dashboard");
            }
        })
    }
}

const updateProductButton = document.querySelectorAll(".updateProductButton");
console.log(updateProductButton);
if (updateProductButton.length > 0) {
    for (let i = 0; i < updateProductButton.length; i++) {
        updateProductButton[i].addEventListener("click", async (e) => {
            sidebar.classList.toggle('hide');
            const dataId = updateProductButton[i].getAttribute("data-id");
            const modal = new bootstrap.Modal(document.getElementById("modalUpdateProduct"));
            modal.show();
            const finalButton = document.getElementById("updateProductFinal");
            finalButton.setAttribute("data-id", dataId);
            const name = document.getElementById("nameUpdate");
            const price = document.getElementById("priceUpdate");
            const categoryId = document.getElementById("categoryIdUpdate");
            const link = document.getElementById("linkUpdate");

            finalButton.addEventListener("click", async (e) => {
                longRunningOperation();
                e.preventDefault();
                // udah kesimpen data-id di final button
                const data = {
                    idProduct: finalButton.getAttribute("data-id"),
                    name: name.value,
                    price: price.value,
                    categoryId: categoryId.value,
                    link: link.value
                }
                const url = `/product`;
                // ambil dulu token dari localstorage
                const token = localStorage.getItem("token")
                const option = {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                }
                const result = await fetch(url, option);
                const dataHasil = await result.json();
                if (dataHasil.detail) {
                    returnLayar(dataHasil, "updateContainer");
                }
                else {
                    location.assign("/dashboard");
                }
            })


        })
    }
}


const logoutButton = document.getElementById("logoutAwal");

function deleteCookie(name) {
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

logoutButton.addEventListener("click", () => {
    sidebar.classList.toggle('hide');
    const modalLogout = new bootstrap.Modal(document.getElementById("modalLogout"));
    modalLogout.show();
    const lastLogoutButton = document.querySelector(".lastLogoutButton");
    lastLogoutButton.addEventListener("click", (e) => {
        e.preventDefault();
        // Menghapus item dari localStorage berdasarkan kunci
        localStorage.removeItem('token');
        deleteCookie('access_token');
        location.assign("/")
    })
})
