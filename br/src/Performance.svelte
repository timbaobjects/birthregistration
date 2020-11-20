<script>
	export let name = '';
	export let performance = 0;
	export let boys = 0;
	export let girls = 0;

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
</div>