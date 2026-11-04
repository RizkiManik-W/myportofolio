const projectGrid = document.getElementById("project-grid");
const projectTemplate = document.getElementById("project-card-template");
const projectSearchForm = document.getElementById("project-search-form");
const projectSearchInput = document.getElementById("project-search-input");
const projectDialog = document.getElementById("project-dialog");
const projectForm = document.getElementById("project-create-form");
const projectDialogTitle = document.getElementById("project-dialog-title");
const projectFormSubmit = document.getElementById("project-form-submit");
const projectIdPlaceholder = "00000000-0000-0000-0000-000000000000";
const createProjectUrl = projectForm?.action;
const ajaxHeaders = {
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json",
};
let projectSearchTimer;
let currentProjectRequest;

function safeHttpUrl(value) {
    try {
        const url = new URL(value);
        return url.protocol === "http:" || url.protocol === "https:" ? url.href : null;
    } catch (error) {
        return null;
    }
}

function showProjectLoadingState() {
    const loadingMessage = document.createElement("p");
    loadingMessage.className = "empty-state";
    loadingMessage.setAttribute("role", "status");
    loadingMessage.textContent = "Loading projects...";
    projectGrid.replaceChildren(loadingMessage);
    projectGrid.setAttribute("aria-busy", "true");
}

function buildProjectCard(project) {
    const card = projectTemplate.content.firstElementChild.cloneNode(true);
    const fields = project.fields;

    card.querySelector("h3").textContent = fields.title;
    card.querySelector(".project-description").textContent = fields.description;
    card.querySelector(".star-count").textContent = fields.star_count;
    card.querySelector(".project-star-summary").title = fields.starred_by_names || "No stars yet";

    const imageUrl = safeHttpUrl(fields.project_image_url);
    if (imageUrl) {
        const thumb = card.querySelector(".project-thumb");
        const image = thumb.querySelector("img");
        image.src = imageUrl;
        image.alt = `${fields.title} preview`;
        image.addEventListener("error", () => thumb.remove());
        thumb.hidden = false;
    } else {
        card.querySelector(".project-thumb").remove();
    }

    const techList = card.querySelector(".project-tech");
    const technologies = fields.tech_stack.split(",").map((tech) => tech.trim()).filter(Boolean);
    if (technologies.length) {
        technologies.forEach((tech) => {
            const item = document.createElement("li");
            item.textContent = tech;
            techList.appendChild(item);
        });
    } else {
        techList.remove();
    }

    const link = card.querySelector(".project-link");
    const projectUrl = safeHttpUrl(fields.project_url);
    if (projectUrl) {
        link.href = projectUrl;
        link.hidden = false;
    } else {
        link.remove();
    }

    const starButton = card.querySelector(".project-star-form button");
    if (starButton) {
        starButton.classList.toggle("is-starred", fields.is_starred);
        starButton.setAttribute("aria-pressed", String(fields.is_starred));
        starButton.querySelector(".star-label").textContent = fields.is_starred ? "Starred" : "Star";
    }

    card.querySelectorAll("[action], [data-update-url]").forEach((element) => {
        const attribute = element.hasAttribute("action") ? "action" : "data-update-url";
        element.setAttribute(
            attribute,
            element.getAttribute(attribute).replace(projectIdPlaceholder, project.pk)
        );
    });

    const editButton = card.querySelector(".project-edit-button");
    if (editButton) {
        editButton.addEventListener("click", () => {
            clearProjectErrors();
            projectForm.action = editButton.dataset.updateUrl;
            projectDialogTitle.textContent = "Edit project";
            projectFormSubmit.textContent = "Save Changes";

            Object.entries({
                title: fields.title,
                description: fields.description,
                tech_stack: fields.tech_stack || "",
                project_url: fields.project_url || "",
                project_image_url: fields.project_image_url || "",
            }).forEach(([name, value]) => {
                projectForm.elements.namedItem(name).value = value;
            });

            projectDialog.showModal();
        });
    }

    return card;
}

