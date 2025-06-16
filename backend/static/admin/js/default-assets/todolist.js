(function ($) {
    'use strict';
    $(function () {
         var todoListItem = $('.todo-list');
        
        $(document).on("click", ".string-check-label", function () {
            if ($(this).prev().prop('checked') == true) {
                $(this).parents(':eq(1)').removeClass("completed text-base");
            } else {
                $(this).parents(':eq(1)').addClass("completed text-base");
            }
        });

        $(document).on("click", ".remove", function () {
            $(this).parent().fadeOut(300, function () {
                $(this).remove();
            });
        });

        todoListItem.on('change', '.checkbox', function () {
            if ($(this).attr('checked')) {
                $(this).removeAttr('checked');
            } else {
                $(this).attr('checked', 'checked');
            }

            $(this).closest("li").toggleClass('completed');

        });

        $(".add-new-todo").click(function () {
            var title = $(this).prev().val();
            if (title != "") {
                var id = Math.random();
                $(".todo-list").append('<li class="d-flex align-items-center justify-content-between mb-20"><div class="string-check string-check-bordered-base checkbox d-inline p-0"><input type="checkbox" name="checkbox-13" id="checkbox-13' + id + '"><label class="string-check-label cr" for="checkbox-13' + id + '"><span class="ml-2">' + title + '</span></label></div><a href="#" class="remove"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-trash-2 todo-icon"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg></a></li>').children(':last').hide().fadeIn(2000);
                feather.replace();
            }
        });
    });
})(jQuery);