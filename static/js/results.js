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
		url: "/feedbacksearch"+window.location.search,
		method: "POST",
		contentType: "application/json",
		data: JSON.stringify(rates)
	}).done(function (res) {
		$(".feedbackmessage").text("New results");
		var rates = {"good":[], "bad":[]};
		$(".unsel, .sel").removeClass("unsel").removeClass("sel");
		hideLoading();
		displayNewResults(res);
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

function displayNewResults(res) {
	$(".resultlist").empty();
	for (var i=0; i<res.length; i++) {
		result = res[i];
		var outterDiv = $("<div></div", {
			class: "result",
			"data-resid": result.id
		});
		$("<h3></h3>", {
			text: result.title
		}).appendTo(outterDiv);
		$("<a></a>", {
			text: result.url,
			href: result.url
		}).appendTo(outterDiv);
		$("<p></p>", {
			text: result.excerpt
		}).appendTo(outterDiv);

		$('<div class="rate"><p>How good was this result?<p><span class="best" data-rate="good"></span><span class="worst" data-rate="bad"></span></div>').appendTo(outterDiv);

		$(".resultlist").append(outterDiv);
	}
}
