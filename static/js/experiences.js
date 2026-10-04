const experienceGrid = document.getElementById("experience-grid");
const experienceTemplate = document.getElementById("experience-card-template");
const experienceSearchForm = document.getElementById("experience-search-form");
const experienceSearchInput = document.getElementById("experience-search-input");
const experienceDialog = document.getElementById("experience-dialog");
const experienceCreateForm = document.getElementById("experience-create-form");
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

experienceGrid.addEventListener("submit", async (event) => {
    const deleteForm = event.target.closest(".experience-delete-form");
    if (!deleteForm) return;

    event.preventDefault();
    if (!window.confirm("Are you sure you want to delete this experience?")) return;

    const deleteButton = deleteForm.querySelector("button[type='submit']");
    deleteButton.disabled = true;

    try {
        const response = await fetch(deleteForm.action, {
            method: "POST",
            body: new FormData(deleteForm),
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "application/json",
            },
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.message || "Could not delete this experience.");

        await loadExperiences();
        showToast("Experience deleted", result.message, "success");
    } catch (error) {
        showToast("Could not delete experience", error.message || "Please try again.", "error");
    } finally {
        deleteButton.disabled = false;
    }
});

if (experienceDialog) {
    document.getElementById("open-experience-dialog").addEventListener("click", () => experienceDialog.showModal());
    document.getElementById("close-experience-dialog").addEventListener("click", () => experienceDialog.close());
    document.getElementById("cancel-experience-dialog").addEventListener("click", () => experienceDialog.close());
}

if (experienceCreateForm) {
    experienceCreateForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const submitButton = experienceCreateForm.querySelector("button[type='submit']");
        const errorMessages = experienceCreateForm.querySelectorAll("[data-error-for]");
        errorMessages.forEach((element) => {
            element.textContent = "";
            element.hidden = true;
        });
        submitButton.disabled = true;

        try {
            const response = await fetch(experienceCreateForm.action, {
                method: "POST",
                body: new FormData(experienceCreateForm),
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "Accept": "application/json",
                },
            });
            const result = await response.json();

            if (!response.ok) {
                if (result.errors) {
                    Object.entries(result.errors).forEach(([field, errors]) => {
                        const target = [...errorMessages].find(
                            (element) => element.dataset.errorFor === field
                        );
                        if (target) {
                            target.textContent = errors.map((error) => error.message).join(" ");
                            target.hidden = false;
                        }
                    });
                    return;
                }
                throw new Error(result.message || "Could not save this experience.");
            }

            experienceCreateForm.reset();
            experienceDialog.close();
            await loadExperiences();
            showToast("Experience added", result.message, "success");
        } catch (error) {
            showToast("Could not add experience", error.message || "Please try again.", "error");
        } finally {
            submitButton.disabled = false;
        }
    });
}

loadExperiences();
