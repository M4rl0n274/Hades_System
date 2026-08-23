document.addEventListener("DOMContentLoaded", function () {
  var overlay = document.getElementById("flashModalOverlay");
  if (!overlay) return; // no hay mensajes flash, no hacemos nada

  var btnX = document.getElementById("flashModalClose");
  var btnCerrar = document.getElementById("flashModalBtnCerrar");

  function cerrarModal() {
    overlay.classList.add("closing");
    overlay.addEventListener(
      "animationend",
      function () {
        overlay.remove();
      },
      { once: true },
    );
  }

  // Cerrar con la X
  btnX.addEventListener("click", cerrarModal);

  // Cerrar con el botón "Cerrar"
  btnCerrar.addEventListener("click", cerrarModal);

  // Cerrar haciendo clic en el fondo (fuera de la caja del modal)
  overlay.addEventListener("click", function (e) {
    if (e.target === overlay) {
      cerrarModal();
    }
  });

  // Cerrar con la tecla Esc
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && document.body.contains(overlay)) {
      cerrarModal();
    }
  });
});
