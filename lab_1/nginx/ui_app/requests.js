document.addEventListener("DOMContentLoaded", () => {
    const submitButton = document.querySelector(".submit-button");
    const privacyPolicyCheckbox = document.querySelector("#privacy_policy");
    const teamForm = document.querySelector("#team-form");

    // Enable submit button if privacy policy is accepted
    privacyPolicyCheckbox.addEventListener("change", () => {
        submitButton.disabled = !privacyPolicyCheckbox.checked;
    });

    // Handle form submission
    teamForm.addEventListener("submit", (event) => {
        event.preventDefault();
        collectDataAndSend();
    });

    fetchItems();  // Load initial users
});

function collectDataAndSend() {
    const firstName = document.querySelector("#first_name").value;
    const lastName = document.querySelector("#last_name").value;
    const role = document.querySelector("#role").value;
    sendPostRequest(firstName, lastName, role);
}

async function sendPostRequest(firstName, lastName, role) {
    const data = { first_name: firstName, last_name: lastName, role: role };

    try {
        const response = await fetch("http://localhost:8000/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error("Network response was not ok");

        fetchItems();  // Refresh the list
    } catch (error) {
        console.error("Error:", error);
    }
}

async function fetchItems() {
    try {
        const response = await fetch("http://localhost:8000/");
        if (!response.ok) throw new Error("Failed to fetch items");
        
        const data = await response.json();
        displayItems(data);
    } catch (error) {
        console.error("Error:", error);
    }
}

function displayItems(items) {
    const itemList = document.getElementById("team-members");
    itemList.innerHTML = "";  // Clear existing items

    items.forEach((item) => {
        const listItem = document.createElement("li");
        listItem.innerHTML = `
            <div class="name-role">
                <span class="name">${item.first_name} ${item.last_name}</span>
                <span class="role">${item.role}</span>
            </div>
            <button class="delete-btn" onclick="deleteItem(${item.id})">🗑️</button>
        `;
        itemList.appendChild(listItem);
    });
}

async function deleteItem(id) {
    try {
        const response = await fetch(`http://localhost:8000/${id}`, {
            method: "DELETE",
            headers: { "Content-Type": "application/json" }
        });

        if (!response.ok) throw new Error("Failed to delete item");

        fetchItems();  // Refresh the list
    } catch (error) {
        console.error("Error:", error);
    }
}
