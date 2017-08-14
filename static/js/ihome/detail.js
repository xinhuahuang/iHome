function hrefBack() {
    history.go(-1);
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(document).ready(function(){
    // 获取详情页面要展示的房屋编号
    var queryData = decodeQuery();
    var houseId = queryData["id"];

    $.get("/api/v1.0/house/" + houseId, function (resp) {
        //$(".book-house").hide();

        if("0" == resp.errno){
            $(".swiper-container").html(template("house-image-tmpl", {img_urls:resp.house.img_urls, price:resp.house.price}));
            $(".detail-con").html(template("house-detail-tmpl", {house:resp.house}));

            // resp.user_id为访问页面用户,resp.data.user_id为房东
            if (resp.user_id != resp.house.user_id) {
                $(".book-house").attr("href", "/booking.html?hid="+resp.house.hid);
                $(".book-house").show();
            }
            var mySwiper = new Swiper ('.swiper-container', {
                loop: true,
                autoplay: 2000,
                autoplayDisableOnInteraction: false,
                pagination: '.swiper-pagination',
                paginationType: 'fraction'
            });
        }
    })
})