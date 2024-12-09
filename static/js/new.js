let form = document.getElementById("newMessage");
form.addEventListener("submit", async function(e) {
    e.preventDefault();
    const formData = new FormData(form);
    
    try {
        const response = await fetch("/send", {
            method: "POST",
            body: formData,
        });

        if (response.ok) {
            const result = await response.json();
            console.log(result);
            if (result.status === "success") {
                window.location.href = "/";
            } else {
                alert(result.message || "Send failed!");
            }
        } else {
            alert("Send failed!");
            console.error('Error:', response.status, response.statusText);
        }
    } catch (error) {
        alert("Send failed!");
        console.error('Fetch error:', error);
    }
});

function toggleOverlay(overlayId) {
    let overlay = document.getElementById(overlayId);
    if (overlay.style.display == "flex") {
        overlay.style.display = "none";
    } else {
        overlay.style.display = "flex";
    }
}

document.getElementById('addFileButton').addEventListener('click', function () {
    // Create a wrapper for the input and remove button
    const wrapper = document.createElement('div');
    wrapper.className = 'file-input-wrapper';
  
    // Create a new input element
    const newInput = document.createElement('input');
    newInput.type = 'file';
    newInput.name = 'files[]';
  
    // Create the remove button
    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.className = 'removeFileButton';
    removeButton.textContent = 'Remove';
  
    // Append input and button to the wrapper
    wrapper.appendChild(newInput);
    wrapper.appendChild(removeButton);
  
    // Append wrapper to the container
    document.getElementById('fileInputs').appendChild(wrapper);
});

document.getElementById('fileInputs').addEventListener('click', function (event) {
    if (event.target.classList.contains('removeFileButton')) {
        const wrapper = event.target.parentElement;
        wrapper.remove();
    }
});