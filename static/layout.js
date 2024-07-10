const loginForm = document.getElementById("login-form");

const items = document.querySelectorAll(".item");
items.forEach(item => {
    item.addEventListener("click", () => {
        const loginForm = document.createElement("a");
        if(item.id == "home"){
            loginForm.setAttribute("href", "/");
        }
        else if(item.id == "people"){
            loginForm.setAttribute("href", "/community");
        }
        else if(item.id == "school"){
            loginForm.setAttribute("href", "/knowledge-base");
        }
        else if(item.id == "spa"){
            loginForm.setAttribute("href", "/plant");
        }
        else if(item.id == "chat"){
            loginForm.setAttribute("href", "/chat");
        }
        else if(item.id == "settings"){
            loginForm.setAttribute("href", "/settings");
        }
        else if(item.id == "account_circle"){
            loginForm.setAttribute("href", "/profile");
        }
        else if(item.id == "account_registration"){
            loginForm.setAttribute("href", "/register");
        }
        else if(item.id == "login"){
            loginForm.setAttribute("href", "/login");
        }
        loginForm.click();
    });
});