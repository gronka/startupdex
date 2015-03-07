$(function() {

	function pullFromAngelCo(rangestart, rangei) {
		$.ajax({
			url: '/db_angelco_get.json',
			data: JSON.stringify({rangestart: rangestart,
														rangei: rangei}),
			success: function(data) {
				//$('#angelco-results').html("sweet results")";
				document.getElementById('angelco-results').innerHTML = "sweet results";
			}
		});


	}

	$('#angelco-get-some').click(function() {
		rangestart = $('#angelco-rangestart').val();
		rangei = $('#angelco-rangei').val();

		pullFromAngelCo(rangestart, rangei);

		});


	function debounce(func, wait, immediate) {
		var timeout;
		return function() {
			var context = this, args = arguments
			clearTimeout(timeout);
			timeout = setTimeout(function() {
				timeout = null;
				if (!immediate) func.apply(context, args);
			}, wait);
			if (immediate && !timeout) func.apply(context, args);
		};
	}

	$(window).bind("load", function() {
		$.ajaxSetup({
			type: 'POST',
			dataType: 'json',
			xhrFields: { withCredentials: true },
			async: true,
			contentType: 'application/json; charset=utf-8',
			error: function() {
				alert("An error occurred.");
			}
		});
	});
});
