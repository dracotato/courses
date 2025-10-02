const content = document.querySelector("textarea.content");
const shortcutList = document.querySelector("ul.shortcuts");

// a function
let selectNextField;
let keybinds = [];

for (let i = 0; i < shortcutList.children.length; i++) {
  const shortcut = shortcutList.children[i].querySelector("button");
  const dataset = shortcut.dataset;

  // handle shortcut buttons' click event
  shortcut.addEventListener("click", (_) => insertShortcut(dataset.content));

  // load keybinds
  const keyparts = dataset.keybind.toLowerCase().split("+");
  keybinds.push({
    shortcutData: dataset.content,
    ctrl: keyparts.includes("ctrl"),
    shift: keyparts.includes("shift"),
    alt: keyparts.includes("alt"),
    key: keyparts[keyparts.length - 1],
  });
}

// handle keybind
content.addEventListener("keydown", (e) => {
  if (e.key === "Tab") {
    e.preventDefault();
    if (selectNextField !== undefined) {
      selectNextField();
    }
  } else {
    const match = keybinds.find((entry) => {
      return (
        e.key === entry.key &&
        e.ctrlKey === entry.ctrl &&
        e.shiftKey === entry.shift &&
        e.altKey === entry.alt
      );
    });

    if (match) {
      e.preventDefault();
      insertShortcut(match.shortcutData);
    }
  }
});

function insertShortcut(shortcut) {
  content.value = formatShortcut(shortcut, content.value);
  content.focus();
  // initialization
  selectNextField = selector();
  // set inital selection
  selectNextField();
}

function formatShortcut(string, text) {
  let formatted = string.replaceAll("\\n", "\n");

  // multiline shortcuts
  if (formatted.includes("\n")) {
    if (content.value !== "") {
      text = text.trimEnd();
      formatted = "\n\n" + formatted;
    }
  }

  // inline shortcuts
  else {
    if (content.value[content.value.length - 1] !== " ") {
      formatted = " " + formatted;
    }
  }

  return text + formatted;
}

function extractFields(string) {
  const fieldRegex = /<<[A-z.]+>>/g;

  if (!string) {
    return {
      // always return done
      next: () => ({ done: true }),
    };
  }

  let matches = string.matchAll(fieldRegex);
  let fieldData = [
    ...matches.map((match) => ({
      start: match.index,
      end: match.index + match[0].length,
    })),
  ];

  lengthPreShortcut = content.value.length - 1;

  let iteratorIndex = 0;
  const fieldIterator = {
    next() {
      let result;
      if (iteratorIndex < fieldData.length) {
        result = { field: fieldData[iteratorIndex], done: false };
        iteratorIndex++;
        return result;
      }
      return { done: true };
    },
  };

  return fieldIterator;
}

function selector() {
  const fieldIterator = extractFields(content.value);
  let lengthBeforeField = content.value.length;

  function next() {
    const result = fieldIterator.next();

    if (!result.done) {
      const diff = content.value.length - lengthBeforeField || 0;
      content.setSelectionRange(
        result.field.start + diff,
        result.field.end + diff,
      );
    } else {
      content.setSelectionRange(content.value.length, content.value.length);
    }
  }

  return next;
}
