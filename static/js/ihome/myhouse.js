$(document).ready(function(){
    $(".auth-warn").show();

    // 如果姓名和身份证有值的话，则显示
    $.get("/api/v1.0/userinfo", function(resp){
        // 如果用户未登录，则让其跳转到login
        if(resp.errno == "4101"){
            location.href = "./login.html";
            return;
        }

        // 如果用户已认证，则隐藏认证按钮；否则，隐藏发布新房源按钮
        if(resp.data.real_name != "" && resp.data.id_card != ""){
            $(".auth-warn").hide();
            $(".new-house").show();
        }
        else{
            $(".auth-warn").show();
            $(".new-house").hide();
        }
    });

    // 获取房屋基本信息
    $.get("/api/v1.0/house", function (resp) {
        if("0" == resp.errno){
            // var houses_info = resp.data;
            //
            // for(var i=0; i<houses_info.length; i++){
            //     $("#houses-list").append(
            //         '<li>\
            //         <a href="/detail.html?id='+houses_info[i].hi_house_id+'">\
            //             <div class="house-title">\
            //                 <h3>房屋ID:'+ houses_info[i].hi_house_id +' —— '+ houses_info[i].hi_title+'</h3>\
            //             </div>\
            //             <div class="house-content">\
            //                 <img src="'+ houses_info[i].hi_index_image_url+'">\
            //                 <div class="house-text">\
            //                     <ul>\
            //                         <li>位于：'+ houses_info[i].ai_name +'</li>\
            //                         <li>价格：￥'+ houses_info[i].hi_price+'/晚</li>\
            //                         <li>发布时间：'+ houses_info[i].hi_utime+'</li>\
            //                     </ul>\
            //                 </div> \
            //             </div>\
            //         </a>\
            //     </li>'
            //     );
            // }

            $("#houses-list").html(template("houses-list-tmpl", {houses: resp.data}));
        }
    })
});