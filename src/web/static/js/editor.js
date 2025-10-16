const content = document.querySelector("textarea.content");
const shortcutList = document.querySelector("ul.shortcuts");

let selectNextField; // a function
let keybinds = [];

for (let i = 0; i < shortcutList.children.length; i++) {
  const shortcut = shortcutList.children[i].querySelector("button");
  const dataset = shortcut.dataset;

  // handle shortcut buttons' click event
  shortcut.addEventListener("click", (_) => {
    insertShortcut(dataset.content.replaceAll("\\n", "\n"));
    initFieldSelection();
  });

  // load keybinds
  const keyparts = dataset.keybind.toLowerCase().split("+");
  keybinds.push({
    shortcutData: dataset.content.replaceAll("\\n", "\n"),
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
      if (isSelection()) {
        let fields = getFields(match.shortcutData);
        let styled =
          match.shortcutData.slice(0, fields[0].start) +
          getSelectionStr() +
          match.shortcutData.slice(fields[0].end);
        content.setRangeText(styled);
        initFieldSelection();
      } else {
        insertShortcut(match.shortcutData);
        initFieldSelection();
      }
    }
  }
});

function initFieldSelection() {
  content.focus();
  // initialization
  selectNextField = selector();
  // set inital selection if there's no selection
  if (!isSelection()) {
    selectNextField();
  }
}

function insertShortcut(shortcut) {
  content.value = formatShortcut(shortcut, content.value);
}

function isSelection() {
  return content.selectionStart !== content.selectionEnd;
}

function getSelectionStr() {
  return content.value.slice(content.selectionStart, content.selectionEnd);
}

function formatShortcut(string, text) {
  let formatted = string;

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

function getFields(string) {
  const fieldRegex = /<<[A-z.]+>>/g;
  let matches = string.matchAll(fieldRegex);
  let fieldData = [
    ...matches.map((match) => ({
      start: match.index,
      end: match.index + match[0].length,
    })),
  ];

  return fieldData;
}

function fieldIterator(string) {
  if (!string) {
    return {
      // always return done
      next: () => ({ done: true }),
    };
  }

  fieldData = getFields(string);

  let index = 0;
  const iterator = {
    next() {
      let result;
      if (index < fieldData.length) {
        result = { field: fieldData[index], done: false };
        index++;
        return result;
      }
      return { done: true };
    },
  };

  return iterator;
}

function selector() {
  const fields = fieldIterator(content.value);
  // used to know the new position of the fields
  // after the user edits
  let lengthBeforeField = content.value.length;

  function next() {
    const result = fields.next();

    if (!result.done) {
      const diff = content.value.length - lengthBeforeField || 0;
      content.setSelectionRange(
        result.field.start + diff,
        result.field.end + diff,
      );
    } else {
      // set the caret at the last character
      content.setSelectionRange(content.value.length, content.value.length);
    }
  }

  return next;
}
