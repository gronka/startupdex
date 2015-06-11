$(function() {
	var url = window.location.href.split('/');
	var current_page = url[url.length - 1];
	// get next page path if we're simply pulling an ID
	if (isNaN(current_page) == false) {
		current_page = url[url.length -2];
	}
	var current_host = "http://"+url[2];
	//var startup_scroller_trigger = 110;
	//var startup_scroller_pull_count = 10;

	function parseStartupScroller(startups, el, options) {
		//alert(current_host);
		options = options || [];
		$(el).empty();
		$.each(startups, function(i, startup) {
			var div = document.createElement('div');
			div.className = "startup-scroller-result";

			var a = document.createElement('a');
			a.href = current_host + "/startup/" + startup.local_url;
			a.textContent = "link";
			var img = document.createElement('img');
			img.src = current_host + "/images/" + startup.logo_url;
			img.width = "80";
			img.height = "50";
			var h4 = document.createElement('h4');
			h4.textContent = startup.name;

			var p = document.createElement('p');
			p.textContent = startup.short_info;

			var id = document.createElement('div');
			//id.className = startup.id
			id.className = "id"
			id.textContent = startup.id;
			id.style.visibility = "hidden";


			div.appendChild(img);
			div.appendChild(h4);

			$.each(options, function(j, option) {
				//TODO: parse text so that frontpage-db isn't manually inserted here
				if (option == "remove") {
					var button = document.createElement('div');
					button.className = "btn btn-danger remove-from-frontpage-db";
					var i = document.createElement('i');
					i.className = "glyphicon glyphicon-remove";
				} else if (option == "add") {
					var button = document.createElement('div');
					button.className = "btn btn-success add-to-frontpage-db";
					var i = document.createElement('i');
					i.className = "glyphicon glyphicon-plus";
				}
				button.appendChild(i);
				div.appendChild(button);
			});

			div.appendChild(p);
			div.appendChild(a);
			div.appendChild(id);

			$(el).append(div);
		});
	}

	function startupSearchByName() {
		$.ajax({
			url: '/startup_search_by_name.json',
			data: JSON.stringify({startup_search_by_name: $('#startup_search_by_name').val()}),
			success: function(data) {
			  parseStartupScroller(data, $("#startup-search-scroller"), ['add']);
				$('.add-to-frontpage-db').click(function() {
					addToFrontpageDB(this)
				});
			}
		});
	}
	$('#startup-search-by-name').keyup(debounce(function() {
			startupSearchByName()
		}, 400)
	);
	$('#startup-search-by-name').click(function() {
			startupSearchByName()
		}
	);


	function getFrontpageDB() {
		$.ajax({
			url: '/admin_get_frontpage_db.json',
			data: JSON.stringify(),
			success: function(data) {
				parseStartupScroller(data, $("#frontpage-db-scroller"), ['remove']);
				$('.remove-from-frontpage-db').click(function() {
					removeFromFrontpageDB(this);
				});
			}
		});

	}
	function addToFrontpageDB(el) {
		//startupid = $(el).find(".id").attr("class");
		var startup = $(el).parent();
		var startupid = startup.find(".id").html();
		$.ajax({
			url: '/admin_add_to_frontpage_db.json',
			data: JSON.stringify({startupid: startupid}),
			success: function(data) {
				if (data == "Already listed") {
					alert("Startup is already listed on the frontpage");
				} else {
					getFrontpageDB();
				}
			}
		});
	}

	function removeFromFrontpageDB(el) {
		var startup = $(el).parent();
		var startupid = startup.find(".id").html();
		$.ajax({
			url: '/admin_remove_from_frontpage_db.json',
			data: JSON.stringify({startupid: startupid}),
			success: function(data) {
				getFrontpageDB();
			}
		});
	}


	function pullFromAngelCo(rangestart, rangei) {
		$.ajax({
			url: '/db_angelco_get.json',
			data: JSON.stringify({rangestart: rangestart,
														rangei: rangei}),
			success: function(data) {
				//$('#angelco-results').html("sweet results")";
				document.getElementById('angelco-results').innerHTML = "sweet results";
				alert("pull completed");
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
	
	function admin_change_password(el) {
		var pr = $(el).parent().parent();
		var userid = pr.find("id").html();
		var password = pr.find(".password").val();
		$.ajax({
			url: '/admin_change_password.json',
			data: JSON.stringify({
				userid: userid,
				password: password
			}),
			success: function(data) {
				alert("Password was updated.");
			}
		});
	}
	$(".admin-change-password").click(function () {
		var r = confirm("Are you sure you want to change this password?");
		if (r == true) {
			admin_change_password(this);
		} else {
			alert("Action canceled");
		}
	});

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
		if (document.getElementById('frontpage-db-scroller') != 'undefined') {
			getFrontpageDB();
		}
		//$('.startup-search-scroller').scroll(debounce(function() {
			//if ($('.startup-search-scroller').height() - $('.startup-search-scroller').scrollTop()  < startup_scroller_trigger){
				//alert('okay');
			//}
		//}, 400));
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
