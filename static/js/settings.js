let selfForm = document.getElementById("settingsForm");
selfForm.addEventListener("submit", async function(e) {
    e.preventDefault();
    const formData = new FormData(selfForm);
    
    try {
        const response = await fetch("/usersettings", {
            method: "POST",
            body: formData,
        });

        if (response.ok) {
            const result = await response.json();
            console.log(result);
            if (result.status === "success") {
                alert(result.message || "Update Successful!");
                window.location.href = "/settings";
            } else {
                alert(result.message || "Update failed!");
            }
        } else {
            alert("Update failed!");
            console.error('Error:', response.status, response.statusText);
        }
    } catch (error) {
        alert("Update failed!");
        console.error('Fetch error:', error);
    }
});

if (document.getElementById("createUserForm")) {
    let createUserForm = document.getElementById("createUserForm");
    createUserForm.addEventListener("submit", async function(e) {
        e.preventDefault();
        const formData = new FormData(createUserForm);
        
        try {
            const response = await fetch("/createuser", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                console.log(result);
                if (result.status === "success") {
                    alert(result.message || "Create Successful!");
                    window.location.href = "/settings";
                } else {
                    alert(result.message || "Create failed!");
                }
            } else {
                alert("Create failed!");
                console.error('Error:', response.status, response.statusText);
            }
        } catch (error) {
            alert("Create failed!");
            console.error('Fetch error:', error);
        }
    });
}

if (document.getElementById("nmSettingsForm")) {
    let numailForm = document.getElementById("nmSettingsForm");
    numailForm.addEventListener("submit", async function(e) {
        e.preventDefault();
        const formData = new FormData(numailForm);
        
        try {
            const response = await fetch("/mbsettings", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                console.log(result);
                if (result.status === "success") {
                    alert(result.message || "Update Successful!");
                    window.location.href = "/settings";
                } else {
                    alert(result.message || "Update failed!");
                }
            } else {
                alert("Update failed!");
                console.error('Error:', response.status, response.statusText);
            }
        } catch (error) {
            alert("Update failed!");
            console.error('Fetch error:', error);
        }
    });
}

if (document.getElementById("nmSettingsFormAccount")) {
    let numailFormAccount = document.getElementById("nmSettingsFormAccount");
    numailFormAccount.addEventListener("submit", async function(e) {
        e.preventDefault();
        const formData = new FormData(numailFormAccount);
        
        try {
            const response = await fetch("/mbsettings", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                console.log(result);
                if (result.status === "success") {
                    alert(result.message || "Update Successful!");
                    window.location.href = "/settings";
                } else {
                    alert(result.message || "Update failed!");
                }
            } else {
                alert("Update failed!");
                console.error('Error:', response.status, response.statusText);
            }
        } catch (error) {
            alert("Update failed!");
            console.error('Fetch error:', error);
        }
    });
}

if (document.getElementById("userSettingsForm")) {
    let userSettingsForm = document.getElementById("userSettingsForm");
    userSettingsForm.addEventListener("submit", async function(e) {
        e.preventDefault();
        const formData = new FormData(userSettingsForm);
        
        try {
            const response = await fetch("/usersettings", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                console.log(result);
                if (result.status === "success") {
                    alert(result.message || "Update Successful!");
                    window.location.href = "/settings";
                } else {
                    alert(result.message || "Update failed!");
                }
            } else {
                alert("Update failed!");
                console.error('Error:', response.status, response.statusText);
            }
        } catch (error) {
            alert("Update failed!");
            console.error('Fetch error:', error);
        }
    });
}

