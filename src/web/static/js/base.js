const sidebar = document.querySelector(".sidebar");
const menuIcon = document.querySelector(".topbar .menu-icon");
const closeIcon = document.querySelector(".sidebar .close-icon");

menuIcon.addEventListener("click", openSidebar);
closeIcon.addEventListener("click", closeSidebar);

function closeSidebar() {
  sidebar.style.left = "-100%";
}

function openSidebar() {
  sidebar.style.left = "0";
}
