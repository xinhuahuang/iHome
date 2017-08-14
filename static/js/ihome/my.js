function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
function logout() {
    $.ajax({
        url: "/api/v1.0/session",
        type: "delete",
        data: {_xsrf: getCookie("_xsrf")},
        dataType: "json",
        success: function(resp){
            if ("0" == resp.errno) {
                location.href = "/index.html";
            }
        }
    });
}

$(document).ready(function(){
    $.get('/api/v1.0/userinfo', function(resp){
        $("#user-avatar").attr("src", resp.data.avatar);
        $("#user-name").html(resp.data.name);
        $("#user-mobile").html(resp.data.mobile);
    });
})