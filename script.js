// --- Grab UI elements ---
const modeSelect = document.getElementById("mode");
const outputTypeSelect = document.getElementById("outputType");
const inputBox = document.getElementById("input");
const outputBox = document.getElementById("output");
const formatBtn = document.getElementById("formatBtn");
const copyBtn = document.getElementById("copyBtn");
const clearBtn = document.getElementById("clearBtn");
const downloadLink = document.getElementById("downloadLink");

// --- State ---
let currentMode = "agenda";      // agenda | minutes
let currentOutput = "txt";       // txt | md | pdf

// --- Mode change handler ---
modeSelect.addEventListener("change", () => {
  currentMode = modeSelect.value;
});

// --- Output type change handler ---
outputTypeSelect.addEventListener("change", () => {
  currentOutput = outputTypeSelect.value;

  if (currentOutput === "pdf") {
    outputBox.style.display = "none";
  } else {
    outputBox.style.display = "block";
  }
});

// ------------------------------------------------------------
// UTILITIES
// ------------------------------------------------------------

function cleanInput(text) {
  return text
    .split("\n")
    .map(line => line.trim())
    .filter(line => line.length > 0);
}

function normalizeBullet(line) {
  return line
    .replace(/^[-*•>\u2022]\s+/, "")
    .replace(/^\d+[\.\)]\s+/, "")
    .trim();
}

