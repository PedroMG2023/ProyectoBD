document.addEventListener("DOMContentLoaded", () => {
    const loginButton = document.querySelector("button");

    loginButton.addEventListener("mouseover", () => {
        loginButton.style.backgroundColor = "#a06b5d";
    });

    loginButton.addEventListener("mouseout", () => {
        loginButton.style.backgroundColor = "#8d5a44";
    });
});
