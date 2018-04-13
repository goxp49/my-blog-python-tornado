//打开字滑入效果
window.onload = function () {
    $(".connect p").eq(0).animate({"left": "0%"}, 600);
    $(".connect p").eq(1).animate({"left": "0%"}, 400);
};
//jquery.validate表单验证
$(document).ready(function () {
    //登陆表单验证
    $("#loginForm").validate({
        rules: {
            username: {
                required: true,//必填
                minlength: 3, //最少6个字符
                maxlength: 20,//最多20个字符
            },
            password: {
                required: true,
                minlength: 3,
                maxlength: 20,
            },
        },
        //错误信息提示
        messages: {
            username: {
                required: "必须填写用户名",
                minlength: "用户名至少为3个字符",
                maxlength: "用户名至多为20个字符",
                remote: "用户名已存在",
            },
            password: {
                required: "必须填写密码",
                minlength: "密码至少为3个字符",
                maxlength: "密码至多为20个字符",
            },
        },

    });
    //注册表单验证
    $("#registerForm").validate({
        rules: {
            username: {
                required: true,//必填
                minlength: 3, //最少6个字符
                maxlength: 20,//最多20个字符
                remote: {
                    url: "/register",//用户名重复检查，别跨域调用
                    type: "post",
                    dateType: "json",
                    cache: false,
                    data: {
                        target: "username",
                        //此处一定要写成匿名函数形式，不能写成username:$(".username").val()，否则一直返回空值
                        username: function () {
                            return $(".username").val();
                        }
                    }
                },
            },
            password: {
                required: true,
                minlength: 3,
                maxlength: 20,
            },
            email: {
                required: true,
                email: true,
            },
            confirm_password: {
                required: true,
                minlength: 3,
                equalTo: '.password'
            },
            phone_number: {
                required: true,
                phone_number: true,//自定义的规则
                digits: true,//整数
            }
        },
        //错误信息提示
        messages: {
            username: {
                required: "必须填写用户名",
                minlength: "用户名至少为3个字符",
                maxlength: "用户名至多为20个字符",
                remote: "用户名已存在",
            },
            password: {
                required: "必须填写密码",
                minlength: "密码至少为3个字符",
                maxlength: "密码至多为20个字符",
            },
            email: {
                required: "请输入邮箱地址",
                email: "请输入正确的email地址"
            },
            confirm_password: {
                required: "请再次输入密码",
                minlength: "确认密码不能少于3个字符",
                equalTo: "两次输入密码不一致",//与另一个元素相同
            },
            phone_number: {
                required: "请输入手机号码",
                digits: "请输入正确的手机号码",
            },

        },
    });
    //添加自定义验证规则
    jQuery.validator.addMethod("phone_number", function (value, element) {
        var length = value.length;
        var phone_number = /^(((13[0-9]{1})|(15[0-9]{1}))+\d{8})$/
        //当element为空时this.optional(element)=true，用于在该控件为非必填项目时可以通过验证，及条件可以不填但是不能填错格式。
        return this.optional(element) || (length == 11 && phone_number.test(value));
    }, "手机号码格式错误");
});
//点击登录时，通过ajax提交
$(function () {
    $('#submit_login').click(function () {
        alert("000000！");
        //如果不满足填写要求，则不执行操作
        if (!$("#loginForm").valid()) {
            return;
        }
        var params = $('#loginForm').serializeArray();
        var values = {};
        for (x in params) {
            values[params[x].name] = params[x].value;
        }
        alert("111111！");
        $.ajax({
            type: "post",
            dataType: "json",
            url: "/login",
            async: false,
            data: values,
            timeout: 5000,
            //因为dataType设为json，所以回传来的res已经被解析，可以通过XXX.YYY来调用里面的内容
            success: function (data) {
                alert("22222！");
                //判断用户名是否正确
                if (data.status) {
                    //跳转至管理界面
                    alert(data.url);
                    window.location.replace(data.url);
                    alert("4444444444444");
                }
                else {
                    alert(data.message);
                    window.location.replace(data.url);
                }
            },
            error: function () {
                alert("请检查账号或密码是否按要求输入！");
            }
        });
    });
});

//点击注册时，通过ajax提交
$(function () {
    $('#submit_register').click(function () {
        //如果不满足填写要求，则不执行操作
        if (!$("#registerForm").valid()) {
            return;
        }
        var params = $('#registerForm').serializeArray();
        var values = {};
        for (x in params) {
            values[params[x].name] = params[x].value;
            console.log(values[params[x].name]);
            console.log(params[x].value);
        }
        $.ajax({
            type: "post",
            dataType: "json",
            url: "/register",
            async: false,
            data: values,
            timeout: 5000,
            //因为dataType设为json，所以回传来的res已经被解析，可以通过XXX.YYY来调用里面的内容
            success: function (data) {
                //判断是否注册成功
                if (data.status) {
                    //跳转至登录界面
                    alert(data.message);
                    window.location.replace(data.url);
                }
                else {
                    alert(data.message);
                    window.location.replace(data.url);
                }
            },
            error: function () {
                alert("请先按要求输入信息！");
            }
        });
    });
});
