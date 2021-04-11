$.ajax({
        type: "GET",
        url: "http://xtra3090.d2.comp.nus.edu.sg:8000/getIdentity",
        xhrFields: {withCredentials: true},
        success: function (res) {
            if(res.status!=200) {
                window.location.href = "/modelmarket";
            }else{
                app.$data.username = res.username;
                app.$data.role = res.role;
            }
        },
});
function logout()
{
    $.ajax({
            type: "GET",
            url: "http://xtra3090.d2.comp.nus.edu.sg:8000/logout",
            xhrFields: {withCredentials: true},
    });
    window.location.href="index.html"
}