$(".rate span").on("click", function (e) {
	var spans = $(e.target).parent().find("span");
	spans.removeClass("sel");
	spans.addClass("unsel");
	$(e.target).removeClass("unsel");
	$(e.target).addClass("sel");
});
