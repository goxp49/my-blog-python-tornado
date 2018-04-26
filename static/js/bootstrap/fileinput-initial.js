// initialize with defaults
$("#input-file").fileinput({

    language: 'zh', //设置语言

    uploadUrl: "/system/handle/fileupload", //上传的地址

    allowedFileExtensions: ['jpg', 'gif', 'png'],//接收的文件后缀

    //uploadExtraData:{"id": 1, "fileName":'123.mp3'},

    uploadAsync: true, //默认异步上传

    showUpload: false, //是否显示上传按钮

    showRemove: true, //显示移除按钮

    showPreview: true, //是否显示预览

    showCaption: false,//是否显示标题

    browseClass: "btn btn-primary", //按钮样式

    dropZoneEnabled: false,//是否显示拖拽区域

    //minImageWidth: 50, //图片的最小宽度

    //minImageHeight: 50,//图片的最小高度

    //maxImageWidth: 1000,//图片的最大宽度

    //maxImageHeight: 1000,//图片的最大高度

    maxFileSize: 5 * 1024,//单位为kb，如果为0表示不限制文件大小

    //minFileCount: 0,

    maxFileCount: 1, //表示允许同时上传的最大文件个数

    enctype: 'multipart/form-data',

    validateInitialCount: true,

    previewFileIcon: "<iclass='glyphicon glyphicon-king'></i>",

    msgFilesTooMany: "选择上传的文件数量({n}) 超过允许的最大数值{m}！",

    layoutTemplates: {
        actionDelete:'', //去除上传预览的缩略图中的删除图标
        actionUpload: '',//去除上传预览缩略图中的上传图片；
        actionZoom: ''   //去除上传预览缩略图中的查看详情预览的缩略图标。
    },

}).on("fileuploaded", function (event, data, previewId, index) {


});

// with plugin options
//$("#input-file").fileinput({'showUpload':false, 'previewFileType':'any'});