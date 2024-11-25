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
    const noticeBox = document.getElementById("notice-box");
    const noticeMessage = document.getElementById("notice-message");

    let selectedBatchStock = 0; // Track the stock for the selected batch

    // Utility: Show notice box
    function showNotice(message) {
        noticeMessage.textContent = message;
        noticeBox.style.display = "block";
    }

    // Utility: Hide notice box
    function hideNotice() {
        noticeBox.style.display = "none";
        noticeMessage.textContent = "";
    }

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
                    suggestion.dataset.stock = batch.stock; // Include stock for validation
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
            selectedBatchStock = parseInt(e.target.dataset.stock); // Update stock for validation
            batchSuggestionsBox.innerHTML = "";

            // Enable quantity and add-to-cart button
            quantityField.disabled = false;
            addToCartButton.disabled = false;

            // Reset quantity field and enforce stock limit
            quantityField.value = 1;
            quantityField.max = selectedBatchStock;
        }
    });

    // Validate quantity field input
    quantityField.addEventListener("input", function () {
        const enteredQuantity = parseInt(quantityField.value);
        if (enteredQuantity > selectedBatchStock) {
            showNotice(`You cannot add more than ${selectedBatchStock} items for this batch.`);
            quantityField.value = selectedBatchStock;
        } else if (enteredQuantity < 1) {
            showNotice("Quantity cannot be less than 1.");
            quantityField.value = 1;
        } else {
            hideNotice();
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

    // Adjust Quantity in Cart
    function adjustQuantity(productVersionId, delta) {
        const row = document.querySelector(`tr[data-product-version-id="${productVersionId}"]`);
        const quantitySpan = row.querySelector(".quantity");
        let quantity = parseInt(quantitySpan.textContent);
        const maxStock = parseInt(row.dataset.stock); // Max stock from dataset

        if (delta === 1 && quantity >= maxStock) {
            showNotice(`Cannot add more than ${maxStock} items for this product.`);
            return;
        }

        if (delta === -1 && quantity <= 1) {
            showNotice("Quantity cannot be less than 1.");
            return;
        }

        quantity += delta;

        // Update the UI
        quantitySpan.textContent = quantity;
        const price = parseFloat(row.querySelector("td:nth-child(4)").textContent.replace("₱", ""));
        const itemTotalPrice = row.querySelector(".total-price");
        itemTotalPrice.textContent = `₱${(quantity * price).toFixed(2)}`;
        updateTotal();

        // Update the server
        fetch(`/pos_app/update_cart_item/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken(),
            },
            body: JSON.stringify({ product_version_id: productVersionId, quantity }),
        }).then(response => response.json()).then(data => {
            if (!data.success) {
                showNotice("Error updating cart item.");
            }
        });
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
                showNotice("Error removing item.");
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
        const cartItemsContainer = document.getElementById("cart-items");
        cartItemsContainer.innerHTML = `
            <tr>
                <td colspan="6" class="empty-cart">No items in the cart.</td>
            </tr>`;
        totalAmount.textContent = "0.00";

        fetch(`/pos_app/clear_cart/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken(),
            },
        }).then(response => response.json())
          .then(data => {
              if (!data.success) {
                  showNotice("Error clearing the cart.");
              }
          }).catch(error => {
              console.error("Error clearing the cart:", error);
              showNotice("Unexpected error while clearing the cart.");
          });
    };

    function getCsrfToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]").value;
    }
});
