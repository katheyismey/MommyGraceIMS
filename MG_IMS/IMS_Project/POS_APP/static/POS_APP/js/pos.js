document.addEventListener("DOMContentLoaded", function () {
    const productSearch = document.getElementById("product-search");
    const suggestionsBox = document.getElementById("product-suggestions");
    const selectedProductId = document.getElementById("selected-product-id");
    const batchSearch = document.getElementById("batch-search");
    const batchSuggestionsBox = document.getElementById("batch-suggestions");
    const selectedBatchId = document.getElementById("selected-batch-id");
    const quantityField = document.getElementById("quantity-sold");
    const addToCartButton = document.querySelector(".add-to-cart-button");
    const totalAmount = document.getElementById("total");

    // Fetch product suggestions
    function fetchProducts(query = "") {
        fetch(`/pos_app/search_products/?q=${query}`)
            .then(response => response.json())
            .then(data => {
                suggestionsBox.innerHTML = "";
                data.forEach(product => {
                    const suggestion = document.createElement("div");
                    suggestion.classList.add("suggestion-item");
                    suggestion.textContent = `${product.name}`;
                    suggestion.dataset.productId = product.id;
                    suggestionsBox.appendChild(suggestion);
                });
            });
    }

    // Fetch batch suggestions
    function fetchBatches(productId) {
        fetch(`/pos_app/search_batches/?product_id=${productId}`)
            .then(response => response.json())
            .then(data => {
                batchSuggestionsBox.innerHTML = "";
                data.forEach(batch => {
                    const suggestion = document.createElement("div");
                    suggestion.classList.add("suggestion-item");
                    suggestion.textContent = `Batch ${batch.batch_id} - ₱${batch.price} (Stock: ${batch.stock})`;
                    suggestion.dataset.batchId = batch.id;
                    batchSuggestionsBox.appendChild(suggestion);
                });
            });
    }

    // Handle product selection
    suggestionsBox.addEventListener("click", function (e) {
        if (e.target && e.target.matches(".suggestion-item")) {
            productSearch.value = e.target.textContent;
            selectedProductId.value = e.target.dataset.productId;
            suggestionsBox.innerHTML = "";

            // Enable batch search and fetch batches
            batchSearch.disabled = false;
            fetchBatches(e.target.dataset.productId);
        }
    });

    // Handle batch selection
    batchSuggestionsBox.addEventListener("click", function (e) {
        if (e.target && e.target.matches(".suggestion-item")) {
            batchSearch.value = e.target.textContent;
            selectedBatchId.value = e.target.dataset.batchId;
            batchSuggestionsBox.innerHTML = "";

            // Enable quantity and add-to-cart button
            quantityField.disabled = false;
            addToCartButton.disabled = false;
        }
    });

    // Fetch products when search box is focused
    productSearch.addEventListener("focus", () => fetchProducts());

    // Fetch products on input
    productSearch.addEventListener("input", () => {
        const query = productSearch.value.trim();
        fetchProducts(query);
    });

    // Re-fetch batch suggestions on focus if a product is already selected
    batchSearch.addEventListener("focus", () => {
        if (selectedProductId.value) {
            fetchBatches(selectedProductId.value);
        }
    });

    // Hide suggestions when clicking outside
    document.addEventListener("click", function (e) {
        if (!productSearch.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.innerHTML = "";
        }
        if (!batchSearch.contains(e.target) && !batchSuggestionsBox.contains(e.target)) {
            batchSuggestionsBox.innerHTML = "";
        }
    });

    // Event delegation for cart actions
    const cartTable = document.getElementById("cart-items");

    cartTable.addEventListener("click", function (e) {
        const button = e.target;

        if (button.classList.contains("quantity-button")) {
            const productVersionId = button.closest("tr").dataset.productVersionId;
            const delta = button.textContent === "+" ? 1 : -1;
            adjustQuantity(productVersionId, delta);
        }

        if (button.classList.contains("remove-button")) {
            const productVersionId = button.closest("tr").dataset.productVersionId;
            removeItem(productVersionId);
        }
    });

    function adjustQuantity(productVersionId, delta) {
        const row = document.querySelector(`tr[data-product-version-id="${productVersionId}"]`);
        const quantitySpan = row.querySelector(".quantity");
        let quantity = parseInt(quantitySpan.textContent) + delta;

        if (quantity > 0) {
            quantitySpan.textContent = quantity;
            const price = parseFloat(row.querySelector("td:nth-child(4)").textContent.replace("₱", ""));
            const itemTotalPrice = row.querySelector(".total-price");
            itemTotalPrice.textContent = `₱${(quantity * price).toFixed(2)}`;
            updateTotal();

            fetch(`/pos_app/update_cart_item/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken(),
                },
                body: JSON.stringify({ product_version_id: productVersionId, quantity }),
            }).then(response => response.json()).then(data => {
                if (!data.success) {
                    alert("Error updating cart item.");
                }
            });
        }
    }

    function removeItem(productVersionId) {
        const row = document.querySelector(`tr[data-product-version-id="${productVersionId}"]`);
        row.remove();
        updateTotal();

        fetch(`/pos_app/remove_from_cart/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken(),
            },
            body: JSON.stringify({ product_version_id: productVersionId }),
        }).then(response => response.json()).then(data => {
            if (!data.success) {
                alert("Error removing item.");
            }
        });
    }

    function updateTotal() {
        let total = 0;
        document.querySelectorAll("#cart-items tr").forEach(row => {
            const quantity = parseInt(row.querySelector(".quantity").textContent);
            const price = parseFloat(row.querySelector("td:nth-child(4)").textContent.replace("₱", ""));
            total += quantity * price;
        });
        totalAmount.textContent = total.toFixed(2);
    }

    window.clearCart = function () {
        // Clear the UI cart table
        const cartItemsContainer = document.getElementById("cart-items");
        cartItemsContainer.innerHTML = `
            <tr>
                <td colspan="6" class="empty-cart">No items in the cart.</td>
            </tr>`;
        totalAmount.textContent = "0.00";

        // Send the request to clear the server-side cart
        fetch(`/pos_app/clear_cart/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken(),
            },
        }).then(response => response.json())
          .then(data => {
              if (!data.success) {
                  alert("Error clearing the cart.");
              }
          }).catch(error => {
              console.error("Error clearing the cart:", error);
          });
    };

    function getCsrfToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]").value;
    }

});
