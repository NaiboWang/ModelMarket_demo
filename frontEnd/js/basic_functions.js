function logout()
{
    $.ajax({
            type: "GET",
            url: "http://xtra3090.d2.comp.nus.edu.sg:8000/logout",
            xhrFields: {withCredentials: true},
    });
    window.location.href="index.html"
}
// Check the status of the message
function check_status(result)
{
    if(result["status"]!=200) {
        alert(result["reason"]);
        return false;
    }else{
        return true;
    }
}