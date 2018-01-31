$(window).keydown(function(event){
	if(event.keyCode == 13) {
		event.preventDefault();
		return false;
	}
});

$("#uploadbtn").click(function (e) {
	$(".notice").text("");
	var name = $("#namebox").val().trim();
	if (name == "") {
		$(".notice").text("No collection name given");
		return;
	}

	var files = $("#collectionbox")[0].files;
	if (files.length == 0) {
		$(".notice").text("Collection is empty");
		return;
	}

	var fd = new FormData($("#mainform")[0]);
	$("#uploadbtn").prop("disabled", true);
	$.ajax({
		xhr: function() {
			var xhr = new window.XMLHttpRequest();
			xhr.upload.addEventListener("progress", function(evt) {
				if (evt.lengthComputable) {
					var percent = Math.floor((evt.loaded / evt.total) * 100);
					if (percent == 100)
						$("#uploadbtn").text("Preprocessing collection");
					else
						$("#uploadbtn").text(percent + "%");
				}
			}, false);
			return xhr;
		},
		url: "/uploadcollection",
		processData: false,
		method: "POST",
		contentType: false,
		data: fd,
	})
	.then(function (resp) {
		if (resp.success) {
			$(".notice").text("The collection has been created");
		} else {
			$(".notice").text(resp.message);
		}

		$("#uploadbtn").text("Upload collection");
		$("#uploadbtn").prop("disabled", false);
	});
});
