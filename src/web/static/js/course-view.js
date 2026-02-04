const lessonContainer = document.querySelector(".cards-container");

// to ensure the cards order is always up to date
function getCards() {
  return lessonContainer.querySelectorAll(".card[data-lesson-id]");
}

async function submitOrder() {
  const parts = location.pathname.split("/");
  const id = location.pathname.endsWith("/")
    ? parts[parts.length - 2]
    : parts[parts.length - 1];
  const url = `/course/${id}/`;
  let data = [];

  const cards = getCards();

  for (let i = 0; i < cards.length; i++) {
    const card = cards[i];

    data.push({ id: card.dataset.lessonId, ord: i + 1 });
  }

  const response = await fetch(url, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    console.error(`failed to update lesson ordering: ${response.status}`);
  }
}

function getTargetCard(event) {
  const cards = getCards();
  for (let i = 0; i < cards.length; i++) {
    const card = cards[i];
    const cardRect = card.getBoundingClientRect();
    const cardCenter = cardRect.top + cardRect.height / 2;

    if (event.clientY <= cardCenter) {
      return card;
    } else if (i == cards.length - 1 && event.clientY >= cardCenter) {
      return card.nextSibling;
    }
  }
}

function createPlaceholder() {
  const placeholder = document.createElement("div");
  placeholder.classList.add("drag-placeholder");
  placeholder.style.height = `${document.querySelector("#dragged-card").offsetHeight}px`;

  return placeholder;
}

function movePlaceholder(event) {
  const draggedCard = lessonContainer.querySelector("#dragged-card");
  const target = getTargetCard(event);

  if (
    (target == draggedCard) |
    (target.previousElementSibling == draggedCard)
  ) {
    return;
  }

  let placeholder = lessonContainer.querySelector(".drag-placeholder");
  if (!placeholder) {
    placeholder = createPlaceholder();
  }

  lessonContainer.insertBefore(placeholder, target);
}

lessonContainer.addEventListener("dragover", (e) => {
  if (e.dataTransfer.types.includes("card")) {
    e.preventDefault();
    movePlaceholder(e);
  }
});
lessonContainer.addEventListener("drop", (e) => {
  if (!e.dataTransfer.types.includes("card")) {
    return;
  }
  e.preventDefault();
  let draggedCard = document.querySelector("#dragged-card");
  lessonContainer.insertBefore(draggedCard, getTargetCard(e));
  lessonContainer.querySelector(".drag-placeholder")?.remove();
  submitOrder();
});

getCards().forEach((card) => {
  card.addEventListener("dragstart", (e) => {
    // prevent unintended drags
    if (!card.querySelector(".drag-area").matches(":hover")) {
      e.preventDefault();
      return;
    }
    card.id = "dragged-card";
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("card", "");
  });
  card.addEventListener("dragend", (_) => {
    card.removeAttribute("id");
  });
});
