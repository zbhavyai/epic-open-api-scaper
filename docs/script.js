document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("search-input");
    const sections = document.querySelectorAll(".interface-section");

    // Toggle collapse/expand on header click
    document.querySelectorAll(".interface-header").forEach(header => {
        header.addEventListener("click", (e) => {
            if (e.target.closest("a")) return;
            const section = header.closest(".interface-section");
            section.classList.toggle("collapsed");
        });
    });

    // Real-time search filter
    searchInput.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase().trim();

        sections.forEach(section => {
            let visibleCount = 0;
            const items = section.querySelectorAll(".api-item");

            items.forEach(item => {
                const name = item.querySelector(".api-name").textContent.toLowerCase();
                const desc = item.querySelector(".api-desc").textContent.toLowerCase();

                if (name.includes(query) || desc.includes(query)) {
                    item.style.display = "";
                    visibleCount++;
                } else {
                    item.style.display = "none";
                }
            });

            if (visibleCount > 0 || query === "") {
                section.style.display = "";
                if (query !== "") {
                    section.classList.remove("collapsed");
                }
            } else {
                section.style.display = "none";
            }
        });
    });
});
