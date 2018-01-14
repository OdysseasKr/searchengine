var rates = {"good":[], "bad":[]};

$(".rate span").on("click", function (e) {
	var target = $(e.target);
	var spans = target.parent().find("span");
	if (target.hasClass("sel")) return;
	if (target.hasClass("unsel")) {
		if (target.data("rate") == "good") {
			rates.bad = rates.bad.filter(function(e) {
				return e !== target.closest(".result").data("resid");
			});
		} else {
			rates.good = rates.good.filter(function(e) {
				return e !== target.closest(".result").data("resid");
			});
		}
	}
	spans.removeClass("sel");
	spans.addClass("unsel");
	target.removeClass("unsel");
	target.addClass("sel");

	rates[$(e.target).data("rate")].push(target.closest(".result").data("resid"));
});


$(".feedbacksearch").on("click", function (e) {
	showLoading();
	$(".feedbacksearch").text("New results");
	$.ajax({
		url: "/feedbacksearch",
		method: "POST",
		data: rates
	}).done(function (res) {
		$(".feedbackmessage").text("New results");
		hideLoading();
		console.log(res);
	}).fail(function (res) {
		$(".feedbackmessage").text("There has been an error");
		hideLoading();
		console.log(res);
	});
});

function showLoading() {
	$(".fa-circle-o-notch").css("display","inline-block");
	$(".feedbacksearch").text("Finding new results");
}

function hideLoading() {
	$(".fa-circle-o-notch").css("display","none");
	$(".feedbacksearch").text("Repeat search with feedback");
}
