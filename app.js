const data = window.WE_STUDY_DATA;
const state = {
  day: "all",
  view: "material",
  search: "",
  imageKind: "all",
  currentQuestion: null,
};

const progress = JSON.parse(localStorage.getItem("we-study-progress") || '{"correct":0,"answered":0}');
const savedTheme = localStorage.getItem("we-study-theme") || "light";
document.documentElement.dataset.theme = savedTheme;

const stats = document.getElementById("stats");
const dayList = document.getElementById("dayList");
const searchInput = document.getElementById("searchInput");
const materialList = document.getElementById("materialList");
const summaryGrid = document.getElementById("summaryGrid");
const questionList = document.getElementById("questionList");
const imageGrid = document.getElementById("imageGrid");
const imageKind = document.getElementById("imageKind");
const quizCard = document.getElementById("quizCard");
const imageDialog = document.getElementById("imageDialog");
const dialogImage = document.getElementById("dialogImage");
const dialogCaption = document.getElementById("dialogCaption");
const themeToggle = document.getElementById("themeToggle");

function saveProgress() {
  localStorage.setItem("we-study-progress", JSON.stringify(progress));
}

function normalize(value) {
  return String(value || "").toLowerCase().trim();
}

function matchesSearch(item) {
  if (!state.search) return true;
  const haystack = normalize(
    [item.day, item.topic, item.question, item.answer, item.folder, item.label, item.note, item.title, item.text].filter(Boolean).join(" ")
  );
  return haystack.includes(normalize(state.search));
}

function activeQuestions() {
  return data.questions.filter((question) => {
    return (state.day === "all" || question.day === state.day) && matchesSearch(question);
  });
}

function activeImages() {
  return data.images.filter((image) => {
    const dayMatch = state.day === "all" || image.day === state.day;
    const kindMatch = state.imageKind === "all" || image.kind === state.imageKind;
    return dayMatch && kindMatch && matchesSearch(image);
  });
}

function activeMaterials() {
  return data.materials.filter((material) => {
    return (state.day === "all" || material.day === state.day) && matchesSearch(material);
  });
}

function setView(view) {
  state.view = view;
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.classList.toggle("is-active", tab.dataset.view === view);
  });
  document.querySelectorAll(".view").forEach((panel) => panel.classList.remove("is-active"));
  document.getElementById(`${view}View`).classList.add("is-active");
  if (view === "quiz" && !state.currentQuestion) chooseQuestion();
}

function renderStats() {
  const score = progress.answered ? Math.round((progress.correct / progress.answered) * 100) : 0;
  stats.innerHTML = `
    <div class="stat"><strong>${data.questions.length}</strong><span>سؤال</span></div>
    <div class="stat"><strong>${data.images.length}</strong><span>صورة</span></div>
    <div class="stat"><strong>${data.materials.length}</strong><span>شرح</span></div>
    <div class="stat"><strong>${score}%</strong><span>نتيجتك</span></div>
  `;
}

function renderDays() {
  const allCount = data.questions.length;
  const buttons = [
    `<button class="day-button ${state.day === "all" ? "is-active" : ""}" data-day="all">
      <span>كل الأيام</span><span>${allCount}</span>
    </button>`,
    ...data.days.map((day) => `
      <button class="day-button ${state.day === day.name ? "is-active" : ""}" data-day="${day.name}">
        <span>${day.name}</span><span>${day.questionCount} سؤال · ${day.materialCount} شرح</span>
      </button>
    `),
  ];
  dayList.innerHTML = buttons.join("");
}

