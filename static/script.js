const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');

registerBtn.addEventListener('click', () => {
    container.classList.add("active");
});

loginBtn.addEventListener('click', () => {
    container.classList.remove("active");
});



// Event listener yang membutuhkan waktu lama
function longRunningOperation() {
    // Menampilkan overlay atau elemen pemuatan saat operasi dimulai
    document.getElementById('loading-overlay').style.display = 'flex';

    // Proses operasi yang membutuhkan waktu lama
    setTimeout(function () {
        // Selesai, menyembunyikan overlay atau elemen pemuatan
        document.getElementById('loading-overlay').style.display = 'none';
    }, 12000); // Contoh: Menunggu 3 detik
}

// Menetapkan event listener ke elemen atau kejadian tertentu
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('loading-overlay').style.display = 'none'; // Pastikan overlay tersembunyi awalnya
    document.getElementById('loading-spinner').style.display = 'none'; // Optional: Jika tidak menggunakan animasi spinner

    // Menetapkan event listener ke tombol atau elemen yang akan memicu operasi yang membutuhkan waktu lama

    // const form = document.querySelector("form");
    //   const emailError = document.querySelector(".email.error");
    //   const passwordError = document.querySelector(".password.error");
    const buttonLogin = document.getElementById("signIn");
    const passwordError = document.querySelector(".password.error");
    const inputUsernameLogin = document.getElementById("usernameLogin");
    const inputPasswordLogin = document.getElementById("passwordLogin");

    // console.log(buttonLogin);
    // console.log(passwordError);
    // console.log(inputUsernameLogin);
    // console.log(inputPasswordLogin);

    buttonLogin.addEventListener("click", async (e) => {
        e.preventDefault();
        longRunningOperation();
        // console.log("halo");
        // reset errors
        passwordError.textContent = "";

        // get values
        const username = inputUsernameLogin.value;
        const password = inputPasswordLogin.value;

        try {
            const res = await fetch("/token", {
                method: "POST",
                body: JSON.stringify({ username: username, password: password }),
                headers: { "Content-Type": "application/json" },
            });
            const data1 = await res.json();
            console.log(data1.access_token);
            // console.log(data);
            if (data1.detail) {
                passwordError.textContent = data1.detail;
            }
            else {
                // todo taro di local storage
                localStorage.setItem("token", data1.access_token)
                location.assign("/dashboard")
            }
            // console.log(data);

        } catch (err) {
            console.log(err);
        }
    });


    const usernameInputRegister = document.getElementById("usernameInputRegister");
    const passwordInputRegister = document.getElementById("passwordInputRegister");
    const selectOption = document.getElementById("role");
    const errorEmail = document.querySelector(".error.email");
    const buttonSignup = document.getElementById("buttonSignup");

    console.log({ usernameInputRegister, passwordInputRegister, selectOption, errorEmail, buttonSignup });

    buttonSignup.addEventListener("click", async (e) => {
        e.preventDefault();
        longRunningOperation();
        // console.log("halo");
        // reset errors
        errorEmail.textContent = "";

        // get values
        const username = usernameInputRegister.value;
        const password = passwordInputRegister.value;
        const role = selectOption.value;
        console.log(username);
        console.log(password);
        console.log(role);
        if (role == "user") {
            try {
                const res = await fetch("/createUser", {
                    method: "POST",
                    body: JSON.stringify({ username, password }),
                    headers: { "Content-Type": "application/json" },
                });
                const data = await res.json();
                console.log(data);
                if (data.detail) {
                    errorEmail.textContent = data.detail;
                }
                else {
                    // todo taro di local storage
                    localStorage.setItem("token", data.access_token)
                    const res = await fetch("/token", {
                        method: "POST",
                        body: JSON.stringify({ username, password }),
                        headers: { "Content-Type": "application/json" },
                    });
                    const token = await res.json();
                    // console.log(token.access_token);
                    console.log((token));
                    localStorage.setItem("token", token.access_token)
                    location.assign("/dashboard")
                }
                // console.log(data);

            } catch (err) {
                console.log(err);
            }
        }
        else {
            try {
                const res = await fetch("/createUAdmin", {
                    method: "POST",
                    body: JSON.stringify({ username, password }),
                    headers: { "Content-Type": "application/json" },
                });
                const data = await res.json();
                console.log(data);
                if (data.detail) {
                    errorEmail.textContent = data.detail;
                }
                else {
                    // todo taro di local storage
                    localStorage.setItem("token", data.access_token)
                    const res = await fetch("/token", {
                        method: "POST",
                        body: JSON.stringify({ username, password }),
                        headers: { "Content-Type": "application/json" },
                    });
                    const token = await res.json();
                    // console.log(token.access_token);
                    console.log((token));
                    localStorage.setItem("token", token.access_token)
                    location.assign("/dashboard")
                }
                // console.log(data);

            } catch (err) {
                console.log(err);
            }
        }
    });

});