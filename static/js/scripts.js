"use strict";

var staffImgUpdateForm = function(){
    var file = $(this).siblings('.fileinput');
    var img = $(this).children('img');

    file.click();
    file.fileupload({
        dataType: 'json',
        sequentialUploads: true,
        done: function(e, data){
            if (data.result.is_valid){
                img.attr("src", data.result.img_url);
            }
        }

    });
};


var commentForm = function () {
    var form = $(this).closest("form");

    $.ajax({
        url: $(this).attr("data-url"),
        data: form.serialize(),
        type: form.attr("method"),
        dataType: 'json',
        success: function (data) {
            if (data.is_valid){
                form[0].reset();
                var count = '#count-' + data.obj_pk;
                $(count).html(data.count);
                $("#new-comment-" + data.obj_pk).prepend(
                    '<div class="media mt-3">' +
                        '<img src="' + data.user_url + '" class="rounded-circle img-fluid' +
                        'profile-photo" height="30" width="30">' +
                        '<div class="media-body ml-2">' +
                            '<a href="' + data.usr_detail_url +'" class="mr-2 font-weight-bold">' + data.username + '</a>' +
                            '<span>' + data.body + '</span></div></div>'
                );
            }
        }
    });
    return false;
};

var deleteForm = function () {
    var form = $(this).closest("form");
    var cont = $(this).closest(".media");

    $.ajax({
        url: form.attr("action"),
        data: form.serialize(),
        type: form.attr("method"),
        dataType: 'json',
        success: function (data) {
            if (data.is_valid){
                cont.addClass('d-none');
                var count = '#count-' + data.obj_pk;
                $(count).html(data.count);
            }
            
        }
    });
    return false;
};

function uploadImages() {
    /* 1. OPEN THE FILE EXPLORER WINDOW */
    $(".js-upload-photos").click(function () {
    $("#fileupload").click();
    });

    /* 2. INITIALIZE THE FILE UPLOAD COMPONENT */
    $("#fileupload").fileupload({
        dataType: 'json',
        sequentialUploads: true,  /* 3. SEND THE FILES ONE BY ONE */

        start: function (e) {  /* 2. WHEN THE UPLOADING PROCESS STARTS, SHOW THE MODAL */
          // $("#modal-progress").modal("show");
        },
        // stop: function(e){},
        progressall: function (e, data) {  /* 4. UPDATE THE PROGRESS BAR */
            var progress = parseInt(data.loaded / data.total * 100, 10);
            var strProgress = progress + "%";
            $(".progress-bar").css({"width": strProgress});
            $(".progress-bar").text(strProgress);
        },

        done: function(e, data){
            if (data.result.is_valid){
                $('#staff-imgs-list').append(
                    '<div class="col-md-3 col-sm-4 col-6 order-1 mb-1">'
                        + '<a href="' + data.result.next + '?img='+ data.result.pk +'">' 
                            + '<img src="'+ data.result.url +'" class="img-fluid">'
                        + '</a>'
                    + '</div>'
                );
                // $("#modal-progress").modal("hide");
            }
        }
    });

};


$(function infinite_scroll(){
    var infinite = new Waypoint.Infinite({
        element: $('.infinite-container')[0],
        onBeforePageLoad: function () {
            $('.loading').show();
        },
        onAfterPageLoad: function ($items) {
            $('.loading').hide();
        }
    });
});


$(function masonry(){
    var $container = $('#masonry-gallery');
        $container.masonry({
            columnWidth: '#item',
            itemSelector: '#item'
          }); 

    $container.imagesLoaded(function() {
      $container.masonry('layout');
        
    });
});