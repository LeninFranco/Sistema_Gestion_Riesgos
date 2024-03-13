const expresiones = {
    password: /^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/
}

document.addEventListener("DOMContentLoaded", function () {
    let formulario = document.getElementById("formulario");

    const validarPassword = (e) => {
        const inputPassword = document.getElementsByName("password-new")[0];
        if (expresiones.password.test(e.target.value)) {
            inputPassword.style.backgroundColor = "#c3e6cb"; // Color verde para válido
        } else {
            inputPassword.style.backgroundColor = "#f5c6cb"; // Color rojo para inválido
        }
    }

    document.getElementsByName("password")[0].addEventListener('keyup', validarPassword);
    document.getElementsByName("password")[0].addEventListener('blur', validarPassword);
});