function renderMaterialText(text) {
  const blocks = text.split(/\n{2,}/).map((block) => block.trim()).filter(Boolean);
  return blocks.map((block) => {
    const lines = block.split("\n").map((line) => line.trim()).filter(Boolean);
    const first = lines[0] || "";
    const heading = /^(🟦|[0-9]+️⃣|##|المحور|DAY\s+\d+|[0-9]+\.\s+|[A-Z][A-Z\s/&-]{6,})/i.test(first);
    if (heading && first.length < 140) {
      const title = first.replace(/^##\s*/, "");
      const rest = lines.slice(1);
      return `
        <section class="study-section">
          <h3>${title}</h3>
          ${rest.length ? renderMaterialLines(rest) : ""}
        </section>
      `;
    }
    return `<section class="study-section">${renderMaterialLines(lines)}</section>`;
  }).join("");
}

function renderMaterialLines(lines) {
  const bulletLines = lines.filter((line) => line.startsWith("- "));
  if (bulletLines.length === lines.length && lines.length > 1) {
    return `<ul>${lines.map((line) => `<li>${line.replace(/^- /, "")}</li>`).join("")}</ul>`;
  }
  return lines.map((line) => {
    if (line.startsWith("- ")) return `<ul><li>${line.replace(/^- /, "")}</li></ul>`;
    return `<p>${line}</p>`;
  }).join("");
}

function renderMaterials() {
  const materials = activeMaterials();
  if (!materials.length) {
    materialList.innerHTML = `<div class="empty-state">مفيش شرح نصي مطابق للفلتر الحالي.</div>`;
    return;
  }
  materialList.innerHTML = materials.map((material) => `
    <article class="material-card">
      <div class="material-source">${material.day} · ${material.title}</div>
      <div class="material-body">${renderMaterialText(material.text)}</div>
    </article>
  `).join("");
}

function renderSummaries() {
  const days = data.days.filter((day) => state.day === "all" || day.name === state.day);
  summaryGrid.innerHTML = days.map((day) => `
    <article class="summary-card">
      <h3>${day.name}</h3>
      <ul>${day.summary.map((item) => `<li>${item}</li>`).join("")}</ul>
      <div class="meta-row">
        <span class="badge">${day.questionCount} سؤال</span>
        <span class="badge">${day.imageCount} صورة</span>
      </div>
    </article>
  `).join("");
}

function chooseQuestion() {
  const questions = activeQuestions().filter((question) => question.answer);
  if (!questions.length) {
    quizCard.innerHTML = `<div class="empty-state">مفيش أسئلة مطابقة للبحث الحالي.</div>`;
    state.currentQuestion = null;
    return;
  }
  state.currentQuestion = questions[Math.floor(Math.random() * questions.length)];
  renderQuiz();
}

function renderQuiz() {
  const question = state.currentQuestion;
  const options = question.options.length ? question.options : [question.answer];
  quizCard.innerHTML = `
    <div class="quiz-topic">${question.day} · ${question.topic} · سؤال ${question.number}</div>
    <div class="quiz-question">${question.question}</div>
    ${renderQuestionImages(question)}
    <div class="options">
      ${options.map((option) => `<button class="option-button" data-answer="${encodeURIComponent(option)}">${option}</button>`).join("")}
    </div>
    <div class="answer-box" hidden></div>
  `;
}

function renderQuestionImages(question) {
  if (!question.images || !question.images.length) return "";
  return `
    <div class="question-images" aria-label="صور مرتبطة بالسؤال">
      ${question.images.map((path) => `
        <button class="question-image-button" data-image="${encodeURI(path)}" data-caption="${question.day} - سؤال ${question.number}">
          <img src="${encodeURI(path)}" alt="${question.day} سؤال ${question.number}" loading="lazy">
        </button>
      `).join("")}
    </div>
  `;
}

function answerQuiz(selected, button) {
  const answer = state.currentQuestion.answer;
  const isCorrect = normalize(selected) === normalize(answer);
  progress.answered += 1;
  if (isCorrect) progress.correct += 1;
  saveProgress();
  renderStats();

  quizCard.querySelectorAll(".option-button").forEach((optionButton) => {
    const value = decodeURIComponent(optionButton.dataset.answer);
    optionButton.disabled = true;
    if (normalize(value) === normalize(answer)) optionButton.classList.add("is-correct");
  });
  if (!isCorrect) button.classList.add("is-wrong");
  const answerBox = quizCard.querySelector(".answer-box");
  answerBox.hidden = false;
  answerBox.textContent = isCorrect ? "إجابة صحيحة" : `الإجابة الصحيحة: ${answer}`;
}

function renderQuestions() {
  const questions = activeQuestions();
  if (!questions.length) {
    questionList.innerHTML = `<div class="empty-state">مفيش أسئلة مطابقة للفلتر الحالي.</div>`;
    return;
  }
  questionList.innerHTML = questions.map((question) => `
    <article class="question-card">
      <h3>${question.day} · سؤال ${question.number}</h3>
      <p>${question.question}</p>
      ${renderQuestionImages(question)}
      ${question.options.length ? `<div class="meta-row">${question.options.map((option) => `<span class="badge">${option}</span>`).join("")}</div>` : ""}
      <div class="question-answer">${question.answer || "راجع الصورة أو المصدر"}</div>
    </article>
  `).join("");
}

function renderImages() {
  const images = activeImages();
  if (!images.length) {
    imageGrid.innerHTML = `<div class="empty-state">مفيش صور مطابقة للفلتر الحالي.</div>`;
    return;
  }
  imageGrid.innerHTML = images.map((image) => `
    <article class="image-card">
      <button data-image="${encodeURI(image.path)}" data-caption="${image.label}">
        <img src="${encodeURI(image.path)}" alt="${image.label}" loading="lazy">
      </button>
      <p>${image.label}</p>
      ${image.note ? `<div class="image-note">${image.note}</div>` : ""}
    </article>
  `).join("");
}

function renderAll() {
  renderStats();
  renderDays();
  renderMaterials();
  renderSummaries();
  renderQuestions();
  renderImages();
  if (state.view === "quiz" && !state.currentQuestion) chooseQuestion();
}

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => setView(tab.dataset.view));
});

