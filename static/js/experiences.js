const experienceGrid = document.getElementById("experience-grid");
const experienceTemplate = document.getElementById("experience-card-template");
const experienceSearchForm = document.getElementById("experience-search-form");
const experienceSearchInput = document.getElementById("experience-search-input");
const experienceDialog = document.getElementById("experience-dialog");
const experienceIdPlaceholder = "00000000-0000-0000-0000-000000000000";
let experienceSearchTimer;
let currentExperienceRequest;

async function loadExperiences(title = experienceSearchInput.value.trim()) {
    if (currentExperienceRequest) currentExperienceRequest.abort();
    currentExperienceRequest = new AbortController();

    const url = new URL(experienceGrid.dataset.apiUrl, window.location.origin);
    if (title) url.searchParams.set("title", title);

    try {
        const response = await fetch(url, { signal: currentExperienceRequest.signal });
        if (!response.ok) throw new Error("Could not load experiences");
        const experiences = await response.json();
        const cards = document.createDocumentFragment();

        experiences.forEach((experience) => {
            const card = experienceTemplate.content.firstElementChild.cloneNode(true);
            const fields = experience.fields;

            card.querySelector(".experience-category").textContent = fields.category_display;
            card.querySelector("h2").textContent = fields.title;
            card.querySelector(".experience-description").textContent = fields.description;
            card.querySelector(".experience-status").textContent = fields.is_ongoing
                ? "Sedang berlangsung"
                : "Selesai";

            card.querySelectorAll("[action], [href]").forEach((element) => {
                const attribute = element.hasAttribute("action") ? "action" : "href";
                element.setAttribute(
                    attribute,
                    element.getAttribute(attribute).replace(experienceIdPlaceholder, experience.pk)
                );
            });

            cards.appendChild(card);
        });

        if (experiences.length === 0) {
            const emptyState = document.createElement("p");
            emptyState.className = "empty-state";
            emptyState.textContent = title
                ? "No experience found with that title."
                : "Belum ada pengalaman yang ditambahkan.";
            cards.appendChild(emptyState);
        }

        experienceGrid.replaceChildren(cards);
        experienceGrid.setAttribute("aria-busy", "false");
    } catch (error) {
        if (error.name !== "AbortError") {
            experienceGrid.setAttribute("aria-busy", "false");
            experienceGrid.textContent = "Experience could not be loaded. Please try again.";
            showToast("Could not load experience", "Please try again in a moment.", "error");
        }
    }
}

experienceSearchInput.addEventListener("input", () => {
    clearTimeout(experienceSearchTimer);
    experienceSearchTimer = setTimeout(() => loadExperiences(), 300);
});

experienceSearchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    clearTimeout(experienceSearchTimer);
    loadExperiences();
});

if (experienceDialog) {
    document.getElementById("open-experience-dialog").addEventListener("click", () => experienceDialog.showModal());
    document.getElementById("close-experience-dialog").addEventListener("click", () => experienceDialog.close());
    document.getElementById("cancel-experience-dialog").addEventListener("click", () => experienceDialog.close());
}

loadExperiences();
