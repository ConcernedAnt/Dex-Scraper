$(document).ready(function() {
    console.log("Hey carousel");
    $('.owl-carousel').owlCarousel({
        loop: $('.owl-carousel .item').length> 1 ? true:false,
        margin:10,
        nav:true,
        autoplay: true,
        responsive:{
            0:{
                items:1
            },
            600:{
                items:3
            },
            1000:{
                items:5
            }
        }
    })
} );

