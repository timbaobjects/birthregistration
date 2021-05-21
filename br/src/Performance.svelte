<script>
	export let name = '';
	export let performance = 0;
	export let boys = 0;
	export let girls = 0;
	export let downloadHandler = () => {};

	const number = (val) => new Intl.NumberFormat().format(val)
</script>

<style>
	div.performance-overlay {
		position: absolute;
		z-index: 999;
		top: 5em;
		left: 10px;
		backdrop-filter: saturate(100%) blur(5px);
		background-color: rgba(255, 255, 255, .90);
	}
</style>

<div class="card performance-overlay shadow w-25">
	<h5 class="card-header">{name.toUpperCase()}</h5>
	<div class="card-body">
		<div class="text-center mb-4">
			<h2 class="display-2">{number(Math.round(performance))}%</h2>
			<p class="lead mt-n2">Performance</p>
		</div>
		<div class="d-flex flex-row justify-content-between">
			<div class="w-50 text-center border-right">
				<h5 class="lead">Boys</h5>
				<h4><strong>{number(boys)}</strong></h4>
			</div>
			<div class="w-50 text-center">
				<h5 class="lead">Girls</h5>
				<h4><strong>{number(girls)}</strong></h4>
			</div>
		</div>
	</div>
	<div class="card-footer">
		<button class="btn btn-outline-dark" on:click={downloadHandler}><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-download" viewBox="0 0 16 16"><path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/><path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/></svg> Export</button>
	</div>
</div>