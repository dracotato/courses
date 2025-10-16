const editorArea = document.querySelector("textarea.editor-area");
const actionsContainer = document.querySelector("ul.actions");

const fieldPattern = "<<[A-z.]+>>";
const fieldRegex = new RegExp(fieldPattern);
const fieldRegexGlobal = new RegExp(fieldPattern, "g");

let selectNextField; // a function
let keybinds = [];

for (let i = 0; i < actionsContainer.children.length; i++) {
  const actionBtn = actionsContainer.children[i].querySelector("button");
  const dataset = actionBtn.dataset;

  dataset.template = dataset.template.replaceAll("\\n", "\n");

  // handle shortcut buttons' click event
  actionBtn.addEventListener("click", (_) => {
    setFormat(dataset.template);
  });

  // load keybinds
  const keyparts = dataset.keybind.toLowerCase().split("+");
  keybinds.push({
    formatTemplate: dataset.template,
    ctrl: keyparts.includes("ctrl"),
    shift: keyparts.includes("shift"),
    alt: keyparts.includes("alt"),
    key: keyparts[keyparts.length - 1],
  });
}

// handle keybind
editorArea.addEventListener("keydown", (e) => {
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
      setFormat(match.formatTemplate);
    }
  }
});

/**
 * dynamically handle a format template
 * and initialize the field selection mechanism
 * @param {string} template the format template to handle
 */
function setFormat(template) {
  if (isSelection()) {
    formatSelection(template);
  } else {
    appendFormat(template);
  }

  // initialize field selection
  editorArea.focus();
  selectNextField = selector();
  if (!isSelection()) {
    selectNextField();
  }
}

/**
 * appends template to the editorArea
 * @param {string} template
 */
function appendFormat(template) {
  if (template.includes("\n")) {
    if (editorArea.value !== "") {
      editorArea.value = editorArea.value.trimEnd() + "\n\n";
    }
  } else {
    if (editorArea.value[editorArea.textLength - 1] !== " ") {
      editorArea.value += " ";
    }
  }

  editorArea.value += template;
}

/**
 * inserts template in place of the selection and fills
 * the first field with the selection
 * @param {string} template
 */
function formatSelection(template) {
  editorArea.setRangeText(template.replace(fieldRegex, getSelectionStr()));
}

/** returns a method to select the next field
 */
function selector() {
  const fields = fieldIterator(editorArea.value);
  // used to know the new position of the next field
  // after the user fills the placeholders
  let lengthBeforeField = editorArea.textLength;

  function next() {
    const result = fields.next();

    if (!result.done) {
      const diff = editorArea.textLength - lengthBeforeField;
      editorArea.setSelectionRange(
        result.field.start + diff,
        result.field.end + diff,
      );
    } else {
      // move the caret to the end
      editorArea.setSelectionRange(
        editorArea.textLength,
        editorArea.textLength,
      );
    }
  }

  return next;
}

/**
 * returns a bool indicating whether a selection exists inside editorArea
 * @returns {boolean}
 */
function isSelection() {
  return editorArea.selectionStart !== editorArea.selectionEnd;
}

/**
 * returns the contents of the current selection inside editorArea
 * @returns {string}
 */
function getSelectionStr() {
  return editorArea.value.slice(
    editorArea.selectionStart,
    editorArea.selectionEnd,
  );
}

/**
 * returns an iterator over fields extracted from string
 * @param {string} string
 * @returns {iterator}
 */
function fieldIterator(string) {
  const fields = getFields(string);

  let index = 0;
  const iterator = {
    next() {
      if (index < fields.length) {
        index++;
        return { field: fields[index - 1], done: false };
      }
      return { done: true };
    },
  };

  return iterator;
}

/** returns list of fields found in string
 * @param {string} string
 * @returns {{start: number, end: number}[]} fields[]
 */
function getFields(string) {
  let matches = string.matchAll(fieldRegexGlobal);
  let fields = [
    ...matches.map((match) => ({
      start: match.index,
      end: match.index + match[0].length,
    })),
  ];

  return fields;
}
