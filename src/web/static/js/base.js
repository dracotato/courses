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

document.querySelectorAll(".dropdown").forEach((entry) => {
  entry.querySelector(".dropdown-btn").addEventListener("click", (_) => {
    entry.classList.toggle("open");
  });
});

/* close any open dropdowns when clicking outside of them */
document.addEventListener("click", (e) => {
  const openDropdowns = document.querySelectorAll(".dropdown.open");
  if (openDropdowns.length == 0) {
    return;
  } else {
    openDropdowns.forEach((entry) => {
      if (!entry.contains(e.target)) {
        entry.classList.remove("open");
      }
    });
  }
});

async function deleteLessons(lessonIds) {
  const url = "/lesson/";

  const response = await fetch(url, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(lessonIds),
  });

  if (!response.ok) {
    console.log(`status code: ${response.status}`);
  } else {
    console.log(await response.json());
  }
}
