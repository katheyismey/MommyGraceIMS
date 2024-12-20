document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("payDebtModal");
    const form = document.getElementById("payDebtForm");
    const amountInput = document.getElementById("amount");
    const debtIdInput = document.getElementById("debtId");

    // Modal detail fields
    const modalCustomerName = document.getElementById("modalCustomerName");
    const modalTransactionId = document.getElementById("modalTransactionId");
    const modalAmountDue = document.getElementById("modalAmountDue");
    const modalRemainingBalance = document.getElementById("modalRemainingBalance"); // Add reference for Remaining Balance

    // Open modal when "Pay Debt" button is clicked
    document.querySelectorAll(".pay-debt-button").forEach(button => {
        button.addEventListener("click", () => {
            const debtId = button.dataset.debtId;
            const customerName = button.dataset.customerName;
            const transactionId = button.dataset.transactionId;
            const amountDue = button.dataset.amountDue;
            const remaining = parseFloat(button.dataset.remaining);
    
            // Populate modal fields
            debtIdInput.value = debtId;
            modalCustomerName.textContent = customerName;
            modalTransactionId.textContent = transactionId;
            modalAmountDue.textContent = `${parseFloat(amountDue).toFixed(2)}`; // Proper template literal usage
            modalRemainingBalance.textContent = `₱${remaining.toFixed(2)}`; // Proper template literal usage
            amountInput.max = remaining; // Set max to remaining balance
            amountInput.value = ""; // Reset value
    
            modal.style.display = "block";
        });
    });

    // Close modal
    window.closeModal = () => {
        modal.style.display = "none";
    };

    // Handle form submission
    form.addEventListener("submit", async event => {
        event.preventDefault();
        const amount = parseFloat(amountInput.value);
        const debtId = debtIdInput.value;
    
        if (!debtId || amount <= 0) {
            alert("Please provide a valid amount.");
            return;
        }
    
        const formData = {
            debt_id: debtId,
            amount: amount.toFixed(2), // Ensure it's a string with two decimal places
        };
    
        try {
            const response = await fetch(`/debt_management/pay_debt/`, {
                method: "POST",
                body: JSON.stringify(formData),
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                },
            });
    
            const data = await response.json();
            if (data.success) {
                location.reload();
            } else {
                alert(data.error || "An error occurred.");
            }
        } catch (error) {
            console.error("Error submitting payment:", error);
        }
    });

    // Close modal when clicking outside content
    window.onclick = event => {
        if (event.target === modal) {
            closeModal();
        }
    };
});


document.addEventListener("DOMContentLoaded", () => {
    const payAllButton = document.getElementById("payAllButton");
    const payAllModal = document.getElementById("payAllModal");
    const payAllForm = document.getElementById("payAllForm");
    const payAllAmountInput = document.getElementById("payAllAmount");
    const totalRemainingBalance = document.getElementById("totalRemainingBalance");

    if (payAllButton) {
        payAllButton.addEventListener("click", () => {
            payAllModal.style.display = "block";
        });
    }

    // Close modal
    document.querySelector(".close-button").onclick = () => (payAllModal.style.display = "none");

    // Handle form submission
    payAllForm.addEventListener("submit", async event => {
        event.preventDefault();
        const formData = {
            customer_id: payAllForm.customer_id.value,
            amount: parseFloat(payAllAmountInput.value).toFixed(2),
        };

        try {
            const response = await fetch(`/debt_management/pay_all_debts/`, {
                method: "POST",
                body: JSON.stringify(formData),
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                },
            });

            const data = await response.json();
            if (data.success) {
                location.reload();
            } else {
                alert(data.error || "An error occurred.");
            }
        } catch (error) {
            console.error("Error submitting payment:", error);
        }
    });

    // Close modal when clicking outside
    window.onclick = event => {
        if (event.target === payAllModal) payAllModal.style.display = "none";
    };
});
