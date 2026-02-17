const nouns = ["printers", "sidewalks", "footnotes", "backrooms", "receipts", "daydreams"];
const verbs = ["refuse", "remix", "reboot", "echo", "collide with", "invent"];
const objects = ["quiet systems", "neon rituals", "small rebellions", "paper futures", "midnight maps", "friendly chaos"];

const line = document.querySelector("#zine-line");
const button = document.querySelector("#shuffle");

function pick(list) {
  return list[Math.floor(Math.random() * list.length)];
}

function makeLine() {
  return `${pick(nouns)} ${pick(verbs)} ${pick(objects)}.`;
}

button.addEventListener("click", () => {
  line.textContent = makeLine();
});

line.textContent = makeLine();
