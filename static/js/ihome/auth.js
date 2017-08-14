function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}


$(function(){
    // 如果姓名和身份证有值的话，则显示
    $.get("/api/v1.0/userinfo", function(resp){
        if(resp.data.real_name != "" && resp.data.id_card != ""){
            $("#real-name").val(resp.data.real_name);
            $("#real-name").attr("disabled", true);
            $("#id-card").val(resp.data.id_card);
            $("#id-card").attr("disabled", true);
            $(".btn-success").hide();
        }
    });

    $("#form-auth").submit(function(e){
        // 禁止浏览器的默认行为
        e.preventDefault();

        var real_name = $("#real-name");
        var id_card = $("#id-card");

        // 验证用户名或者身份证ID不能为空
        if( real_name.val() == "" || id_card.val() == ""){
            $(".error-msg").show();
            return;
        }

        req = {
            "real_name":real_name.val(),
            "id_card":id_card.val()
        }

        // 将信息提交到服务器
        $.ajax({
            url: "/api/v1.0/userinfo",
            type: "POST",
            contentType: "application/json",
            data:JSON.stringify(req),
            headers:{
                "X-XSRFToken": getCookie("_xsrf")
            },
            dataType: "json",
            success: function(resp){
                if (resp.errno == "0"){
                    $(".btn-success").hide();
                    showSuccessMsg();
                }
                else{
                    $(".error-msg").html(resp.errmsg);
                    $(".error-msg").show();
                }
            }
        });
    })
})

