function showLoading(){
    form = document.querySelector("form")
    loader = document.querySelector(".loader")
    loader.removeAttribute("hidden")
    form.setAttribute("hidden", "hidden")
}

addEventListener('submit', showLoading)