dayList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-day]");
  if (!button) return;
  state.day = button.dataset.day;
  state.currentQuestion = null;
  renderAll();
});

searchInput.addEventListener("input", (event) => {
  state.search = event.target.value;
  state.currentQuestion = null;
  renderAll();
});

imageKind.addEventListener("change", (event) => {
  state.imageKind = event.target.value;
  renderImages();
});

document.getElementById("newQuiz").addEventListener("click", chooseQuestion);

document.getElementById("resetProgress").addEventListener("click", () => {
  progress.correct = 0;
  progress.answered = 0;
  saveProgress();
  renderStats();
});

themeToggle.addEventListener("click", () => {
  const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = nextTheme;
  localStorage.setItem("we-study-theme", nextTheme);
  themeToggle.textContent = nextTheme === "dark" ? "وضع نهاري" : "وضع ليلي";
});

quizCard.addEventListener("click", (event) => {
  const button = event.target.closest("[data-answer]");
  if (!button || button.disabled) return;
  answerQuiz(decodeURIComponent(button.dataset.answer), button);
});

imageGrid.addEventListener("click", (event) => {
  const button = event.target.closest("[data-image]");
  if (!button) return;
  dialogImage.src = button.dataset.image;
  dialogImage.alt = button.dataset.caption;
  dialogCaption.textContent = button.dataset.caption;
  imageDialog.showModal();
});

document.addEventListener("click", (event) => {
  const button = event.target.closest(".question-image-button");
  if (!button) return;
  dialogImage.src = button.dataset.image;
  dialogImage.alt = button.dataset.caption;
  dialogCaption.textContent = button.dataset.caption;
  imageDialog.showModal();
});

document.getElementById("closeDialog").addEventListener("click", () => imageDialog.close());

themeToggle.textContent = savedTheme === "dark" ? "وضع نهاري" : "وضع ليلي";
renderAll();