function toggleOverlay(overlayId, userId=null, close=false) {
    if (close) {
        document.getElementById("addMB").innerHTML = "";
    }

    if (userId !== null && overlayId === "userForm") {
        let arrayUserId = null;
        for (let index = 0; index < ALL_USERS.length; index++) {
            const element = ALL_USERS[index];
            if (element["userId"] == userId) {
                arrayUserId = index;
                break;
            }
        }

        if (arrayUserId !== null) {
            if (ALL_USERS[arrayUserId]["userId"] !== null) {
                document.getElementById("accountUser").value = ALL_USERS[arrayUserId]["userId"];
            }

            if (ALL_USERS[arrayUserId]["firstName"] !== null) {
                document.getElementById("accountFName").value = ALL_USERS[arrayUserId]["firstName"];
            }

            if (ALL_USERS[arrayUserId]["lastName"] !== null) {
                document.getElementById("accountLName").value = ALL_USERS[arrayUserId]["lastName"];
            }

            if (ALL_USERS[arrayUserId]["displayName"] !== null) {
                document.getElementById("accountDName").value = ALL_USERS[arrayUserId]["displayName"];
            }

            if (ALL_USERS[arrayUserId]["company"] !== null) {
                document.getElementById("accountCompany").value = ALL_USERS[arrayUserId]["company"];
            }

            if (ALL_USERS[arrayUserId]["userName"] !== null) {
                document.getElementById("accountUName").value = ALL_USERS[arrayUserId]["userName"];
            }

            document.getElementById("isAdmin").checked = ALL_USERS[arrayUserId]["isAdmin"];

            let overlay = document.getElementById(overlayId);
            if (overlay.style.display == "flex") {
                overlay.style.display = "none";
            } else {
                overlay.style.display = "flex";
            }
        }
    } else if (userId !== null && overlayId === "mailboxForm") {
        document.getElementById("addEmail").setAttribute("data-uid", userId);
        let arrayUserId = [];
        for (let index = 0; index < ALL_MAILBOXES.length; index++) {
            const element = ALL_MAILBOXES[index];
            if (element["mbUser"] == userId) {
                arrayUserId.push(index);
            }
        }

        if (arrayUserId.length !== 0) {
            for (let index = 0; index < arrayUserId.length; index++) {
                const element = ALL_MAILBOXES[arrayUserId[index]];
                let parentContainer = document.getElementById('addMB');

                const heading = document.createElement('h2');
                heading.classList.add('mbs');
                heading.textContent = element["mbName"] + "@" + VISIBLE_DOMAIN;

                parentContainer.appendChild(heading);

                const hidden = document.createElement('input');
                hidden.type = 'hidden';
                hidden.name = "hidden_"+element["mbName"];
                hidden.value = element["mbName"];
                
                parentContainer.appendChild(hidden);

                function createCheckbox(name, id, labelText, checked) {
                    const checkboxDiv = document.createElement('div');
                    checkboxDiv.classList.add('checkbox');

                    const input = document.createElement('input');
                    input.type = 'checkbox';
                    input.name = name;
                    input.id = id;
                    input.checked = checked

                    const label = document.createElement('label');
                    label.setAttribute('for', id);
                    label.textContent = labelText;

                    checkboxDiv.appendChild(input);
                    checkboxDiv.appendChild(label);

                    return checkboxDiv;
                }

                const canSendCheckbox = createCheckbox('canSend_'+element["mbName"], 'canSendAccount_'+element["mbName"], 'Can Send', element["mbSend"]);
                const canReceiveCheckbox = createCheckbox('canReceive_'+element["mbName"], 'canReceiveAccount_'+element["mbName"], 'Can Receive', element["mbReceive"]);
                const deleteCheckbox = createCheckbox('delete_'+element["mbName"], 'delete_'+element["mbName"], 'Delete Mailbox', false);

                parentContainer.appendChild(canSendCheckbox);
                parentContainer.appendChild(canReceiveCheckbox);
                parentContainer.appendChild(deleteCheckbox);
            }
        } else {
            document.getElementById("nmSettingsFormAccount").style.display = "none";
        }

        let overlay = document.getElementById(overlayId);
        if (overlay.style.display == "flex") {
            overlay.style.display = "none";
        } else {
            overlay.style.display = "flex";
        }
    } else {
        let overlay = document.getElementById(overlayId);
        if (overlay.style.display == "flex") {
            overlay.style.display = "none";
        } else {
            overlay.style.display = "flex";
        }
    }
}

async function addMB(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
        const response = await fetch("/createmb", {
            method: "POST",
            body: formData,
        });

        if (response.ok) {
            const result = await response.json();
            console.log(result);
            if (result.status === "success") {
                alert(result.message || "Create Successful!");
                window.location.href = "/settings";
            } else {
                alert(result.message || "Create failed!");
            }
        } else {
            alert("Create failed!");
            console.error('Error:', response.status, response.statusText);
        }
    } catch (error) {
        alert("Create failed!");
        console.error('Fetch error:', error);
    }
}

if (document.getElementById("addEmail")) {
    document.getElementById("addEmail").addEventListener("click", function (e) {

        let parentContainer = document.createElement('form');
        parentContainer.onsubmit = addMB;
        parentContainer.className = "addForm";
    
        const hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.name = "uid";
        hidden.value = document.getElementById("addEmail").dataset.uid;
        
        parentContainer.appendChild(hidden);
    
        const mailbox = document.createElement('input');
        mailbox.type = 'text';
        mailbox.name = "email";
        mailbox.placeholder = "Mail Box Name";
        
        parentContainer.appendChild(mailbox);
    
        function createCheckbox(name, id, labelText, checked) {
            const checkboxDiv = document.createElement('div');
            checkboxDiv.classList.add('checkbox');
    
            const input = document.createElement('input');
            input.type = 'checkbox';
            input.name = name;
            input.id = id;
            input.checked = checked
    
            const label = document.createElement('label');
            label.setAttribute('for', id);
            label.textContent = labelText;
    
            checkboxDiv.appendChild(input);
            checkboxDiv.appendChild(label);
    
            return checkboxDiv;
        }
    
        const canSendCheckbox = createCheckbox('canSend', 'canSendNew', 'Can Send', true);
        const canReceiveCheckbox = createCheckbox('canReceive', 'canReceiveNew', 'Can Receive', true);
    
        parentContainer.appendChild(canSendCheckbox);
        parentContainer.appendChild(canReceiveCheckbox);
    
        const submit = document.createElement('button');
        submit.type = 'submit';
        submit.innerHTML = "Create";
        
        parentContainer.appendChild(submit);
        document.getElementById('newMB').appendChild(parentContainer);
        document.getElementById("addEmail").style.display = "none";
    });
}

async function deleteAccount(id) {
    
    try {
        const response = await fetch("/deleteuser/"+id, {
            method: "POST"
        });

        if (response.ok) {
            const result = await response.json();
            console.log(result);
            if (result.status === "success") {
                alert(result.message || "Delete Successful!");
                window.location.href = "/settings";
            } else {
                alert(result.message || "Delete failed!");
            }
        } else {
            alert("Delete failed!");
            console.error('Error:', response.status, response.statusText);
        }
    } catch (error) {
        alert("Delete failed!");
        console.error('Fetch error:', error);
    }
}