/**

jQuery Awselect
Developed by: Prev Wong
Documentation: https://prevwong.github.io/awesome-select/
Github: https://github.com/prevwong/awesome-select/

**/

var awselect_count = 0; // used for generating sequential ID for <select> that does not have ID
var mobile_width = 800;

(function($) {
    $(document).mouseup(function(e) {
        var awselect = $(".awselect");
        if (!awselect.is(e.target) && awselect.has(e.target).length === 0) 
        {
            deanimate();
        }
    });
    $.fn.awselect = function(options) {
        var element = $(this);
        var opts = $.extend({}, $.fn.awselect.defaults, options);
        element.each(function() {
            awselect_count += 1;
            build($(this), opts);
        });
        this.on("aw:animate", function() {
            animate(getawselectElement($(this)));
            
        });
        this.on("change", function() {
            setValue(this);
        });
        this.on("aw:deanimate", function() {
           deanimate(getawselectElement($(this)))
        });

        console.log(element.attr("id"));
        return {
            blue: function() {
                element.css("color", "blue");
            }
        };
    };
    $.fn.awselect.defaults = {
        background: "#e5e5e5",
        active_background: "#fff",
        placeholder_color: "#000",
        placeholder_active_color: "#000",
        option_color: "#000",
        vertical_padding: "15px",
        horizontal_padding: "40px",
        immersive: false,
    };
    function getawselectElement(select) {
        return $('.awselect[data-select="' + select.attr("id") + '"]');
    }
    function build(element, opts) {
        var placeholder = element.attr("data-placeholder");
        var id = element.attr("id");
        var options = element.children("option");
        var selected = false;
        var classes = "awselect";
        var options_html = "";
        var background = opts["background"];
        var active_background = opts["active_background"];
        var placeholder_color = opts["placeholder_color"];
        var placeholder_active_color = opts["placeholder_active_color"];
        var option_color = opts["option_color"];
        var vertical_padding = opts["vertical_padding"];
        var horizontal_padding = opts["horizontal_padding"];
        var immersive = opts["immersive"];
        if ( immersive !== true ) {
            var immersive = false;
        }

        options.each(function() {
            if (typeof $(this).attr("selected") !== typeof undefined && $(this).attr("selected") !== false) {
                selected = $(this).text();
            }
            options_html += '<li><a style="padding: 2px '+ horizontal_padding +'">' + $(this).text() + '</a></li>';
        });
        if (selected !== false) {
            classes += " hasValue";
        }
        if (typeof id !== typeof undefined && id !== false) {
            id_html = id;
        } else {
            id_html = "awselect_" + awselect_count;
            $(element).attr("id", id_html);
        }
        var awselect_html = '<div data-immersive="'+ immersive +'" id="awselect_' + id_html + '" data-select="' + id_html + '" class = "' + classes + '"><div style="opacity:1;background:' + active_background + '" class = "bg"></div>';
        awselect_html += '<div style="padding:' + vertical_padding + " " + horizontal_padding + '" class = "front_face">';
        awselect_html += '<div style="background:' + background + '" class = "bg"></div>';
        awselect_html += '<div data-inactive-color="' + placeholder_active_color + '" style="color:' + placeholder_color + '" class = "content">';
        if (selected !== false) {
            awselect_html += '<span class="current_value">' + selected + "</span>";
        }
        awselect_html += '<span class = "placeholder">' + placeholder + "</span>";
        awselect_html += '<i class = "icon">' + icon(placeholder_color) + "</i>";
        awselect_html += "</div>";
        awselect_html += "</div>";
        awselect_html += '<div style="padding:' + vertical_padding + ' 0;" class = "back_face"><ul style="color:' + option_color + '">';
        awselect_html += options_html;
        awselect_html += "</ul></div>";
        awselect_html += "</div>";
        $(awselect_html).insertAfter(element);
       element.hide();
    }

    function animate(element) {
        if (element.hasClass("animating") == false) {
            element.addClass("animating");
            if ($(".awselect.animate").length > 0) {
                deanimate($(".awselect").not(element));
                var timeout = 600;
            } else {
                var timeout = 100;
            }
            var immersive = element.attr('data-immersive')
            
            if ($(window).width() < mobile_width || immersive == "true" ) {
                immersive_animate(element);
                timeout += 200
            }
            setTimeout(function() {
                var back_face = element.find(".back_face");
                back_face.show();
                var bg = element.find("> .bg");
                bg.css({
                    height: element.outerHeight() + back_face.outerHeight()
                });
                back_face.css({
                    "margin-top": $(element).outerHeight()
                });
                
                if ( $(window).width() < mobile_width || immersive === "true" ) {
                    element.css({
                        "top": parseInt(element.css('top')) - back_face.height()
                    })
                }
                element.addClass("placeholder_animate");
                setTimeout(function() {
                    switchPlaceholderColor(element);
                    setTimeout(function(){
                        if (back_face.outerHeight() == 200) {
                            back_face.addClass("overflow");
                        }
                    }, 200);
                  
                    
                    element.addClass("placeholder_animate2");
                    element.addClass("animate");
                    element.addClass("animate2");
                    element.removeClass("animating");
                }, 100);
            }, timeout);
        }
    }

    function immersive_animate(element) {
        $(".awselect_bg").remove()
        $('body, html').addClass('immersive_awselect')
        $('body').prepend('<div class = "awselect_bg"></div>')
        setTimeout(function(){
             $('.awselect_bg').addClass('animate')
        }, 100)
       
       
        var current_width = element.outerWidth()
        var current_height = element.outerHeight()
        var current_left = element.offset().left
        var current_top = element.offset().top - $(window).scrollTop() 
        element.attr('data-o-width', current_width)
        element.attr('data-o-left', current_left)
        element.attr('data-o-top', current_top)
        element.addClass('transition_paused').css({
            "width" : current_width,
            "z-index": "9999"
       })
        setTimeout(function(){
            $('<div class = "awselect_placebo" style="position:relative; width:'+ current_width +'px; height:'+ current_height +'px; float:left;ß"></div>').insertAfter(element)
            element.css({
                "position": "fixed",
                "top" : current_top,
                "left": current_left
            })
            element.removeClass('transition_paused')
            setTimeout(function(){
                if ( $(window).width() < mobile_width ) {
                     element.css('width', $(window).outerWidth() - 40 )
                } else {
                     element.css('width', $(window).outerWidth() / 2)
                }
               
                element.css({
                    "top" : $(window).outerHeight() / 2 + element.outerHeight() / 2,
                    "left" : "50%",
                    "transform": "translateX(-50%) translateY(-50%)"
                })
                setTimeout(function(){
                    animate(element)
                 }, 100)
            }, 100)
        }, 50)
    }

    function deanimate(awselects) {
        if (awselects == null) {
            var awselect = $(".awselect");
        } else {
            var awselect = awselects;
        }
        $(awselect).each(function() {
            var element = $(this);
            
            if (element.hasClass("animate")) {
                setTimeout(function() {
               
                }, 300);
                element.removeClass("animate2");
                element.find(".back_face").hide();
                element.find('.back_face').removeClass('overflow')
                element.removeClass("animate");
                switchPlaceholderColor(element);

                element.children(".bg").css({
                    height: 0
                });
                element.removeClass("placeholder_animate2");
                setTimeout(function() {
                    immersive_deanimate(element)
                    element.removeClass("placeholder_animate");
                }, 100);
            }
        });
    }
    function immersive_deanimate(element){
       
        if ( element.siblings('.awselect_placebo').length > 0 ) {
           

            setTimeout(function(){
                var original_width = element.attr('data-o-width')
                var original_left = element.attr('data-o-left')
                var original_top = element.attr('data-o-top')

                element.css({
                    "width" : original_width,
                    "left" : original_left + "px",
                    "transform": "translateX(0) translateY(0)",
                    "top" : original_top + "px"
                })
                 $('.awselect_bg').removeClass('animate')
                setTimeout(function(){
                    $('.awselect_placebo').remove()
                    $('body, html').removeClass('immersive_awselect')
                    setTimeout(function(){ 
                        $('.awselect_bg').removeClass('animate').remove()
                    }, 200);
                    element.attr('style', '')
                }, 300)
            }, 100)
            
        }
        

    }

    function switchPlaceholderColor(element) {
        var placeholder_inactive_color = element.find(".front_face .content").attr("data-inactive-color");
        var placeholder_normal_color = element.find(".front_face .content").css("color");
        element.find(".front_face .content").attr("data-inactive-color", placeholder_normal_color);
        element.find(".front_face .content").css("color", placeholder_inactive_color);
        element.find(".front_face .icon svg").css("fill", placeholder_inactive_color);
    }
    function setValue(select) {
        var val = $(select).val();
        var awselect = getawselectElement($(select));
        var option_value = $(select).children('option[value="' + val + '"]').eq(0);
        var callback = $(select).attr("data-callback");
        $(awselect).find(".current_value").remove();
        $(awselect).find(".front_face .content").prepend('<span class = "current_value">' + option_value.text() + "</span>");
        $(awselect).addClass("hasValue");
        if (typeof callback !== typeof undefined && callback !== false) {
            window[callback](option_value.val());
        }
        setTimeout(function() {
            deanimate();
        }, 100);
    }
    function icon(color) {
        
        return '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" viewBox="0 0 700 700">\
        <g>\
         <path d="m451.49 332.5c-1.8594 0-3.4102 1.3008-3.8398 3.0352-0.0625 0.30859-0.125 0.62109-0.125 0.92969 0 11.586-9.418 21.004-21.004 21.004-11.586 0-21.004-9.418-21.004-21.004 0-3.4102 0.80469-6.6914 2.3516-9.7266 0.18359-0.24609 0.30859-0.55859 0.37109-0.86719 0.42969-1.7344-0.37109-3.5938-2.043-4.4648-1.9219-1.0547-4.3398-0.24609-5.332 1.6758-2.168 4.0898-3.2812 8.7344-3.2812 13.383 0 15.988 12.945 28.934 28.934 28.934 15.926 0 28.934-12.945 28.934-28.934 0.003906-2.1758-1.793-3.9648-3.9609-3.9648z"/>\
         <path d="m293.8 321.4c-1.6758 0.86719-2.4805 2.7266-2.043 4.4648 0.0625 0.30859 0.18359 0.62109 0.37109 0.86719 1.5508 3.0352 2.3516 6.3242 2.3516 9.7266 0 11.586-9.418 21.004-21.004 21.004-11.586 0-21.004-9.418-21.004-21.004 0-0.30859-0.0625-0.62109-0.125-0.92969-0.42969-1.7344-1.9805-3.0352-3.8398-3.0352-2.168 0-3.9648 1.7969-3.9648 3.9648 0 15.988 13.016 28.934 28.934 28.934 15.988 0 28.934-12.945 28.934-28.934 0-4.6484-1.1133-9.2969-3.2812-13.383-0.99609-1.9219-3.4062-2.7305-5.3281-1.6758z"/>\
         <path d="m399.63 257.14c-1.6758-0.30859-3.2812 0.42969-4.1484 1.7344-0.24609 0.42969-0.42969 0.86719-0.55859 1.3594-3.9648 19.641-11.586 32.777-19.023 32.777-5.0195 0-10.473-6.3828-14.621-17.039-4.0273-10.41-6.5078-23.672-7.125-38.102 0.92969 0.0625 1.8594 0.125 2.7891 0.125 1.5508 0 3.0352-0.18359 4.4023-0.74609 0.68359-0.30859 1.3594-0.74609 1.9805-1.3008 1.6133-1.4883 2.4141-3.7188 2.4141-6.5703 0-8.6758-7.0625-15.734-15.734-15.734-8.6758 0-15.734 7.0625-15.734 15.734 0 2.8516 0.80469 5.0781 2.4141 6.5703 0.62109 0.55859 1.3008 0.99219 1.9805 1.3008 2.168 0.92969 4.7109 0.80469 7.1836 0.62109-0.68359 14.438-3.0977 27.699-7.125 38.102-4.1484 10.656-9.6055 17.039-14.621 17.039-7.4375 0-15.059-13.137-19.023-32.777-0.125-0.5-0.30859-0.92969-0.55859-1.3594-0.86719-1.3008-2.4805-2.043-4.1484-1.7344-2.1055 0.42969-3.5352 2.543-3.0977 4.6484 4.957 24.535 14.996 39.16 26.828 39.16 8.6758 0 16.48-7.8672 21.996-22.121 1.5508-3.9023 2.8516-8.1133 3.9023-12.699 1.0547 4.5859 2.3516 8.7969 3.9023 12.699 5.5156 14.254 13.324 22.121 21.996 22.121 11.832 0 21.875-14.621 26.828-39.16 0.43359-2.1055-0.98828-4.2109-3.0977-4.6484z"/>\
         <path d="m249.75 71.895c-13.016-10.965-30.234-17.781-48.512-19.145-2.168-0.18359-4.0898 1.4219-4.2734 3.6562-0.125 2.168 1.4883 4.0898 3.6562 4.2109 33.27 2.543 60.66 24.91 63.816 52.047 2.2891 20.137-9.6641 36.434-14.93 42.566-1.4297 1.6133-1.2383 4.1484 0.37109 5.5781 0.80469 0.62109 1.6758 0.92969 2.6055 0.92969 1.1133 0 2.2305-0.42969 3.0352-1.3594 5.9453-6.875 19.453-25.34 16.789-48.637-1.7383-14.824-9.7344-29.008-22.559-39.848z"/>\
         <path d="m447.52 161.73c0.92969 0 1.7969-0.30859 2.6055-0.92969 1.6133-1.4297 1.7969-3.9648 0.37109-5.5781-5.2656-6.1328-17.227-22.43-14.93-42.566 3.1602-27.137 30.547-49.504 63.816-52.047 2.168-0.125 3.7812-2.043 3.6562-4.2109-0.18359-2.2305-2.1055-3.8398-4.2734-3.6562-18.277 1.3594-35.504 8.1758-48.512 19.145-12.824 10.84-20.82 25.031-22.551 39.84-2.6641 23.297 10.84 41.758 16.789 48.637 0.80078 0.92969 1.9141 1.3672 3.0273 1.3672z"/>\
         <path d="m303.41 182.55c-9.4805 0-17.164 7.6836-17.164 17.164 0 9.4805 7.6836 17.164 17.164 17.164s17.164-7.6836 17.164-17.164c0-9.4805-7.6797-17.164-17.164-17.164zm-2.8477 17.164c0 2.1055-1.7344 3.8398-3.9023 3.8398-2.1055 0-3.8398-1.7344-3.8398-3.8398 0-1.8594 1.3008-3.4102 3.0352-3.7812-0.30859-0.68359-0.42969-1.3594-0.42969-2.1055 0-2.8516 2.2891-5.1406 5.1406-5.1406 2.7891 0 5.1406 2.2891 5.1406 5.1406 0 2.8516-2.3516 5.1406-5.1406 5.1406h-0.125c0.058594 0.25 0.12109 0.5 0.12109 0.74609zm4.3945 5.457c-1.2383 0-2.2305-0.99219-2.2305-2.2891 0-1.2383 0.99219-2.2891 2.2305-2.2891 1.3008 0 2.2891 1.0547 2.2891 2.2891 0.007812 1.2969-0.98438 2.2891-2.2891 2.2891z"/>\
         <path d="m396.59 216.88c9.4805 0 17.164-7.6836 17.164-17.164 0-9.4805-7.6836-17.164-17.164-17.164s-17.164 7.6836-17.164 17.164c0 9.4844 7.6797 17.164 17.164 17.164zm3.8398-14.004c0 1.3008-0.99219 2.2891-2.2891 2.2891-1.2383 0-2.2305-0.99219-2.2305-2.2891 0-1.2383 0.99219-2.2891 2.2305-2.2891 1.2969 0 2.2891 1.0508 2.2891 2.2891zm-11.402-6.9375c-0.30859-0.68359-0.42969-1.3594-0.42969-2.1055 0-2.8516 2.2891-5.1406 5.1406-5.1406 2.7891 0 5.1406 2.2891 5.1406 5.1406s-2.3516 5.1406-5.1406 5.1406h-0.125c0.0625 0.24609 0.125 0.5 0.125 0.74609 0 2.1055-1.7344 3.8398-3.9023 3.8398-2.1055 0-3.8398-1.7344-3.8398-3.8398-0.003906-1.8594 1.3008-3.4141 3.0312-3.7812z"/>\
         <path d="m552.05 269.54c-7.5-5.5781-16.664-11.586-27.324-17.289-8.7969-21.254-19.699-41.945-32.344-61.027 8.4883-1.7969 16.664-5.1406 23.98-9.7891 9.4805-6.1328 17.164-14.254 22.863-24.102 9.6055-16.664 14.621-40.891 13.137-63.262-1.7344-25.715-11.402-44.922-27.199-54.027-15.734-9.1055-37.238-7.8672-60.352 3.4727-20.137 9.9102-38.602 26.395-48.203 43.004-4.4023 7.6211-7.2461 15.676-8.6133 24.227-19.086-9.7266-38.539-14.684-57.992-14.684s-38.91 4.957-57.992 14.684c-1.3594-8.5508-4.2109-16.605-8.6133-24.227-9.6055-16.605-28.066-33.086-48.203-43.004-23.109-11.34-44.547-12.578-60.352-3.4727-15.797 9.1055-25.465 28.312-27.199 54.027-1.4883 22.367 3.5352 46.594 13.137 63.262 5.6992 9.8516 13.383 17.969 22.863 24.102 7.3125 4.6484 15.488 7.9922 23.98 9.7891-12.641 19.086-23.543 39.777-32.344 61.027-10.656 5.6992-19.828 11.711-27.324 17.289-1.7344 1.3008-2.1055 3.7812-0.80469 5.5781 0.74609 1.0547 1.9805 1.6133 3.1602 1.6133 0.80469 0 1.6758-0.30859 2.3516-0.80469 5.2031-3.8398 11.277-7.9297 18.031-11.957-12.762 34.266-19.953 69.395-19.953 100.74 0 26.707 5.332 50.434 15.797 70.57 8.7969 16.918 21.312 31.477 37.301 43.371-3.2812 18.031 6.1953 36.617 23.793 44.117 5.0781 2.168 10.41 3.2188 15.797 3.2188 5.0781 0 10.098-0.92969 14.996-2.9102 6.9375-2.7891 12.887-7.375 17.289-13.262 22.305 5.0195 47.273 7.5586 74.289 7.5586s51.984-2.543 74.289-7.5586c4.4023 5.8867 10.348 10.473 17.289 13.262 4.8945 1.9805 9.9102 2.9102 14.996 2.9102 5.3945 0 10.719-1.0547 15.797-3.2188 17.594-7.5 27.074-26.086 23.793-44.117 15.988-11.895 28.504-26.453 37.301-43.371 10.473-20.137 15.797-43.863 15.797-70.57 0-31.348-7.1836-66.484-19.953-100.74 6.7539 4.0273 12.824 8.1133 18.031 11.957 0.68359 0.5 1.5508 0.80469 2.3516 0.80469 1.1758 0 2.418-0.55859 3.1602-1.6133 1.3086-1.7969 0.93359-4.2734-0.80469-5.5781zm-58.484 200.38c-2.543-5.9453-6.5078-11.277-11.523-15.305-1.6758-1.4219-4.1484-1.1758-5.5781 0.55859-1.1758 1.4297-1.1758 3.4727-0.0625 4.8945 0.18359 0.24609 0.37109 0.5 0.62109 0.68359 4.0898 3.2812 7.1836 7.4375 9.2969 12.332 0.30859 0.74609 0.55859 1.4883 0.86719 2.2891 0.42969 1.3008 0.80469 2.6641 1.0547 4.0273 0.30859 1.4219 0.5 2.9102 0.62109 4.4023 0.80469 13.199-6.6914 26.145-19.578 31.664-7.9297 3.4102-16.727 3.4727-24.723 0.30859-4.5234-1.8594-8.4883-4.5859-11.711-8.0547-0.99219-1.0547-1.8594-2.168-2.7266-3.4102-0.80469-1.1133-1.4883-2.3516-2.168-3.5938-0.37109-0.74609-0.74609-1.4883-1.0547-2.2891-0.125-0.24609-0.30859-0.55859-0.49219-0.80469-1.0547-1.4219-3.0352-1.9805-4.7109-1.2383-2.043 0.86719-2.9727 3.1602-2.1055 5.2031 0.125 0.30859 0.30859 0.68359 0.42969 0.99219-21.133 4.5117-44.617 6.8711-70.02 6.8711s-48.887-2.3516-70.016-6.875c0.125-0.30859 0.30859-0.68359 0.42969-0.99219 0.86719-2.043-0.0625-4.3398-2.1055-5.2031-1.6758-0.74609-3.6562-0.18359-4.7109 1.2383-0.18359 0.24609-0.37109 0.55859-0.49219 0.80469-0.30859 0.80469-0.68359 1.5508-1.0547 2.2891-0.68359 1.2383-1.3594 2.4805-2.168 3.5938-0.86719 1.2383-1.7969 2.3516-2.7266 3.4102-3.2188 3.4727-7.1836 6.1953-11.711 8.0547-7.9922 3.1602-16.789 3.0977-24.723-0.30859-2.2891-0.99219-4.4023-2.2305-6.3828-3.6562-1.3008-0.92969-2.4805-1.9805-3.5938-3.0977-6.6289-6.5078-10.098-15.676-9.6055-24.91 0.125-1.4883 0.30859-2.9727 0.62109-4.4023 0.24609-1.3594 0.62109-2.7266 1.0547-4.0273 0.18359-0.49219 0.30859-0.92969 0.5-1.3594 0.125-0.30859 0.24609-0.62109 0.42969-0.92969 1.0547-2.4805 2.2891-4.7109 3.8398-6.7539 1.5508-2.043 3.3438-3.9023 5.3945-5.5781 0.24609-0.18359 0.42969-0.42969 0.62109-0.68359 1.1133-1.4297 1.1133-3.4727-0.0625-4.8945-0.18359-0.24609-0.42969-0.42969-0.68359-0.68359-1.4219-1.1133-3.4727-1.0547-4.8945 0.125-5.0195 4.0273-8.9805 9.3594-11.523 15.305-0.0625 0.18359-0.18359 0.37109-0.24609 0.55859-31.539-24.602-47.523-60.098-47.523-105.77 0-33.145 8.2422-70.633 22.863-106.76 19.953-10.289 45.109-19.145 74.66-21.438 19.516-1.4883 39.285 0 58.676 4.5234 2.1055 0.5 4.2734-0.86719 4.7695-2.9727 0.5-2.168-0.86719-4.2734-2.9727-4.7695-20.199-4.6484-40.707-6.2539-61.09-4.6484-26.77 2.043-50.062 9.2969-69.332 18.219 8.7344-19.699 19.27-38.785 31.414-56.32l3.7188-5.3945-6.5703-0.74609c-19.953-2.3516-37.109-13.691-47.152-31.039-8.8594-15.367-13.508-37.855-12.086-58.738 0.86719-13.324 5.0781-37.238 23.234-47.707 6.2539-3.5938 13.074-5.0195 19.828-5.0195 12.762 0 25.219 4.8945 33.086 8.7344 18.77 9.2344 35.934 24.535 44.793 39.84 4.7695 8.3047 7.5586 17.289 8.3047 26.77l0.42969 6.1953 5.4531-3.0352c19.516-10.902 39.469-16.418 59.293-16.418s39.777 5.5156 59.293 16.418l5.4531 3.0352 0.42969-6.1953c0.74609-9.4805 3.5352-18.465 8.3047-26.77 17.102-29.617 67.66-60.906 97.707-43.559 18.156 10.473 22.367 34.391 23.234 47.707 1.4219 20.883-3.2188 43.371-12.086 58.738-10.035 17.348-27.199 28.688-47.152 31.039l-6.5703 0.74609 3.7188 5.3945c12.145 17.535 22.68 36.617 31.414 56.32-19.27-8.9219-42.566-16.172-69.332-18.219-20.383-1.6133-40.891 0-61.09 4.6484-2.1055 0.5-3.4727 2.6055-2.9727 4.7695 0.49219 2.1055 2.6641 3.4727 4.7695 2.9727 19.395-4.5234 39.16-6.0078 58.676-4.5234 29.559 2.2891 54.711 11.156 74.66 21.438 14.621 36.121 22.863 73.605 22.863 106.76 0 45.664-15.988 81.168-47.523 105.77-0.039062-0.17969-0.10156-0.36719-0.22266-0.55078z"/>\
         <path d="m504.59 277.04c-18.219-14.375-38.723-24.594-60.969-30.418-18.898-4.957-38.355-6.5078-57.934-4.5859-2.168 0.18359-3.7188 2.1055-3.5352 4.3398 0.18359 2.168 2.168 3.7812 4.3398 3.5352 18.586-1.7969 37.109-0.37109 55.145 4.3359 21.191 5.5781 40.707 15.305 57.992 29.059 0.74609 0.55859 1.6133 0.86719 2.4805 0.86719 1.1758 0 2.2891-0.55859 3.0977-1.5508 1.3633-1.6797 1.0547-4.2227-0.61719-5.582z"/>\
         <path d="m313.5 249.9c2.168 0.18359 4.1484-1.3594 4.3398-3.5352 0.18359-2.2305-1.3594-4.1484-3.5352-4.3398-19.578-1.9219-39.031-0.37109-57.934 4.5859-22.242 5.8242-42.75 16.051-60.969 30.418-1.6758 1.3594-1.9805 3.9023-0.62109 5.5781 0.80469 0.99219 1.9219 1.5508 3.0977 1.5508 0.86719 0 1.7344-0.30859 2.4805-0.86719 17.289-13.754 36.805-23.48 57.992-29.059 18.039-4.6992 36.562-6.1289 55.148-4.332z"/>\
        </g>\
       </svg>'

        // return '<svg style="fill:' + color + '" version="1.1" id="Chevron_thin_down" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 20 20" enable-background="new 0 0 20 20" xml:space="preserve"><path d="M17.418,6.109c0.272-0.268,0.709-0.268,0.979,0c0.27,0.268,0.271,0.701,0,0.969l-7.908,7.83c-0.27,0.268-0.707,0.268-0.979,0l-7.908-7.83c-0.27-0.268-0.27-0.701,0-0.969c0.271-0.268,0.709-0.268,0.979,0L10,13.25L17.418,6.109z"/></svg>';
    }
    function change(elem) {
        elem.css("color", "green");
    }
})(jQuery);


$(document).ready(function() {
    $("body").on("click", ".awselect .front_face", function() {
        var dropdown = $(this).parent('.awselect');
       
        if ( dropdown.hasClass("animate") == false) {
            $("select#" + dropdown.attr("id").replace("awselect_", "")).trigger("aw:animate");
        } else {
             $("select#" + dropdown.attr("id").replace("awselect_", "")).trigger("aw:deanimate");
        }
        
    });



    $("body").on("click", ".awselect ul li a", function() {
        var dropdown = $(this).parents(".awselect");
        var value_index = $(this).parent("li").index();
        var id = dropdown.attr("data-select");
        var select = $("select#" + id);
        var option_value = $(select).children("option").eq(value_index);
        var callback = $(select).attr("data-callback");
        $(select).val(option_value.val());
        $(select).trigger("change");
    });
});