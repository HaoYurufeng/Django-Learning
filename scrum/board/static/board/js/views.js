/**
 * Created by li on 2017/1/12.
 */

(function ($, Backbone, _, app) {

    var TemplateView = Backbone.View.extend({
        templateName: '',
        initialize: function () {
            this.template = _.template($(this.templateName).html());
        },
        render: function () {
            var context = this.getContext(),
                html = this.template(context);
            this.$el.html(html)
        },
        getContext: function () {
            return {};
        }
    });
    /**
    var LoginView = Backbone.View.extend({
        id: 'login',
        templateName: '#login-template',
        initialize: function () {
            this.template = _.template($(this.templateName).html());
        },
        render: function () {
            var context = this.getContext(),
                html = this.template(context);
            this.$el.html(html);
        },
        getContext: function () {
            return {};
        }
    });

    var HomepageView = Backbone.View.extend({
        id: 'home',
        templateName: '#home-template',
        initialize: function() {
            this.template = _.template($(this.templateName).html());
        },
        render: function() {
            var context = this.getContext(),
            html = this.template(context);
            this.$el.html(html);
        },
        getContext: function () {
            return {};
        }
    });
     */
    /**出现重复，定义模板，调用模板，减少重复代码，以上代码用下边继承代替*/

    var HomepageView = TemplateView.extend({
        templateName: '#home-template'
    });

    var LoginView = TemplateView.extend({
        id: 'login',
        templateName: '#login-template',
        events:{
            'submit form': 'submit'
        },
        submit: function (event) {
            var data = {};
            event.preventDefault();
            this.form = $(event.currentTarget);
            data = {
                username:$(':input[name="username"]', this.form).val(),
                password:$(':input[name="password"]', this.form).val()
            };
            //Submit the login form
            $.post(app.apiLogin, data)
                .done($.proxy(this.loginSuccess, this))
                .fail($.proxy(this.loginFailure, this));
        },
        loginSuccess: function (data) {
            app.session.save(data.token);
            this.trigger('login', data.token);
        },
        loginFailure: function (xhr, status, error) {
            var errors = xhr.responseJSON;
            this.showErrors(errors);
        },
        showErrors: function () {
            // TODO: Show the errors from the response
        }
    });

    app.views.HomepageView = HomepageView;
    app.views.LoginView = LoginView;
})(jQuery, Backbone, _, app);