async function loadProjects(title = projectSearchInput.value.trim()) {
    if (currentProjectRequest) currentProjectRequest.abort();
    currentProjectRequest = new AbortController();
    showProjectLoadingState();

    const url = new URL(projectGrid.dataset.apiUrl, window.location.origin);
    if (title) url.searchParams.set("title", title);

    try {
        const response = await fetch(url, { signal: currentProjectRequest.signal });
        if (!response.ok) throw new Error("Could not load projects");
        const projects = await response.json();
        const cards = document.createDocumentFragment();

        projects.forEach((project) => cards.appendChild(buildProjectCard(project)));

        if (projects.length === 0) {
            const emptyState = document.createElement("p");
            emptyState.className = "empty-state";
            emptyState.textContent = title
                ? "No projects found with that title."
                : "Belum ada project yang ditambahkan.";
            cards.appendChild(emptyState);
        }

        projectGrid.replaceChildren(cards);
        projectGrid.setAttribute("aria-busy", "false");
    } catch (error) {
        if (error.name !== "AbortError") {
            projectGrid.setAttribute("aria-busy", "false");
            projectGrid.textContent = "Projects could not be loaded. Please try again.";
            showToast("Could not load projects", "Please try again in a moment.", "error");
        }
    }
}

function clearProjectErrors() {
    if (!projectForm) return;
    projectForm.querySelectorAll("[data-error-for]").forEach((element) => {
        element.textContent = "";
        element.hidden = true;
    });
}

function openCreateProjectDialog() {
    clearProjectErrors();
    projectForm.reset();
    projectForm.action = createProjectUrl;
    projectDialogTitle.textContent = "Add a project";
    projectFormSubmit.textContent = "Add Project";
    projectDialog.showModal();
}

projectSearchInput.addEventListener("input", () => {
    clearTimeout(projectSearchTimer);
    projectSearchTimer = setTimeout(() => loadProjects(), 300);
});

projectSearchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    clearTimeout(projectSearchTimer);
    loadProjects();
});

projectGrid.addEventListener("submit", async (event) => {
    const starForm = event.target.closest(".project-star-form");
    if (!starForm) return;

    event.preventDefault();
    const button = starForm.querySelector("button");
    if (button.disabled) return;
    button.disabled = true;

    try {
        const response = await fetch(starForm.action, {
            method: "POST",
            body: new FormData(starForm),
            headers: ajaxHeaders,
        });
        if (!response.headers.get("content-type")?.includes("application/json")) {
            throw new Error("Could not update this star. Please refresh and try again.");
        }
        const result = await response.json();
        if (!response.ok) throw new Error(result.message || "Could not update this star.");

        button.classList.toggle("is-starred", result.is_starred);
        button.setAttribute("aria-pressed", String(result.is_starred));
        button.querySelector(".star-label").textContent = result.is_starred ? "Starred" : "Star";
        const card = starForm.closest(".project-card");
        card.querySelector(".star-count").textContent = result.star_count;
        card.querySelector(".project-star-summary").removeAttribute("title");
    } catch (error) {
        showToast("Could not update star", error.message, "error");
    } finally {
        button.disabled = false;
    }
});

projectGrid.addEventListener("submit", async (event) => {
    const deleteForm = event.target.closest(".project-delete-form");
    if (!deleteForm) return;

    event.preventDefault();
    if (!window.confirm("Are you sure you want to delete this project?")) return;

    const deleteButton = deleteForm.querySelector("button[type='submit']");
    deleteButton.disabled = true;

    try {
        const response = await fetch(deleteForm.action, {
            method: "POST",
            body: new FormData(deleteForm),
            headers: ajaxHeaders,
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.message || "Could not delete this project.");

        await loadProjects();
        showToast("Project deleted", result.message, "success");
    } catch (error) {
        showToast("Could not delete project", error.message || "Please try again.", "error");
    } finally {
        deleteButton.disabled = false;
    }
});

if (projectDialog) {
    const openButton = document.getElementById("open-project-dialog");
    if (openButton) openButton.addEventListener("click", openCreateProjectDialog);
    document.getElementById("close-project-dialog").addEventListener("click", () => projectDialog.close());
    document.getElementById("cancel-project-dialog").addEventListener("click", () => projectDialog.close());
}

if (projectForm) {
    projectForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const isEditing = projectForm.action !== createProjectUrl;
        const submitButton = projectForm.querySelector("button[type='submit']");
        const errorMessages = projectForm.querySelectorAll("[data-error-for]");
        clearProjectErrors();
        submitButton.disabled = true;

        try {
            const response = await fetch(projectForm.action, {
                method: "POST",
                body: new FormData(projectForm),
                headers: ajaxHeaders,
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
                throw new Error(result.message || "Could not save this project.");
            }

            projectForm.reset();
            projectDialog.close();
            await loadProjects();
            showToast(isEditing ? "Project updated" : "Project added", result.message, "success");
        } catch (error) {
            showToast(
                isEditing ? "Could not update project" : "Could not add project",
                error.message || "Please try again.",
                "error"
            );
        } finally {
            submitButton.disabled = false;
        }
    });
}

loadProjects();
