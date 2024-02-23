window.addEventListener("load", function () {

    // icono para poder interaccionar con el elemento
    showPassword = document.querySelector('.show-password');
    showPassword.addEventListener('click', () => {

        // elementos input de tipo password
        password = document.querySelector('.password');

        if (password.type === "text") {
            password.type = "password"
            showPassword.classList.remove('fa-eye-slash');
            showPassword.classList.toggle('fa-eye')
        } else {
            password.type = "text"
            showPassword.classList.remove('fa-eye');
            showPassword.classList.toggle("fa-eye-slash");
        }
    })
});