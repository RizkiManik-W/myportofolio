const projectGrid = document.getElementById("project-grid");
const projectTemplate = document.getElementById("project-card-template");
const projectSearchForm = document.getElementById("project-search-form");
const projectSearchInput = document.getElementById("project-search-input");
const projectDialog = document.getElementById("project-dialog");
const projectForm = document.getElementById("project-create-form");
const projectDialogTitle = document.getElementById("project-dialog-title");
const projectFormSubmit = document.getElementById("project-form-submit");
const projectIdPlaceholder = "00000000-0000-0000-0000-000000000000";
const PROJECT_LIST_URL = projectGrid.dataset.listUrl;
const PROJECT_DETAIL_URL = projectGrid.dataset.detailUrl;
const PROJECT_STAR_URL = projectGrid.dataset.starUrl;
const PROJECT_FIELDS = ["title", "description", "tech_stack", "project_url", "project_image_url"];
const projectsById = new Map();
let editingProjectId = null;
let projectSearchTimer;
let currentProjectRequest;

function getCookie(name) {
    const prefix = `${name}=`;
    const cookie = document.cookie.split(";").map((value) => value.trim())
        .find((value) => value.startsWith(prefix));
    return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
}

function projectEndpoint(pattern, id) {
    return pattern.replace(projectIdPlaceholder, id);
}

function safeHttpUrl(value) {
    try {
        const url = new URL(value);
        return url.protocol === "http:" || url.protocol === "https:" ? url.href : null;
    } catch (error) {
        return null;
    }
}

class ApiError extends Error {
    constructor(message, status, data) {
        super(message);
        this.status = status;
        this.data = data;
    }
}

function apiErrorMessage(data, status) {
    const messages = Object.values(data).flat().filter((value) => typeof value === "string");
    return messages.join(" ") || `Request failed (HTTP ${status}).`;
}

// Single place for POST/PUT/PATCH/DELETE: JSON body, CSRF header, consistent errors.
async function writeProject(url, method, payload) {
    const response = await fetch(url, {
        method,
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken") || "",
        },
        body: payload === undefined ? undefined : JSON.stringify(payload),
    });
    if (response.status === 204) return null;
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new ApiError(apiErrorMessage(data, response.status), response.status, data);
    return data;
}

function showProjectLoadingState() {
    const loadingMessage = document.createElement("p");
    loadingMessage.className = "empty-state";
    loadingMessage.setAttribute("role", "status");
    loadingMessage.textContent = "Loading projects...";
    projectGrid.replaceChildren(loadingMessage);
    projectGrid.setAttribute("aria-busy", "true");
}

function renderStarState(card, project) {
    card.querySelector(".star-count").textContent = project.star_count;
    card.querySelector(".project-star-summary").title = project.starred_by_names || "No stars yet";
    const starButton = card.querySelector(".project-star-button");
    if (starButton) {
        starButton.classList.toggle("is-starred", project.is_starred);
        starButton.setAttribute("aria-pressed", String(project.is_starred));
        starButton.querySelector(".star-label").textContent = project.is_starred ? "Starred" : "Star";
    }
}

function buildProjectCard(project) {
    const card = projectTemplate.content.firstElementChild.cloneNode(true);
    card.dataset.id = project.id;

    // textContent / setAttribute only: API data is never parsed as HTML.
    card.querySelector("h3").textContent = project.title;
    card.querySelector(".project-description").textContent = project.description;

    const imageUrl = safeHttpUrl(project.project_image_url);
    const thumb = card.querySelector(".project-thumb");
    if (imageUrl) {
        const image = thumb.querySelector("img");
        image.src = imageUrl;
        image.alt = `${project.title} preview`;
        image.addEventListener("error", () => thumb.remove());
        thumb.hidden = false;
    } else {
        thumb.remove();
    }

    const techList = card.querySelector(".project-tech");
    const technologies = project.tech_stack.split(",").map((tech) => tech.trim()).filter(Boolean);
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
    const projectUrl = safeHttpUrl(project.project_url);
    if (projectUrl) {
        link.href = projectUrl;
        link.hidden = false;
    } else {
        link.remove();
    }

    renderStarState(card, project);
    return card;
}

