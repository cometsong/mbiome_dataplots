///// run_info javascript /////


// from https://css-tricks.com/snippets/javascript/showhide-element/
function toggle_visibility(id) {
	var e = document.getElementById(id);
	if(e.style.display == 'block')
		e.style.display = 'none';
	else
		e.style.display = 'block';
}
// <!--<a href="#" onclick="toggle_visibility('foo');">Click here to toggle visibility of element #foo</a>-->
// <!--<div id="foo">This is foo</div>-->


// csv-to-table
// https://github.com/derekeder/csv-to-html-table


