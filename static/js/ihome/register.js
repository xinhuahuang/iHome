function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

var imageCodeId = "";

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

function generateImageCode() {
    // 生成一个唯一ID
    imageCodeId = generateUUID();

    // 访问获取验证码的接口
    var url = "/api/v1.0/imagecode?id=" + imageCodeId;
    $(".image-code>img").attr("src", url);
}

function sendSMSCode() {
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    } 
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }
    $.get("/api/v1.0/smscode", {mobile:mobile, code:imageCode, codeId:imageCodeId},
        function(data){
            if (0 != data.errno) {
                if (4103 == data.errno || 4003 == data.errno){
                    $("#mobile-err span").html(data.errmsg);
                    $("#mobile-err").show();
                }
                else{
                    $("#image-code-err span").html(data.errmsg);
                    $("#image-code-err").show();
                    if (2 == data.errno || 3 == data.errno) {
                        generateImageCode();
                    }
                }

                $(".phonecode-a").attr("onclick", "sendSMSCode();");
            }   
            else {
                var $time = $(".phonecode-a");
                var duration = 60;
                var intervalid = setInterval(function(){
                    $time.html(duration + "秒"); 
                    if(duration === 1){
                        clearInterval(intervalid);
                        $time.html('获取验证码'); 
                        $(".phonecode-a").attr("onclick", "sendSMSCode();");
                    }
                    duration = duration - 1;
                }, 1000, 60); 
            }
    }, 'json'); 
}

$(document).ready(function() {
    generateImageCode();
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });
    $(".form-register").submit(function(e){
        e.preventDefault();
        var mobile = $("#mobile").val();
        var phoneCode = $("#phonecode").val();
        var passwd = $("#password").val();
        var passwd2 = $("#password2").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!phoneCode) {
            $("#phone-code-err span").html("请填写短信验证码！");
            $("#phone-code-err").show();
            return;
        }
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (passwd != passwd2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
            return;
        }

        var req = {
            "mobile": mobile,
            "password": passwd,
            "sms_code": phoneCode
        };

        $.ajax({
            url: "/api/v1.0/user",
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
                else if (resp.errno == "4101"){
                    location.href = "/login.html"
                }
                else{
                    $("#password2-err span").html(resp.errmsg);
                    $("#password2-err").show();
                }
            }
        });
    });
})