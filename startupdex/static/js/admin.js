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
		var r = confirm("Are you sure you want to do this?");
		if (r == true) {
			rangestart = $('#angelco-rangestart').val();
			rangei = $('#angelco-rangei').val();
			pullFromAngelCo(rangestart, rangei);
		} else {
			alert("Action canceled");
		}
	});

	$('.remove-user').click(function() { 
		var r = confirm("Are you sure you want to remove this user? This action cannot be undone.");
		if (r == true) {
			admin_remove_user(this);
		} else {
			alert("Action canceled");
		}
	});
	function admin_remove_user(el) {
		var id_split = el.id.split('-');
		var user_id = id_split.pop();
		$.ajax({
			url: '/admin_remove_user.json',
			data: JSON.stringify({user_id: user_id
						}),
			success: function() {
				$(el.id).css( "background-color", "green" );
				alert("User was removed. Refresh the page to see changes.");
			}
		});
	}

	$('.update-user').click(function() { 
		var r = confirm("Are you sure you want to update this user?");
		if (r == true) {
			admin_update_user(this);
		} else {
			alert("Action canceled");
		}
	});
	function admin_update_user(el) {
		var id_split = el.id.split('-');
		var user_id = id_split.pop();
		var tr = $(el).parent().parent()
		$.ajax({
			url: '/admin_update_user.json',
			data: JSON.stringify({id: tr.find('.id').val(),
													 email: tr.find('.email').val(),
													 fullname: tr.find('.fullname').val(),
													 phone: tr.find('.phone').val(),
													 confirmed: tr.find('.confirmed').val(),
													 joined: tr.find('.joined').val(),
													 status: tr.find('.status').val(),
													 location: tr.find('.location').val(),
													 country: tr.find('.country').val(),
													 state_province: tr.find('.state_province').val(),
													 city: tr.find('.city').val(),
													 thumb_url: tr.find('.thumb_url').val(),
													 local_url: tr.find('.local_url').val(),
													 home_url: tr.find('.home_url').val(),
													 twitter_url: tr.find('.twitter_url').val(),
													 blog_url: tr.find('.blog_url').val(),
													 facebook_url: tr.find('.facebook_url').val(),
						}),
			success: function() {
				$(el.id).css( "background-color", "green" );
				alert("User was updated. Refresh the page to see changes.");
			}
		});
	}

	function pushToStartupdex(rangestart, rangei) {
		$.ajax({
			url: '/db_angelco_push_to_startupdex.json',
			data: JSON.stringify({rangestart: rangestart,
														rangei: rangei}),
			success: function(data) {
				//$('#angelco-results').html("sweet results")";
				document.getElementById('angelco-results').innerHTML = "sweet results";
			}
		});
	}
	$('#angelco-push-to-startupdex').click(function() {
		var r = confirm("Are you sure you want to do this?");
		if (r == true) {
			rangestart = $('#angelco-rangestart').val();
			rangei = $('#angelco-rangei').val();
			pushToStartupdex(rangestart, rangei);
		} else {
			alert("Action canceled");
		}
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
		
		$(':input[type=text]').on("input", function(event){
			$(event.target).css( "background-color", "yellow" );
		});
	});
});
