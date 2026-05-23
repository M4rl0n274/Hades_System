const sidebar = document.querySelector(".sidebar");
const sidebarToggler = document.querySelector(".sidebar-toggler");
const menuToggler = document.querySelector(".menu-toggler");

const collapsedSidebarHeight = "56px"
const fullSidebarHeight = "calc(100vh - 32px)";

// Toggle sidebar s collapsed state
sidebarToggler.addEventListener("click", () => {
    sidebar.classList.toggle("collapsed");
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

// Adjust sidebar height on window reesize
window.addEventListener("resize", () => {
    if (window.innerWidth >= 1024){
        sidebar.style.height = fullSidebarHeight;
    } else {
        sidebar.classList.remove("collapsed");
        sidebar.style.height = "auto";
        togglerMenu(sidebar.classList.contains("menu*active"))
    }


})
