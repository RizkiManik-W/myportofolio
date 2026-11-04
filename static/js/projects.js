async function getProjects(url) {
    const response = await fetch(url);

    if (!response.ok) {
        throw new Error("Could not load projects.");
    }

    const projects = await response.json();
    return projects;
}

async function loadProjects() {
    const page = document.getElementById("projects-page");

    try {
        const projects = await getProjects(page.dataset.apiUrl);
        const results = document.getElementById("project-results");
        results.replaceChildren();

        for (const project of projects) {
            const card = document.createElement("article");
            card.className = "project-card";

            const heading = document.createElement("h2");
            heading.textContent = project.fields.title;

            const description = document.createElement("p");
            description.textContent = project.fields.description;

            card.append(heading, description);
            if (project.fields.tech_stack) {
                const technologies = document.createElement("p");
                technologies.textContent =
                    "Technologies: " + project.fields.tech_stack;
                card.append(technologies);
            }
            results.append(card);
        }
    } catch (error) {
        console.error("Could not load projects.", error);
    }
}

loadProjects();