function smartCap(str) {
  if (!str) return "";
  const s = str.trim();
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// Hybrid timestamp detection: prefer start, else anywhere
function detectTimestamp(line) {
  const startRegex = /^\s*((?:[01]?\d|2[0-3]):[0-5]\d(?:\s*(?:am|pm))?|(?:[1-9]|1[0-2])\s*(?:am|pm))/i;
  const anyRegex = /((?:[01]?\d|2[0-3]):[0-5]\d(?:\s*(?:am|pm))?|(?:[1-9]|1[0-2])\s*(?:am|pm))/i;

  let match = line.match(startRegex);
  if (match) {
    const time = match[1].trim();
    const rest = line.slice(match[0].length).trim();
    return { time, rest };
  }

  match = line.match(anyRegex);
  if (match) {
    const time = match[1].trim();
    const rest = line.replace(match[0], "").trim();
    return { time, rest };
  }

  return null;
}

// ------------------------------------------------------------
// AGENDA FORMATTER (with hybrid numbering + timestamps)
// ------------------------------------------------------------
function formatAgenda(lines) {
  const items = lines.map(l => {
    const base = normalizeBullet(l);
    const ts = detectTimestamp(base);
    if (ts) {
      return {
        hasTime: true,
        time: ts.time,
        text: smartCap(ts.rest || "")
      };
    }
    return {
      hasTime: false,
      time: null,
      text: smartCap(base)
    };
  });

  const anyTimestamps = items.some(i => i.hasTime);

  let out = [];
  out.push("AGENDA");
  out.push("--------");
  out.push("");

  if (anyTimestamps) {
    items.forEach(item => {
      if (item.hasTime) {
        out.push(`${item.time} - ${item.text}`);
      } else {
        out.push(item.text);
      }
      out.push("");
    });
  } else {
    items.forEach((item, i) => {
      out.push(`${i + 1}. ${item.text}`);
      out.push("");
    });
  }

  let result = out.join("\n").trim();
  result = result.replace(/\n{3,}/g, "\n\n");
  return result;
}

// ------------------------------------------------------------
// MINUTES FORMATTER (smart inference + fixed section order)
// ------------------------------------------------------------
function classifyLine(line) {
  const lower = line.toLowerCase();

  if (
    lower.includes("decided") ||
    lower.includes("decision") ||
    lower.includes("approve") ||
    lower.includes("approved") ||
    lower.includes("agreed")
  ) {
    return "decisions";
  }

  if (
    lower.includes("action") ||
    lower.includes("todo") ||
    lower.includes("to-do") ||
    lower.includes("next step") ||
    lower.includes("follow up") ||
    lower.includes("follow-up") ||
    lower.startsWith("todo:") ||
    lower.startsWith("to-do:") ||
    lower.startsWith("next steps:")
  ) {
    return "actions";
  }

  if (
    lower.includes("discuss") ||
    lower.includes("talked about") ||
    lower.includes("conversation") ||
    lower.includes("reviewed")
  ) {
    return "discussion";
  }

  return "discussion";
}

function formatMinutes(lines) {
  let discussion = [];
  let decisions = [];
  let actions = [];

  lines.forEach(raw => {
    const base = normalizeBullet(raw);
    const ts = detectTimestamp(base);
    const text = ts ? smartCap(ts.rest || "") : smartCap(base);
    const bucket = classifyLine(base);

    const rendered = ts ? `${ts.time} - ${text}` : text;

    if (bucket === "decisions") {
      decisions.push(rendered);
    } else if (bucket === "actions") {
      actions.push(rendered);
    } else {
      discussion.push(rendered);
    }
  });

  let out = [];
  out.push("MEETING MINUTES");
  out.push("---------------");
  out.push("");

  if (discussion.length > 0) {
    out.push("Discussion");
    out.push("----------");
    discussion.forEach(l => out.push(`• ${l}`));
    out.push("");
  }

  if (decisions.length > 0) {
    out.push("Decisions");
    out.push("---------");
    decisions.forEach(l => out.push(`• ${l}`));
    out.push("");
  }

  if (actions.length > 0) {
    out.push("Action Items");
    out.push("------------");
    actions.forEach(l => out.push(`• ${l}`));
    out.push("");
  }

  let result = out.join("\n").trim();
  result = result.replace(/\n{3,}/g, "\n\n");
  return result;
}

// ------------------------------------------------------------
// Output converters
// ------------------------------------------------------------
function toTxt(text) {
  return text;
}

function toMd(text) {
  return text
    .replace(/^AGENDA$/m, "# Agenda")
    .replace(/^MEETING MINUTES$/m, "# Meeting Minutes")
    .replace(/^Discussion$/gm, "## Discussion")
    .replace(/^Decisions$/gm, "## Decisions")
    .replace(/^Action Items$/gm, "## Action Items")
    .replace(/^[-]+$/gm, "")
    .replace(/^•/gm, "-")
    .trim();
}

// ------------------------------------------------------------
// PDF GENERATOR
// ------------------------------------------------------------
function generatePDF(text) {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF({
    unit: "pt",
    format: "letter"
  });

  const lineHeight = 16;
  const margin = 40;
  let y = margin;

  const lines = doc.splitTextToSize(text, 550);

  lines.forEach(line => {
    if (y > 750) {
      doc.addPage();
      y = margin;
    }
    doc.text(line, margin, y);
    y += lineHeight;
  });

  const filename =
    currentMode === "agenda"
      ? "meeting_agenda.pdf"
      : "meeting_minutes.pdf";

  doc.save(filename);
}

// ------------------------------------------------------------
// FORMAT BUTTON
// ------------------------------------------------------------
formatBtn.addEventListener("click", () => {
  const raw = inputBox.value;
  const lines = cleanInput(raw);

  let formatted = "";

  if (currentMode === "agenda") {
    formatted = formatAgenda(lines);
  } else {
    formatted = formatMinutes(lines);
  }

  if (currentOutput === "txt") {
    outputBox.value = toTxt(formatted);
    downloadLink.style.display = "none";
  }

  if (currentOutput === "md") {
    outputBox.value = toMd(formatted);
    downloadLink.style.display = "none";
  }

  if (currentOutput === "pdf") {
    const finalText = formatted;
    generatePDF(finalText);

    outputBox.value = "";
    downloadLink.style.display = "none";
  }
});

// ------------------------------------------------------------
// COPY BUTTON
// ------------------------------------------------------------
copyBtn.addEventListener("click", () => {
  navigator.clipboard.writeText(outputBox.value);

  const popup = document.getElementById("copyPopup");
  popup.classList.add("show");

  setTimeout(() => {
    popup.classList.remove("show");
  }, 1500);
});

// ------------------------------------------------------------
// CLEAR BUTTON
// ------------------------------------------------------------
clearBtn.addEventListener("click", () => {
  inputBox.value = "";
  outputBox.value = "";
  downloadLink.style.display = "none";

  if (currentOutput !== "pdf") {
    outputBox.style.display = "block";
  }
});
