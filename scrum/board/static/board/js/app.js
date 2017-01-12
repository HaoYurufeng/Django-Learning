/**
 * Created by li on 2017/1/12.
 */

var app = (function ($) {
    var config = $('#config'),
        app = JSON.parse(config.text());

    $(document).ready(function () {
       var router = new app.router();
    });

    return app;
})(jQuery);
