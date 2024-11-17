// static/inventory/search.js
document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.querySelector("input[name='search']");
    
    searchInput.addEventListener("input", function () {
        const searchTerm = searchInput.value;
        const url = new URL(window.location.href);
        url.searchParams.set("search", searchTerm);
        window.history.pushState(null, "", url);

        fetch(url)
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, "text/html");
                const tableBody = doc.querySelector(".product-table tbody");
                document.querySelector(".product-table tbody").innerHTML = tableBody.innerHTML;
            });
    });
});

