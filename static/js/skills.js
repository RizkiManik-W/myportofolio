const skillGrid = document.getElementById("skills-grid");
const skillTemplate = document.getElementById("skill-card-template");
const skillCategoryLabels = new Map(
    JSON.parse(document.getElementById("skill-categories").textContent)
);
const skillIdPlaceholder = "00000000-0000-0000-0000-000000000000";

async function loadSkills() {
    const url = new URL(skillGrid.dataset.apiUrl, window.location.origin);
    const searchTitle = new URLSearchParams(window.location.search).get("title");
    if (searchTitle) url.searchParams.set("title", searchTitle);

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error("Could not load skills");
        const skills = await response.json();
        const cards = document.createDocumentFragment();

        skills.forEach((skill, index) => {
            const card = skillTemplate.content.firstElementChild.cloneNode(true);
            const fields = skill.fields;
            const starred = fields.starred_by.some(
                (username) => username[0] === window.currentSkillUsername
            );

            card.querySelector(".skill-number").textContent = String(index + 1).padStart(2, "0");
            card.querySelector(".skill-type").textContent = skillCategoryLabels.get(fields.category) || fields.category;
            card.querySelector("h3").textContent = fields.title;
            card.querySelector(".skill-description").textContent = fields.description;

            const proficiency = card.querySelector(".skill-proficiency");
            if (fields.proficiency) {
                proficiency.textContent = fields.proficiency;
            } else {
                proficiency.remove();
            }

            const starButton = card.querySelector(".skill-star-form button");
            if (starButton) {
                starButton.classList.toggle("is-starred", starred);
                card.querySelector(".star-label").textContent = starred ? "Starred" : "Star";
                card.querySelector(".star-count").textContent = fields.starred_by.length;
            }

            card.querySelectorAll("[action], [href]").forEach((element) => {
                const attribute = element.hasAttribute("action") ? "action" : "href";
                element.setAttribute(attribute, element.getAttribute(attribute).replace(skillIdPlaceholder, skill.pk));
            });
            cards.appendChild(card);
        });

        if (skills.length === 0) {
            const empty = document.createElement("p");
            empty.className = "empty-state";
            empty.textContent = searchTitle ? "No skills found with that name." : "Belum ada skill yang ditambahkan.";
            cards.appendChild(empty);
        }

        skillGrid.replaceChildren(cards);
    } catch (error) {
        showToast("Could not refresh skills", "The existing list is still available.", "error");
    }
}

loadSkills();
