function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');

    // 获取区域信息
    $.get("/api/v1.0/areas", function(rep){
        for(var i=0; i<rep.data.length; i++)
        {
            var ai_area_id = rep.data[i].ai_area_id;
            var ai_name = rep.data[i].ai_name;

            $("#area-id").append('<option value="'+ ai_area_id +'">'+ ai_name +'</option>');
        }
    });

    // 获取房间设施
    $.get("/api/v1.0/facility", function(rep){
        for(var i=0; i<rep.data.length; i++)
        {
            var ai_area_id = rep.data[i].fc_id;
            var ai_name = rep.data[i].fc_name;

            $(".house-facility-list").append(
                '<li><div class="checkbox"><label><input type="checkbox" name="facility" value="'+ ai_area_id +'">'+ ai_name +'</label> </div></li>'
            );
        }
    });

    // 发送房屋基本信息
    $("#form-house-info").submit(function(e){
        e.preventDefault();

        // 将表单的数据转成json，向后端发送请求
        var formData = {};
        $(this).serializeArray().map(function (x) {formData[x.name] = x.value});

        // 获取所选的房屋设施
        var facility = [];
        $('[name=facility]:checkbox:checked').each(function(i,x){
            facility[i] = x.value;
        });

        formData.facility = facility;

        $.ajax({
            url:"/api/v1.0/house",
            type:"put",
            data:JSON.stringify(formData),
            contentType:"application/json",
            datatype:"json",
            headers:{
                "X-XSRFToken": getCookie("_xsrf")
            },
            success: function(resp){
                if ("4101" == resp.errno){
                    location.href = "/login.html";
                }
                else if ("0" == resp.errno){
                    // 隐藏基本信息表单
                    $("#form-house-info").hide();
                    // 显示上传图片的表单
                    $("#form-house-image").show();
                    // 设置图片表单对应的房屋编号隐藏字段
                    $("#house-id").val(resp.house_id);
                }
                else{
                    alert(resp.errmsg);
                }
            }
        });
    });

    // 上传房屋图片
    $("#form-house-image").submit(function(e){
        e.preventDefault();

        // 使用jquery.form插件，对表单进行异步提交，通过这样的方式，可以添加自定义的回调函数
        $(this).ajaxSubmit({
            url: "/api/v1.0/house/images",
            type: "put",
            headers: {
                "X-XSRFToken": getCookie("_xsrf")
            },
            dataType: "json",
            success: function (resp) {
                if ("4101" == resp.errno) {
                    location.href = "/login.html";
                } else if ("0" == resp.errno) {
                    // 在前端中添加一个img标签，展示上传的图片
                    $(".house-image-cons").append('<img src="'+ resp.image_url+'">');

                    // 清空上传文本框中的数据
                    $("#house-image").outerHTML = "";
                } else {
                    alert(resp.errmsg);
                }
            }
        });
    });
})