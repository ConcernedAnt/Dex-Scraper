//Ajax functions
//Modify the read status of the chapter on clicking checkbox.
$('input.ready_class').on('click', function(e) {
    e.stopPropagation();
    $.ajax({
        type: 'POST',
        url: '/update_read',
        data:{
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
            pk: $(this).attr('data-id')
        },
        success: function(){
        }
    });
});
//Update read status on clicking link and reload the page once done
$('a.ready_class').on('click', function(e) {
    var pk = $(this).attr('data-id');
    $.ajax({
        type: 'POST',
        url: '/update_read',
        data:{
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
            pk: pk
        },
        success: function(){
            location.reload(true);
        }
    });
});

$('button[name= "addcoll"]').on('click', function(e) {
    var pk = $(this).attr('data-id');
    $.ajax({
        type: 'POST',
        url: '/add_to_coll',
        data:{
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
            pk: pk
        },
        dataType: "json",
        success: function(data){
            alert("Added to collection");
            $("#"+pk).replaceWith(function(){
                return "<button type='button' class='btn btn-secondary' disabled>Already In Collection</button>";
            });
        }
    });
});