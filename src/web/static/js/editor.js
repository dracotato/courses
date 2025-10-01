const content = document.querySelector("textarea.content");
const shortcutList = document.querySelector("ul.shortcuts");

let fieldsStartIndex = -1;
let fieldIterator;
let lengthBeforeField;
let diff;

// handle shortcut buttons' click event
for (let i = 0; i < shortcutList.children.length; i++) {
  const shortcut = shortcutList.children[i].querySelector("button");
  shortcut.addEventListener("click", (_) => {
    // reset
    if (fieldsStartIndex + 1 > content.value.length) {
      fieldsStartIndex = content.value.length - 1;
    }

    content.value = appendFormatted(shortcut.dataset.content, content.value);
    content.focus();
    // resets
    lengthBeforeField = content.value.length;
    diff = 0;

    fieldIterator = extractFields(content.value);
    // set inital selection
    let result = fieldIterator.next();
    setSelection(result.field.start, result.field.end);
  });
}

// use tab to go to the next field
content.addEventListener("keydown", (event) => {
  if (event.key !== "Tab") {
    return;
  }

  event.preventDefault();

  if (fieldIterator !== undefined) {
    result = fieldIterator.next();
    if (!result.done) {
      setSelection(result.field.start, result.field.end);
    } else {
      // set the caret at at the end
      content.setSelectionRange(content.value.length, content.value.length);
    }
  }
});

function appendFormatted(string, text) {
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
    if (content.value[content.value.length] !== " ") {
      formatted = " " + formatted;
    }
  }

  return text + formatted;
}

function extractFields(string) {
  const fieldRegex = /<<[A-z.]+>>/g;

  let subString = string.substring(fieldsStartIndex + 1);

  if (subString === "") {
    return null;
  }

  let fields = subString.match(fieldRegex);

  let fieldData = [];

  for (let i = 0; i < fields.length; i++) {
    const field = fields[i];

    let startIndex = subString.indexOf(field) + fieldsStartIndex + 1;
    let endIndex = startIndex + field.length;

    fieldData.push({ start: startIndex, end: endIndex });
  }

  fieldsStartIndex = content.value.length - 1;

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

function setSelection(start, end) {
  diff += lengthBeforeField ? content.value.length - lengthBeforeField : 0;

  content.setSelectionRange(start + diff, end + diff);
  lengthBeforeField = content.value.length;
}
