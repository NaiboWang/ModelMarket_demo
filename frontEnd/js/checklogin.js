$.ajax({
        type: "GET",
        url: "http://192.168.163.129:8080/getIdentity",
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