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
            <th>Category Id</th>
            <th>Category Name</th>
          </tr>
        </thead>
        <tbody>`
        data.forEach((el) => {
            kumpulan = kumpulan + `<tr>
        <td>
        ${el.categoryId}
        </td>
        <td>
        ${el.categoryName}
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
    if (data.detail || data.categoryId == undefined) {
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
            <th>Category Id</th>
            <th>Category Name</th>
          </tr>
        </thead>
        <tbody>
        <tr>
        <td>
        ${data.categoryId}
        </td>
        <td>
        ${data.categoryName}
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
        Category added successfully
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

const getAllCategoryExecute = document.getElementById("getAllCategoryExecute")
console.log(getAllCategoryExecute);
getAllCategoryExecute.addEventListener("click", async function (e) {
    e.preventDefault();
    longRunningOperation();
    // todo hit api getAllProduct
    const url = "/category"
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
    updateTabelProduk(data, "getAllCategory");
    // todo ambil datanya dan ubah dulu menjadi json
    // todo jalankan fungsi updateTabelProduk
})

const getCategoryByIdExecute = document.getElementById("getCategoryByIdExecute");
const inputCategoryId = document.getElementById("inputCategoryId")
getCategoryByIdExecute.addEventListener("click", async (e) => {
    e.preventDefault();
    longRunningOperation();
    // todo hit api getAllProduct
    const url = `/category/${inputCategoryId.value}`;
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
    updateTabelProdukSingle(data, "getCategoryById");
    // todo ambil datanya dan ubah dulu menjadi json
    // todo jalankan fungsi updateTabelProduk
})



const categoryIdPost = document.getElementById("categoryIdPost")
const namePost = document.getElementById("namePost")
const categorySubmitPost = document.getElementById("categorySubmitPost");

// console.log({ categoryIdPost, namePost, pricePost, categoryIdPost, linkPost, categorySubmitPost });
categorySubmitPost.addEventListener("click", async function (e) {
    e.preventDefault();
    longRunningOperation();
    const data = {
        categoryId: categoryIdPost.value,
        categoryName: namePost.value,
    }
    const url = `/category`;
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
    returnLayarPost(dataHasil, "categoryPost");
    if (dataHasil.detail == undefined) {
        location.assign("/categoryDashboard")
    }
})

const deleteCategoryButton = document.querySelectorAll(".deleteCategoryButton");
// console.log(deleteCategoryButton);
// console.log("halo");
if (deleteCategoryButton.length > 0) {
    for (let i = 0; i < deleteCategoryButton.length; i++) {
        deleteCategoryButton[i].addEventListener("click", async (e) => {
            e.preventDefault();
            longRunningOperation();
            const dataId = deleteCategoryButton[i].getAttribute("data-id");
            const url = `/category/${dataId}`;
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
                returnLayar(dataHasil, "categoryDelete");
            }
            else {
                location.assign("/categoryDashboard");
            }
        })
    }
}

const updateCategoryButton = document.querySelectorAll(".updateCategoryButton");
console.log(updateCategoryButton);
if (updateCategoryButton.length > 0) {
    for (let i = 0; i < updateCategoryButton.length; i++) {
        updateCategoryButton[i].addEventListener("click", async (e) => {
            sidebar.classList.toggle('hide');
            const dataId = updateCategoryButton[i].getAttribute("data-id");
            const modal = new bootstrap.Modal(document.getElementById("modalUpdateCategory"));
            modal.show();
            const finalButton = document.getElementById("updateCategoryFinal");
            finalButton.setAttribute("data-id", dataId);
            const name = document.getElementById("nameUpdate");

            finalButton.addEventListener("click", async (e) => {
                longRunningOperation();
                e.preventDefault();
                // udah kesimpen data-id di final button
                const data = {
                    categoryId: finalButton.getAttribute("data-id"),
                    categoryName: name.value,
                }
                const url = `/category`;
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
                    location.assign("/categoryDashboard");
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
