document.addEventListener("DOMContentLoaded", function() {
    const productSearch = document.getElementById("product-search");
    const suggestionsBox = document.getElementById("product-suggestions");
    const selectedProductId = document.getElementById("selected-product-id");
    const totalAmount = document.getElementById("total");

    // Function to fetch and display product suggestions
    function fetchProducts(query = "") {
        fetch(`/pos_app/search_products/?q=` + query)
            .then(response => response.json())
            .then(data => {
                suggestionsBox.innerHTML = "";
                data.forEach(product => {
                    const suggestion = document.createElement("div");
                    suggestion.classList.add("suggestion-item");
                    suggestion.textContent = product.name;
                    suggestion.dataset.productId = product.id;
                    suggestion.dataset.productPrice = product.selling_price;
                    suggestionsBox.appendChild(suggestion);
                });
            });
    }

    // Show initial product list when search box is focused
    productSearch.addEventListener("focus", function() {
        fetchProducts();
    });

    // Fetch product suggestions on input
    productSearch.addEventListener("input", function() {
        const query = productSearch.value;
        if (query.length > 1) {
            fetchProducts(query);
        } else if (query.length === 0) {
            fetchProducts();
        } else {
            suggestionsBox.innerHTML = "";
        }
    });

    // Select product from suggestions
    suggestionsBox.addEventListener("click", function(e) {
        if (e.target && e.target.matches(".suggestion-item")) {
            productSearch.value = e.target.textContent;
            selectedProductId.value = e.target.dataset.productId;
            suggestionsBox.innerHTML = "";
        }
    });

    // Hide suggestions when clicking outside
    document.addEventListener("click", function(e) {
        if (!productSearch.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.innerHTML = "";
        }
    });

    // Function to adjust quantity and update the server-side session cart
    window.adjustQuantity = function(productId, delta) {
        const row = document.querySelector(`tr[data-product-id="${productId}"]`);
        const quantitySpan = row.querySelector(".quantity");
        let quantity = parseInt(quantitySpan.textContent) + delta;

        if (quantity > 0) {
            quantitySpan.textContent = quantity;

            // Update item's total price
            const price = parseFloat(row.querySelector("td:nth-child(3)").textContent.replace("₱", ""));
            const itemTotalPrice = row.querySelector(".total-price");
            itemTotalPrice.textContent = `₱${(quantity * price).toFixed(2)}`;

            // Update total
            updateTotal();

            // Send AJAX request to update session cart
            fetch(`/pos_app/update_cart_item/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ product_id: productId, quantity: quantity })
            }).then(response => response.json()).then(data => {
                if (!data.success) {
                    alert("Error updating cart item quantity on server.");
                }
            });
        }
    };

    window.removeItem = function(productId) {
        const row = document.querySelector(`tr[data-product-id="${productId}"]`);
        row.remove();
        updateTotal();

        fetch(`/pos_app/remove_from_cart/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ product_id: productId })
        }).then(response => response.json()).then(data => {
            if (!data.success) {
                alert("Error removing item from cart.");
            }
        });
    };

    function updateTotal() {
        let total = 0;
        document.querySelectorAll("#cart-items tr").forEach(row => {
            const quantity = parseInt(row.querySelector(".quantity").textContent);
            const price = parseFloat(row.querySelector("td:nth-child(3)").textContent.replace("₱", ""));
            total += quantity * price;
        });
        totalAmount.textContent = total.toFixed(2);
    }

    window.clearCart = function() {
        document.getElementById("cart-items").innerHTML = '<tr><td colspan="5" class="empty-cart">No items in the cart.</td></tr>';
        totalAmount.textContent = "0.00";

        fetch(`/pos_app/clear_cart/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        }).then(response => response.json()).then(data => {
            if (!data.success) {
                alert("Error clearing cart.");
            }
        });
    };

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
});
