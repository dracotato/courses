const editorArea = document.querySelector(".editor-form__editor");
const formatsContainer = document.querySelector(".editor-form__formats");

const helpIcon = document.querySelector(".help-btn");
const helpDialog = document.querySelector(".help-dialog");

const fieldPattern = "<<[A-z0-9.]+>>";
const fieldRegex = new RegExp(fieldPattern);
const fieldRegexGlobal = new RegExp(fieldPattern, "g");

let selectNextField; // a function
let keybinds = [];

helpIcon.addEventListener("click", (e) => {
  e.preventDefault();
  helpDialog.showModal();
});

for (let i = 0; i < formatsContainer.children.length; i++) {
  const formatBtn = formatsContainer.children[i].querySelector("button");
  const dataset = formatBtn.dataset;

  dataset.template = dataset.template.replaceAll("\\n", "\n");

  // handle shortcut buttons' click event
  formatBtn.addEventListener("click", (_) => {
    setFormat(dataset.template);
  });

  // load keybinds
  const keyparts = dataset.keybind.toLowerCase().split("+");

  // populate the help dialog with keybinds
  const keybindsContainer = helpDialog.querySelector(".keybinds-container");

  // create a new keybind div to be added to the DOM
  let newKeybind = document.createElement("div");
  newKeybind.classList.add("keybind");

  let newKeybindTitle = document.createElement("div");
  newKeybindTitle.innerText = formatBtn.getAttribute("title"); // use the elements' title
  newKeybindTitle.classList.add("keybind-title");
  newKeybind.appendChild(newKeybindTitle); // append under newKeybind

  let newKeybindKeys = document.createElement("div");
  keyparts.forEach((part) => {
    let kbdElement = document.createElement("kbd");
    kbdElement.innerText = part;
    newKeybindKeys.appendChild(kbdElement);
  });
  newKeybindKeys.classList.add("keys");
  newKeybind.appendChild(newKeybindKeys); // append under newKeybind

  // finally append the newKeybind itself
  keybindsContainer.appendChild(newKeybind);

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
    if (selectNextField !== undefined) {
      e.preventDefault(); // don't hog the tab key unless there's a next field
      selectNextField();
    }
  } else if (e.key === "/" && e.ctrlKey) {
    e.preventDefault();
    helpDialog.showModal();
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
