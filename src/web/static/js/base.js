const sidebar = document.querySelector(".sidebar");
const menuIcon = document.querySelector(".topbar .menu-icon");
const closeIcon = document.querySelector(".topbar .close-icon");

menuIcon.addEventListener("click", openSidebar);
closeIcon.addEventListener("click", closeSidebar);

function openSidebar() {
  sidebar.classList.add("open");
}

function closeSidebar() {
  sidebar.classList.remove("open");
}
