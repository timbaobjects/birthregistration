<script>
	export let total = 0;
	export let contributing = 0;
	export let fresh = 0;

	const number = (val) => new Intl.NumberFormat().format(val)
</script>

<style>
	div.centres-overlay {
		position: absolute;
		z-index: 999;
		bottom: 2em;
		right: 10px;
		margin-right: 13.5px;
	}
	div.centre {
		backdrop-filter: saturate(100%) blur(5px);
		background-color: rgba(255, 255, 255, .90);
	}
	div.contributing {
		min-width: 11em;
	}
	div.total {
		min-width: 8em;
	}
	div.new {
		min-width: 7em;
	}
</style>

<div class="centres-overlay">
	<div class="row">
		<div class="col">
			<div class="card shadow centre total">
				<div class="card-body">
					<div class="text-center">
						<h5><strong>{number(total)}</strong></h5>
						<small class="font-weight-light">Total Centres</small>
					</div>
				</div>
			</div>
		</div>
		<div class="col">
			<div class="card shadow centre contributing">
				<div class="card-body">
					<div class="text-center">
						<h5><strong>{number(contributing)}</strong></h5>
						<small class="font-weight-light">Contributing Centres</small>
					</div>
				</div>
			</div>
		</div>
		<div class="col">
			<div class="card shadow centre new">
				<div class="card-body">
					<div class="text-center">
						<h5><strong>{number(fresh)}</strong></h5>
						<small class="font-weight-light">New Centres</small>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>