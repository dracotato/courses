const sidebar = document.querySelector(".sidebar");

document
  .querySelector(".topbar .menu-icon")
  .addEventListener("click", openSidebar);
document
  .querySelector(".topbar .close-icon")
  .addEventListener("click", closeSidebar);

function openSidebar() {
  sidebar.classList.add("open");
}

function closeSidebar() {
  sidebar.classList.remove("open");
}

/* toggle dropdown when clicking on dropdown-btn */
document.querySelectorAll(".dropdown").forEach((entry) => {
  entry.querySelector(".dropdown-btn").addEventListener("click", (e) => {
    entry.classList.toggle("open");
    e.preventDefault();
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

async function deleteEnt(entity, ids, redirect = false) {
  const url = `/${entity}/`;

  const many = ids instanceof Array;
  const length = many ? ids.length : 1;
  if (!confirm(`Are you sure you want to delete ${length} ${entity}?`)) {
    return;
  }

  const response = await fetch(url, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(ids),
  });

  if (!response.ok) {
    console.error(`status code: ${response.status}`);
    return;
  }

  if (redirect) {
    location.replace("/");
    return;
  }

  if (many) {
    ids.forEach((id) => {
      document.querySelector(`[data-${entity}-id="${id}"]`).remove();
    });
  } else if (typeof ids == "number") {
    document.querySelector(`[data-${entity}-id="${ids}"]`).remove();
  }
}

function rmMsg(msg) {
  msg.classList.add("fade-out");
  msg.addEventListener("transitionend", (_) => {
    msg.remove();
  });
}

document.querySelectorAll(".msg").forEach((msg, idx) => {
  // delay before any message starts getting deleted
  const baseDelay = 5000;
  // delay between each message deletion
  const stepDelay = 2000;
  msg.addEventListener("click", () => {
    rmMsg(msg);
  });
  setTimeout(
    () => {
      rmMsg(msg);
    },
    baseDelay + stepDelay * (idx + 1), // total delay
  );
});
