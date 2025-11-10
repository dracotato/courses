const container = document.querySelector("div.container");

const ytLink = "https://www.youtube.com/embed/";
const vidIdRegex = /^https:\/\/youtu\.be\/([A-Za-z0-9]+)/;

container.querySelectorAll("a").forEach((element) => {
  let match = element.href.match(vidIdRegex);
  if (match) {
    player = document.createElement("iframe");
    console.log(match);
    player.src = ytLink + match[1];
    player.allow =
      "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
    player.referrerpolicy = "strict-origin-when-cross-origin";
    player.setAttribute("allowfullscreen", "");
    player.classList.add("yt");
    element.parentElement.insertBefore(player, element);
    element.remove();
  }
});
