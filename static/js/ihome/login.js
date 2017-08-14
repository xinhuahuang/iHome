function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $(".form-login").submit(function(e){
        e.preventDefault();
        var mobile = $("#mobile").val();
        var passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }

        req = {
            "mobile":mobile,
            "password":passwd
        };

        $.ajax({
            url: "/api/v1.0/session",
            type: "PUT",
            contentType: "application/json",
            data:JSON.stringify(req),
            headers:{
                "X-XSRFToken": getCookie("_xsrf")
            },
            dataType: "json",
            success: function(resp){
                if (resp.errno == "0"){
                    location.href = "/index.html"
                }
                else if ("4103" == resp.errno || "4104" == resp.errno){
                    $("#mobile-err span").html(resp.errmsg);
                    $("#mobile-err").show();
                }
                else{
                    $("#password2-err span").html(resp.errmsg);
                    $("#password2-err").show();
                }
            }
        });
    });
})