async function loadProjects(title = projectSearchInput.value.trim()) {
    if (currentProjectRequest) currentProjectRequest.abort();
    currentProjectRequest = new AbortController();
    showProjectLoadingState();

    const url = new URL(PROJECT_LIST_URL, window.location.origin);
    if (title) url.searchParams.set("title", title);

    try {
        const response = await fetch(url, {
            headers: { "Accept": "application/json" },
            signal: currentProjectRequest.signal,
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const projects = await response.json();
        const cards = document.createDocumentFragment();

        projectsById.clear();
        projects.forEach((project) => {
            projectsById.set(project.id, project);
            cards.appendChild(buildProjectCard(project));
        });

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
    editingProjectId = null;
    projectDialogTitle.textContent = "Add a project";
    projectFormSubmit.textContent = "Add Project";
    projectDialog.showModal();
}

function openEditProjectDialog(project) {
    clearProjectErrors();
    editingProjectId = project.id;
    projectDialogTitle.textContent = "Edit project";
    projectFormSubmit.textContent = "Save Changes";
    PROJECT_FIELDS.forEach((name) => {
        projectForm.elements.namedItem(name).value = project[name] || "";
    });
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

// Event delegation: keeps working after the grid is re-rendered.
projectGrid.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button || button.disabled) return;

    const card = button.closest(".project-card");
    const project = projectsById.get(card.dataset.id);
    const action = button.dataset.action;
    if (!project) return;

    if (action === "edit") {
        openEditProjectDialog(project);
        return;
    }
    if (action === "delete" && !window.confirm("Are you sure you want to delete this project?")) return;

    button.disabled = true;
    try {
        if (action === "star") {
            const updated = await writeProject(projectEndpoint(PROJECT_STAR_URL, project.id), "POST");
            projectsById.set(updated.id, updated);
            renderStarState(card, updated);
        } else {
            await writeProject(projectEndpoint(PROJECT_DETAIL_URL, project.id), "DELETE");
            await loadProjects();
            showToast("Project deleted", "Project deleted successfully.", "success");
        }
    } catch (error) {
        showToast(
            action === "star" ? "Could not update star" : "Could not delete project",
            error.message || "Please try again.",
            "error"
        );
    } finally {
        button.disabled = false;
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

        const isEditing = editingProjectId !== null;
        const submitButton = projectForm.querySelector("button[type='submit']");
        clearProjectErrors();
        submitButton.disabled = true;

        try {
            const fields = new FormData(projectForm);
            const payload = Object.fromEntries(PROJECT_FIELDS.map((name) => [name, fields.get(name)]));
            if (isEditing) {
                await writeProject(projectEndpoint(PROJECT_DETAIL_URL, editingProjectId), "PATCH", payload);
            } else {
                await writeProject(PROJECT_LIST_URL, "POST", payload);
            }

            projectForm.reset();
            projectDialog.close();
            await loadProjects();
            showToast(
                isEditing ? "Project updated" : "Project added",
                isEditing ? "Project updated successfully." : "Project added successfully.",
                "success"
            );
        } catch (error) {
            // DRF validation errors are flat: {"title": ["..."]}. Show them next to the field.
            const fieldErrors = error.status === 400 ? error.data : null;
            let shownInline = false;
            if (fieldErrors) {
                Object.entries(fieldErrors).forEach(([field, messages]) => {
                    const target = projectForm.querySelector(`[data-error-for="${field}"]`);
                    if (target) {
                        target.textContent = [].concat(messages).join(" ");
                        target.hidden = false;
                        shownInline = true;
                    }
                });
            }
            if (!shownInline) {
                showToast(
                    isEditing ? "Could not update project" : "Could not add project",
                    error.message || "Please try again.",
                    "error"
                );
            }
        } finally {
            submitButton.disabled = false;
        }
    });
}

loadProjects();
