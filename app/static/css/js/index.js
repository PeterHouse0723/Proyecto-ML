document.addEventListener('DOMContentLoaded', function() {
    const userIcon = document.getElementById('userIcon');
    const dropdownMenu = document.getElementById('dropdownMenu');

    userIcon.addEventListener('click', function(e) {
        dropdownMenu.style.display = (dropdownMenu.style.display === 'block' ? 'none' : 'block');
        e.stopPropagation();
    });

    // Cerrar el menú al hacer clic fuera
    document.addEventListener('click', function(e) {
        dropdownMenu.style.display = 'none';
    });

    // Evitar cerrar si se hace clic dentro del menú
    dropdownMenu.addEventListener('click', function(e) {
        e.stopPropagation();
    });
});
