$(".searchbtn").on("click", function (e) {
	var val = $("#searchbox").val().trim();
	if (val == "") return;
	var terms = val.replace(/ /g, "+");
	window.location.href = '/results?type='+e.target.id +
							'&collection='+document.querySelector("#collectionsel").value +
							'&q='+terms;
});
