function logout()
{
    $.ajax({
            type: "GET",
            url: "http://192.168.163.129:8080/logout",
            xhrFields: {withCredentials: true},
    });
    window.location.href="index.html"
}
// Check the status of the message
function check_status(result)
{
    if(result["status"]!=200) {
        alert(result["msg"]);
        return false;
    }else{
        return true;
    }
}