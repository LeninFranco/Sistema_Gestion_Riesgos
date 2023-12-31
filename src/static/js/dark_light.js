const invertirColores = (esOscuro) => {
    const body = document.querySelector("body");
    const navbarDropdown = document.querySelector(".navbar .dropdown-menu");
    const dropdownItems = document.querySelectorAll(".navbar .dropdown-menu .dropdown-item");
    const labels = document.querySelector(".dataTables_filter label");
    const buttons = document.querySelectorAll('.btn-more');

    if (esOscuro) {
        body.setAttribute('data-bs-theme', 'dark');
        body.style.backgroundColor = "#212529";
        body.style.color = "white";
        navbarDropdown.style.backgroundColor = "#212529";
        navbarDropdown.style.color = "white";
        dropdownItems.forEach(item => {
            item.style.backgroundColor = "#212529";
            item.style.color = "white";
        });
        buttons.forEach(button =>{
            button.classList.remove('btn-dark');
            button.classList.add('btn-light');
        });
        if (labels != null){
            labels.style.color = 'white';
        }
    } else {
        body.setAttribute('data-bs-theme', 'light');
        body.style.backgroundColor = "white";
        body.style.color = "black";
        navbarDropdown.style.backgroundColor = "white";
        navbarDropdown.style.color = "black";
        dropdownItems.forEach(item => {
            item.style.backgroundColor = "white";
            item.style.color = "black";
        });
        buttons.forEach(button =>{
            button.classList.remove('btn-light');
            button.classList.add('btn-dark');
        });
        if (labels != null){
            labels.style.color = 'black';
        }
    }
}

const cambiarTema = () => {
    const temaActual = localStorage.getItem('tema');
    if (temaActual === 'claro') {
        invertirColores(true);
        localStorage.setItem('tema', 'oscuro');
    } else {
        invertirColores(false);
        localStorage.setItem('tema', 'claro');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const temaAlmacenado = localStorage.getItem('tema');
    if (temaAlmacenado) {
        invertirColores(temaAlmacenado === 'oscuro');
    }
});