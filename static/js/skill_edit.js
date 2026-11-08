const skillEditForm = document.getElementById("skill-edit-form");

if (skillEditForm) {
    skillEditForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const button = skillEditForm.querySelector("button[type='submit']");
        const errorMessages = skillEditForm.querySelectorAll("[data-error-for]");

        errorMessages.forEach((element) => {
            element.textContent = "";
            element.hidden = true;
        });
        button.disabled = true;

        try {
            const response = await fetch(skillEditForm.dataset.apiUrl, {
                method: "PATCH",
                body: new FormData(skillEditForm),
                headers: {
                    "Accept": "application/json",
                    "X-CSRFToken": skillEditForm.querySelector(
                        "[name='csrfmiddlewaretoken']"
                    ).value,
                },
            });

            const result = await response.json();

            if (!response.ok) {
                const messages = [];

                Object.entries(result).forEach(([field, errors]) => {
                    const message = Array.isArray(errors)
                        ? errors.join(" ")
                        : String(errors);

                    const target = [...errorMessages].find(
                        (element) => element.dataset.errorFor === field
                    );

                    if (target) {
                        target.textContent = message;
                        target.hidden = false;
                    }

                    messages.push(`${field}: ${message}`);
                });

                throw new Error(
                    result.detail || messages.join(" ") || "Could not save changes."
                );
            }

            window.location.assign(skillEditForm.dataset.successUrl);
        } catch (error) {
            showToast("Could not update skill", error.message, "error");
        } finally {
            button.disabled = false;
        }
    });
}