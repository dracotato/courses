const content = document.querySelector("textarea.content");
const shortcutList = document.querySelector("ul.shortcuts");


for (let i = 0; i < shortcutList.children.length; i++) {
  const shortcut = shortcutList.children[i].querySelector("button");
  shortcut.addEventListener("click", e => {
    let appendText = "";

    if (content.value[content.value.length-1] == " ") {
      appendText = shortcut.dataset.content;
    } else {
      appendText = " " + shortcut.dataset.content;
    }

    content.value += appendText
  })
}
