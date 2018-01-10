$(".searchbtn").on("click", function (e) {
	var val = $("#searchbox").val().trim();
	if (val == "") return;
	var terms = val.replace(/ /g, "+");
	var new_url = '/results?type='+e.target.id +
							'&collection='+document.querySelector("#collectionsel").value
	if (e.target.id="vector") {
		new_url += '&topk=' + document.querySelector("#topk").value
	}
	new_url += '&q='+terms;
	window.location.href = new_url;

});
