$(document).ready(function() {
    $.ajax({
        url: "" + ServerIp + "/Teacher/GetTeacher", //加上这句话 
        xhrFields: {
            withCredentials: true
        },
        crossDomain: true,
        type: 'GET',
        async: false,
        dataType: "text",
        data: {
        },
        success: function(data) {
            // alert(data);
            var data = JSON.parse(data);
            
            if (data.status == '4') {
                alert("未登陆");
                window.location.href = '' + ServerIp + '/static/exam/TeacherLogin.html';
            } else if (data.status == 1) {
                // alert(data.message);
                if (data.message == '1') {
                } else {
                    $("#question_back_manage").hide();
                    $("#teacher_manage").hide();
                    
                }
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
        	alert("error");
            window.location.href = '' + ServerIp + '/static/exam/TeacherLogin.html';
        }
    });
});
