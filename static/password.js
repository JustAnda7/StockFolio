var password = document.getElementById("password")

password.onfocus = function () {
    document.getElementById("message").style.display = "block";
}

password.onblur = function () {
    document.getElementById("message").style.display = "none";
}

password.onkeyup = function () {
    var lower = /[a-z]/g;
    if (password.value.match(lower)){
        getELementById("letter").classList.remove("invalid");
        getELementById("letter").classList.add("valid");
    }
    else {
        getELementById("letter").classList.remove("valid");
        getELementById("letter").classList.add("invalid");
    }

    var upper = /[A-Z]/g;
    if (password.value.match(upper)){
        getELementById("letter").classList.remove("invalid");
        getELementById("letter").classList.add("valid");
    }
    else {
        getELementById("letter").classList.remove("valid");
        getELementById("letter").classList.add("invalid");
    }

    var num = /[0-9]/g;
    if (password.value.match(num)){
        getELementById("letter").classList.remove("invalid");
        getELementById("letter").classList.add("valid");
    }
    else {
        getELementById("letter").classList.remove("valid");
        getELementById("letter").classList.add("invalid");
    }

    if (password.value.length >= 8){
        getELementById("letter").classList.remove("invalid");
        getELementById("letter").classList.add("valid");
    }
    else {
        getELementById("letter").classList.remove("valid");
        getELementById("letter").classList.add("invalid");
    }

}