const sidebar = document.querySelector(".sidebar");
const sidebarToggler = document.querySelector(".sidebar-toggler");
const menuToggler = document.querySelector(".menu-toggler");
// Captura dinámicamente el contenedor principal de tu app
const mainContent = document.querySelector("main") || document.querySelector(".main-content");

const collapsedSidebarHeight = "56px";
const fullSidebarHeight = "calc(100vh - 32px)";

// Función auxiliar para sincronizar la clase del elemento principal (main)
const syncMainLayout = () => {
    if (mainContent) {
        if (sidebar.classList.contains("collapsed")) {
            mainContent.classList.add("sidebar-collapsed");
        } else {
            mainContent.classList.remove("sidebar-collapsed");
        }
    }
};

// Toggle sidebar's collapsed state
sidebarToggler.addEventListener("click", () => {
    sidebar.classList.toggle("collapsed");
    syncMainLayout(); // Modificación 1: El main sigue a la barra
});

// Update sidebar height and menu toggle text
const togglerMenu = (isMenuActivate) => {
    sidebar.style.height = isMenuActivate ? `${sidebar.scrollHeight}px` : collapsedSidebarHeight;
    menuToggler.querySelector("span").innerText  = isMenuActivate ? "close" : "menu";
}

// Toggle menu-active class and adjust height 
menuToggler.addEventListener("click", () =>{
    togglerMenu(sidebar.classList.toggle("menu-active"))
});

// Adjust sidebar height on window resize
window.addEventListener("resize", () => {
    if (window.innerWidth >= 1024){
        sidebar.style.height = fullSidebarHeight;
        syncMainLayout();
    } else {
        sidebar.classList.remove("collapsed");
        if (mainContent) mainContent.classList.remove("sidebar-collapsed");
        sidebar.style.height = "auto";
        togglerMenu(sidebar.classList.contains("menu-active")); // Corregido typo nativo 'menu*active'
    }
});

// Modificación 2: Lógica de interacción para los Desplegables solicitados
const targetLabels = ["productos", "clientes", "vendedores", "facturas", "detalle factura"];
const navItems = document.querySelectorAll(".sidebar-nav .nav-item");

navItems.forEach(item => {
    const labelEl = item.querySelector(".nav-label");
    if (!labelEl) return;

    const labelText = labelEl.textContent.trim().toLowerCase();

    if (targetLabels.includes(labelText)) {
        const link = item.querySelector(".nav-link");

        link.addEventListener("click", (e) => {
            // Si la barra está colapsada (vista minimizada), al dar clic se expande completamente
            if (sidebar.classList.contains("collapsed")) {
                e.preventDefault();
                sidebar.classList.remove("collapsed");
                syncMainLayout();
                item.classList.add("dropdown-active"); // Se expande y muestra las opciones
            } else {
                // Si está en vista normal, funciona como un acordeón clásico (abre/cierra)
                e.preventDefault();
                
                // Cierra otros desplegables abiertos opcionalmente para limpieza visual
                navItems.forEach(i => { if (i !== item) i.classList.remove("dropdown-active"); });
                
                item.classList.toggle("dropdown-active");
            }
        });
    }
});