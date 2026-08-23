document.addEventListener("DOMContentLoaded", () => {
    const togglePasswordBtn = document.getElementById("toggle-password");
    const passwordInput = document.getElementById("password");
    const iconoOjo = document.getElementById("icono-ojo");
    const authForm = document.querySelector(".auth-form");
    const btnEntrar = document.getElementById("btn-entrar");

    // Conmutador de la visibilidad de contraseña
    if (togglePasswordBtn && passwordInput && iconoOjo) {
        togglePasswordBtn.addEventListener("click", () => {
            const isPassword = passwordInput.type === "password";
            passwordInput.type = isPassword ? "text" : "password";
            iconoOjo.textContent = isPassword ? "visibility_off" : "visibility";
        });
    }

    // Prevención de doble envío
    if (authForm && btnEntrar) {
        authForm.addEventListener("submit", () => {
            btnEntrar.disabled = true;
            btnEntrar.style.opacity = "0.7";
            btnEntrar.textContent = "Entrando...";
        });
    }
});