const searchInput = document.querySelector("#search");
const categorySelect = document.querySelector("#category");
const eventCards = [...document.querySelectorAll(".event-card")];
const count = document.querySelector("#result-count");
const noResults = document.querySelector("#no-results");

function filterEvents() {
  const query = searchInput.value.trim().toLowerCase();
  const category = categorySelect.value;
  let visible = 0;

  for (const card of eventCards) {
    const searchable = [
      card.dataset.title,
      card.dataset.description,
      card.dataset.location,
    ].join(" ");
    const matchesQuery = searchable.includes(query);
    const matchesCategory = category === "all" || card.dataset.category === category;
    const show = matchesQuery && matchesCategory;
    card.hidden = !show;
    if (show) visible += 1;
  }

  count.textContent = `${visible} event${visible === 1 ? "" : "s"}`;
  noResults.hidden = visible !== 0;
}

searchInput.addEventListener("input", filterEvents);
categorySelect.addEventListener("change", filterEvents);
