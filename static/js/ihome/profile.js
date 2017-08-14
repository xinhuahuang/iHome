function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){
    $.get("/api/v1.0/avatar", function(data){
        $("#user-avatar").attr("src", data.avatar_url);
        if (data.name){
            $("#user-name").val(data.name);
        }
    });

    $("#form-avatar").submit(function(e){
        // 禁止浏览器的默认行为
        e.preventDefault();

        $(this).ajaxSubmit({
            url: "/api/v1.0/avatar",
            type: "put",
            headers: {
                "X-XSRFToken": getCookie("_xsrf"),
            },
            dataType: "json",
            success: function (resp) {
                if (resp.errno == "0") {
                    // 表示上传成功， 将头像图片的src属性设置为图片的url
                    $("#user-avatar").attr("src", resp.avatar_url);
                } else if (resp.errno == "4101") {
                    // 表示用户未登录，跳转到登录页面
                    location.href = "/login.html";
                } else {
                    alert(resp.errmsg);
                }
            }
        });
    });

    $("#form-name").submit(function(e){
         // 禁止浏览器的默认行为
        e.preventDefault();

        // 用户不能为空
        var name = $("#user-name");
        if (name.val() == ""){
            $(".error-msg").html("用户名不能为空");
            $(".error-msg").show();
        }

        req = {
            "name":name.val()
        }

        $.ajax({
            url: "/api/v1.0/avatar",
            type: "POST",
            contentType: "application/json",
            data:JSON.stringify(req),
            headers:{
                "X-XSRFToken": getCookie("_xsrf")
            },
            dataType: "json",
            success: function(resp){
                if (resp.errno == "0"){
                    // 显示用户名
                    $("#user-name").val(resp.name);
                    showSuccessMsg();
                }
                else if ("4003" == resp.errno){
                    // 表示用户名已存在
                    $(".error-msg").show();
                }
                else{
                    $(".error-msg").html(resp.errmsg);
                    $(".error-msg").show();
                }
            }
        });

    })
})


